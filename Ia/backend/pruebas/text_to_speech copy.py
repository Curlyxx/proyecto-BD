from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import analisis_frases
from conversational_handler import ConversationalHandler
from gtts import gTTS
from duckduckgo_search import DDGS
from PIL import Image
from io import BytesIO
import base64
import uuid
import re
import mysql.connector
from datetime import datetime

app = Flask(__name__)
CORS(app)

handler_conversacional = ConversationalHandler()

# Configuración de la base de datos
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "chats1"
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/crear_conversacion', methods=['POST'])
def crear_conversacion():
    data = request.get_json()
    nombre_chat = data.get('nombre_chat', 'Nueva conversación')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO conversaciones (nombre, fecha_creacion) VALUES (%s, %s)",
            (nombre_chat, datetime.now())
        )
        conversacion_id = cursor.lastrowid
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "conversacion_id": conversacion_id,
            "message": "Conversación creada exitosamente"
        })
    except Exception as e:
        print(f"Error al crear conversación: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def guardar_mensaje(conversacion_id, tipo, contenido, sentimiento=None, ruta_audio=None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql = """
            INSERT INTO mensajes (conversacion_id, tipo, contenido, sentimiento, ruta_audio, fecha_creacion)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            conversacion_id,
            tipo,
            contenido,
            sentimiento,
            ruta_audio,
            datetime.now()
        )
        
        cursor.execute(sql, params)
        conn.commit()
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error al guardar mensaje: {e}")
        return False

@app.route('/guardar_mensaje', methods=['POST'])
def api_guardar_mensaje():
    data = request.get_json()
    
    required_fields = ['conversacion_id', 'contenido', 'tipo']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Faltan campos requeridos"}), 400
    
    try:
        success = guardar_mensaje(
            conversacion_id=data['conversacion_id'],
            tipo=data['tipo'],
            contenido=data['contenido'],
            sentimiento=data.get('sentimiento'),
            ruta_audio=data.get('ruta_audio')
        )
        
        if success:
            return jsonify({"success": True})
        return jsonify({"success": False, "error": "No se pudo guardar el mensaje"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def verificar_conversacion(conversacion_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM conversaciones WHERE id = %s", (conversacion_id,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        return result is not None
    except Exception as e:
        print(f"Error al verificar conversación: {e}")
        return False

def es_comando_imagen(texto):
    patrones = [
        r'^generar?\s*imagen:?\s*(.+)$',
        r'^genera:?\s*(.+)$',
        r'^buscar?\s*imagen:?\s*(.+)$',
        r'^imagen\s+de:?\s*(.+)$'
    ]
    
    for patron in patrones:
        match = re.search(patron, texto, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None

def buscar_imagen(prompt):
    try:
        with DDGS() as ddgs:
            results = ddgs.images(prompt, max_results=1)
            if not results:
                return None
            
            imagen_url = results[0]["image"]
            response = requests.get(imagen_url)
            if response.status_code != 200:
                return None
                
            filename = f"{uuid.uuid4()}.jpg"
            img_path = os.path.join(os.path.dirname(__file__), "static", filename)
            
            img = Image.open(BytesIO(response.content))
            img.save(img_path)
            
            return {
                "url": f"/static/{filename}",
                "prompt": prompt
            }
    except Exception as e:
        print(f"Error al buscar imagen: {e}")
        return None

@app.route('/buscar_imagen', methods=['GET'])
def api_buscar_imagen():
    prompt = request.args.get('prompt')
    if not prompt:
        return jsonify({"error": "Prompt no proporcionado"}), 400
        
    resultado = buscar_imagen(prompt)
    if not resultado:
        return jsonify({"error": "No se pudo encontrar o procesar la imagen"}), 404
        
    return jsonify(resultado)

def obtener_info_wikipedia(termino):
    try:
        search_url = f"https://es.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch={termino}"
        search_response = requests.get(search_url).json()

        if not search_response.get('query', {}).get('search'):
            return None

        titulo = search_response['query']['search'][0]['title']
        content_url = f"https://es.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&exintro=true&explaintext=true&titles={titulo}"
        content_response = requests.get(content_url).json()

        page = next(iter(content_response['query']['pages'].values()))
        contenido_completo = page.get('extract', '')

        contenido_completo = re.sub(r'\[\d+\]', '', contenido_completo)
        contenido_completo = contenido_completo.replace('\n', ' ').replace('\r', '')
        contenido_completo = ' '.join(contenido_completo.split())
        
        if len(contenido_completo) > 500:
            ultimo_punto = contenido_completo[:500].rfind('.')
            if ultimo_punto == -1 or 500 - ultimo_punto > 100:
                ultimo_punto = contenido_completo.find('.', 500)
                if ultimo_punto == -1:
                    ultimo_punto = 500
            
            contenido = contenido_completo[:ultimo_punto + 1]
        else:
            contenido = contenido_completo

        contenido_audio = contenido

        return {
            "titulo": titulo,
            "contenido": contenido,
            "contenido_audio": contenido_audio
        }
    except Exception as e:
        print(f"Error en obtener_info_wikipedia: {e}")
        return None

@app.route('/obtener_info', methods=['GET'])
def obtener_info():
    termino = request.args.get('termino')
    if not termino:
        return jsonify({"error": "Término no proporcionado"}), 400
    
    conversacion_id = request.args.get('conversacion_id')
    conversacion_id = int(conversacion_id) if conversacion_id and conversacion_id.isdigit() else None
    
    if conversacion_id and not verificar_conversacion(conversacion_id):
        conversacion_id = None
    
    if not conversacion_id:
        nueva_conversacion = crear_conversacion()
        if not nueva_conversacion or not nueva_conversacion.json['success']:
            return jsonify({"error": "No se pudo crear una nueva conversación"}), 500
        conversacion_id = nueva_conversacion.json['conversacion_id']
    
    guardar_mensaje(conversacion_id, 'usuario', termino)
    
    prompt_imagen = es_comando_imagen(termino)
    if prompt_imagen:
        resultado = buscar_imagen(prompt_imagen)
        if resultado:
            contenido_respuesta = f"Aquí tienes una imagen de '{prompt_imagen}'"
            guardar_mensaje(conversacion_id, 'ai', contenido_respuesta)
            
            return jsonify({
                "tipo": "imagen",
                "contenido": contenido_respuesta,
                "contenido_audio": f"Aquí tienes una imagen de {prompt_imagen}",
                "imagen_url": resultado["url"],
                "prompt": prompt_imagen,
                "conversacion_id": conversacion_id
            })
        else:
            contenido_respuesta = f"Lo siento, no pude encontrar una imagen para '{prompt_imagen}'"
            guardar_mensaje(conversacion_id, 'ai', contenido_respuesta)
            return jsonify({
                "contenido": contenido_respuesta,
                "contenido_audio": f"No pude encontrar una imagen que coincida con tu búsqueda de {prompt_imagen}",
                "conversacion_id": conversacion_id
            })

    respuesta_conversacional = handler_conversacional.procesar_entrada(termino)
    
    if respuesta_conversacional:
        guardar_mensaje(
            conversacion_id, 
            'ai', 
            respuesta_conversacional.get("contenido", ""), 
            sentimiento=respuesta_conversacional.get("sentimiento")
        )
        
        respuesta_conversacional["conversacion_id"] = conversacion_id
        return jsonify(respuesta_conversacional)
    
    sentimiento = analisis_frases.analizar_frase(termino)
    info = obtener_info_wikipedia(termino)
    if not info:
        return jsonify({"error": "No se encontró información", "conversacion_id": conversacion_id}), 404

    info["sentimiento"] = sentimiento
    
    prefijo = ""
    if sentimiento == "NEG":
        prefijo = "⚠️ Detectamos un tono negativo en tu consulta. "
    elif sentimiento == "POS":
        prefijo = "😊 Detectamos un tono positivo en tu consulta. "
    
    info["contenido"] = prefijo + info["contenido"]
    info["contenido_audio"] = prefijo + info["contenido_audio"]
    
    guardar_mensaje(conversacion_id, 'ai', info["contenido"], sentimiento=info.get("sentimiento"))
    info["conversacion_id"] = conversacion_id
    
    return jsonify(info)

@app.route('/hablar', methods=['GET'])
def hablar():
    texto = request.args.get('texto')
    idioma = request.args.get('idioma', 'es')
    tld = request.args.get('tld', 'es')
    rapido = request.args.get('rapido', 'false').lower() == 'true'

    if not texto:
        return jsonify({"error": "Texto no proporcionado"}), 400

    try:
        static_folder = os.path.join(os.path.dirname(__file__), "static")
        if not os.path.exists(static_folder):
            os.makedirs(static_folder)

        output_file = os.path.join(static_folder, "output.mp3")
        
        tts = gTTS(text=texto, lang=idioma, tld=tld, slow=not rapido)
        tts.save(output_file)

        return jsonify({
            "mensaje": "Texto hablado con éxito",
            "audioUrl": f"/static/output.mp3",
            "textoUtilizado": texto[:100] + "..." if len(texto) > 100 else texto
        })
    except Exception as e:
        return jsonify({"error": f"Error en la conversión de texto a voz: {e}"}), 500

@app.route('/static/<filename>')
def serve_file(filename):
    return app.send_static_file(filename)

if __name__ == '__main__':
    static_folder = os.path.join(os.path.dirname(__file__), "static")
    if not os.path.exists(static_folder):
        os.makedirs(static_folder)

    app.run(debug=True, port=5001)
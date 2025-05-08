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

@app.route('/eliminar_conversacion/<int:conversacion_id>', methods=['DELETE'])
def eliminar_conversacion(conversacion_id):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="chats1"
        )
        cursor = conn.cursor()
        
        # Primero eliminar los mensajes asociados a la conversación
        cursor.execute("DELETE FROM mensajes WHERE conversacion_id = %s", (conversacion_id,))
        
        # Luego eliminar la conversación
        cursor.execute("DELETE FROM conversaciones WHERE id = %s", (conversacion_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"success": True, "message": f"Conversación {conversacion_id} eliminada correctamente"})
    except Exception as e:
        print(f"Error al eliminar conversación: {e}")
        return jsonify({"error": str(e)}), 500
def guardar_mensaje(conversacion_id, tipo, contenido, sentimiento=None, ruta_audio=None, ruta_imagen=None):
    try:
        print(f"\n--- Intentando guardar mensaje ---")
        print(f"Conversación ID: {conversacion_id}")
        print(f"Tipo: {tipo}")
        # Muestra solo los primeros 100 caracteres
        print(f"Contenido: {contenido[:100]}...")
        print(f"Sentimiento: {sentimiento}")
        print(f"Ruta audio: {ruta_audio}")
        print(f"Ruta imagen: {ruta_imagen}")

        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="chats1"
        )
        print("Conexión a DB establecida correctamente")

        cursor = conn.cursor()

        # Si es un mensaje de audio, primero verificamos si ya existe uno para esta conversación
        if tipo == 'audio' and ruta_audio:
            print("Verificando si ya existe un audio para esta conversación...")
            cursor.execute("""
                SELECT id FROM mensajes 
                WHERE conversacion_id = %s AND tipo = 'audio'
                LIMIT 1
            """, (conversacion_id,))
            existing_audio = cursor.fetchone()

            if existing_audio:
                print(
                    f"Audio existente encontrado con ID: {existing_audio[0]}, actualizando...")
                update_sql = """
                    UPDATE mensajes 
                    SET contenido = %s, ruta_audio = %s, fecha_creacion = %s
                    WHERE id = %s
                """
                cursor.execute(update_sql, (contenido, ruta_audio,
                               datetime.now(), existing_audio[0]))
                conn.commit()
                print("Audio actualizado correctamente")
                cursor.close()
                conn.close()
                return True

        # Si no es audio o no existía uno previo, insertamos nuevo mensaje
        sql = """
            INSERT INTO mensajes (conversacion_id, tipo, contenido, sentimiento, ruta_audio, ruta_imagen, fecha_creacion)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            conversacion_id,
            tipo,
            contenido,
            sentimiento,
            ruta_audio,
            ruta_imagen,
            datetime.now()
        )
        print(f"Ejecutando SQL con parámetros: {params}")

        cursor.execute(sql, params)
        conn.commit()
        print("Commit realizado correctamente")

        # Verificar si realmente se insertó
        cursor.execute("SELECT LAST_INSERT_ID()")
        last_id = cursor.fetchone()[0]
        print(f"Último ID insertado: {last_id}")

        cursor.close()
        conn.close()
        print(
            f"Mensaje guardado correctamente en la base de datos para la conversación {conversacion_id}")
        return True
    except Exception as e:
        print(f"\n--- ERROR al guardar mensaje ---")
        print(f"Tipo de error: {type(e).__name__}")
        print(f"Mensaje de error: {str(e)}")
        import traceback
        traceback.print_exc()  # Esto imprime el traceback completo
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

            # Descargar la imagen
            response = requests.get(imagen_url)
            if response.status_code != 200:
                return None

            # Guardar la imagen localmente
            filename = f"{uuid.uuid4()}.jpg"
            img_path = os.path.join(
                os.path.dirname(__file__), "static", filename)

            img = Image.open(BytesIO(response.content))
            img.save(img_path)

            return {
                "url": f"http://localhost:5001/static/{filename}",
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


# Nueva función para crear chat explícitamente
@app.route('/crear_chat', methods=['POST'])
def crear_chat():
    """Crear una nueva conversación en la base de datos y devolver su ID"""
    try:
        print("Creando nueva conversación...")
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="chats1"
        )
        cursor = conn.cursor()

        # Extraer título del chat si viene en el request
        data = request.get_json() or {}
        titulo = data.get('titulo', 'Nuevo chat')

        cursor.execute("INSERT INTO conversaciones (titulo, fecha_creacion) VALUES (%s, %s)",
                       (titulo, datetime.now()))
        conversacion_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Nueva conversación creada con ID: {conversacion_id}")
        return jsonify({
            "success": True,
            "conversacion_id": conversacion_id,
            "titulo": titulo
        })
    except Exception as e:
        print(f"Error al crear nueva conversación: {e}")
        return jsonify({"error": f"No se pudo crear la conversación: {str(e)}"}), 500


def verificar_conversacion(conversacion_id):
    """Verificar si la conversación existe en la base de datos"""
    if not conversacion_id:
        return False

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="chats1"
        )
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM conversaciones WHERE id = %s", (conversacion_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        return result is not None
    except Exception as e:
        print(f"Error al verificar conversación: {e}")
        return False


# Nueva ruta para obtener todas las conversaciones
@app.route('/conversaciones', methods=['GET'])
def obtener_conversaciones():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="chats1"
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, titulo, fecha_creacion 
            FROM conversaciones 
            ORDER BY fecha_creacion DESC
        """)
        conversaciones = cursor.fetchall()
        cursor.close()
        conn.close()

        # Convertir las fechas a formato string para evitar problemas con JSON
        for conv in conversaciones:
            if 'fecha_creacion' in conv and conv['fecha_creacion']:
                conv['fecha_creacion'] = conv['fecha_creacion'].isoformat()

        return jsonify({"conversaciones": conversaciones})
    except Exception as e:
        print(f"Error al obtener conversaciones: {e}")
        return jsonify({"error": str(e)}), 500


# Nueva ruta para obtener mensajes de una conversación
@app.route('/mensajes/<int:conversacion_id>', methods=['GET'])
def obtener_mensajes(conversacion_id):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="chats1"
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, tipo, contenido, sentimiento, ruta_audio, ruta_imagen, fecha_creacion
            FROM mensajes
            WHERE conversacion_id = %s
            ORDER BY fecha_creacion ASC
        """, (conversacion_id,))
        mensajes = cursor.fetchall()
        cursor.close()
        conn.close()

        # Convertir las fechas a formato string para evitar problemas con JSON
        for msg in mensajes:
            if 'fecha_creacion' in msg and msg['fecha_creacion']:
                msg['fecha_creacion'] = msg['fecha_creacion'].isoformat()

        return jsonify({"conversacion_id": conversacion_id, "mensajes": mensajes})
    except Exception as e:
        print(f"Error al obtener mensajes: {e}")
        return jsonify({"error": str(e)}), 500


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

        import re
        contenido_completo = re.sub(r'\[\d+\]', '', contenido_completo)
        contenido_completo = contenido_completo.replace(
            '\n', ' ').replace('\r', '')
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
    """
    Flujo modificado:
    1. Exigir un ID de conversación válido
    2. Verificar que ese ID exista en la base de datos
    3. Si no existe, devolver un error indicando que se debe crear una conversación
    4. Guardar el mensaje del usuario
    5. Procesar la respuesta
    6. Guardar la respuesta del asistente
    """
    termino = request.args.get('termino')
    if not termino:
        return jsonify({"error": "Término no proporcionado"}), 400

    # Depuración para verificar qué parámetros se reciben
    print("\n--- Parámetros recibidos ---")
    print(f"Todos los parámetros: {request.args}")
    print(f"Término: {termino}")

    # Exigimos el ID de conversación
    conversacion_id = request.args.get('conversacion_id')
    if not conversacion_id:
        return jsonify({
            "error": "Es necesario un ID de conversación. Crea un nuevo chat primero.",
            "code": "NO_CONVERSATION_ID"
        }), 400

    print(
        f"Conversación ID recibido: {conversacion_id}, tipo: {type(conversacion_id)}")

    # Validar el ID de conversación
    try:
        conversacion_id = int(conversacion_id)
        print(f"Conversación ID convertido a entero: {conversacion_id}")

        # Verificar que la conversación existe en la BD
        if not verificar_conversacion(conversacion_id):
            return jsonify({
                "error": f"La conversación con ID {conversacion_id} no existe. Crea un nuevo chat primero.",
                "code": "INVALID_CONVERSATION_ID"
            }), 404

    except (ValueError, TypeError):
        print(
            f"Error al convertir conversacion_id: {conversacion_id} a entero")
        return jsonify({
            "error": "El ID de conversación debe ser un número entero válido.",
            "code": "INVALID_CONVERSATION_ID_FORMAT"
        }), 400

    # Guardar mensaje del usuario
    guardado = guardar_mensaje(conversacion_id, 'usuario', termino)
    print(f"Mensaje del usuario guardado: {guardado}")

    # Verificar si es un comando de imagen
    prompt_imagen = es_comando_imagen(termino)
    if prompt_imagen:
        resultado = buscar_imagen(prompt_imagen)
        if resultado:
            contenido_respuesta = f"Aquí tienes una imagen de '{prompt_imagen}'"

            # Guardar la respuesta del asistente con la ruta de la imagen
            guardar_mensaje(
                conversacion_id,
                'ai',
                contenido_respuesta,
                ruta_imagen=resultado["url"]
            )

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

            # Guardar la respuesta del asistente primero
            guardar_mensaje(conversacion_id, 'ai', contenido_respuesta)

            return jsonify({
                "contenido": contenido_respuesta,
                "contenido_audio": f"No pude encontrar una imagen que coincida con tu búsqueda de {prompt_imagen}",
                "conversacion_id": conversacion_id
            })

    # Si no es un comando de imagen, continuar con el procesamiento normal
    respuesta_conversacional = handler_conversacional.procesar_entrada(termino)

    if respuesta_conversacional:
        # Guardar la respuesta del asistente
        guardar_mensaje(
            conversacion_id,
            'ai',
            respuesta_conversacional.get("contenido", ""),
            sentimiento=respuesta_conversacional.get("sentimiento")
        )

        # Añadir el ID de conversación a la respuesta
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

    # Guardar la respuesta del asistente
    guardar_mensaje(conversacion_id, 'ai',
                    info["contenido"], sentimiento=info.get("sentimiento"))

    # Añade el ID de conversación a la respuesta
    info["conversacion_id"] = conversacion_id

    return jsonify(info)


@app.route('/hablar', methods=['GET'])
def hablar():
    texto = request.args.get('texto')
    idioma = request.args.get('idioma', 'es')
    tld = request.args.get('tld', 'es')
    rapido = request.args.get('rapido', 'false').lower() == 'true'
    conversacion_id = request.args.get('conversacion_id')

    if not texto:
        return jsonify({"error": "Texto no proporcionado"}), 400

    try:
        static_folder = os.path.join(os.path.dirname(__file__), "static")
        if not os.path.exists(static_folder):
            os.makedirs(static_folder)

        # Generamos un nombre de archivo único basado en el conversation_id
        if conversacion_id and conversacion_id.isdigit():
            output_filename = f"audio_{conversacion_id}.mp3"
        else:
            output_filename = "output.mp3"

        output_file = os.path.join(static_folder, output_filename)

        print(f"\n--- Generando audio ---")
        print(f"Texto a convertir: {texto[:100]}...")
        print(f"Archivo de salida: {output_file}")
        print(f"Conversación ID: {conversacion_id}")

        tts = gTTS(text=texto, lang=idioma, tld=tld, slow=not rapido)
        tts.save(output_file)
        print("Audio generado correctamente")

        audio_url = f"http://localhost:5001/static/{output_filename}"

        # Si se proporciona un conversacion_id válido, actualiza el último mensaje de tipo 'ai'
        if conversacion_id and conversacion_id.isdigit():
            conversacion_id = int(conversacion_id)
            print(
                f"Actualizando mensaje de AI con ruta de audio para conversación {conversacion_id}")

            try:
                conn = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",
                    database="chats1"
                )
                cursor = conn.cursor()

                # Buscar el último mensaje de tipo 'ai' para esta conversación
                cursor.execute("""
                    SELECT id FROM mensajes 
                    WHERE conversacion_id = %s AND tipo = 'ai'
                    ORDER BY fecha_creacion DESC
                    LIMIT 1
                """, (conversacion_id,))

                ultimo_mensaje = cursor.fetchone()

                if ultimo_mensaje:
                    mensaje_id = ultimo_mensaje[0]
                    print(f"Actualizando mensaje AI con ID: {mensaje_id}")

                    # Actualizar el mensaje existente con la ruta de audio
                    cursor.execute("""
                        UPDATE mensajes 
                        SET ruta_audio = %s
                        WHERE id = %s
                    """, (audio_url, mensaje_id))

                    conn.commit()
                    print(
                        f"Mensaje AI actualizado con la ruta de audio: {audio_url}")
                else:
                    print(
                        "No se encontró un mensaje de AI reciente para actualizar")

                cursor.close()
                conn.close()

            except Exception as e:
                print(
                    f"Error al actualizar mensaje de AI con ruta de audio: {e}")
                import traceback
                traceback.print_exc()

        return jsonify({
            "mensaje": "Texto hablado con éxito",
            "audioUrl": audio_url,
            "textoUtilizado": texto[:100] + "..." if len(texto) > 100 else texto,
            "conversacion_id": conversacion_id
        })
    except Exception as e:
        print(f"\n--- ERROR en la función hablar ---")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error en la conversión de texto a voz: {e}"}), 500


@app.route('/static/<filename>')
def serve_file(filename):
    return app.send_static_file(filename)


if __name__ == '__main__':
    static_folder = os.path.join(os.path.dirname(__file__), "static")
    if not os.path.exists(static_folder):
        os.makedirs(static_folder)

    app.run(debug=True, port=5001)
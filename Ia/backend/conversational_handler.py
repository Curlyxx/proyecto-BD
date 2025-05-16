import random
import re
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher

class ConversationalHandler:
    def __init__(self):
        # Diccionario de patrones conversacionales
        self.patterns: Dict[str, List[str]] = {
            "saludos": [
                "hola", "buenos días", "buenas tardes", "buenas noches", "qué tal", 
                "saludos", "hey", "ey", "que onda", "que hay", "cómo estás", "como estas"
            ],
            "despedidas": [
                "adiós", "hasta luego", "nos vemos", "hasta pronto", "chao", 
                "bye", "me voy", "hasta mañana", "hasta la próxima"
            ],
            "agradecimientos": [
                "gracias", "te lo agradezco", "muchas gracias", "mil gracias",
                "te debo una", "genial gracias", "excelente gracias"
            ],
            "preguntas_estado": [
                "cómo estás", "qué tal estás", "cómo te encuentras", 
                "cómo te va", "todo bien", "estás bien"
            ],
            "preguntas_nombre": [
                "cómo te llamas", "cuál es tu nombre", "quién eres",
                "tienes nombre", "con quién hablo"
            ],
             "preguntas_objetivo": [
                "cual es tu proposito en general?"
            ],
            "preguntas_función": [
                "qué puedes hacer", "para qué sirves", "en qué me puedes ayudar",
                "cuáles son tus funciones", "qué sabes hacer"
            ]
        }
        
        # Prefijos de preguntas que indican búsqueda de información
        self.prefijos_informacion = [
            "que es", "qué es", "quien es", "quién es", "como es", "cómo es",
            "donde es", "dónde es", "cuando es", "cuándo es", "por que", "por qué",
            "para que", "para qué", "cómo funciona", "como funciona", "que significa",
            "qué significa", "definicion de", "definición de", "concepto de",
            "qué quiere decir", "que quiere decir", "cuál es el significado de",
            "cual es el significado de", "dime sobre", "háblame de", "hablame de",
            "información sobre", "informacion sobre", "qué sabes de", "que sabes de"
        ]
        
        # Lista de palabras muy cortas que son claramente conversacionales
        self.palabras_cortas = {
            "ok": ["Entendido. ¿En qué puedo ayudarte?", 
                   "Perfecto. ¿Qué información necesitas?", 
                   "De acuerdo. ¿Sobre qué tema quieres conocer más?"],
            "si": ["Bien. ¿En qué te puedo ayudar?", 
                   "Genial. ¿Qué información estás buscando?", 
                   "Perfecto. ¿Qué deseas saber?"],
            "sí": ["Bien. ¿En qué te puedo ayudar?", 
                   "Genial. ¿Qué información estás buscando?", 
                   "Perfecto. ¿Qué deseas saber?"],
            "no": ["Entiendo. ¿Hay algo más en lo que pueda ayudarte?", 
                   "De acuerdo. ¿Qué otra cosa necesitas?", 
                   "Vale. ¿Puedo asistirte con alguna búsqueda de información?"],
            "eh": ["¿Hay algo en lo que pueda ayudarte?", 
                   "Estoy aquí para ayudarte con información. ¿Qué necesitas?", 
                   "¿Tienes alguna pregunta o tema que te interese?"],
            "ah": ["¿Necesitas información sobre algún tema?", 
                   "¿Puedo ayudarte con alguna búsqueda?", 
                   "¿Qué te gustaría conocer hoy?"],
            "xd": ["¿Necesitas información sobre algún tema?", 
                   "Que te hizo tanta gracia hpta", 
                   "¿Qué te gustaría conocer hoy?"],
            "oh": ["¿Hay algo que quieras saber?", 
                   "¿Puedo brindarte información sobre algún tema?", 
                   "¿En qué puedo asistirte hoy?"]
        }
        
        # Respuestas para cada categoría
        self.respuestas: Dict[str, List[str]] = {
            "saludos": [
                "¡Hola! ¿En qué puedo ayudarte hoy?",
                "¡Buen día! Estoy aquí para asistirte.",
                "¡Hola! ¿Sobre qué tema te gustaría obtener información?",
                "¡Saludos! ¿Qué deseas conocer hoy?"
            ],
            "despedidas": [
                "¡Hasta pronto! Fue un placer ayudarte.",
                "¡Adiós! Vuelve cuando necesites más información.",
                "¡Nos vemos! Estaré aquí cuando me necesites.",
                "¡Hasta la próxima! Espero haber sido de ayuda."
            ],
            "agradecimientos": [
                "¡De nada! Estoy aquí para ayudarte.",
                "Es un placer poder asistirte.",
                "No hay de qué. ¿Necesitas algo más?",
                "¡Encantado de ayudar! ¿Hay algo más en lo que pueda asistirte?"
            ],
            "preguntas_estado": [
                "¡Muy bien, gracias por preguntar! Listo para ayudarte con lo que necesites.",
                "Estoy funcionando perfectamente y listo para asistirte.",
                "¡Excelente! Siempre dispuesto a proporcionar información.",
                "¡Todo bien por aquí! ¿Y tú? ¿En qué puedo ayudarte hoy?"
            ],
            "preguntas_nombre": [
                "Me llamo VANIA (Voz Autónoma de Navegación e Interacción Artificial), tu asistente de búsqueda de información.",
                "Soy VANIA (Voz Autónoma de Navegación e Interacción Artificial), estoy aquí para ayudarte a encontrar información.",
                "Puedes llamarme VANIA (Voz Autónoma de Navegación e Interacción Artificial). ¿En qué puedo asistirte hoy?",
                "Soy tu asistente VANIA (Voz Autónoma de Navegación e Interacción Artificial), especializado en búsquedas de información."
            ],
            "preguntas_objetivo": [
                "Soy tu asistente, especializado en búsquedas de información y generación de imágenes que tu me pidas, además de guardar y leerte las respuestas."
            ],
            "preguntas_función": [
                "Puedo buscar información en la web sobre diversos temas y leértela en voz alta.",
                "Estoy diseñado para proporcionarte información de Wikipedia y convertirla en audio si lo deseas.",
                "Mi función principal es buscar y presentar información de Wikipedia, además puedo conversar contigo de manera básica.",
                "Te ayudo a encontrar información sobre los temas que te interesen y puedo leerla para ti."
            ]
        }
    
    def es_pregunta_informacion(self, texto: str) -> bool:
        """
        Determina si el texto es una pregunta sobre información.
        
        Args:
            texto: El texto a analizar
            
        Returns:
            True si es una pregunta de información, False en caso contrario
        """
        texto_lower = texto.lower()
        
        # Verificar si comienza con alguno de los prefijos de información
        for prefijo in self.prefijos_informacion:
            if texto_lower.startswith(prefijo + " "):
                return True
                
        # Verificar patrones de pregunta como "¿qué es...?"
        patrones_pregunta = [
            r"^¿.*\?$",  # Texto entre signos de interrogación
            r"^(qué|que|cómo|como|quién|quien|cuándo|cuando|dónde|donde|cuál|cual|por qué|por que) .*",  # Comienza con palabra interrogativa
        ]
        
        for patron in patrones_pregunta:
            if re.match(patron, texto_lower):
                return True
                
        return False
    
    def extraer_termino_busqueda(self, texto: str) -> Optional[str]:
        """
        Extrae el término de búsqueda de una pregunta.
        
        Args:
            texto: El texto de la pregunta
            
        Returns:
            El término de búsqueda o None si no se puede extraer
        """
        texto_lower = texto.lower()
        
        # Intentar extraer el término después de los prefijos conocidos
        for prefijo in self.prefijos_informacion:
            if texto_lower.startswith(prefijo + " "):
                return texto[len(prefijo) + 1:].strip()
        
        # Para preguntas entre signos de interrogación, eliminar los signos
        if texto.startswith("¿") and texto.endswith("?"):
            texto = texto[1:-1].strip()
            
        # Para preguntas que comienzan con palabra interrogativa
        palabras_interrogativas = ["qué", "que", "cómo", "como", "quién", "quien", 
                                  "cuándo", "cuando", "dónde", "donde", "cuál", 
                                  "cual", "por qué", "por que"]
                                  
        for palabra in palabras_interrogativas:
            if texto_lower.startswith(palabra + " "):
                resto = texto[len(palabra) + 1:].strip()
                # Eliminar "es", "son", etc. si están presentes
                for verbo in ["es ", "son ", "está ", "esta ", "será "]:
                    if resto.lower().startswith(verbo):
                        return resto[len(verbo):].strip()
                return resto
                
        return None
    
    def calcular_similitud(self, texto1: str, texto2: str) -> float:
        """
        Calcula la similitud entre dos textos usando SequenceMatcher.
        
        Args:
            texto1: Primer texto a comparar
            texto2: Segundo texto a comparar
            
        Returns:
            Puntuación de similitud entre 0 y 1
        """
        return SequenceMatcher(None, texto1, texto2).ratio()
    
    def detectar_tipo_conversacion(self, texto: str) -> Optional[str]:
        """
        Detecta si el texto es un patrón conversacional conocido.

        Args:
            texto: El texto de entrada a analizar

        Returns:
            El tipo de conversación detectado o None si no es conversacional
        """
        texto = texto.lower().strip()
        
        # Verificar primero si es una pregunta de información
        if self.es_pregunta_informacion(texto):
            # Si es una pregunta sobre un patrón conocido, es una búsqueda
            # Por ejemplo "¿qué es hola?" debería ser una búsqueda, no un saludo
            termino = self.extraer_termino_busqueda(texto)
            if termino:
                return None  # Es una búsqueda de información
        
        # Verificar si es una palabra corta conversacional
        if texto in self.palabras_cortas:
            return f"palabra_corta:{texto}"
        
        # Normalizar texto (eliminar acentos y caracteres especiales)
        texto_norm = re.sub(r'[^a-zA-Z0-9\s]', '', texto.lower())
        
        mejor_coincidencia = None
        mejor_puntuacion = 0.7  # Umbral mínimo de similitud (70%)
        
        # Comprobar todas las categorías de patrones
        for categoria, patrones in self.patterns.items():
            for patron in patrones:
                # Primero verificar coincidencia exacta o como parte de una frase
                if patron == texto or f"{patron} " in texto or f" {patron}" in texto:
                    return categoria
                
                # Si no hay coincidencia exacta, intentar buscar similitud
                patron_norm = re.sub(r'[^a-zA-Z0-9\s]', '', patron.lower())
                
                # Solo comparar si son de longitud similar
                if 0.5 <= len(patron_norm) / max(1, len(texto_norm)) <= 2.0:
                    similitud = self.calcular_similitud(patron_norm, texto_norm)
                    if similitud > mejor_puntuacion:
                        mejor_puntuacion = similitud
                        mejor_coincidencia = categoria
        
        return mejor_coincidencia
    
    def obtener_respuesta(self, tipo_conversacion: str) -> Tuple[str, Dict]:
        """
        Genera una respuesta para el tipo de conversación detectado.

        Args:
            tipo_conversacion: El tipo de conversación detectado

        Returns:
            Una tupla con la respuesta y un diccionario con los datos formatados para la API
        """
        # Verificar si es una palabra corta específica
        if tipo_conversacion.startswith("palabra_corta:"):
            palabra = tipo_conversacion.split(":")[1]
            respuesta = random.choice(self.palabras_cortas[palabra])
        elif tipo_conversacion in self.respuestas:
            respuesta = random.choice(self.respuestas[tipo_conversacion])
        else:
            # Respuesta genérica por defecto
            respuesta = "No estoy seguro de entender. ¿Quieres buscar información sobre algún tema específico?"
            
        # Formar la respuesta en el formato que espera la API
        datos = {
            "titulo": "Conversación",
            "contenido": respuesta,
            "contenido_audio": respuesta,
            "es_conversacional": True,
            "tipo_conversacion": tipo_conversacion
        }
        
        return respuesta, datos
        
    def procesar_entrada(self, texto: str) -> Optional[Dict]:
        """
        Procesa un texto de entrada y determina si es conversacional.
        
        Args:
            texto: El texto de entrada a procesar
            
        Returns:
            Un diccionario con la respuesta si es conversacional, o None si debe procesarse como búsqueda
        """
        tipo = self.detectar_tipo_conversacion(texto)
        
        if tipo:
            _, datos = self.obtener_respuesta(tipo)
            return datos
            
        # Si no es conversacional, devolvemos None para que se procese como búsqueda
        return None
import spacy
import re
from collections import Counter
from transformers import pipeline
import random

# Configuración mejorada
try:
    nlp = spacy.load("es_core_news_sm")
    # Intentar cargar el modelo de sentiment analysis
    try:
        sentiment_analyzer = pipeline("sentiment-analysis", model="finiteautomata/beto-sentiment-analysis")
        use_transformer = True
        print("Usando modelo avanzado de análisis de sentimiento")
    except:
        use_transformer = False
        print("Usando análisis de sentimiento básico (instala transformers para mejor precisión)")
except:
    # Si no está instalado, sugerir instalación
    print("Es necesario instalar el modelo de spaCy: python -m spacy download es_core_news_sm")
    # Crear un sustituto básico para evitar errores
    class DummyNLP:
        def __call__(self, text):
            return text
    nlp = DummyNLP()
    use_transformer = False

# Diccionarios ampliados para seguridad informática
PALABRAS_POSITIVAS = {
    # Términos generales
    "seguro", "protegido", "eficiente", "fuerte", "confiable", "actualizado",
    "robusto", "seguridad", "protección", "bueno", "excelente", "óptimo",
    
    # Técnicos
    "encriptado", "parcheado", "hardening", "mitigado", "blindado", "respaldado",
    "autenticado", "verificado", "certificado", "monitoreado", "actualizado",
    
    # Coloquiales (MX)
    "chido", "padrísimo", "chingón", "bien hecho", "a prueba de balas"
}

PALABRAS_NEGATIVAS = {
    # Términos generales
    "malo", "vulnerable", "hackeado", "ataque", "riesgo", "peligro",
    "desactualizado", "débil", "inseguro", "pésimo", "terrible", "crítico",
    
    # Amenazas
    "virus", "phishing", "malware", "ransomware", "exploit", "spyware",
    "troyano", "botnet", "keylogger", "rootkit", "adware", "backdoor",
    
    # Vulnerabilidades
    "brecha", "infección", "comprometido", "exposición", "fuga", "falla",
    "error", "bug", "zero-day", "inyección", "bypass", "escalada",
    
    # Coloquiales (MX)
    "gacho", "culero", "de la chingada", "peligroso", "chafa"
}

FRASES_NEGATIVAS = {
    # Técnicas
    "vulnerabilidad crítica", "fallo de seguridad", "riesgo alto",
    "amenaza persistente", "ataque exitoso", "sin protección",
    "datos expuestos", "credenciales robadas", "infracción de datos",
    "sistema comprometido", "acceso no autorizado", "exploit disponible",
    
    # Coloquiales (MX)
    "está de la verga", "no sirve", "es un peligro", "te van a hackear",
    "pura vulnerabilidad"
}

FRASES_POSITIVAS = {
    # Técnicas
    "protección avanzada", "seguridad robusta", "encriptación fuerte",
    "sistema actualizado", "respaldos completos", "monitoreo constante",
    "autenticación multifactor", "parches aplicados", "hardening completo",
    
    # Coloquiales (MX)
    "bien protegido", "a toda madre", "super seguro", "chingón el sistema"
}

# Términos que invalidan el contexto positivo (aunque contengan palabras positivas)
INVERSORES_NEGATIVOS = {
    "no", "nunca", "jamás", "tampoco", "sin", "falta", "carece", "excepto"
}

# Nuevas respuestas personalizadas según sentimiento y temas
RESPUESTAS_PERSONALIZADAS = {
    "POS": {
        "general": [
            "Me alegra que estés interesado en este tema positivo. ",
            "Excelente elección de tema. ",
            "Qué bueno que buscas información sobre esto. "
        ],
        "seguridad": [
            "Buen enfoque en seguridad informática. ",
            "Es importante mantener este enfoque positivo sobre la seguridad. ",
            "Te comparto información confiable sobre este tema de seguridad. "
        ],
        "tecnologia": [
            "Excelente interés en esta tecnología. ",
            "La tecnología que mencionas tiene gran potencial. ",
            "Me alegra tu curiosidad por esta innovación tecnológica. "
        ]
    },
    "NEG": {
        "general": [
            "Entiendo tu preocupación sobre este tema. ",
            "Veo que este tema puede generar inquietud. ",
            "Comprendo el tono de tu consulta. Permíteme darte información objetiva. "
        ],
        "seguridad": [
            "Las preocupaciones de seguridad que mencionas son válidas. ",
            "Es importante abordar estos riesgos de seguridad con cautela. ",
            "Ante esta amenaza, puedo darte información para protegerte mejor. "
        ],
        "tecnologia": [
            "Los problemas tecnológicos que mencionas merecen atención. ",
            "Entiendo tus dudas sobre esta tecnología. ",
            "Es válido cuestionar estos aspectos tecnológicos. "
        ]
    },
    "NEU": {
        "general": [
            "Aquí tienes información objetiva sobre el tema. ",
            "Te comparto datos relevantes sobre tu consulta. ",
            "Esta información podría serte útil. "
        ],
        "seguridad": [
            "Sobre este tema de seguridad, te puedo informar que: ",
            "Desde una perspectiva de seguridad informática: ",
            "Considerando el contexto de seguridad: "
        ],
        "tecnologia": [
            "Respecto a esta tecnología: ",
            "Desde el punto de vista técnico: ",
            "La información disponible sobre esta tecnología indica que: "
        ]
    }
}

def analizar_frase(frase):
    """
    Analiza una frase y determina su sentimiento (positivo, negativo o neutro)
    
    Args:
        frase (str): La frase a analizar
        
    Returns:
        str: "POS" para positivo, "NEG" para negativo, "NEU" para neutro
    """
    if not frase:
        return "NEU"
        
    frase = frase.lower()
    
    # Si tenemos el modelo avanzado, usarlo primero
    if globals().get('use_transformer', False) and globals().get('sentiment_analyzer', None):
        try:
            resultado = sentiment_analyzer(frase)
            etiqueta = resultado[0]['label']
            # Convertir al formato simplificado
            if etiqueta == 'POS':
                return "POS"
            elif etiqueta == 'NEG':
                return "NEG"
            else:
                return "NEU"
        except Exception as e:
            print(f"Error en análisis avanzado: {e}, usando análisis básico")
            # Fallback al análisis básico
            pass
    
    # Análisis básico
    # Verificar inversores primero
    if any(inv + " " in frase + " " for inv in INVERSORES_NEGATIVOS):
        return "NEG"
        
    # Verificar frases completas
    if any(fneg in frase for fneg in FRASES_NEGATIVAS):
        return "NEG"
    if any(fpos in frase for fpos in FRASES_POSITIVAS):
        return "POS"
    
    # Conteo de palabras
    count_pos = sum(1 for p in PALABRAS_POSITIVAS if " " + p + " " in " " + frase + " ")
    count_neg = sum(1 for n in PALABRAS_NEGATIVAS if " " + n + " " in " " + frase + " ")
    
    return "POS" if count_pos > count_neg else "NEG" if count_neg > count_pos else "NEU"

def obtener_prefijo_sentimiento(sentimiento, termino=None):
    """
    Genera un prefijo para la respuesta basado en el sentimiento
    Esta función es usada por la aplicación Flask
    
    Args:
        sentimiento (str): El sentimiento detectado ("POS", "NEG", "NEU")
        termino (str, optional): El término de búsqueda para personalizar más
        
    Returns:
        str: Prefijo para la respuesta
    """
    if sentimiento == "NEG":
        return "⚠️ Detectamos un tono negativo en tu consulta. "
    elif sentimiento == "POS":
        return "😊 Detectamos un tono positivo en tu consulta. "
    else:
        return ""

def mejorar_respuesta(contenido, sentimiento, termino):
    """
    Mejora la respuesta basada en el sentimiento y el contexto de la consulta
    
    Args:
        contenido (str): El contenido original de la respuesta
        sentimiento (str): El sentimiento detectado ("POS", "NEG", "NEU")
        termino (str): La consulta original del usuario
        
    Returns:
        str: Respuesta mejorada y personalizada
    """
    # Identificar el contexto temático
    termino_lower = termino.lower()
    
    # Detectar temas
    temas_seguridad = ["seguridad", "hack", "virus", "malware", "protección", "firewall", 
                      "antivirus", "ciberseguridad", "ataque", "contraseña"]
    temas_tecnologia = ["tecnología", "sistema", "software", "hardware", "aplicación", 
                       "programa", "dispositivo", "red", "internet", "wifi", "código"]
    
    # Determinar el tema principal
    if any(tema in termino_lower for tema in temas_seguridad):
        categoria = "seguridad"
    elif any(tema in termino_lower for tema in temas_tecnologia):
        categoria = "tecnologia"
    else:
        categoria = "general"
    
    # Obtener respuestas personalizadas para el sentimiento y categoría
    respuestas = RESPUESTAS_PERSONALIZADAS.get(sentimiento, RESPUESTAS_PERSONALIZADAS["NEU"])
    respuestas_tema = respuestas.get(categoria, respuestas["general"])
    
    # Seleccionar una respuesta aleatoria
    prefijo = random.choice(respuestas_tema)
    
    # Añadir un consejo o información adicional
    if sentimiento == "NEG" and categoria == "seguridad":
        prefijo += "Recuerda siempre verificar la información de fuentes confiables. "
    elif sentimiento == "POS" and categoria == "tecnologia":
        prefijo += "La tecnología avanza rápidamente, así que esta información podría actualizarse pronto. "
    
    # Analizar la consulta para extraer palabras clave
    if not isinstance(nlp, DummyNLP):
        try:
            doc = nlp(termino)
            # Extraer palabras clave significativas
            keywords = [token.text for token in doc if token.pos_ in ("NOUN", "PROPN", "ADJ") and not token.is_stop]
            if keywords:
                prefijo += f"Veo que te interesa específicamente {', '.join(keywords[:2])}. "
        except Exception as e:
            print(f"Error al procesar palabras clave: {e}")
    
    # Combinar con el contenido original
    return prefijo + contenido

# Función para usar en el código de Flask
def procesar_respuesta(termino, contenido, contenido_audio=None):
    """
    Procesa una respuesta completa basada en el término y contenido
    
    Args:
        termino (str): La consulta del usuario
        contenido (str): El contenido completo de la respuesta
        contenido_audio (str, optional): Versión reducida para audio
        
    Returns:
        dict: Diccionario con la respuesta procesada
    """
    # Analizar el sentimiento
    sentimiento = analizar_frase(termino)
    
    # Si no se proporciona contenido de audio, usar el contenido completo
    if contenido_audio is None:
        contenido_audio = contenido
    
    # Mejorar las respuestas
    contenido_mejorado = mejorar_respuesta(contenido, sentimiento, termino)
    contenido_audio_mejorado = mejorar_respuesta(contenido_audio, sentimiento, termino)
    
    return {
        "contenido": contenido_mejorado,
        "contenido_audio": contenido_audio_mejorado,
        "sentimiento": sentimiento
    }

# Ejemplo de uso directo
if __name__ == "__main__":
    # Prueba rápida
    frase_test = "Me preocupa mucho la seguridad de mi sistema"
    sentimiento = analizar_frase(frase_test)
    contenido = "La seguridad informática es el conjunto de herramientas, políticas y conceptos de seguridad..."
    respuesta = mejorar_respuesta(contenido, sentimiento, frase_test)
    print(f"Sentimiento detectado: {sentimiento}")
    print(f"Respuesta mejorada: {respuesta}")
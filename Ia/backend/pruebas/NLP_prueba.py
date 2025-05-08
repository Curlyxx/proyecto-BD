import spacy
import re
from transformers import pipeline
from collections import Counter

# Configuración mejorada
nlp = spacy.load("es_core_news_sm")

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

def analizar_frase(frase):
    frase = frase.lower()
    
    # Verificar inversores primero
    if any(inv in frase for inv in INVERSORES_NEGATIVOS):
        return "NEG"
        
    # Verificar frases completas
    if any(fneg in frase for fneg in FRASES_NEGATIVAS):
        return "NEG"
    if any(fpos in frase for fpos in FRASES_POSITIVAS):
        return "POS"
    
    # Conteo de palabras
    count_pos = sum(1 for p in PALABRAS_POSITIVAS if p in frase)
    count_neg = sum(1 for n in PALABRAS_NEGATIVAS if n in frase)
    
    return "POS" if count_pos > count_neg else "NEG" if count_neg > count_pos else "NEU"


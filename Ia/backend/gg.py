from conversational_handler import ConversationalHandler

# Crear una instancia del manejador conversacional
handler = ConversationalHandler()

# Lista de frases para probar
frases_prueba = [
    "Hola, ¿cómo estás?",
    "Buenos días",
    "¿Qué es la fotosíntesis?",
    "Gracias por la información",
    "¿Cómo te llamas?",
    "Adiós",
    "ok",
    "¿Qué puedes hacer?"
]

# Probar cada frase
for frase in frases_prueba:
    print(f"\nProbando: '{frase}'")
    resultado = handler.procesar_entrada(frase)
    
    if resultado:
        print(f"Detectado como conversacional: {resultado['tipo_conversacion']}")
        print(f"Respuesta: {resultado['contenido']}")
    else:
        print("No es conversacional, se procesaría como búsqueda.")
from textblob import TextBlob

def chatbot():
    print("Hola, soy un chatbot básico. Escribe 'salir' para terminar.")
    
    while True:
        user_input = input("Tú: ")
        if user_input.lower() == "salir":
            print("Chatbot: ¡Hasta luego!")
            break
        
        # Analiza el texto y responde
        analysis = TextBlob(user_input)
        respuesta = analysis.correct()  # Corrige errores ortográficos
        print(f"Chatbot: {respuesta}")

chatbot()

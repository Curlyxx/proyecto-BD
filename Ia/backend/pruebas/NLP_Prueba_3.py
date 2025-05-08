from flask import Flask, request, jsonify
from flask_cors import CORS
import nltk
from textblob import TextBlob
import spacy
from transformers import pipeline
import pyttsx3

app = Flask(__name__)
CORS(app)

# Cargar modelos de NLP
nlp_spacy = spacy.load("es_core_news_sm")  # Cambiar a 'en_core_web_sm' para inglés
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

# Inicializar motor de voz
engine = pyttsx3.init()

@app.route("/analyze_sentiment", methods=["POST"])
def analyze_sentiment():
    text = request.json.get("text", "")
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity  # -1 (negativo) a 1 (positivo)
    sentiment = "positivo" if polarity > 0 else "negativo" if polarity < 0 else "neutral"
    return jsonify({"sentiment": sentiment, "polarity": polarity})

@app.route("/summarize", methods=["POST"])
def summarize():
    text = request.json.get("text", "")
    summary = summarizer(text, max_length=130, min_length=30, do_sample=False)
    return jsonify({"summary": summary[0]["summary_text"]})

@app.route("/chatbot", methods=["POST"])
def chatbot():
    user_input = request.json.get("message", "")
    doc = nlp_spacy(user_input)
    
    # Respuestas basadas en palabras clave
    if any(token.text.lower() in ["hola", "saludos"] for token in doc):
        response = "¡Hola! ¿Cómo estás?"
    elif any(token.text.lower() in ["adiós", "chao"] for token in doc):
        response = "¡Hasta luego! Que tengas un buen día."
    else:
        response = "No entendí tu mensaje. ¿Puedes reformularlo?"
    
    # Opcional: Convertir respuesta a voz
    engine.say(response)
    engine.runAndWait()
    
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
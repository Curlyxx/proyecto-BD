from duckduckgo_search import DDGS
import requests
from PIL import Image
from io import BytesIO

def buscar_y_guardar_imagen(prompt):
    with DDGS() as ddgs:
        results = ddgs.images(prompt, max_results=1)
        if not results:
            print("No se encontró ninguna imagen.")
            return
        imagen_url = results[0]["image"]
        print("Imagen encontrada:", imagen_url)

        # Descargar y mostrar la imagen
        response = requests.get(imagen_url)
        img = Image.open(BytesIO(response.content))
        img.show()

        # Guardar localmente
        img.save("imagen_descargada.png")
        print("Imagen guardada como: imagen_descargada.png")

# Cambia aquí el texto según lo que necesites
buscar_y_guardar_imagen(" league of legends ")

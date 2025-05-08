import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import datetime
import os

# Verifica si hay GPU
device = "cuda" if torch.cuda.is_available() else "cpu"
print("Usando:", device)

# Carga el modelo (solo la primera vez tarda, luego se cachea)
print("Cargando modelo...")
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16 if device == "cuda" else torch.float32
).to(device)

# Bucle para generar múltiples imágenes
while True:
    prompt = input("\n🔤 Escribe la descripción de la imagen (o 'salir'): ")
    if prompt.lower() == "salir":
        break

    # Generar imagen
    print("Generando imagen...")
    image = pipe(prompt).images[0]

    # Mostrar imagen
    image.show()

    # Guardar con nombre basado en hora
    filename = f"imagen_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    image.save(filename)
    print(f"✅ Imagen guardada como: {filename}")

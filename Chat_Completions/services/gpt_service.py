import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def consultar_con_historial(historial):
    try:
        respuesta = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=historial,
            max_tokens=250
        )
        return f"{respuesta.choices[0].message.content}".replace("\n", "<br>")
    except Exception as e:
        print(f"Error al consultar la API de OpenAI: {e}")
        raise RuntimeError("Servicio no disponible. Intente nuevamente más tarde.")

import openai
import os
from dotenv import load_dotenv
from openai import OpenAI
import tiktoken
import json
from datetime import datetime

# ==================================================
# Carga variables de entorno
# ==================================================
from config.logging_config import logger

load_dotenv(override=True)
OpenAI_key = os.getenv("GPT_TICS_KEY")
Moderation_Key = os.getenv("MODERATION_KEY")
model_moderation = os.getenv("MODEL_MODERATION")
encoding_base = os.getenv("ENCODING_BASE")

if not  OpenAI_key :
    logger.error("La Api_key 'GPT_TICS_KEY' de OpenAI no está configura en la variables de entorno.")
    raise ValueError("La Api_key 'GPT_TICS_KEY' de OpenAI no está configura en la variables de entorno.")

if not  Moderation_Key :
    logger.error("La Api_key 'MODERATION_KEY' de OpenAI no está configura en la variables de entorno.")
    raise ValueError("La Api_key 'MODERATION_KEY' de OpenAI no está configura en las variables de entorno.")

if not  model_moderation :
    logger.error("El modelo 'MODEL_MODERATION' de OpenAI no está configura en las variables de entorno.")
    raise ValueError("El modelo 'MODEL_MODERATION' de OpenAI no está configura en las variables de entorno.")

if not  encoding_base :
    logger.error("El encoding 'ENCODING_BASE' de TikToken no está configura en las variables de entorno.")
    raise ValueError("El encoding 'ENCODING_BASE' de TikToken no está configura en las variables de entorno.")


# ==================================================
# Crear una instancia de OpenAI
# ==================================================
client = OpenAI(api_key = OpenAI_key)
moderation = OpenAI(api_key = Moderation_Key)


# ==================================================
# Verificar si el asistente existe o crear uno nuevo
# ==================================================
def verify_or_create_assistant(contexto):
    assistant_id = os.getenv("ASSISTANT_ID")
    assistant = None

    if assistant_id:
        try:
            assistant = client.beta.assistants.retrieve(assistant_id=assistant_id)
        except Exception as e:
            assistant = None
            raise RuntimeError(e)

    if not assistant:
        # ---- DESABILITAR ESTA SECCIÓN SI SE DESEA CREAR UN NUEVO ASISTENTE ----
        raise ValueError("El id del asistente no fue encontrado.")
        # ----------------------------------------------------------------------
        
        # ---- HABILITAR ESTA SECCIÓN SI SE DESEA CREAR UN NUEVO ASISTENTE ----
        # try:
        #     assistant = create_asistente(contexto)
        #     env_path = os.path.join(os.path.dirname(__file__), '../.env')

        #     if not os.path.exists(env_path):
        #         with open(env_path, 'w') as file:
        #             pass

        #     with open(env_path, 'a') as file:
        #         file.write(f'\nASSISTANT_ID = "{assistant.id}"')
        
        #     print(f"ID del asistente guardado en {env_path}")
        #     print(f"Nuevo asistente creado con ID: {assistant.id}")
        
        # except Exception as e:
        #     raise RuntimeError(f"Error al crear un nuevo asistente: {e}")
        # ----------------------------------------------------------------------
        
    return assistant


# ==================================================
# Crear un asistente nuevo
# ==================================================
def create_asistente(contexto):
    try:
        assistant = client.beta.assistants.create(
            name="Asistente de Soporte TIC",
            instructions=(
            "Eres un asistente diseñado exclusivamente para proporcionar soporte tecnológico en el área de TIC de la Universidad Católica de Cuenca. "
            "Tu función principal es ofrecer asistencia y resolver dudas relacionadas con los servicios tecnológicos de la Universidad Católica de Cuenca. "
            "Responde siempre de forma clara y directa basándote únicamente en el contenido del documento proporcionado. "
            "Si no encuentras información relevante en el documento, no menciones ni hagas referencia al documento en tus respuestas. En su lugar, indica que no dispones de esa información en tu conocimiento actual. "
            "No respondas a preguntas que no estén relacionadas con el contenido del documento proporcionado. "
            f"Contenido del documento: {contexto}"
            ),
            tools=[],
            model="gpt-3.5-turbo",
        )
        return assistant
    except Exception as e:
        raise RuntimeError(e)


# ==================================================
# Obtener respuesta del asistente
# ==================================================
def get_response(assistant_id, ask, thread_id, name_user):
    try:
        
        thread = get_or_create_thread(thread_id)
        
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=ask
        )
        
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant_id,
            additional_instructions=(f"Dirigete al usuario utilizando el nombre '{name_user}'.")
        )  
        
        if run.status == 'completed':
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            for msg in messages.data:
                if msg.role == 'assistant':
                    return msg.content[0].text.value, thread.id
        else:
            return f"La ejecución no se completó correctamente. Estado: {run.status}", thread.id
    except ValueError as e:
        raise ValueError(e)
    except Exception as e:
        raise RuntimeError(e)


# ==================================================
# Modelo de moderación de texto
# ==================================================
def moderation_text(texto):
    try:
        response = moderation.moderations.create(
            model=model_moderation,
            input=texto,
        )
        
        response_dict = response.to_dict()
        response_json = json.dumps(response_dict, indent=4)
        response_data = json.loads(response_json)
        flagged = response_data["results"][0]["flagged"]
        
        return flagged
    except Exception as e:
        raise RuntimeError(e)
    
    
# ==================================================
# Obtener el número de tokens en una cadena de texto
# ==================================================
def num_tokens_from_string(answerToToken: str, encoding_name: str = encoding_base) -> int:
    try:
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(answerToToken))
        return num_tokens
    except Exception as e:
        raise RuntimeError(e)


# ==================================================
# Verificar si un hilo existe o crear uno nuevo
# ==================================================
def get_or_create_thread(thread_id=None):
    if thread_id:
        try:
            thread = client.beta.threads.retrieve(thread_id=thread_id)
            return thread
        except openai.OpenAIError as e:
            if "No thread found" in str(e):
                thread = client.beta.threads.create()
                return thread
            else:
                raise e
        except Exception as e:
            raise RuntimeError(f"Error inesperado al recuperar el hilo con ID {thread_id}: {e}")
    try:
        thread = client.beta.threads.create()
        return thread
    except Exception as e:
        raise RuntimeError(f"Error al crear un nuevo hilo: {e}")
    
    
# ==================================================
# Ver historial de mensajes de un hilo
# ==================================================
def view_history(thread_id):
    try:
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        history = []
        for msg in messages.data:
            history.append({
                "role": msg.role,
                "content": msg.content[0].text.value if msg.content else "Sin contenido",
                "timestamp": datetime.fromtimestamp(msg.created_at).strftime("%d-%m-%Y %H:%M:%S")
            })
        return history
    except openai.OpenAIError as e:
        if "No thread found" in str(e):
            raise ValueError(f"Hilo con ID {thread_id} no encontrado o ha sido eliminado.")
        else:
            raise e
    except Exception as e:
        raise RuntimeError(f"Error al recuperar Historail del hilo: {str(e)}")


# ==================================================
# Eliminar un hilo
# ==================================================
def delete_thread(thread_id):
    try:
        client.beta.threads.delete(thread_id=thread_id)
        return f"Hilo con ID {thread_id} eliminado exitosamente."
    except openai.OpenAIError as e:
        if "No thread found" in str(e):
            raise ValueError(f"Hilo con ID {thread_id} no encontrado o ya ha sido eliminado.")
        else:
            raise e
    except Exception as e:
        raise RuntimeError(f"Error al eliminar el hilo con ID {thread_id}: {e}")


# ==================================================
# Eliminar múltiples hilos
# ==================================================
def delete_threads(thread_ids):
    if not isinstance(thread_ids, list):
        raise TypeError("El argumento debe ser una lista de IDs de hilos.")

    resultados = []
    for thread_id in thread_ids:
        resultado = delete_thread(thread_id)
        resultados.append(resultado)

    return resultados

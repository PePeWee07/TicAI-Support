import openai
import os
from dotenv import load_dotenv
from openai import OpenAI
import tiktoken
import json
from datetime import datetime
import re
import time

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
def verify_assistant():
    assistant_id = os.getenv("ASSISTANT_ID")
    assistant = None

    if assistant_id:
        try:
            assistant = client.beta.assistants.retrieve(assistant_id=assistant_id)
        except Exception as e:
            assistant = None
            raise RuntimeError(e)

    if not assistant:
        raise ValueError("El ASSISTANT_ID del asistente no fue encontrado.")
        
    return assistant


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
            additional_instructions=(f"Tratamiento del Usuario: Dirigite al usuario utilizando el nombre '{name_user}' en tus respuestas.")
        )
        
        # REQUIERE UNA ACCION
        if run.required_action is not None:
            tools_to_call = run.required_action.submit_tool_outputs.tool_calls
            
            print(f"Número de tool_calls: {len(tools_to_call)}")
            
            tools_output_array = []
            for tool_call in tools_to_call:
                
                print(f"Función: {tool_call.function.name}")
                print(f"Argumentos: {tool_call.function.arguments}")
                
                # Aquí podrías ejecutar la función real. En este ejemplo se envía 'True'
                tools_output_array.append({
                    "tool_call_id": tool_call.id,
                    "output": "True"
                })
                
            print("Enviando outputs:", tools_output_array)
            
            run = client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id, 
                run_id=run.id, 
                tool_outputs=tools_output_array
            )
            print(f"Estado tras enviar outputs: {run.status}")
            
            timestamp_after_tool_call = time.time()
            
            # Espera a que el run se complete o falle
            while run.status not in ['completed', 'failed']:
                run = client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                print(f"Estado del run: {run.status}")
                time.sleep(10)
                
        if run.status == 'completed':
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            assistant_messages = [msg for msg in messages.data if msg.role == 'assistant' and msg.content]
            if assistant_messages:
                final_message = max(assistant_messages, key=lambda m: m.created_at)
                text_response = final_message.content[0].text.value
                clean_message = clean_response(text_response)
                return clean_message, thread.id
            else:
                return "No se encontró respuesta del asistente.", thread.id
        else:
            return f"La ejecución no se completó correctamente. Estado: {run.status}", thread.id

    except ValueError as e:
        raise ValueError(e)
    except Exception as e:
        raise RuntimeError(e)
    
def clean_response(text_response: str) -> str:
    # 1) Eliminar referencias del formato antiguo, si aún las usas
    text_response = re.sub(r'【\d+:\d+†[a-zA-Z]+】', '', text_response)
    
    # 2) Esta expresión elimina:
    # - Todo el contenido desde \ue200 hasta \ue201 (non-greedy)
    # - Opcionalmente, una coma, punto y coma o dos puntos que le sigan,
    # - Y cualquier espacio en blanco que haya después.
    text_response = re.sub(r'\ue200.*?\ue201[,;:]?\s*', '', text_response)
    
    return text_response


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

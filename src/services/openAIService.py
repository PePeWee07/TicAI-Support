import openai
import os
from dotenv import load_dotenv
from openai import OpenAI
import tiktoken
import json
from datetime import datetime
import re
import time
from tools.config.registry import function_registry
from config.logging_config import logger
from models.userData import UserData
from services.permissions import is_globally_restricted

# ==================================================
# Carga variables de entorno
# ==================================================

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
def clean_response(text_response: str) -> str:
    text_response = re.sub(r'【.*?】', '', text_response)
    text_response = re.sub(r'\ue200.*?\ue201[,;:]?\s*', '', text_response)
    return text_response

def parse_tool_arguments(args):
    if isinstance(args, str):
        try:
            return json.loads(args)
        except Exception as e:
            logger.error(f"Error al parsear los argumentos de la herramienta: {e}")
            return {}
    return args

def execute_tool_function(tool_call, user: UserData) -> dict:
    func_id = tool_call.function.name
    entry = function_registry.get(func_id)

    if entry is None:
        return {
            "tool_call_id": tool_call.id,
            "output": f"Función '{func_id}' no encontrada."
        }

    func = entry["func"]
    allowed_roles = entry["allowed_roles"]

    user_roles = {r.strip().upper() for r in user.roles}

    # En caso de no exita nigún rol permitido, denegar acceso
    if not allowed_roles:
        return {
            "tool_call_id": tool_call.id,
            "output": f"Esta accion no esta permitida para ningún rol."
        }

    # Verificar si el usuario tiene al menos un rol permitido
    if user_roles.isdisjoint(allowed_roles):
        restricted_msg = f"Esta accion no esta permitida para usuarios con rol de {sorted(user_roles)}."
        print(restricted_msg);  #! Debug
        return {
            "tool_call_id": tool_call.id,
            "output": restricted_msg
        }

    args = parse_tool_arguments(tool_call.function.arguments)
    user_args = {
        "phone": user.phone,
        "names": user.name,
        "roles": user.roles,
        "identificacion": user.identificacion,
        "emailInstitucional": user.emailInstitucional,
        "emailPersonal": user.emailPersonal,
        "sexo": user.sexo,
    }
    for key, val in user_args.items():
        if val is not None:
            args.setdefault(key, val)

    try:
        output = func(**args)
    except Exception as e:
        output = "False"
        logger.error(f"Error al ejecutar '{func_id}': {e}")

    return {
        "tool_call_id": tool_call.id,
        "output": output
    }


def process_required_action(tools_to_call, user: UserData, restricted: bool):
    tools_output_array = []
    for tool_call in tools_to_call:
        if restricted:
            restricted_msg = f"Esta accion no esta permitida para usuarios con rol de {user.roles}."
            print(restricted_msg);  #! Debug
            tools_output_array.append({
                "tool_call_id": tool_call.id,
                "output": restricted_msg
            })
        else:
            tool_output = execute_tool_function(tool_call, user)
            tools_output_array.append(tool_output)
    return tools_output_array

def get_response(assistant_id, user: UserData):
    try:
        print(f"Datos recibidos: {user}")  #! Debug
        thread = get_or_create_thread(user.thread_id)
        
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user.ask
        )
        
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant_id,
            additional_instructions=(
                f"Estás conversando con {user.name} (Roles: {', '.join(user.roles)}; Identificación oficial: {user.identificacion}). Eres CatIA y debes usar estos datos para personalizar y orientar tus respuestas."
            ),
            parallel_tool_calls=True
        )

        while run.status not in ['completed', 'failed']:
            if run.required_action is not None:
                tools_to_call = run.required_action.submit_tool_outputs.tool_calls
                
                restricted_global = is_globally_restricted(user.roles)
                
                tools_output_array = process_required_action(
                    tools_to_call, user, restricted_global
                )
                
                run = client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tools_output_array
                )
            
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            time.sleep(2)
            
            print(f"Estado del run: {run.status}")  #! Debug
                
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


# ==================================================
# Modelo de moderación de texto
# ==================================================
UMBRAL_CATEGORIES = {
    "harassment": 0.47,
    "harassment/threatening": 0.47,
    "hate": 0.47,
    "hate/threatening": 0.47,
    "illicit": 0.47,
    "illicit/violent": 0.47,
    "self-harm": 0.47,
    "self-harm/instructions": 0.47,
    "self-harm/intent": 0.47,
    "sexual": 0.47,
    "sexual/minors": 0.47,
    "violence": 0.47,
    "violence/graphic": 0.47,
}

def moderation_text(texto, umbrales=UMBRAL_CATEGORIES):
    try:
        response = moderation.moderations.create(
            model=model_moderation,
            input=texto,
        )
        resp_dict = response.to_dict()
        scores = resp_dict["results"][0]["category_scores"]
        
        for categoria, umbral in umbrales.items():
            valor = scores.get(categoria, 0.0)
            if valor >= umbral:
                return True

        return False
    
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

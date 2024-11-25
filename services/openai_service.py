import openai
import os
from dotenv import load_dotenv
from openai import OpenAI
import tiktoken
from config.logging_config import logger

# Carga variables de entorno
dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path)

# Configurar la clave de API de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    logger.error("La clave de API de OpenAI no está configurada en el archivo .env.")
    raise ValueError("La clave de API de OpenAI no está configurada en el archivo .env.")


# Crear una instancia de OpenAI
client = OpenAI()


# Crear un asistente con el contenido del documento proporcionado
def crear_asistente(contexto):
    try:
        assistant = client.beta.assistants.create(
            name="Asistente de Soporte TIC",
            instructions=(
                "Eres un asistente diseñado unicamente para proporcionar soporte tecnológico en el área de TIC de la Universidad Católica de Cuenca. "
                "Tu función principal es ofrecer asistencia y resolver dudas relacionadas con los servicios tecnológicos de la Universidad Católica de Cuenca."
                "Responde siempre de forma clara y directa basándote únicamente en el contenido del documento proporcionado."
                "Si no encuentras información relacionada en el documento, indica que no tienes esa información en tu conocimiento actual."
                "No respondas a preguntas que no esten relacionadas con el contenido del documento proporcionado."
                f"Contenido del documento: {contexto}"
            ),
            tools=[],
            model="gpt-3.5-turbo",
        )
        return assistant
    except Exception as e:
        raise RuntimeError(e)


# Verificar si el asistente existe o crear uno nuevo
def verificar_o_crear_asistente(contexto):
    
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
        #     assistant = crear_asistente(contexto)
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


# Verificar si un hilo existe o crear uno nuevo
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


# Obtener respuesta del asistente para una pregunta específica
def obtener_respuesta(assistant_id, pregunta, thread_id, nombre_usuario):
    try:
        
        if num_tokens_from_string(PreguntaToToken=pregunta) > 500:
            raise ValueError("La pregunta excede el límite de tokens permitido.")
        
        thread = get_or_create_thread(thread_id)
        
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=pregunta
        )
        
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant_id,
            additional_instructions=(f"Dirigete al usuario utilizando el nombre '{nombre_usuario}'.")
            # max_prompt_tokens=500,  # Limitar pregunta y historial de mensajes
            # max_completion_tokens=500, # Limitar respuesta
            # temperature=0.77
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


# Obtener el número de tokens en una cadena de texto
def num_tokens_from_string(PreguntaToToken: str, encoding_name: str = "cl100k_base") -> int:
    try:
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(PreguntaToToken))
        return num_tokens
    except Exception as e:
        raise RuntimeError(e)


# Ver historial de mensajes de un hilo
def ver_historial(thread_id):
    try:
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        
        historial = []
        for msg in messages.data:
            historial.append({
                "role": msg.role,
                "content": msg.content[0].text.value if msg.content else "Sin contenido",
                "timestamp": msg.created_at
            })
        
        return historial
    except openai.OpenAIError as e:
        if "No thread found" in str(e):
            raise ValueError(f"Hilo con ID {thread_id} no encontrado o ha sido eliminado.")
        else:
            raise e
    except Exception as e:
        raise RuntimeError(f"Error al recuperar Historail del hilo: {str(e)}")


# Eliminar un hilo
def eliminar_hilo(thread_id):
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
    
# Función para eliminar múltiples hilos
def eliminar_hilos(thread_ids):
    if not isinstance(thread_ids, list):
        raise TypeError("El argumento debe ser una lista de IDs de hilos.")

    resultados = []
    for thread_id in thread_ids:
        resultado = eliminar_hilo(thread_id)
        resultados.append(resultado)

    return resultados

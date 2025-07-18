import openai
import os
from dotenv import load_dotenv
from openai import OpenAI
import tiktoken
import json
from datetime import datetime
import re
from tools.config.registry import function_registry
from config.logging_config import logger
from models.userData import UserData
from services.permissions import is_globally_restricted
import pprint

load_dotenv(override=True)
GPT_TICS_KEY = os.getenv("GPT_TICS_KEY")
MODERATION_KEY = os.getenv("MODERATION_KEY")
MODEL_MODERATION = os.getenv("MODEL_MODERATION")
ENCODING_BASE = os.getenv("ENCODING_BASE")
PROMPT_ID = os.getenv("PROMPT_ID")
if not GPT_TICS_KEY:
    logger.error(
        "La Api_key 'GPT_TICS_KEY' de OpenAI no está configura en la variables de entorno."
    )
    raise ValueError(
        "La Api_key 'GPT_TICS_KEY' de OpenAI no está configura en la variables de entorno."
    )
if not MODERATION_KEY:
    logger.error(
        "La Api_key 'MODERATION_KEY' de OpenAI no está configura en la variables de entorno."
    )
    raise ValueError(
        "La Api_key 'MODERATION_KEY' de OpenAI no está configura en las variables de entorno."
    )
if not MODEL_MODERATION:
    logger.error(
        "El modelo 'MODEL_MODERATION' de OpenAI no está configura en las variables de entorno."
    )
    raise ValueError(
        "El modelo 'MODEL_MODERATION' de OpenAI no está configura en las variables de entorno."
    )
if not ENCODING_BASE:
    logger.error(
        "El encoding 'ENCODING_BASE' de TikToken no está configura en las variables de entorno."
    )
    raise ValueError(
        "El encoding 'ENCODING_BASE' de TikToken no está configura en las variables de entorno."
    )
if not PROMPT_ID:
    logger.error(
        "El Prompt 'PROMPT_ID' no está configurado en las variables de entorno."
    )
    raise ValueError(
        "El Prompt 'PROMPT_ID' no está configurado en las variables de entorno."
    )

# ========== Instancia de OpenAI ======================
client = OpenAI(api_key=GPT_TICS_KEY)
moderation = OpenAI(api_key=MODERATION_KEY)


# =========== Obtener respuesta del asistente ==========
def clean_response(text: str) -> str:
    """Limpia caracteres de control en la respuesta."""
    text = re.sub(r"【.*?】", "", text)
    text = re.sub(r".*?[,;:]?\s*", "", text)
    return text


def process_required_action(tool_calls: list, user: UserData, restricted: bool) -> list:
    results = []
    user_roles = {r.strip().upper() for r in user.roles}

    for call in tool_calls:
        tid = call.call_id
        # Bloqueo global
        if restricted:
            msg = f"El usuario no tiene permitodo realizar esta acción por su roles: {user_roles}"
            results.append({"tool_call_id": tid, "output": msg})
            continue

        entry = function_registry.get(call.name)
        if not entry:
            results.append(
                {
                    "tool_call_id": tid,
                    "output": f"Esta Función '{call.name}' no esta definida en tus procesos de ejecucion.",
                }
            )
            continue

        allowed = entry.get("allowed_roles", set())
        if not allowed:
            results.append(
                {
                    "tool_call_id": tid,
                    "output": "Esta acción no está permitida para ningún rol.",
                }
            )
            continue
        if user_roles.isdisjoint(allowed):
            results.append(
                {
                    "tool_call_id": tid,
                    "output": f"El usuario no tiene permitodo realizar esta acción por su roles: {sorted(user_roles)}.",
                }
            )
            continue

        # Parsear args y completar con datos de usuario
        try:
            args = json.loads(call.arguments) if call.arguments else {}
        except json.JSONDecodeError:
            args = {}

        for key, val in {
            "phone": user.phone,
            "names": user.name,
            "roles": user.roles,
            "identificacion": user.identificacion,
            "emailInstitucional": user.emailInstitucional,
            "emailPersonal": user.emailPersonal,
            "sexo": user.sexo,
        }.items():
            if val is not None and key not in args:
                args[key] = val

        # Ejecutar función
        try:
            output = entry["func"](**args)
        except Exception as e:
            logger.error(f"Error ejecutando {call.name}: {e}")
            output = "Error interno al ejecutar la función."

        results.append({"tool_call_id": tid, "output": output})

    return results


def get_response(user: UserData) -> tuple[str, str, list]:
    # 1) Historial de conversación
    conversation = [{"role":"user","content":user.ask}]
    audit_logs = []
    prev_conv_len = 0                # indice donde empezo este turno

    # 2) Primera llamada
    response = client.responses.create(
        prompt={
            "id": PROMPT_ID,
            "variables": {
                "phone": user.phone if user.phone else "unknown",
                "names": user.name if user.name else "unknown",
                "roles": ", ".join(user.roles) if user.roles else "unknown",
                "identificacion": user.identificacion if user.identificacion else "unknown",
                "email_institucional": user.emailInstitucional if user.emailInstitucional else "unknown",
                "email_personal": user.emailPersonal if user.emailPersonal else "unknown",
                "sexo": user.sexo if user.sexo else "unknown"
            }
        },
        input=conversation,
        previous_response_id=user.previousResponseId,
        store=True,
        parallel_tool_calls=True
    )
    full = response.to_dict()
    # --- guardo solo los bloques nuevos ---
    new_input = conversation[prev_conv_len:]      # aqui solo la pregunta del user
    audit_logs.append({
        "response_id":         full["id"],
        "previous_response_id":full["previous_response_id"],
        "created_at":          full["created_at"],
        "model":               full["model"],
        "prompt":              full["prompt"],
        "usage":               full["usage"],
        "input":               new_input,
        "output":              full["output"],
        "metadata":            full.get("metadata", {}),
        "reasoning":           full.get("reasoning", {})
    })
    prev_conv_len = len(conversation)              # actualizo indice

    # 3) Bucle de function calls
    while True:
        calls = [item for item in response.output if item.type=="function_call"]
        if not calls:
            break

        # ejecuto las funciones y las añado a conversation
        outputs = process_required_action(calls, user, is_globally_restricted(user.roles))
        for call, out in zip(calls, outputs):
            conversation.append({
                "type":       "function_call",
                "name":       call.name,
                "arguments":  call.arguments,
                "call_id":    call.call_id
            })
            conversation.append({
                "type":       "function_call_output",
                "call_id":    call.call_id,
                "output":     out["output"]
            })

        # 4) Segunda llamada con la conversacion extendida
        response = client.responses.create(
            prompt={
                "id": PROMPT_ID,
                "variables": {
                    "phone": user.phone if user.phone else "unknown",
                    "names": user.name if user.name else "unknown",
                    "roles": ", ".join(user.roles) if user.roles else "unknown",
                    "identificacion": user.identificacion if user.identificacion else "unknown",
                    "email_institucional": user.emailInstitucional if user.emailInstitucional else "unknown",
                    "email_personal": user.emailPersonal if user.emailPersonal else "unknown",
                    "sexo": user.sexo if user.sexo else "unknown"
                }
            },
            input=conversation,
            previous_response_id=full["id"],
            store=True,
            parallel_tool_calls=True
        )
        full = response.to_dict()

        # --- de nuevo guardo sólo los bloques añadidos desde prev_conv_len ---
        new_input = conversation[prev_conv_len:]
        audit_logs.append({
            "response_id":         full["id"],
            "previous_response_id":full["previous_response_id"],
            "created_at":          full["created_at"],
            "model":               full["model"],
            "prompt":              full["prompt"],
            "usage":               full["usage"],
            "input":               new_input,
            "output":              full["output"],
            "metadata":            full.get("metadata", {}),
            "reasoning":           full.get("reasoning", {})
        })
        prev_conv_len = len(conversation)          # muevo el indice

    # 5) Extraigo la respuesta final
    texts = [
        item.content[0].text
        for item in response.output
        if item.type=="message"
    ]
    answer = clean_response("\n\n".join(texts))
    return answer, response.id, audit_logs

# =========== Umbral de moderación ===================
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
            model=MODEL_MODERATION,
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


# ========== tokens en una cadena de texto ===========
def num_tokens_from_string(
    answerToToken: str, encoding_name: str = ENCODING_BASE
) -> int:
    try:
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(answerToToken))
        return num_tokens
    except Exception as e:
        raise RuntimeError(e)

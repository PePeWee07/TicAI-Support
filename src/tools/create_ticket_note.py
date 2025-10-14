import requests
from tools.config.registry import register_function, requires_roles
from config.logging_config import logger
import os

@requires_roles("create_ticket_note", ["DOCENTE", "ADMINISTRATIVO", "ENCARGATURA"])
@register_function("create_ticket_note")
def create_ticket_note(**kwargs):
    """
    Crea una nota en un ticket existente.
    
    Parámetros esperados:
    - ticket_id: ID del Ticket
    - content: Comentario o nota para el seguimiento

    Datos del usuario:
    - phone
    """
    ticket_id = kwargs.get("ticket_id")
    phone = kwargs.get("phone")
    content = kwargs.get("content")
    
    url = os.getenv("URL_BACKEND") + "v1/whatsapp/user/ticket/create/note"
    params = {
        "whatsappPhone": phone,
        "ticketId": ticket_id
    }
    headers = {
        os.getenv("BACKEND_HEADER"): os.getenv("API_KEY_BACKEND"),
        "Content-Type": "text/plain"
    }
    
    try:
        resp = requests.post(url, params=params, headers=headers, data=content)
        resp.raise_for_status()
        data = resp.json()
        return data.get("message") or data.get("error")
    except requests.exceptions.RequestException as ex:
        error_message = ""
        if ex.response is not None:
            try:
                error_data = ex.response.json()
                error_message = error_data.get("error", str(ex))
            except Exception:
                error_message = str(ex)
        else:
            error_message = str(ex)
        logger.error(f"Error al crear nota para ticket {ticket_id}: {ex}")
        return f"No se pudo registrar el seguimeinto para el ticket #{ticket_id}: {error_message}"
    
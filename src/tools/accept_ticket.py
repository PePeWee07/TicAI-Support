import requests
from tools.config.registry import register_function, requires_roles
from config.logging_config import logger
import os

@requires_roles("accept_ticket", ["DOCENTE", "ADMINISTRATIVO", "ENCARGATURA"])
@register_function("accept_ticket")
def accept_ticket(**kwargs):
    """
    Tomar una decisión sobre la solución dada de un caso.

    Parámetros esperados:
    - ticket_id: ID del Ticket

    Datos del usuario:
    - phone
    """
    ticket_id = kwargs.get("ticket_id")
    phone = kwargs.get("phone")

    url = os.getenv("URL_BACKEND") + "v1/whatsapp/user/ticket/solution/decision"
    params = {"whatsappPhone": phone, "ticketId": ticket_id}
    headers = {
        os.getenv("BACKEND_HEADER"): os.getenv("API_KEY_BACKEND")
    }

    try:
        response = requests.post(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
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
        logger.error(f"Error al aceptar la solución del ticket {ticket_id}: {error_message}")
        return f"No se pudo aceptar la solución del ticket #{ticket_id}: {error_message}"

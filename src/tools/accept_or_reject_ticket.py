import requests
from tools.config.registry import register_function, requires_roles
from config.logging_config import logger
import os

@requires_roles("accept_or_reject_ticket", ["ADMIN"])
@register_function("accept_or_reject_ticket")
def accept_or_reject_ticket(**kwargs):
    """
    Tomar una decisión sobre la solución dada de un caso.

    Parámetros esperados:
    - ticket_id: ID del Ticket
    - status: 'aceptada' o 'rechazada'
    - rejection_reason: motivo del rechazo (solo si es rechazada)

    Datos del usuario:
    - phone
    """
    ticket_id = kwargs.get("ticket_id")
    phone = kwargs.get("phone")
    status = kwargs.get("status")
    rejection_reason = kwargs.get("rejection_reason")

    # Convertimos el texto a booleano
    accepted = status == "aceptada"

    payload = {
        "accepted": accepted,
        "ticketId": ticket_id,
        "content": rejection_reason if not accepted else ""
    }

    url = os.getenv("URL_BACKEND") + "v1/glpi/ticket/solution/decision"
    params = {"whatsappPhone": phone}
    headers = {
        os.getenv("BACKEND_HEADER"): os.getenv("API_KEY_BACKEND")
    }

    try:
        response = requests.post(url, json=payload, params=params, headers=headers)
        response.raise_for_status()

        data = response.json()
        return data.get("message") or data.get("error")

    except requests.exceptions.RequestException as ex:
        logger.error(f"Error al registrar la decisión del ticket {ticket_id}: {ex}")
        return f"No se pudo registrar la decisión sobre el ticket #{ticket_id}. Intenta nuevamente más tarde."

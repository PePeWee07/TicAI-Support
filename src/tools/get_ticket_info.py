import requests
from tools.config.registry import register_function, requires_roles
from config.logging_config import logger
import os

@requires_roles("get_ticket_info", ["ADMINISTRATIVO", "ESTUDIANTE"])
@register_function("get_ticket_info")
def get_ticket_info(**kwargs):
    """
    Obtiene información detallada de un ticket específico por su ID.
    
    Parámetros de la función:
    - ticket_id: ID del Ticket
    
    Datos del usuario
    - phone
    - names 
    - roles []
    - indetificacion 
    - emailInstitucional
    - emailPersonal
    - sexo 
    """ 
    
    ticket_id = kwargs.get("ticket_id")
    phone = kwargs.get("phone")

    urlBase = os.getenv("URL_BACKEND")
    url = urlBase + "v1/whatsapp/user/ticket/info"
    params = {
        "whatsappPhone": phone,
        "ticketId": ticket_id
    }
    headers = {
        os.getenv("BACKEND_HEADER"): os.getenv("API_KEY_BACKEND")
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        message = data.get("message")
        has_solution = data.get("hasSolution")

        if has_solution:
            return f"{message} Si lo deseas, ahora puedes aceptar o rechazar la solución registrada para este caso."
        else:
            return message
    except requests.exceptions.RequestException as ex:
        logger.error(f"Error al obtener la información del ticket {ticket_id}: {ex}")
        return f"No se pudo obtener la información del ticket #{ticket_id}. Intenta nuevamente más tarde."

import requests
from tools.config.registry import register_function, requires_roles
from config.logging_config import logger
import os

@requires_roles("get_user_tickets", ["DOCENTE", "ADMINISTRATIVO", "ENCARGATURA"])
@register_function("get_user_tickets")
def get_user_tickets(**kwargs):
    """
    Devuelve los tickets abiertos registrados por el usuario.
    
    Parámetros de la función:
    - (No tiene)
    
    Datos del usuario
    - phone
    - names 
    - roles []
    - indetificacion 
    - emailInstitucional
    - emailPersonal
    - sexo 
    """

    phone = kwargs.get("phone")

    urlBase = os.getenv("URL_BACKEND")
    url = urlBase + "v1/whatsapp/user/tickets/open"
    params = {"whatsappPhone": phone}

    headers = {
        os.getenv("BACKEND_HEADER"): os.getenv("API_KEY_BACKEND")
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        tickets = response.json()
        return f"Tickets: {tickets}, si algun ticket tiene estado resuelto, propon consultar la resolucion"
    except requests.exceptions.RequestException as ex:
        logger.error(f"Error al obtener tickets: {ex}")
        return "No se pudo obtener la información de tus tickets. Intenta más tarde."

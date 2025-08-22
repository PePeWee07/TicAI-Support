import requests
from tools.config.registry import register_function, requires_roles
from config.logging_config import logger
import os

@requires_roles("agg_attachment_existing_ticket", ["DOCENTE", "ADMINISTRATIVO", "ENCARGATURA"])
@register_function("agg_attachment_existing_ticket")
def agg_attachment_existing_ticket(**kwargs):
    """
    Desconectara el usario temporalmente de CATIA para que cargue los adjuntos a ticket previamente creados.
    
    Parámetros la función:
    - ticket_id: ID del ticket existente al que se le agregarán los adjuntos.
    
    Datos del usuario
    - phone
    - names 
    - roles []
    - indetificacion 
    - emailInstitucional
    - emailPersonal
    - sexo 
    """
    
    print("agg_attachment_existing_ticket called with kwargs: ", kwargs)
    
    ticket_id = kwargs.get("ticket_id")
    
    ttl_minutes = "15"
    allowed = "JPG/PNG/PDF/WORD/EXCEL"
    max_size_doc = "100MB"
    max_size_img = "5MB"
    
    # Datos del usuario
    phone = kwargs.get("phone")
    
    # URL del endpoint
    url = os.getenv("URL_BACKEND") + "v1/whatsapp/user/state/waiting-attachment/existing-ticket"
    params = {
        "ticketId": ticket_id,
        "whatsappPhone": phone
    }
    
    # Encabaezados
    headers = {
        os.getenv("BACKEND_HEADER"): os.getenv("API_KEY_BACKEND")
    }
    
    try:
        response = requests.patch(url, params=params, headers=headers)
        response.raise_for_status()
        print("Response received: ", response.text)
        return (
            f"""
            Ya está disponible la sesión/pasarela de adjuntos puedes enviar archivos o imágenes.
            - Se tomarán en cuenta solo los que envíes a partir de este mensaje.
            - Formatos permitidos: {allowed}. Tamaño máximo {max_size_doc} (documentos) y {max_size_img} (imágenes). 
            - Tienes {ttl_minutes} minutos para enviarlos. Cuando termines hazmelo saber.
            """
        )
    except requests.exceptions.RequestException as ex:
        logger.error(f"Error al enviar el ticket: {ex}")
        return "No se puede receptar adjuntos debido a un error interno, inténtalo más tarde."
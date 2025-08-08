import requests
from tools.config.registry import register_function, requires_roles
from config.logging_config import logger
import os

@requires_roles("agg_attachment", ["DOCENTE", "ADMINISTRATIVO", "ENCARGATURA"])
@register_function("agg_attachment")
def agg_attachment(**kwargs):
    """
    Desconectara el usario temporalmente de CATIA para que cargue los adjuntos.
    
    Sin Parámetros la función:
    
    Datos del usuario
    - phone
    - names 
    - roles []
    - indetificacion 
    - emailInstitucional
    - emailPersonal
    - sexo 
    """
    
    print("agg_attachment called with kwargs: ", kwargs)
    
    ttl_minutes = "15"
    allowed = "JPG/PNG/PDF/WORD/EXCEL"
    max_size_doc = "100MB"
    max_size_img = "5MB"
    
    # Datos del usuario
    phone = kwargs.get("phone")
    
    # URL del endpoint
    url = os.getenv("URL_BACKEND") + "v1/whatsapp/user/state/waiting-attachment"
    params = {"whatsappPhone": phone}
    
    # Encabaezados
    headers = {
        os.getenv("BACKEND_HEADER"): os.getenv("API_KEY_BACKEND")
    }
    
    try:
        print("Sending request to URL: ", url)
        response = requests.patch(url, params=params, headers=headers)
        response.raise_for_status()
        print("Response received: ", response.text)
        return (
            f"Ya está disponible la opción para enviar archivos o imágenes en esta conversación de WhatsApp. • Se tomarán en cuenta solo los que envíes a partir de este mensaje. • Formatos permitidos: {allowed}. Tamaño máximo {max_size_doc} (documentos) y {max_size_img} (imágenes). • Tienes {ttl_minutes} minutos para enviarlos. Cuando termines, escribeme solo un mensaje de texto para continuar."
        )
    except requests.exceptions.RequestException as ex:
        logger.error(f"Error al enviar el ticket: {ex}")
        return "No se puede receptar adjuntos debido a un error interno, inténtalo más tarde."
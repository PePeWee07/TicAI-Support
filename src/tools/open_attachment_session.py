import requests
from tools.config.registry import register_function, requires_roles
from config.logging_config import logger
import os

@requires_roles("open_attachment_session", ["DOCENTE", "ADMINISTRATIVO", "ENCARGATURA"])
@register_function("open_attachment_session")
def open_attachment_session(**kwargs):
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
    
    ttl_minutes = "10"
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
        return (
            f"Ya está disponible la sesión/pasarela de adjuntos.\n"
            f"- Se tomarán en cuenta solo los archivos enviados desde este mensaje y durante los próximos {ttl_minutes} minutos.\n"
            f"- Formatos permitidos: {allowed}.\n"
            f"- Tamaño máximo: {max_size_doc} (documentos) y {max_size_img} (imágenes)."
        )

    except requests.exceptions.RequestException as ex:
        logger.error(f"Error al enviar el ticket: {ex}")
        return "No se puede receptar adjuntos debido a un error interno, inténtalo más tarde."
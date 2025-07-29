import requests
import json
from tools.config.registry import register_function, requires_roles
from config.logging_config import logger
import os

@requires_roles("invite_user_feedback", ["DOCENTE", "ADMINISTRATIVO", "ENCARGATURA"])
@register_function("invite_user_feedback")
def invite_user_feedback(**kwargs):
    """
    Obtiene información detallada de un ticket específico por su ID.
    
    Parámetros de la función:
    - Ninguno
    
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
    url = urlBase + "v1/whatsapp/template-feedback"
    params = {"to": phone}
    headers = {os.getenv("BACKEND_HEADER"): os.getenv("API_KEY_BACKEND")}
    
    try:
        res = requests.post(url, params=params, headers=headers)
        res.raise_for_status()
        return "Se envió la encuesta al usuario; agradécele su disposición para completarla."
    except requests.exceptions.RequestException as ex:
        logger.error(f"Error al enviar la encuesta de feedback: {ex}")
        return "Lo siento, no pude enviarte la encuesta de feedback. Intenta más tarde."
    
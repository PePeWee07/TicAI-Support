from tools.registry import register_function
import requests
import os
from models.sendMessageToWhatsapp import WhatsAppMessage
from config.logging_config import logger

url = os.getenv("URL_BACKEND")
header = os.getenv("API_KEY_HEADER")
apiKey = os.getenv("API_KEY_BACKEND")

@register_function("solicitarTecnicoCambioCartucho")
def solicitarTecnicoCambioCartucho(**kwargs):
    """
    Solicita un técnico para cambiar cartuchos de tinta
    
    Parametros esperados:
    - phoneUser: numero de WhatsApp del solicitante
    - nameUser: Nombre del solicitante
    
    Parametros de Functions:
    - colorCartucho: color de tinta
    - tipoImpresora: modelo de impresora (Opcional)
    - ubicacion: Dirección del solicitante 
    """
    phoneTecnico = "593983439289"
    phoneUser = kwargs.get("phoneUser")
    nameUser = kwargs.get("nameUser")
    colorCartucho = kwargs.get("colorCartucho")
    tipoImpresora = kwargs.get("tipoImpresora", "No especificado")
    ubicacion = kwargs.get("ubicacion")
    
    for key, value in kwargs.items():
        print(f"{key}: {value}")
    
    mensaje_text = (
        f"Se solicita intervención técnica inmediata para cambio de cartucho de tinta. \n"
        f"Usuario: *{nameUser}* \n"
        f"Telefono del solicitante: *{phoneUser}* \n"
        f"Color: *{colorCartucho}* \n"
        f"Modelo impresora: *{tipoImpresora}* \n"
        f"Ubicación: *{ubicacion}* \n"
        f"Por favor, coordinar asistencia técnica."
    )
    
    mensaje = WhatsAppMessage( 
        number=phoneTecnico, 
        message=mensaje_text
    ) 
    
    try:
        headers = {header: apiKey}
        response = requests.post(
            url + "/send", 
            json=mensaje.model_dump(),
            headers=headers
        )
        
        if response.ok:
            return "True"
        else:
            logger.error(f"Error al enviar mensjae por la API WhatsApp-Backend: {response.text}")
            return "False"
    except Exception as e:
        logger.error(f"Excepción al enviar el mensaje: {e}")
        return "False"

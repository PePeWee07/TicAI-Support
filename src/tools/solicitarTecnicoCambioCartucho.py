from tools.registry import register_function
import requests
import os
from models.sendMessageToWhatsappDto import WhatsAppMessage
from models.sendEmailDto import EmailMessage
from config.logging_config import logger
import services.senEmail as ServiceEmail

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
    # PARAMETROS
    phoneTecnico = "593983439289"
    phoneUser = kwargs.get("phoneUser")
    nameUser = kwargs.get("nameUser")
    colorCartucho = kwargs.get("colorCartucho")
    tipoImpresora = kwargs.get("tipoImpresora", "No especificado")
    ubicacion = kwargs.get("ubicacion")
    
    mensaje = WhatsAppMessage( 
        number=phoneTecnico, 
        message=sendWhatsAppMessage(nameUser, phoneUser, colorCartucho, tipoImpresora, ubicacion)
    )
    
    sendEmailuser()
    
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

# ==================================================
# MENSAJE DE TEXTO
# ==================================================
def sendWhatsAppMessage(nameUser, phoneUser, colorCartucho, tipoImpresora, ubicacion):
    mensajeText = (
        f"Se solicita intervención técnica inmediata para cambio de cartucho de tinta. \n"
        f"Usuario: *{nameUser}* \n"
        f"Telefono del solicitante: *{phoneUser}* \n"
        f"Color: *{colorCartucho}* \n"
        f"Modelo impresora: *{tipoImpresora}* \n"
        f"Ubicación: *{ubicacion}* \n"
        f"Por favor, coordinar asistencia técnica."
    )
    return mensajeText
  
  
# ==================================================
# ENVIO DE EMAIL
# ==================================================
def sendEmailuser():
    email_data = EmailMessage(
        fromEmail=None,
        to=["pepewee07@gmail.com"],
        cc=["pepewee070@yopmail.com"],
        bcc=["pepewee071@yopmail.com"],
        subject="Prueba de envío",
        body="<h1>Hola, este es un correo de prueba para Asistente Virtual</h1>",
        html=True,
        attachments=["src/docs/albiononline-key.pdf", "src/docs/ucacue-logo-centro-mediacion.png"]
    )
    
    res = ServiceEmail.sendEmail(email_data)
    print("RESPUESTA EMAIL: ",res)

from typing import List, Optional
from pydantic import BaseModel, EmailStr

class EmailMessage(BaseModel):
    # Dirección del remitente (opcional si se define a nivel de configuración)
    fromEmail: Optional[EmailStr] = None
    # Lista de destinatarios principales
    to: List[EmailStr]
    # Lista de direcciones para CC (copia visible)
    cc: Optional[List[EmailStr]] = None
    # Lista de direcciones para BCC (copia oculta)
    bcc: Optional[List[EmailStr]] = None
    # Asunto del correo
    subject: str
    # Cuerpo del mensaje
    body: str
    # Indica si el cuerpo es HTML (True) o texto plano (False)
    html: bool = False
    # Lista de rutas de archivos a adjuntar
    attachments: Optional[List[str]] = None

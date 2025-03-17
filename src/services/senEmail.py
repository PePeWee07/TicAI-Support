import smtplib
import logging
import os
import mimetypes
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from models.sendEmailDto import EmailMessage

# Variables globales de configuración
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")

def sendEmail(email: EmailMessage, retries: int = 3, retry_delay: int = 5) -> bool:
    """
    Envía un correo electrónico con soporte para:
      - destinatario (debe ser una dirección de correo válida) o default
      - Múltiples destinatarios (to, cc, bcc)
      - Adjuntar archivos
      - Cuerpo en texto plano o HTML
      - Reintentos automáticos en caso de error

    Parámetros:
      - email: instancia de EmailMessage.
      - retries: número de intentos en caso de error (default: 3).
      - retry_delay: segundos de espera entre reintentos (default: 5).
    Retorna:
      - True si se envía correctamente; False en caso contrario.
    """
    if not all([SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD, DEFAULT_FROM_EMAIL]):
        logging.error("Credenciales de SMTP no configuradas o erróneas.")
        return False

    from_email = email.fromEmail or DEFAULT_FROM_EMAIL
    toEmails = email.to
    ccEmails = email.cc or []
    bccEmails = email.bcc or []
    attachments = email.attachments or []

    # Crear el objeto de mensaje
    mensaje = MIMEMultipart()
    mensaje['From'] = from_email
    mensaje['To'] = ", ".join(toEmails)
    mensaje['Subject'] = email.subject
    if ccEmails:
        mensaje['Cc'] = ", ".join(ccEmails)

    subtype = 'html' if email.html else 'plain'
    mensaje.attach(MIMEText(email.body, subtype))

    # Adjuntar archivos
    for filepath in attachments:
        if os.path.exists(filepath):
            ctype, encoding = mimetypes.guess_type(filepath)
            if ctype is None or encoding is not None:
                ctype = "application/octet-stream"
            maintype, subtype_file = ctype.split('/', 1)
            try:
                with open(filepath, 'rb') as f:
                    part = MIMEBase(maintype, subtype_file)
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                filename = os.path.basename(filepath)
                part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                mensaje.attach(part)
            except Exception as attach_error:
                logging.error("Error al adjuntar %s: %s", filepath, attach_error)
        else:
            logging.warning("Archivo no encontrado: %s", filepath)

    all_recipients = toEmails + ccEmails + bccEmails

    attempt = 0
    while attempt < retries:
        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as servidor:
                servidor.ehlo()
                servidor.starttls()
                servidor.ehlo()
                servidor.login(SMTP_USERNAME, SMTP_PASSWORD)
                servidor.sendmail(from_email, all_recipients, mensaje.as_string())
            logging.info("Correo enviado a: %s", ", ".join(all_recipients))
            return True
        except smtplib.SMTPAuthenticationError as auth_err:
            attempt += 1
            logging.error("Error de autenticación en intento %d: %s", attempt, auth_err)
            if attempt < retries:
                logging.info("Reintentando en %d segundos...", retry_delay)
                time.sleep(retry_delay)
        except smtplib.SMTPException as smtp_err:
            attempt += 1
            logging.error("Error SMTP en intento %d: %s", attempt, smtp_err)
            if attempt < retries:
                logging.info("Reintentando en %d segundos...", retry_delay)
                time.sleep(retry_delay)
        except Exception as e:
            attempt += 1
            logging.error("Error inesperado en intento %d: %s", attempt, e)
            if attempt < retries:
                logging.info("Reintentando en %d segundos...", retry_delay)
                time.sleep(retry_delay)
    return False

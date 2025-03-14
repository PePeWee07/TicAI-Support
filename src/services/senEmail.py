import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

# Configuración del servidor SMTP de AWS SES
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")

def sendEmail(toEmail, subjectEmail, bodyEmail):
    # Crear el objeto del mensaje
    mensaje = MIMEMultipart()
    mensaje['From'] = FROM_EMAIL
    mensaje['To'] = toEmail
    mensaje['Subject'] = subjectEmail

    # Cuerpo del mensaje
    cuerpo = bodyEmail
    mensaje.attach(MIMEText(cuerpo, 'plain'))

    # Enviar el correo usando TLS
    try:
        # Conexión al servidor SMTP
        servidor = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        servidor.ehlo()
        servidor.starttls()
        servidor.ehlo()

        # Autenticación en el servidor
        servidor.login(SMTP_USERNAME, SMTP_PASSWORD)

        # Envío del correo
        servidor.sendmail(FROM_EMAIL, toEmail, mensaje.as_string())
        print("Correo enviado exitosamente.")
    except Exception as e:
        print("Error al enviar el correo:", e)
    finally:
        servidor.quit()


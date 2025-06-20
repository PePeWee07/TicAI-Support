import services.senEmail as ServiceEmail
from models.sendEmailDto import EmailMessage
from tools.config.registry import register_function, requires_roles
from config.logging_config import logger

@requires_roles("send_support_email", ["DOCENTE", "ADMINISTRATIVO", "ENCARGATURA"])
@register_function("send_support_email")
def send_support_email(**kwargs):
    """
    Envía un correo electrónico con la consulta y los datos del usuario a soporte Tic.
    
    Parámetros de la función:
    - user_query: Texto original de la consulta del usuario
    - subject: Asunto del correo electrónico
    - body: Cuerpo del correo electrónico
    
    Datos del usuario
    - phone
    - names 
    - roles ["...", "...", "..."]
    - indetificacion 
    - emailInstitucional
    - emailPersonal
    - sexo 
    """
    print("send_support_email called with kwargs:", kwargs)
    
    user_query = kwargs.get("user_query", "No query provided")
    subject = kwargs.get("subject", "No subject provided")
    body = kwargs.get("body", "No body provided")
    
    # Datos del usaurio
    phone = kwargs.get("phone")
    nameUser = kwargs.get("names")
    indentification = kwargs.get("identificacion")

    try:
        email_body = f"""
        <html>
            <body>
            <h2>Consulta del Usuario</h2>
            <p><strong>Consulta:</strong> {user_query}</p>
            <h3>Detalles del Usuario</h3>
            <ul>
                <li><strong>Nombre:</strong> {nameUser}</li>
                <li><strong>Teléfono:</strong> {phone}</li>
                <li><strong>Identificación:</strong> {indentification}</li>
            </ul>
            <h3>Mensaje</h3>
            <p>{body}</p>
            </body>
        </html>
        """
        
        email_data = EmailMessage(
            to=["pepewee010101@yopmail.com"],
            subject=subject,
            body=email_body,
            html=True
        )
        success = ServiceEmail.sendEmail(email_data)  # True/False
        
        if success:
            return "Email enviado con éxito"
        else:
            return "No se pudo enviar el email"  
            
    except Exception as e:
        logger.error(f"Error al enviar el email: {e}")
        return "No se pudo enviar el email debido a un error interno"

from tools.registry import register_function
import services.senEmail as ServiceEmail
from models.sendEmailDto import EmailMessage

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
            to=["pepewee07@gmail.com"],
            subject=subject,
            body=email_body,
            html=True
        )
        success = ServiceEmail.sendEmail(email_data)  # True/False
        return str(success)   
    except Exception as e:
        print(f"Error sending email: {e}")
        return "Error sending email"

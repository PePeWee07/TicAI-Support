from tools.registry import register_function
import services.senEmail as ServiceEmail
from models.sendEmailDto import EmailMessage

@register_function("send_support_email")
def send_support_email(**kwargs):
    """
    Sends a support email with the provided details.
    
    Expected parameters:
    - email: Email address of the recipient
    - subject: Subject of the email
    - message: Body of the email
    """
    print("send_support_email called with kwargs:", kwargs)
    
    user_query = kwargs.get("user_query", "No query provided")
    subject = kwargs.get("subject", "No subject provided")
    body = kwargs.get("body", "No body provided")
    
    # Datos del usaurio
    phoneUser = kwargs.get("phoneUser", "No phone provided")
    nameUser = kwargs.get("nameUser", "No name provided")

    try:
        email_data = EmailMessage(
            to=["pepewee07@gmail.com"],
            subject=subject,
            body=f"<h6>{user_query}</h6> <br> <p>{body}</p>",
            html=True
        )
        success = ServiceEmail.sendEmail(email_data)  # True/False
        return str(success)   
    except Exception as e:
        print(f"Error sending email: {e}")
        return "Error sending email"

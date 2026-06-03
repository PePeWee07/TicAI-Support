import services.senEmail as ServiceEmail
from models.sendEmailDto import EmailMessage
from tools.config.registry import register_function, requires_roles
from config.logging_config import logger

# Destinatario del aviso de escalamiento a agente humano.
HANDOFF_RECIPIENT = "jose.roman@ucacue.edu.ec"

@requires_roles("request_human_handoff", ["DOCENTE", "ADMINISTRATIVO", "ENCARGATURA"])
@register_function("request_human_handoff")
def request_human_handoff(**kwargs):
    """
    Notifica por correo al equipo de soporte que el usuario solicita ser
    atendido por un agente humano, para que una persona tome la conversación.

    Parámetros de la función (provistos por el modelo):
    - reason: Motivo principal por el que se solicita el agente humano.
    - summary: Resumen breve del historial/problema para dar contexto al agente.

    Datos del usuario (inyectados por el despachador):
    - phone
    - names
    - roles ["...", "...", "..."]
    - identificacion
    - emailInstitucional
    - emailPersonal
    - sexo
    """
    print("request_human_handoff called with kwargs:", kwargs)

    # Argumentos del modelo
    reason = kwargs.get("reason", "No se especificó motivo")
    summary = kwargs.get("summary", "No se proporcionó resumen")

    # Datos del usuario
    phone = kwargs.get("phone")
    name_user = kwargs.get("names")
    identificacion = kwargs.get("identificacion")
    roles = kwargs.get("roles") or []
    email_institucional = kwargs.get("emailInstitucional")
    email_personal = kwargs.get("emailPersonal")

    roles_str = ", ".join(roles) if isinstance(roles, list) else str(roles)

    try:
        email_body = f"""
        <html>
            <body>
            <h2>🚨 Solicitud de atención por agente humano</h2>
            <p>Un usuario solicitó, a través de CatIA, ser transferido a un agente humano de soporte.</p>

            <h3>Detalle de la solicitud</h3>
            <ul>
                <li><strong>Motivo:</strong> {reason}</li>
                <li><strong>Resumen:</strong> {summary}</li>
            </ul>

            <h3>Datos del usuario</h3>
            <ul>
                <li><strong>Nombre:</strong> {name_user}</li>
                <li><strong>Teléfono (WhatsApp):</strong> {phone}</li>
                <li><strong>Identificación:</strong> {identificacion}</li>
                <li><strong>Roles:</strong> {roles_str}</li>
                <li><strong>Email institucional:</strong> {email_institucional}</li>
                <li><strong>Email personal:</strong> {email_personal}</li>
            </ul>
            </body>
        </html>
        """

        email_data = EmailMessage(
            to=[HANDOFF_RECIPIENT],
            subject=f"[CatIA] Escalamiento a agente humano - {name_user or phone or 'Usuario'}",
            body=email_body,
            html=True
        )
        success = ServiceEmail.sendEmail(email_data)  # True/False

        if success:
            return (
                "Se notificó al equipo de soporte para que un agente humano tome la "
                "conversación. Informa al usuario que en breve será atendido por una persona."
            )
        else:
            return "No se pudo notificar al equipo de soporte en este momento. Intenta nuevamente más tarde."

    except Exception as e:
        logger.error(f"Error al solicitar handoff a agente humano: {e}")
        return "No se pudo procesar la solicitud de agente humano debido a un error interno."

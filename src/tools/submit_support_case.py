import requests
from tools.config.registry import register_function, requires_roles
from config.logging_config import logger
import os

@requires_roles("submit_support_case", ["DOCENTE", "ADMINISTRATIVO", "ENCARGATURA"])
@register_function("submit_support_case")
def submit_support_case(**kwargs):
    """
    Crea un ticket a la mesa de servicios para soporte Tic.
    
    Parámetros de la función:
    - asunto: titulo del incidente
    - description: Descripcion del incidente
    - observadores: lista de correos de observadores (opcional)
    
    Datos del usuario
    - phone
    - names 
    - roles []
    - indetificacion 
    - emailInstitucional
    - emailPersonal
    - sexo 
    """
    
    print("submit_support_case called with kwargs: ", kwargs)
    
    # Datos Funcion
    description = kwargs.get("description")
    asunto = kwargs.get("asunto")
    
    # Datos del usuario
    phone = kwargs.get("phone")
    emailInstitucional = kwargs.get("emailInstitucional")
    emailPersonal = kwargs.get("emailPersonal")
    emailObservers = kwargs.get("observadores", [])

    email = emailInstitucional or emailPersonal or "virtual.assistant.uc@ucacue.edu.ec"
    ticket_data = {
        "input": {
            "name": asunto,
            "content": description,
            "entities_id": 0,
            "requesttypes_id": 1,
            "_users_id_requester": 0,
            "_users_id_requester_notif": {
                "use_notification": 1,
                "alternative_email": [email]
            },
            "users_id_lastupdater": 0
        }
    }
    
    if emailObservers:
        ticket_data["input"]["_users_id_observer"] = [0] * len(emailObservers)
        ticket_data["input"]["_users_id_observer_notif"] = {
            "use_notification": [1] * len(emailObservers),
            "alternative_email": emailObservers
        }
    # else:
    #     ticket_data["input"]["_users_id_observer"] = None
    #     ticket_data["input"]["_users_id_observer_notif"] = None
        
    print("Ticket data prepared: ", ticket_data)
    
    # URL del endpoint
    urlBase = os.getenv("URL_BACKEND")
    url = urlBase + "v1/glpi/ticket"
    params = {"whatsappPhone": phone}
    
    # Encabaezados
    headers = {
        os.getenv("BACKEND_HEADER"): os.getenv("API_KEY_BACKEND")
    }
    
    try:
        response = requests.post(url, json=ticket_data, params=params, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        return f"Ticket creado: {response_data}, puedes requerir la informacion del ticket para ver su avance"
    except requests.exceptions.RequestException as ex:
        logger.error(f"Error al enviar el ticket: {ex}")
        return "No se pudo enviar el ticket debido a un error interno"
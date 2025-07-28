import requests
import json
from tools.config.registry import register_function, requires_roles
from config.logging_config import logger
import os

@requires_roles("get_ticket_info", ["DOCENTE", "ADMINISTRATIVO", "ENCARGATURA"])
@register_function("get_ticket_info")
def get_ticket_info(**kwargs):
    """
    Obtiene información detallada de un ticket específico por su ID.
    
    Parámetros de la función:
    - ticket_id: ID del Ticket
    
    Datos del usuario
    - phone
    - names 
    - roles []
    - indetificacion 
    - emailInstitucional
    - emailPersonal
    - sexo 
    """ 
    ticket_id = kwargs.get("ticket_id")
    phone = kwargs.get("phone")

    urlBase = os.getenv("URL_BACKEND")
    url = urlBase + "v1/whatsapp/user/ticket/info"
    params = {"whatsappPhone": phone, "ticketId": ticket_id}
    headers = {os.getenv("BACKEND_HEADER"): os.getenv("API_KEY_BACKEND")}

    try:
        resp = requests.get(url, params=params, headers=headers)
        resp.raise_for_status()
        info = resp.json()

        output = {}

        # 1) Datos básicos
        if info.get("requester_email"):
            output["requester_email"] = info["requester_email"]
        if info.get("watcher_emails"):
            output["watcher_emails"] = info["watcher_emails"]

        # 2) Técnicos asignados (solo datos útiles)
        techs = info.get("assigned_techs", [])
        if techs:
            output["assigned_techs"] = [
                {
                    "name": f"{t.get('firstname','')} {t.get('realname','')}".strip(),
                    "location": t.get("locations_id"),
                    "title": t.get("usertitles_id")
                }
                for t in techs
            ]

        # 3) Datos del ticket (solo claves no nulas)
        ticket = info.get("ticket", {})
        if ticket:
            output["ticket"] = {
                k: v for k, v in ticket.items()
                if v not in (None, "", [], {})
                and k in (
                    "id",
                    "name",
                    "closedate",
                    "solvedate",
                    "date_mod",
                    "status",
                    "content",
                    "urgency",
                    "impact",
                    "priority",
                    "itilcategories_id",
                    "type",
                    "locations_id",
                    "date_creation",
                )
            }

        # 4) Soluciones válidas
        sols = [
            {
                "content": s["content"],
                "date": s["date_creation"],
                "has_attachments": bool(s.get("mediaFiles"))
            }
            for s in info.get("solutions", [])
            if s.get("status", "").lower() != "rechazado"
        ]
        if sols:
            output["solutions"] = sols

        # 5) Notas o seguimientos
        notes = [
            {
                "date": n["date_creation"],
                "content": n["content"],
                "has_attachments": bool(n.get("mediaFiles"))
            }
            for n in info.get("notes", [])
        ]
        if notes:
            output["notes"] = notes

        return json.dumps(output)

    except requests.exceptions.RequestException as ex:
        logger.error(f"Error al obtener la información del ticket {ticket_id}: {ex}")
        error_obj = {
            "error": f"No se pudo obtener la información del ticket #{ticket_id}. Intenta nuevamente más tarde."
        }
        return json.dumps(error_obj)
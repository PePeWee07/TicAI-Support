import requests
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

        # 1) Solución válida
        sol = next(
            (s for s in info.get("solutions", [])
            if s.get("status","").lower() != "Rechazado"),
            None
        )
        if sol:
            lines = [
                f"Tu ticket *{ticket_id}* tiene solución:",
                f"Fecha: {sol['date_creation']}",
                sol["content"],
            ]
            media = sol.get("mediaFiles", [])
            if media:
                names = [m["name"] for m in media]
                lines.append(
                    f"Se enviaron {len(media)} archivo(s) adjunto(s): " +
                    ", ".join(names)
                )
            lines.append("\n¿Deseas *Aceptar solución* o *Rechazar solución*?")
            return "\n".join(lines)

        # 2) Seguimiento
        notes = info.get("notes", [])
        if notes:
            last = notes[-1]
            return (
                f"Tu ticket *{ticket_id}* no tiene solución aún, "
                "pero aquí está el último seguimiento:\n"
                f"Fecha: {last['date_creation']}\n"
                f"{last['content']}"
            )

        # 3) Asignación
        techs = info.get("assigned_techs", [])
        if techs:
            names = [f"{t['firstname']} {t['realname']}" for t in techs]
            return (
                f"Tu ticket *{ticket_id}* aún no tiene solución ni seguimiento, "
                f"pero está asignado a: {', '.join(names)}."
            )

        # 4) Nada
        return (
            f"Tu ticket *{ticket_id}* aún no tiene solución, "
            "seguimiento ni técnico asignado."
        )
    except requests.exceptions.RequestException as ex:
        logger.error(f"Error al obtener la información del ticket {ticket_id}: {ex}")
        return f"No se pudo obtener la información del ticket #{ticket_id}. Intenta nuevamente más tarde."

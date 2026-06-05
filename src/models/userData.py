from pydantic import BaseModel, Field, EmailStr
from typing import Dict, List, Optional

class UserData(BaseModel):
    ask: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=1)
    roles: List[str] = Field(..., min_items=1)
    identificacion: str = Field(..., min_length=1)

    # Campos opcionales
    previousResponseId: Optional[str] = None
    emailInstitucional: Optional[EmailStr] = None
    emailPersonal: Optional[EmailStr] = None
    sexo: Optional[str] = None

    # Permisos dinámicos de tools enviados por el core: { "tool_name": ["ROL1", "ROL2"] }.
    # Si una tool aparece aquí, manda sobre el decorador estático (lista vacía = denegar a todos).
    # Si es None o la tool no aparece, se usa el @requires_roles estático como fallback.
    toolPermissions: Optional[Dict[str, List[str]]] = None

    # Enfriamiento (cooldown) por tool, enviado por el core:
    #  - toolCooldowns: segundos configurados { "tool_name": 300 }. Si > 0, la tool es "limitada".
    #  - toolCooldownRemaining: segundos que le quedan a ESTE usuario { "tool_name": 120 }.
    toolCooldowns: Optional[Dict[str, int]] = None
    toolCooldownRemaining: Optional[Dict[str, int]] = None

from pydantic import BaseModel, Field, model_validator, EmailStr
from typing import List, Optional

class UserData(BaseModel):
    ask: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=1)
    roles: List[str] = Field(..., min_items=1)
    identificacion: str = Field(..., min_length=1)

    # Campos opcionales
    thread_id: Optional[str] = None
    emailInstitucional: Optional[EmailStr] = None
    emailPersonal: Optional[EmailStr] = None
    sexo: Optional[str] = None

@model_validator(mode="after")
def al_menos_un_correo(cls, data: "UserData") -> "UserData":
    if not data.emailInstitucional and not data.emailPersonal:
        raise ValueError(
            "Se requiere al menos un correo electrónico (institucional o personal)."
        )
    return data
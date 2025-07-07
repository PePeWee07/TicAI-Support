from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

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

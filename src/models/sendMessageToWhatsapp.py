from pydantic import BaseModel

class WhatsAppMessage(BaseModel):
    number: str
    message: str

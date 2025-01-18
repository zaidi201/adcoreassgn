from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class PaymentSchema(BaseModel):
    payee_first_name: str
    payee_last_name: str
    payee_email: EmailStr
    # Add all other fields with types

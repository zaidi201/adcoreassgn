from pydantic import BaseModel, Field, EmailStr
from datetime import datetime,date

class Payment(BaseModel):
    payee_first_name: str
    payee_last_name: str
    payee_payment_status: str
    payee_added_date_utc: datetime
    payee_due_date: datetime
    payee_address_line_1: str
    payee_address_line_2: str = None
    payee_city: str
    payee_country: str
    payee_province_or_state: str = None
    payee_postal_code: str
    payee_phone_number: str
    payee_email: EmailStr
    currency: str
    discount_percent: float = 0.0
    tax_percent: float = 0.0
    due_amount: float
    total_due: float = Field(default=0.0)

from pydantic import BaseModel
from typing import Optional

class SigninInput(BaseModel):
    name: str
    email: str
    password: str
    phone: str
    address: str

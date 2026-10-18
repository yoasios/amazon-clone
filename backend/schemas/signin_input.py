from pydantic import BaseModel

class signin_input(BaseModel):
    name: str
    email: str
    password: str

from pydantic import BaseModel

class login_input(BaseModel):
    email: str
    password: str

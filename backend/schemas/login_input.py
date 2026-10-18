from pydantic import BaseModel

class LoginInput(BaseModel):
    email: str
    password: str

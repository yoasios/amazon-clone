from pydantic import BaseModel

class SigninInput(BaseModel):
    name: str
    email: str
    password: str

from pydantic import BaseModel, EmailStr

class CreateRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
from pydantic import BaseModel, EmailStr

class CreateResponse(BaseModel):
    username: str
    email: EmailStr
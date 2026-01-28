from pydantic import BaseModel, EmailStr

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str
    is_admin: bool

    class Config:
        from_attributes = True

from typing import Literal

from pydantic import BaseModel, Field


class AdminCreateUserRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    role: Literal["student", "teacher", "admin"]
    password: str = Field(min_length=8, max_length=128)


class AdminCreateUserResponse(BaseModel):
    id: int
    email: str
    role: str
    is_admin: bool


class AdminUserOut(BaseModel):
    id: int
    email: str
    role: str
    is_admin: bool
    must_change_password: bool

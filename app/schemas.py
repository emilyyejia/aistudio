from pydantic import BaseModel, EmailStr
from typing import Optional
import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: Optional[datetime.datetime]


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

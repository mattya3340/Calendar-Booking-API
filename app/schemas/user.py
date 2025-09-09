from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    email: EmailStr
    password: str
    full_name: str
    phone_number: str

class UserUpdate(UserBase):
    password: Optional[str] = Field(None, min_length=6, max_length=100)
    phone_number: Optional[str] = None

class UserInDBBase(UserBase):
    id: int
    email: EmailStr
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime

class UserBase(BaseModel):
    email: Optional[EmailStr] = Field(None, description="メールアドレス")
    full_name: Optional[str] = Field(None, description="氏名")
    is_active: bool = Field(True, description="アカウントが有効かどうか")
    is_superuser: bool = Field(False, description="管理者権限を持つかどうか")

class UserCreate(UserBase):
    email: EmailStr = Field(..., description="登録するメールアドレス")
    password: str = Field(..., description="パスワード")
    full_name: str = Field(..., description="氏名")
    phone_number: str = Field(..., description="電話番号")

class UserUpdate(UserBase):
    password: Optional[str] = Field(None, min_length=6, max_length=100, description="新しいパスワード")
    phone_number: Optional[str] = Field(None, description="新しい電話番号")

class UserInDBBase(UserBase):
    id: int = Field(..., description="ユーザーID")
    email: EmailStr = Field(..., description="メールアドレス")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: Optional[datetime] = Field(None, description="更新日時")

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str
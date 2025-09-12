from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class Token(BaseModel):
    """
    認証トークンと関連情報を含むレスポンスのスキーマです。
    """
    access_token: str = Field(..., description="JWTアクセストークン")
    token_type: str = Field(default="bearer", description="トークンの種別")
    expires_in: int = Field(..., description="トークンの有効期限（秒）")
    key_expires_at: int = Field(
        ...,
        description="署名に使われた鍵の有効期限（UNIXタイムスタンプ）"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "key_expires_at": 1735689600
            }
        }

class TokenPayload(BaseModel):
    """
    JWTトークンのペイロード（中身）のスキーマです。
    """
    sub: Optional[int] = Field(None, description="サブジェクト（通常はユーザーID）")
    exp: Optional[int] = Field(None, description="トークンの有効期限（UNIXタイムスタンプ）")
    iat: Optional[int] = Field(None, description="トークンの発行日時（UNIXタイムスタンプ）")
    key_exp: Optional[int] = Field(
        None,
        description="署名鍵の有効期限（UNIXタイムスタンプ）"
    )
    is_superuser: bool = Field(False, description="ユーザーが管理者権限を持つかどうか")

    class Config:
        json_schema_extra = {
            "example": {
                "sub": 1,
                "exp": 1672531200,
                "iat": 1672527600,
                "key_exp": 1675119600,
                "is_superuser": False
            }
        }

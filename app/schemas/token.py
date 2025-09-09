from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class Token(BaseModel):
    """
    Token response schema including access token and metadata.
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Type of token")
    expires_in: int = Field(..., description="Time in seconds until the token expires")
    key_expires_at: int = Field(
        ...,
        description="Timestamp when the current signing key will expire"
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
    JWT token payload schema.
    """
    sub: Optional[int] = Field(None, description="Subject (user ID)")
    exp: Optional[int] = Field(None, description="Expiration time (UNIX timestamp)")
    iat: Optional[int] = Field(None, description="Issued at (UNIX timestamp)")
    key_exp: Optional[int] = Field(
        None, 
        description="Signing key expiration time (UNIX timestamp)"
    )
    is_superuser: bool = Field(False, description="Whether the user is a superuser")

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

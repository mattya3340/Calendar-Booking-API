from typing import Generator, Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud, models
from app.schemas.token import TokenPayload
from app.core import security
from app.core.config import settings
from app.core.jwt_key_manager import jwt_key_manager
from app.db.session import SessionLocal

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login/access-token"
)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db), 
    token: str = Depends(reusable_oauth2)
) -> models.User:
    """
    Get the current user from the JWT token in the Authorization header.
    
    Args:
        request: The FastAPI request object
        db: Database session
        token: JWT token from the Authorization header
        
    Returns:
        models.User: The authenticated user
        
    Raises:
        HTTPException: If the token is invalid or the user doesn't exist
    """
    try:
        # Verify the token using our security module
        payload = security.verify_jwt_token(token)
        token_data = TokenPayload(**payload)
        
        # Get the user from the database
        user = crud.user.get(db, id=token_data.sub)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        # Check if the user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
            
        # Optional: Log the request
        if hasattr(request.state, 'user_agent'):
            user_agent = request.state.user_agent
            print(f"User {user.email} authenticated from {request.client.host} using {user_agent}")
            
        return user
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (jwt.JWTError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Wrapper for get_current_user that ensures the user is active.
    
    This is kept for backward compatibility and follows the principle of
    least surprise, but get_current_user already checks for active status.
    """
    return current_user

async def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Get the current user and verify they are a superuser.
    
    Args:
        current_user: The authenticated user from get_current_user
        
    Returns:
        models.User: The authenticated superuser
        
    Raises:
        HTTPException: If the user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user

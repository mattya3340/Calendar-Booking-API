from datetime import datetime, timedelta
from typing import Any, Optional, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings
from .jwt_key_manager import jwt_key_manager

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a new JWT access token.
    
    Args:
        subject: The subject of the token (usually user ID)
        expires_delta: Optional timedelta for token expiration
        
    Returns:
        str: Encoded JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # Get the current key and its expiry time
    secret_key, key_expiry = jwt_key_manager.get_current_key()
    
    # Include key expiry in the token payload for verification
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "key_exp": int(key_expiry.timestamp()),  # Add key expiry timestamp
        "iat": int(datetime.utcnow().timestamp())  # Issued at
    }
    
    # Encode the token with the current key
    encoded_jwt = jwt.encode(
        to_encode,
        secret_key,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        plain_password: The plain text password
        hashed_password: The hashed password to verify against
        
    Returns:
        bool: True if the password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Generate a secure password hash.
    
    Args:
        password: The plain text password to hash
        
    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)

def verify_jwt_token(token: str) -> dict:
    """
    Verify a JWT token and return its payload.
    
    Args:
        token: The JWT token to verify
        
    Returns:
        dict: The decoded token payload
        
    Raises:
        JWTError: If the token is invalid or expired
    """
    try:
        # Get the unverified header to check for key ID (if using multiple keys)
        unverified_header = jwt.get_unverified_header(token)
        key_id = unverified_header.get('kid')
        
        # Get the appropriate key for verification
        secret_key = jwt_key_manager.get_key_for_verification(key_id)
        
        # Decode and verify the token
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=[settings.ALGORITHM]
        )
        
        # Additional verification for key expiry if needed
        key_expiry = payload.get('key_exp')
        if key_expiry and datetime.utcnow().timestamp() > key_expiry:
            raise jwt.ExpiredSignatureError('Key has expired')
            
        return payload
        
    except jwt.JWTError as e:
        # Re-raise with a more descriptive message
        raise jwt.JWTError(f'Invalid token: {str(e)}')

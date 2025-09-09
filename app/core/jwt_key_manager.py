import secrets
import time
from datetime import datetime, timedelta
from typing import Tuple, Optional

class JWTKeyManager:
    _instance = None
    _current_key: str
    _key_expiry: datetime
    _key_lifetime: timedelta
    _key_length: int = 32  # 256 bits

    def __new__(cls, key_lifetime_days: int = 30):
        if cls._instance is None:
            cls._instance = super(JWTKeyManager, cls).__new__(cls)
            cls._key_lifetime = timedelta(days=key_lifetime_days)
            cls._rotate_key()
        return cls._instance

    @classmethod
    def _generate_key(cls) -> str:
        """Generate a new secure random key"""
        return secrets.token_urlsafe(cls._key_length)

    @classmethod
    def _rotate_key(cls):
        """Rotate to a new key"""
        cls._current_key = cls._generate_key()
        cls._key_expiry = datetime.utcnow() + cls._key_lifetime

    @classmethod
    def get_current_key(cls) -> Tuple[str, datetime]:
        """
        Get the current key and its expiry time.
        Automatically rotates the key if it has expired.
        """
        if datetime.utcnow() >= cls._key_expiry:
            cls._rotate_key()
        return cls._current_key, cls._key_expiry

    @classmethod
    def get_key_for_verification(cls, key_id: Optional[str] = None) -> str:
        """
        Get a key for verification.
        In a distributed system, you would use the key_id to get the correct key.
        For simplicity, we're just returning the current key here.
        """
        current_key, _ = cls.get_current_key()
        return current_key

# Initialize with default 30-day key rotation
jwt_key_manager = JWTKeyManager()

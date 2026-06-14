from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import jwt, JWTError
import bcrypt
from cryptography.fernet import Fernet
from app.core.config import settings

def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    try:
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt())
    return hashed.decode('utf-8')

# JWT helpers
def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    """
    Decodes a JWT token. Raises JWTError if invalid or expired.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

# Fernet encryption for API keys stored in DB
def get_fernet_cipher() -> Fernet:
    # Ensure key is correctly padded/valid bytes
    key = settings.ENCRYPTION_KEY.encode()
    return Fernet(key)

def encrypt_api_key(api_key: str) -> str:
    if not api_key:
        return ""
    cipher = get_fernet_cipher()
    return cipher.encrypt(api_key.encode()).decode()

def decrypt_api_key(encrypted_api_key: str) -> str:
    if not encrypted_api_key:
        return ""
    cipher = get_fernet_cipher()
    return cipher.decrypt(encrypted_api_key.encode()).decode()

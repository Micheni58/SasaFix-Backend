# server/core/security.py - Dev 1
import base64
import hashlib
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from jose import jwt
from passlib.context import CryptContext

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))


def _pre_hash(password: str) -> str:
    """SHA-256 pre-hash to remove bcrypt 72 byte limit."""
    return base64.b64encode(hashlib.sha256(password.encode()).digest()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(_pre_hash(plain_password), hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(_pre_hash(password))


def create_access_token(data: dict) -> str:
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is not set.")
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
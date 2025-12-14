from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET = "dev-secret"

def get_password_hash(p: str):
    return pwd.hash(p)

def verify_password(p: str, h: str):
    return pwd.verify(p, h)

def create_token(data: dict):
    data["exp"] = datetime.utcnow() + timedelta(hours=6)
    return jwt.encode(data, SECRET, algorithm="HS256")
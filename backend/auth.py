from datetime import datetime, timezone
from passlib.hash import bcrypt
import jwt
from config import Config

def hash_password(password: str) -> str:
    return bcrypt.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.verify(password, password_hash)

def create_token(user_id: int, role: str, email: str):
    now = datetime.now(tz=timezone.utc)
    payload = {
        "sub": str(user_id),
        "role": role,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int((now + Config.JWT_EXPIRES_DELTA).timestamp()),
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")

def decode_token(token: str):
    return jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])

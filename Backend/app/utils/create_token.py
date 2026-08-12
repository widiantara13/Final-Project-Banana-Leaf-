from jose import jwt
from datetime import datetime, timedelta, timezone
from app.schemas.create_token_schema import Token
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

secret = os.getenv("SESS_TOKEN")
algoritma = os.getenv("HASH_ALGORITMA")

def create_access_token(data: Token):
    payload = {"sub": data.email, "email": data.email, "uuid": data.uuid}
    expire = datetime.now(timezone.utc) + data.expire_delta
    payload.update({"exp": expire})
    return jwt.encode(payload, secret, algoritma)

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher
from fastapi import HTTPException
import os
from datetime import datetime, timedelta, timezone
import secrets
import crud
import hashlib



SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

pwd_context = PasswordHash((BcryptHasher(),))

def hash_password(password: str):
    return pwd_context.hash(password)

def hash_token(token: str):
    return hashlib.sha256(token.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="無効なトークンです")
        return user_id
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="トークンが不正です")

def create_refresh_token(db, user_id: int):
    expire = datetime.now(timezone.utc) + timedelta(days=30)
    token_string = secrets.token_urlsafe(32)
    crud.data_save_refresh_token(db, user_id, hash_token(token_string), expire)
    return token_string

def verify_refresh_token(db,refresh_token: str):
    row = crud.get_refresh_token(db, hash_token(refresh_token))
    if row is None or row.revoked == True or row.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="トークンが不正です")
    return row
        
        
    
    

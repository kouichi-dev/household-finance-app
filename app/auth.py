
from jose import JWTError, jwt
from fastapi import HTTPException



from datetime import datetime, timedelta, timezone




SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minute=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY , algorithm=ALGORITHM)
        

def verify_token(token: str):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="無効なトークンです")

        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="トークンが不正です")


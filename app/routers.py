

from fastapi import APIRouter,Depends,HTTPException
from database import SessionLocal
from sqlalchemy.orm import Session
import crud
import schemas
import auth
import services
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from fastapi import Depends



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    email = auth.verify_token(token)
    user = crud.get_user_by_email(db,email)
    if not user:
        raise HTTPException(status_code=401, detail="ユーザーが存在しません")
    return user


@router.post("/users", response_model=schemas.UserResponse)
async def create_user_endpoint(user:schemas.UserCreate, db: Session = Depends(get_db)):
    return services.create_user(db,user)


@router.get("/users/{user_id}", response_model=schemas.UserResponse)
async def get_user_endpoint(user_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="権限がありません")
    return crud.get_users(db,user_id)


@router.patch("/users/{user_id}", response_model=schemas.UserResponse)
async def update_user_endpoint(user_id: int, user: schemas.UserCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="権限がありません")
    return services.update_user(db,user,user_id)

@router.delete("/users/{user_id}")
async def delete_user_endpoint(user_id: int, db: Session = Depends(get_db),  current_user = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="権限がありません")crud.delete_user(db,user_id)
    return {"message":"deleted"}



@router.post("/auth/login")
async def login_user_endpoint(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db,form_data.username)

    if not db_user:
        raise HTTPException(status_code=401, detail="ユーザーが存在しません")
    
    if not auth.verify_password(form_data.password,db_user.password):
        raise HTTPException(status_code=401, detail="パスワードが一致しません")

    token = auth.create_access_token({"sub":db_user.email})
    return {"access_token": token, "token_type": "bearer"}


from fastapi import APIRouter,Depends
from database import SessionLocal
from sqlalchemy.orm import Session
import crud
import schemas

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/users")
async def create_user_endpoint(user:schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db,user)


@router.get("/users/{user_id}")
async def get_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    return crud.get_users(db,user_id)


@router.patch("/users/{user_id}")
async def update_user_endpoint(user_id: int, user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.update_user(db,user,user_id)

@router.delete("/users/{user_id}")
async def delete_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    crud.delete_user(db,user_id)
    return {"message":"deleted"}




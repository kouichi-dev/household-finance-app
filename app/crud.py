

from sqlalchemy.orm import Session
from models import User
from schemas import UserCreate

def get_current_user(db: Session, token: str):
    pass
def create_user(db: Session, user: UserCreate):
    db_user = User(name=user.name,email=user.email,password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, user_id: int):
    return db.query(User).filter(User.id==user_id).first()

def update_user(db: Session, user:UserCreate, user_id: int):
    db_user = db.query(User).filter(User.id==user_id).first()
    db_user.name=user.name
    db_user.email=user.email
    db_user.password=user.password
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id==user_id).first()
    db.delete(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user







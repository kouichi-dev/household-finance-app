

from sqlalchemy.orm import Session
from sqlalchemy import func
from models import User,Transaction
from schemas import UserCreate,TransactionCreate,TransacionSummary



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

    return db_user



def get_user_by_email(db: Session,email: str):
    return db.query(User).filter(User.email==email).first()


def create_transaction(db: Session, user_id: int, transaction: TransactionCreate):
    db_transaction = Transaction(
        user_id=user_id,
        amount=transaction.amount,
        type=transaction.type,
        description=transaction.description,
        category_id=transaction.category_id)
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_transactions_summary(db: Session, user_id: int, year: int | None, month: int | None, week: int | None):
    query = db.query(Transaction).filter(
        Transaction.user_id==user_id,
        func.extract('year',Transaction.created_at) == year
    )

    if month is not None:
        query = query.filter(
            func.extract('month',Transaction.created_at) == month
        )
    
    if week is not None:
        query = query.filter(
            func.extract('week',Transaction.created_at) == week
        )
    
    return query.all()

def get_transactions(db: Session, user_id: int, page: int, limit: int):
    offset = (page - 1) * limit
    return db.query(Transaction).filter(Transaction.user_id == user_id).offset(offset).limit(limit).all()


def update_transaction(db: Session, user_id: int, transaction_id: int, transaction: TransactionCreate):
    db_transaction = db.query(Transaction).filter(Transaction.user_id==user_id,Transaction.id==transaction_id).first()
    db_transaction.amount=transaction.amount
    db_transaction.type=transaction.type
    db_transaction.description=transaction.description
    db_transaction.category_id=transaction.category_id
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def delete_transaction(db: Session, user_id: int, transaction_id: int):
    db_transaction = db.query(Transaction).filter(Transaction.user_id==user_id,Transaction.id==transaction_id).first()
    db.delete(db_transaction)
    db.commit()
    return db_transaction


from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from models import User,Transaction,Category
from schemas import UserCreate,TransactionCreate,CategoryCreate
from exceptions import EmailAlreadyExistsError
from datetime import date

# user_crud

def create_user(db: Session, user: UserCreate):
    db_user = User(name=user.name,email=user.email,password=user.password)
    db.add(db_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise EmailAlreadyExistsError()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, user_id: int):
    return db.query(User).filter(User.id==user_id).first()

def update_user(db: Session, user:UserCreate, user_id: int):
    db_user = db.query(User).filter(User.id==user_id).first()
    if not db_user:
        return None
    db_user.name=user.name
    db_user.email=user.email
    db_user.password=user.password
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise EmailAlreadyExistsError()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id==user_id).first()
    if not db_user:
        return None
    db.delete(db_user)
    db.commit()

    return db_user



def get_user_by_email(db: Session,email: str):
    return db.query(User).filter(User.email==email).first()

# transaction_crud


def create_transaction(db: Session, user_id: int, transaction: TransactionCreate):
    db_transaction = Transaction(
        user_id=user_id,
        amount=transaction.amount,
        type=transaction.type,
        description=transaction.description,
        category_id=transaction.category_id,
        transaction_date=transaction.transaction_date)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_transactions_summary(db: Session, user_id: int, year: int | None, month: int | None, week: int | None):
    query = db.query(Transaction).filter(
        Transaction.user_id==user_id,
        func.extract('year',Transaction.transaction_date) == year
    )


    if month is not None:
        query = query.filter(
            func.extract('month',Transaction.transaction_date) == month
        )
    
    if week is not None:
        query = query.filter(
            func.extract('week',Transaction.transaction_date) == week
        )
    
    return query.all()

def get_transactions(db: Session, user_id: int, page: int, limit: int):
    offset = (page - 1) * limit
    return (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .order_by(Transaction.id)
        .offset(offset).limit(limit).all()
    )


def update_transaction(db: Session, user_id: int, transaction_id: int, transaction: TransactionCreate):
    db_transaction = db.query(Transaction).filter(Transaction.user_id==user_id,Transaction.id==transaction_id).first()
    if not db_transaction:
        return None
    db_transaction.amount=transaction.amount
    db_transaction.type=transaction.type
    db_transaction.description=transaction.description
    db_transaction.category_id=transaction.category_id
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def delete_transaction(db: Session, user_id: int, transaction_id: int):
    db_transaction = db.query(Transaction).filter(Transaction.user_id==user_id,Transaction.id==transaction_id).first()
    if not db_transaction:
        return None
    db.delete(db_transaction)
    db.commit()
    return db_transaction

# category_crud

def create_category(db: Session, user_id: int, category: CategoryCreate):
    db_category = Category(user_id=user_id,name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_categories(db: Session, user_id: int):
    return db.query(Category).filter(Category.user_id==user_id).all()

def update_category(db: Session, user_id: int, category_id: int, category: CategoryCreate):
    db_category = db.query(Category).filter(Category.user_id==user_id,Category.id==category_id).first()
    if not db_category:
        return None
    db_category.name=category.name
    db.commit()
    db.refresh(db_category)
    return db_category

def delete_category(db: Session, user_id: int, category_id: int):
    db_category = db.query(Category).filter(Category.user_id==user_id,Category.id==category_id).first()
    if not db_category:
        return None
    db.delete(db_category)
    db.commit()
    return db_category



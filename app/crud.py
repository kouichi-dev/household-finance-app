

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import User,Transaction,Category
from schemas import UserCreate,TransactionCreate,CategoryCreate
from exceptions import EmailAlreadyExistsError, CategoryAlreadyExistsError
from sqlalchemy import func, case, select


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
    return db.get(User, user_id)

def update_user(db: Session, data: dict, user_id: int):
    db_user = db.get(User, user_id)
    if not db_user:
        return None
    for key, value in data.items():
        setattr(db_user, key, value)                     # 送られた項目だけ上書き
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise EmailAlreadyExistsError()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = db.get(User, user_id)
    if not db_user:
        return None
    db.delete(db_user)
    db.commit()

    return db_user



def get_user_by_email(db: Session,email: str):
    stmt = select(User).where(User.email == email)
    return db.execute(stmt).scalar_one_or_none()

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

def get_transactions_summary(db: Session, user_id: int, start_date, end_date):
    stmt = (
        select(
            func.coalesce(func.sum(case((Transaction.type == 'income', Transaction.amount), else_=0)), 0).label("income"),
            func.coalesce(func.sum(case((Transaction.type == 'expense', Transaction.amount), else_=0)), 0).label("expense"),
        )
        .where(
            Transaction.user_id == user_id,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date,
        )
    )
    return db.execute(stmt).first()


def get_transactions(db: Session, user_id: int, page: int, limit: int):
    offset = (page - 1) * limit
    stmt = (
        select(Transaction)
        .where(Transaction.user_id == user_id)
        .order_by(Transaction.id)
        .offset(offset)
        .limit(limit)
    )
    return db.execute(stmt).scalars().all()


def update_transaction(db: Session, user_id: int, transaction_id: int, data: dict):
    stmt = select(Transaction).where(Transaction.user_id == user_id, Transaction.id == transaction_id)
    db_transaction = db.execute(stmt).scalar_one_or_none()
    if not db_transaction:
        return None
    for key, value in data.items():
        setattr(db_transaction, key, value)  # transaction_date も含め送られた項目を全反映
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


def delete_transaction(db: Session, user_id: int, transaction_id: int):
    stmt = select(Transaction).where(Transaction.user_id == user_id, Transaction.id == transaction_id)
    db_transaction = db.execute(stmt).scalar_one_or_none()
    if not db_transaction:
        return None
    db.delete(db_transaction)
    db.commit()
    return db_transaction

# category_crud

def create_category(db: Session, user_id: int, category: CategoryCreate):
    db_category = Category(user_id=user_id,name=category.name)
    db.add(db_category)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise CategoryAlreadyExistsError()
    db.refresh(db_category)
    return db_category

def get_category(db: Session, user_id: int, category_id: int):
    stmt = select(Category).where(Category.user_id==user_id, Category.id==category_id)
    return db.execute(stmt).scalar_one_or_none()

def get_categories(db: Session, user_id: int):
    stmt = select(Category).where(Category.user_id==user_id)
    return db.execute(stmt).scalars().all()

def update_category(db: Session, user_id: int, category_id: int, data: dict):
    stmt = select(Category).where(Category.user_id==user_id, Category.id==category_id)
    db_category = db.execute(stmt).scalar_one_or_none()
    if not db_category:
        return None
    for key, value in data.items():
        setattr(db_category, key, value)
    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, user_id: int, category_id: int):
    stmt = select(Category).where(Category.user_id==user_id,Category.id==category_id)
    db_category = db.execute(stmt).scalar_one_or_none()
    if not db_category:
        return None
    db.delete(db_category)
    db.commit()
    return db_category



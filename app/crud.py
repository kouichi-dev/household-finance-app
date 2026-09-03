

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import User,Transaction,Category,RefreshTokens
from schemas import UserCreate,TransactionCreate,CategoryCreate
from exceptions import EmailAlreadyExistsError,CategoryAlreadyExistsError,TokenAlreadyExistsError
from sqlalchemy import func,case,select
from datetime import datetime,date

# refresh_token

def data_save_refresh_token(db: Session, user_id: int, token: str, expires_at: datetime):
    db_refresh_tokens = RefreshTokens(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    db.add(db_refresh_tokens)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise TokenAlreadyExistsError()
    db.refresh(db_refresh_tokens)
    return db_refresh_tokens

def get_refresh_token(db: Session, token):
    refresh_token = select(RefreshTokens).where(RefreshTokens.token==token)
    return db.execute(refresh_token).scalar_one_or_none()

def revoke_refresh_token(db: Session, token):
    stmt = select(RefreshTokens).where(RefreshTokens.token==token)
    db_refresh_token = db.execute(stmt).scalar_one_or_none()
    if not db_refresh_token:
        return None
    db_refresh_token.revoked=True
    db.flush()
    db.refresh(db_refresh_token)
    return db_refresh_token

# user_crud

def create_user(db: Session, user: UserCreate):
    db_user = User(name=user.name,email=user.email,password=user.password)
    db.add(db_user)
    try:
        db.flush()
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
        db.flush()
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
    db.flush()

    return db_user



def get_user_by_email(db: Session,email: str):
    stmt = select(User).where(User.email == email)
    return db.execute(stmt).scalar_one_or_none()

# transaction_crud


def create_transaction(db: Session, user_id: int, transaction: TransactionCreate):
    db_transaction = Transaction(
        user_id=user_id,
        amount=transaction.amount,
        kind=transaction.kind,
        description=transaction.description,
        category_id=transaction.category_id,
        transaction_date=transaction.transaction_date)
    db.add(db_transaction)
    db.flush()
    db.refresh(db_transaction)
    return db_transaction

def build_filters(user_id: int, start: date | None, end: date | None, category_id, kind):
    filters = [Transaction.user_id == user_id]
    if category_id == "none":
        filters.append(Transaction.category_id.is_(None))
    elif category_id is not None:
        filters.append(Transaction.category_id == category_id)

    if kind is not None:
        filters.append(Transaction.kind == kind)

    if start is not None:
        filters.append(Transaction.transaction_date >= start)
        filters.append(Transaction.transaction_date <= end)
    return filters

def get_transactions(db: Session, user_id: int, page: int, limit: int, start: date, end: date, category_id, kind):
    offset = (page - 1) * limit
    filters = build_filters(user_id, start, end, category_id, kind)
    stmt = (
        select(Transaction, Category.name)
        .outerjoin(Category, Transaction.category_id == Category.id)
        .where(*filters)
        .order_by(Transaction.transaction_date.desc(), Transaction.id.desc())
        .offset(offset)
        .limit(limit)
    )
    rows = db.execute(stmt).all()
    transactions = []
    for transaction, category_name in rows:
        transaction.category_name = category_name
        transactions.append(transaction)
    return transactions

def count_transactions(db: Session, user_id: int, start: date, end: date, category_id, kind):
    filters = build_filters(user_id, start, end, category_id, kind)
    stmt = select(func.count()).select_from(Transaction).where(*filters)
    return db.execute(stmt).scalar_one()

def get_transactions_summary(db: Session, user_id: int, start: date, end: date, category_id, kind):
    filters = build_filters(user_id, start, end, category_id, kind)
    stmt = (
        select(
            func.coalesce(func.sum(case((Transaction.kind == 'income', Transaction.amount), else_=0)), 0).label("income"),
            func.coalesce(func.sum(case((Transaction.kind == 'expense', Transaction.amount), else_=0)), 0).label("expense"),
        )
        .where(*filters)
    )
    return db.execute(stmt).first()

def update_transaction(db: Session, user_id: int, transaction_id: int, data: dict):
    stmt = select(Transaction).where(Transaction.user_id == user_id, Transaction.id == transaction_id)
    db_transaction = db.execute(stmt).scalar_one_or_none()
    if not db_transaction:
        return None
    for key, value in data.items():
        setattr(db_transaction, key, value)  # transaction_date も含め送られた項目を全反映
    db.flush()
    db.refresh(db_transaction)
    return db_transaction


def delete_transaction(db: Session, user_id: int, transaction_id: int):
    stmt = select(Transaction).where(Transaction.user_id == user_id, Transaction.id == transaction_id)
    db_transaction = db.execute(stmt).scalar_one_or_none()
    if not db_transaction:
        return None
    db.delete(db_transaction)
    db.flush()
    return db_transaction

# category_crud

def create_category(db: Session, user_id: int, category: CategoryCreate):
    db_category = Category(user_id=user_id,name=category.name)
    db.add(db_category)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise CategoryAlreadyExistsError()
    db.refresh(db_category)
    return db_category

def get_category(db: Session, user_id: int, category_id: int):
    stmt = select(Category).where(Category.user_id==user_id, Category.id==category_id)
    return db.execute(stmt).scalar_one_or_none()

def get_categories(db: Session, user_id: int):
    stmt = select(Category).where(Category.user_id==user_id).order_by(Category.name)
    return db.execute(stmt).scalars().all()

def update_category(db: Session, user_id: int, category_id: int, data: dict):
    stmt = select(Category).where(Category.user_id==user_id, Category.id==category_id)
    db_category = db.execute(stmt).scalar_one_or_none()
    if not db_category:
        return None
    for key, value in data.items():
        setattr(db_category, key, value)
    db.flush()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, user_id: int, category_id: int):
    stmt = select(Category).where(Category.user_id==user_id,Category.id==category_id)
    db_category = db.execute(stmt).scalar_one_or_none()
    if not db_category:
        return None
    db.delete(db_category)
    db.flush()
    return db_category



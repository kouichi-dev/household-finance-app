

import crud
import auth
from fastapi import HTTPException
from exceptions import EmailAlreadyExistsError

_EMAIL_DUP = "このメールアドレスは既に使われています"


# ---- users ----
def create_user(db,user):
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=409, detail= _EMAIL_DUP)
    user.password = auth.hash_password(user.password)
    try:
        return crud.create_user(db, user)
    except EmailAlreadyExistsError:
        raise HTTPException(status_code=409, detail= _EMAIL_DUP)    

def update_user(db,user,user_id):
    existing = crud.get_user_by_email(db, user.email)
    if existing and existing.id != user_id:
        raise HTTPException(status_code=409, detail = _EMAIL_DUP)
    user.password = auth.hash_password(user.password)
    try:
        updated = crud.update_user(db, user, user_id)
    except EmailAlreadyExistsError:
        raise HTTPException(status_code=409, detail=_EMAIL_DUP)
    if updated is None:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    return updated


def get_transactions_summary(db,user_id,type,year,month,week):

    if year is None:
        raise HTTPException(status_code=422, detail="年の入力がありません")
    if type == 'monthly' and not month:
        raise HTTPException(status_code=422, detail="月の入力がありません")
    if type == 'weekly' and not week:
        raise HTTPException(status_code=422, detail="週の入力がありません")
    
    transactions = crud.get_transactions_summary(db,user_id,year,month,week)
    
    income_total = 0
    expense_total = 0

    for t in transactions:
        if t.type == 'income':
            income_total += t.amount
        elif t.type == 'expense':
            expense_total += t.amount
    
    balance = income_total - expense_total

    return {"income": income_total, "expense": expense_total, "balance": balance}

def get_user(db, user_id):
    return crud.get_users(db, user_id)

def delete_user(db, user_id):
    if crud.delete_user(db, user_id) is None:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")

# ---- transactions ----
def create_transaction(db, user_id, transaction):
    return crud.create_transaction(db, user_id, transaction)

def get_transactions(db, user_id, page, limit):
    return crud.get_transactions(db, user_id, page, limit)

def update_transaction(db, user_id, transaction_id, transaction):
    updated = crud.update_transaction(db, user_id, transaction_id, transaction)
    if updated is None:
        raise HTTPException(status_code=404, detail="取引が見つかりません")
    return updated

def delete_transaction(db, user_id, transaction_id):
    if crud.delete_transaction(db, user_id, transaction_id) is None:
        raise HTTPException(status_code=404, detail="取引が見つかりません")

# ---- categories ----
def create_category(db, user_id, category):
    return crud.create_category(db, user_id, category)

def get_categories(db, user_id):
    return crud.get_categories(db, user_id)

def update_category(db, user_id, category_id, category):
    updated = crud.update_category(db, user_id, category_id, category)
    if updated is None:
        raise HTTPException(status_code=404, detail="カテゴリが見つかりません")
    return updated

def delete_category(db, user_id, category_id):
    if crud.delete_category(db, user_id, category_id) is None:
        raise HTTPException(status_code=404, detail="カテゴリが見つかりません")
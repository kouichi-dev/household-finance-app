

import crud
import auth
from fastapi import HTTPException
from exceptions import EmailAlreadyExistsError, CategoryAlreadyExistsError
from datetime import date, datetime
from zoneinfo import ZoneInfo
import calendar


_EMAIL_DUP = "このメールアドレスは既に使われています"

def refresh_access_token(db,refresh_token):
    refresh_token = auth.verify_refresh_token(db,refresh_token)
    access_token = auth.create_access_token({"sub": str(refresh_token.user_id)})
    return {"access_token": access_token}

def revoke_refresh_token(db,refresh_token):
    db_refresh_token = crud.revoke_refresh_token(db,refresh_token)
    if db_refresh_token is None:
        raise HTTPException(status_code=404, detail="リフレッシュトークンが存在しません")
    return db_refresh_token

    
# ---- users ----
def create_user(db,user):
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=409, detail= _EMAIL_DUP)
    user.password = auth.hash_password(user.password)
    try:
        return crud.create_user(db, user)
    except EmailAlreadyExistsError:
        raise HTTPException(status_code=409, detail= _EMAIL_DUP)

def update_user(db, user, user_id):
    data = user.model_dump(exclude_unset=True)          # 送られたキーだけ
    if "email" in data:                                  # email 送られた時だけ重複チェック
        existing = crud.get_user_by_email(db, data["email"])
        if existing and existing.id != user_id:
            raise HTTPException(status_code=409, detail=_EMAIL_DUP)
    if "password" in data:                               # password 送られた時だけハッシュ
        data["password"] = auth.hash_password(data["password"])
    updated = crud.update_user(db, data, user_id)
    if updated is None:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    return updated



def login_user(db, username, password):
    db_user = crud.get_user_by_email(db, username)
    if not db_user or not auth.verify_password(password, db_user.password):
        raise HTTPException(status_code=401, detail="メールアドレスまたはパスワードが正しくありません")
    access_token = auth.create_access_token({"sub": str(db_user.id)})
    refresh_token = auth.create_refresh_token(db,db_user.id)
    return access_token,refresh_token

def resolve_period(type, year, month):
    if month is None:
        raise HTTPException(status_code=422, detail="月の入力がありません")
    start = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]   # その月の日数
    end = date(year, month, last_day)
    return start,end

def get_user(db, user_id):
    db_user = crud.get_users(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    return db_user


def delete_user(db, user_id):
    if crud.delete_user(db, user_id) is None:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")

# ---- transactions ----

#自分のカテゴリが存在するかをチェック、カテゴリ未指定の場合はそのまま通す
def _ensure_category_owned(db, user_id, category_id):
    if category_id is not None and crud.get_category(db, user_id, category_id) is None:
        raise HTTPException(status_code=404, detail="カテゴリが見つかりません")

def create_transaction(db, user_id, transaction):
    if transaction.transaction_date is None:
        transaction.transaction_date = datetime.now(ZoneInfo("Asia/Tokyo")).date()
    _ensure_category_owned(db, user_id, transaction.category_id)
    return crud.create_transaction(db, user_id, transaction)

def get_transactions(db, user_id, page, limit, type, year, month):
    if year is None:
        start, end = None, None
    else:
        start, end = resolve_period(type, year, month)
    return crud.get_transactions(db, user_id, page, limit, start, end)

def get_transactions_summary(db, user_id, type, year, month):
    start, end = resolve_period(type, year, month)
    row = crud.get_transactions_summary(db, user_id, start, end)
    balance = row.income - row.expense
    return {"income": row.income, "expense": row.expense, "balance": balance}

def update_transaction(db, user_id, transaction_id, transaction):
    data = transaction.model_dump(exclude_unset=True)
    if "category_id" in data:                          # category_id を送った時だけ検証
        _ensure_category_owned(db, user_id, data["category_id"])
    updated = crud.update_transaction(db, user_id, transaction_id, data)
    if updated is None:
        raise HTTPException(status_code=404, detail="取引が見つかりません")
    return updated

def delete_transaction(db, user_id, transaction_id):
    if crud.delete_transaction(db, user_id, transaction_id) is None:
        raise HTTPException(status_code=404, detail="取引が見つかりません")

# ---- categories ----
def create_category(db, user_id, category):
    try:
        return crud.create_category(db, user_id, category)
    except CategoryAlreadyExistsError:
        raise HTTPException(status_code=409, detail="このカテゴリ名は既に存在します")


def get_categories(db, user_id):
    return crud.get_categories(db, user_id)

def update_category(db, user_id, category_id, category):
    data = category.model_dump(exclude_unset=True)
    updated = crud.update_category(db, user_id, category_id, data)
    if updated is None:
        raise HTTPException(status_code=404, detail="カテゴリが見つかりません")
    return updated


def delete_category(db, user_id, category_id):
    if crud.delete_category(db, user_id, category_id) is None:
        raise HTTPException(status_code=404, detail="カテゴリが見つかりません")
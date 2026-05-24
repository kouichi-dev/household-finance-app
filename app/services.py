

import crud
import auth
from fastapi import HTTPException
from sqlalchemy import func


def create_user(db,user):
    hashed = auth.hash_password(user.password)
    user.password = hashed
    return crud.create_user(db,user)

def update_user(db,user,user_id):
    hashed = auth.hash_password(user.password)
    user.password = hashed
    return crud.update_user(db,user,user_id)


def get_transactions_summary(db,user_id,type,year,month,week):

    if not year:
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

    return {"income": income_total, "expense": expense_total}



from fastapi import APIRouter,Depends,HTTPException, Query
from database import SessionLocal
from sqlalchemy.orm import Session
import crud
from schemas import UserCreate,UserResponse,TransactionCreate,TransactionResponse,CategoryCreate,CategoryResponse,PeriodUnit,UserUpdate,TransactionUpdate,CategoryUpdate,RefreshTokenBody,AccessTokenResponse,TransactionKind,TransactionListResponse, TransactionSummaryResponse
import auth
import services
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from fastapi import Depends
from datetime import date
from typing import Literal


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = auth.verify_token(token)
    user = crud.get_users(db, int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="ユーザーが存在しません")
    return user

def verify_self(user_id: int, current_user = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="権限がありません")
    return current_user

@router.post("/users", response_model=UserResponse)
def create_user_endpoint(user:UserCreate, db: Session = Depends(get_db)):
    return services.create_user(db,user)

@router.get("/users/me",response_model=UserResponse)
def get_current_user_endpoint(current_user = Depends(get_current_user)):
    return current_user

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_endpoint(user_id: int, db: Session = Depends(get_db), current_user = Depends(verify_self)):
    return services.get_user(db,user_id)

@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user_endpoint(user_id: int, user: UserUpdate, db: Session = Depends(get_db), current_user = Depends(verify_self)):
    return services.update_user(db,user,user_id)

@router.delete("/users/{user_id}", status_code=204)
def delete_user_endpoint(user_id: int, db: Session = Depends(get_db), current_user = Depends(verify_self)):
    services.delete_user(db,user_id)


@router.post("/auth/login")
def login_user_endpoint(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    access_token,refresh_token = services.login_user(db, form_data.username, form_data.password)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/auth/refresh",response_model=AccessTokenResponse)
def refresh_token_endpoint(token: RefreshTokenBody, db: Session = Depends(get_db)):
    return services.refresh_access_token(db,token.refresh_token)

@router.post("/auth/logout", status_code=204)
def logout_endpoint(token: RefreshTokenBody, db: Session = Depends(get_db)):
    services.revoke_refresh_token(db,token.refresh_token)

@router.post("/transactions",response_model=TransactionResponse)
def create_transaction_endpoint(transaction: TransactionCreate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    return services.create_transaction(db, current_user.id, transaction)

@router.get("/transactions",response_model=TransactionListResponse)
def get_transaction_endpoint(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    unit: PeriodUnit = Query(PeriodUnit.monthly),
    on: date | None = Query(None),
    category_id: int | Literal["none"] | None = Query(None),
    kind: TransactionKind | None = Query(None),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_transaction = services.get_transactions(db,current_user.id,page,limit,unit,on,category_id,kind)
    return db_transaction

@router.get("/transactions/summary", response_model=TransactionSummaryResponse)
def get_transactions_summary_endpoint(
    on: date,
    unit: PeriodUnit = Query(PeriodUnit.monthly),
    category_id: int | Literal["none"] | None = Query(None),
    kind: TransactionKind | None = Query(None),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return services.get_transactions_summary(db,current_user.id,unit,on,category_id,kind)

@router.patch("/transactions/{transaction_id}",response_model=TransactionResponse)
def update_transaction_endpoint(transaction: TransactionUpdate, transaction_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    return services.update_transaction(db,current_user.id,transaction_id,transaction)

@router.delete("/transactions/{transaction_id}", status_code=204)
def delete_transaction_endpoint(transaction_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    services.delete_transaction(db, current_user.id, transaction_id)


#categories_endpoint

@router.post("/categories",response_model=CategoryResponse)
def create_category_endpoint(category: CategoryCreate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    return services.create_category(db,current_user.id,category)

@router.get("/categories",response_model=list[CategoryResponse])
def get_category_endpoint(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    return services.get_categories(db,current_user.id)


@router.patch("/categories/{category_id}",response_model=CategoryResponse)
def update_category_endpoint(category_id: int, category: CategoryUpdate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    return services.update_category(db,current_user.id,category_id,category)


@router.delete("/categories/{category_id}", status_code=204)
def delete_category_endpoint(category_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    services.delete_category(db,current_user.id,category_id)




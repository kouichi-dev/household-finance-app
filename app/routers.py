

from fastapi import APIRouter,Depends,HTTPException
from database import SessionLocal
from sqlalchemy.orm import Session
import crud
from schemas import UserCreate,UserResponse,TransactionCreate,TransactionResponse,CategoryCreate,CategoryResponse,SummaryType
import auth
import services
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from fastapi import Depends



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    email = auth.verify_token(token)
    user = crud.get_user_by_email(db,email)
    if not user:
        raise HTTPException(status_code=401, detail="ユーザーが存在しません")
    return user


@router.post("/users", response_model=UserResponse)
async def create_user_endpoint(user:UserCreate, db: Session = Depends(get_db)):
    return services.create_user(db,user)

@router.get("/users/me",response_model=UserResponse)
async def get_current_user_endpoint(current_user = Depends(get_current_user)):
    return current_user

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_endpoint(user_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="権限がありません")
    return services.get_user(db,user_id)


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user_endpoint(user_id: int, user: UserCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="権限がありません")
    return services.update_user(db,user,user_id)

@router.delete("/users/{user_id}")
async def delete_user_endpoint(user_id: int, db: Session = Depends(get_db),  current_user = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="権限がありません")
    services.delete_user(db,user_id)
    return {"message":"deleted"}



@router.post("/auth/login")
async def login_user_endpoint(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    token = services.login_user(db, form_data.username, form_data.password)
    return {"access_token": token, "token_type": "bearer"}



@router.post("/transactions",response_model=TransactionResponse)
async def create_transaction_endpoint(transaction: TransactionCreate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    return services.create_transaction(db, current_user.id, transaction)


@router.get("/transactions",response_model=list[TransactionResponse])
async def get_transaction_endpoint(page: int = 1, limit: int = 20, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    db_transaction = services.get_transactions(db,current_user.id,page,limit)

    return db_transaction

@router.get("/transactions/summary")
async def get_transactions_summary_endpoint(
    type: SummaryType,
    year: int,
    month: int | None = None,
    week: int | None = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return services.get_transactions_summary(db,current_user.id,type,year,month,week)

@router.patch("/transactions/{transaction_id}",response_model=TransactionResponse)
async def update_transaction_endpoint(transaction: TransactionCreate, transaction_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    return services.update_transaction(db,current_user.id,transaction_id,transaction)

@router.delete("/transactions/{transaction_id}")
async def delete_transaction_endpoint(transaction_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    services.delete_transaction(db, current_user.id, transaction_id)
    return {"message":"deleted"}

#categories_endpoint

@router.post("/categories",response_model=CategoryResponse)
async def create_category_endpoint(category: CategoryCreate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    return services.create_category(db,current_user.id,category)

@router.get("/categories",response_model=list[CategoryResponse])
async def get_category_endpoint(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    return services.get_categories(db,current_user.id)


@router.patch("/categories/{category_id}",response_model=CategoryResponse)
async def update_category_endpoint(category_id: int, category: CategoryCreate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    return services.update_category(db,current_user.id,category_id,category)


@router.delete("/categories/{category_id}")
async def delete_category_endpoint(category_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    services.delete_category(db,current_user.id,category_id)
    return {"message":"deleted"}



from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime,date

class RefreshTokenBody(BaseModel):
    refresh_token: str

class AccessTokenResponse(BaseModel):
    access_token: str

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    password: str | None = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

class TransactionKind(str, Enum):
    income = 'income'
    expense = 'expense'

class TransactionCreate(BaseModel):
    amount: int = Field(ge=0)
    kind: TransactionKind
    transaction_date: date | None = None
    description: str | None = None
    category_id: int | None = None

class TransactionUpdate(BaseModel):
    amount: int | None = Field(default=None, ge=0)
    kind: TransactionKind | None = None
    transaction_date: date | None = None
    description: str | None = None
    category_id: int | None = None

class TransactionResponse(BaseModel):
    id: int
    amount: int
    kind: TransactionKind
    description: str | None = None
    category_name: str | None = None
    category_id: int | None = None
    created_at: datetime
    transaction_date: date

class PeriodUnit(str, Enum):
    yearly = 'yearly'
    monthly = 'monthly'

class PeriodResponse(BaseModel):
    unit: PeriodUnit
    start: date
    end: date

class CategoryCreate(BaseModel):
    name: str

class CategoryUpdate(BaseModel):
    name: str | None = None

class CategoryResponse(BaseModel):
    id: int
    name: str

class TransactionListResponse(BaseModel):
    period: PeriodResponse | None
    prev_on: date | None
    next_on: date | None
    items: list[TransactionResponse]
    total_count: int
    page: int
    limit: int
    

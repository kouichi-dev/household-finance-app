from pydantic import BaseModel, EmailStr, Field
from enum import Enum
from datetime import datetime,date

class RefreshTokenBody(BaseModel):
    refresh_token: str

class AccessTokenResponse(BaseModel):
    access_token: str

class UserCreate(BaseModel):
    name: str = Field(max_length=20)
    email: EmailStr = Field(max_length=30)
    password: str

class UserUpdate(BaseModel):
    name: str = Field(default=None, max_length=20)
    email: EmailStr = Field(default=None, max_length=30)
    password: str = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

class TransactionKind(str, Enum):
    income = 'income'
    expense = 'expense'

class TransactionCreate(BaseModel):
    amount: int = Field(ge=0, le=2147483647)   # PostgreSQL の INTEGER の上限
    kind: TransactionKind
    transaction_date: date | None = None
    description: str | None = Field(default=None, max_length=50)
    category_id: int | None = None

class TransactionUpdate(BaseModel):
    amount: int = Field(default=None, ge=0, le=2147483647)
    kind: TransactionKind = None
    transaction_date: date = None
    description: str | None = Field(default=None, max_length=50)
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
    name: str = Field(max_length=50)

class CategoryUpdate(BaseModel):
    name: str = Field(default=None, max_length=50)

class CategoryResponse(BaseModel):
    id: int
    name: str

class TransactionListResponse(BaseModel):
    period: PeriodResponse
    prev_on: date
    next_on: date
    items: list[TransactionResponse]
    total_count: int
    page: int
    limit: int

class DateSummaryResponse(BaseModel):
    date: date
    income: int
    expense: int

class CategorySummaryResponse(BaseModel):
    category_id: int | None = None
    category_name: str | None = None
    income: int
    expense: int

class TransactionSummaryResponse(BaseModel):
    period: PeriodResponse
    prev_on: date
    next_on: date
    income: int
    expense: int
    balance: int
    by_category: list[CategorySummaryResponse]
    by_date: list[DateSummaryResponse]

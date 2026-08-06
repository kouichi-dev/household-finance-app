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

class TransactionType(str, Enum):
    income = 'income'
    expense = 'expense'

class TransactionCreate(BaseModel):
    amount: int = Field(ge=0)
    type: TransactionType
    transaction_date: date
    description: str | None = None
    category_id: int | None = None

class TransactionUpdate(BaseModel):
    amount: int | None = Field(default=None, ge=0)
    type: TransactionType | None = None
    transaction_date: date | None = None
    description: str | None = None
    category_id: int | None = None

class TransactionResponse(BaseModel):
    id: int
    amount: int
    type: TransactionType
    description: str | None = None
    category_id: int | None = None
    created_at: datetime
    transaction_date: date

class SummaryType(str, Enum):
    monthly = 'monthly'
    weekly = 'weekly'

class CategoryCreate(BaseModel):
    name: str

class CategoryUpdate(BaseModel):
    name: str | None = None

class CategoryResponse(BaseModel):
    id: int
    name: str
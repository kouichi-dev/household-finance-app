from pydantic import BaseModel
from enum import Enum
from datetime import datetime,date

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

class TransactionType(str, Enum):
    income = 'income'
    expense = 'expense'

class TransactionCreate(BaseModel):
    amount: int
    type: TransactionType
    transaction_date: date
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

class CategoryResponse(BaseModel):
    id: int
    name: str








from pydantic import BaseModel
from enum import Enum

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
    description: str | None = None
    category_id: int | None = None


class SummaryType(str, Enum):
    monthly = 'monthly'
    weekly = 'weekly'

class TransactionSummary(BaseModel):
    type: SummaryType
    year: int
    month: int | None = None
    week: int | None = None

class CategoryCreate(BaseModel):
    name: str
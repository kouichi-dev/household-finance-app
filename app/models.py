from database import Base
from sqlalchemy import String,ForeignKey,DateTime,func,CheckConstraint,UniqueConstraint,Index
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date, datetime

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(String(30), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class Transaction(Base):
    __tablename__ = 'transactions'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    category_id: Mapped[int | None] = mapped_column(ForeignKey('categories.id', ondelete='SET NULL'))
    amount: Mapped[int]
    description: Mapped[str | None] = mapped_column(String(50))
    kind: Mapped[str] = mapped_column(String(10))
    transaction_date: Mapped[date]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (
    CheckConstraint("kind IN ('income','expense')", name='ck_transactions_kind'),
    CheckConstraint("amount >= 0", name='ck_transactions_amount_nonneg'),
    Index('ix_transactions_user_id_transaction_date', 'user_id', 'transaction_date'),
    )


class Category(Base):
    __tablename__ = 'categories'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    name: Mapped[str] = mapped_column(String(50))
    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uq_categories_user_id_name'),
    )

class RefreshTokens(Base):
    __tablename__ = 'refresh_tokens'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    token: Mapped[str] = mapped_column(String(255), unique=True)
    revoked: Mapped[bool] = mapped_column(default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


from database import Base
from sqlalchemy import Column,Integer,String,ForeignKey,DateTime,func,CheckConstraint,Date,UniqueConstraint,Boolean

class User(Base):
    __tablename__ = 'users'
    id = Column('id',Integer,primary_key=True)
    name = Column('name',String(20),nullable=False)
    email = Column('email',String(30),unique=True,nullable=False)
    password = Column('password',String(100),nullable=False)
    created_at = Column('created_at',DateTime(timezone=True),server_default=func.now(),nullable=False)

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column('id',Integer,primary_key=True)
    user_id = Column('user_id',Integer,ForeignKey('users.id', ondelete='CASCADE'),nullable=False, index=True)
    category_id = Column('category_id',Integer,ForeignKey('categories.id', ondelete='SET NULL'),nullable=True)
    amount = Column('amount',Integer,nullable=False)
    description = Column('description',String(50),nullable=True)
    kind = Column('kind',String(10),nullable=False)
    transaction_date = Column('transaction_date', Date, nullable=False)
    created_at = Column('created_at',DateTime(timezone=True),server_default=func.now(),nullable=False)
    __table_args__ = (
    CheckConstraint("kind IN ('income','expense')", name='ck_transactions_kind'),
    CheckConstraint("amount >= 0", name='ck_transactions_amount_nonneg'),
    )

class Category(Base):
    __tablename__ = 'categories'
    id = Column('id',Integer,primary_key=True)
    user_id = Column('user_id',Integer,ForeignKey('users.id', ondelete='CASCADE'),nullable=False)
    name = Column('name',String(50),nullable=False)
    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uq_categories_user_id_name'),
    )

class RefreshTokens(Base):
    __tablename__ = 'refresh_tokens'
    id = Column('id',Integer,primary_key=True)
    user_id = Column('user_id',Integer,ForeignKey('users.id', ondelete='CASCADE'),nullable=False)
    token = Column('token',String(255), unique=True,nullable=False)
    revoked = Column('revoked',Boolean,default=False,nullable=False)
    expires_at = Column('expires_at',DateTime(timezone=True),nullable=False)
    created_at = Column('created_at',DateTime(timezone=True),server_default=func.now(),nullable=False)

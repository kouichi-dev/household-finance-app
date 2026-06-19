
from database import Base
from sqlalchemy import Column,Integer,String,ForeignKey,DateTime,func,CheckConstraint,Date



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
    user_id = Column('user_id',Integer,ForeignKey('users.id'),nullable=False)
    category_id = Column('category_id',Integer,ForeignKey('categories.id'),nullable=True)
    amount = Column('amount',Integer,nullable=False)
    description = Column('description',String(50),nullable=True)
    type = Column('type',String(10),nullable=False)
    transaction_date = Column('transaction_date', Date, nullable=False)
    created_at = Column('created_at',DateTime(timezone=True),server_default=func.now(),nullable=False)
    __table_args__ = (
        CheckConstraint("type IN ('income','expense')", name='ck_transactions_type'),
    )
    

class Category(Base):
    __tablename__ = 'categories'
    id = Column('id',Integer,primary_key=True)
    user_id = Column('user_id',Integer,ForeignKey('users.id'),nullable=False)
    name = Column('name',String(50),nullable=False)
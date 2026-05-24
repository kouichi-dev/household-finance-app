
from database import Base
from sqlalchemy import Column,Integer,String,ForeignKey,DateTime



class User(Base):
    __tablename__ = 'users'
    id = Column('id',Integer,primary_key=True)
    name = Column('name',String(20))
    email = Column('email',String(30))
    password = Column('password',String(100))

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column('id',Integer,primary_key=True)
    user_id = Column('user_id',Integer,ForeignKey('users.id'))
    category_id = Column('category_id',Integer,ForeignKey('categories.id'), nullable=True)
    amount = Column('amount',Integer)
    description = Column('description',String(50),nullable=True)
    type = Column('type',String(10))
    created_at = Column('create_at',DateTime)
    

class Category(Base):
    __tablename__ = 'category'
    id = Column('id',Integer,primary_key=True)
    user_id = Column('user_id',Integer,ForeignKey('users.id'))
    name = Column('name',String(50),nullable=False)
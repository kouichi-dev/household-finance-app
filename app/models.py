
from database import Base
from sqlalchemy import Column,Integer,String,ForeignKey



class User(Base):
    __tablename__ = 'users'
    id = Column('id',Integer,primary_key=True)
    name = Column('name',String(20))
    email = Column('email',String(30))
    password = Column('password',String(50))

class transaction(Base):
    __tablename__ = 'transaction'
    tran_id = Column('id',Integer,primary_key=True)
    user_id = Column('user_id',String(100),ForeignKey('users.id'))
    income = Column('deposit',Integer)
    expense = Column('expense',Integer)
    balance = Column('balance',Integer)
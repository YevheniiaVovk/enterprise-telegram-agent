from datetime import datetime
from sqlalchemy import Column, BigInteger, String, DateTime
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    
    user_id = Column(BigInteger, primary_key=True)
    thread_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_interaction = Column(DateTime, nullable=True)
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


class User(Base):
    """Telegram user"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True)  # Telegram user_id
    thread_id = Column(String, unique=True, index=True)  # LangChain thread_id
    created_at = Column(DateTime, default=datetime.utcnow)


class Checkpoint(Base):
    """Agent checkpoint for memory storage"""
    __tablename__ = "checkpoints"
    
    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String, index=True)  # Link to conversation
    checkpoint_id = Column(String, unique=True, index=True)
    values = Column(JSON)  # Snapshot of state
    metadata = Column(JSON)  # Additional info
    created_at = Column(DateTime, default=datetime.utcnow)
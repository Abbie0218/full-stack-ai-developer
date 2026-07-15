from database import Base
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text  # ✅
from sqlalchemy.orm import mapped_column, relationship
from datetime import datetime

class User(Base):
    __tablename__ = "ai_chat_users"
    id         = mapped_column(Integer, primary_key=True)
    name       = mapped_column(String(200), nullable=False)
    email      = mapped_column(String(100), nullable=False, unique=True)
    password   = mapped_column(String(200), nullable=False)
    created_at = mapped_column(DateTime, default=datetime.now)

    sessions = relationship("Session", back_populates="user")  # ✅ plural

class Session(Base):
    __tablename__ = "ai_chat_sessions"
    id         = mapped_column(Integer, primary_key=True)
    user_id    = mapped_column(Integer, ForeignKey("ai_chat_users.id"))  # ✅
    title      = mapped_column(String(200), nullable=True)
    created_at = mapped_column(DateTime, default=datetime.now)

    user     = relationship("User", back_populates="sessions")      # ✅
    messages = relationship("Message", back_populates="session")    # ✅

class Message(Base):
    __tablename__ = "ai_chat_messages"
    id         = mapped_column(Integer, primary_key=True)
    session_id = mapped_column(Integer, ForeignKey("ai_chat_sessions.id"))  # ✅
    role       = mapped_column(String(20), nullable=False)          # ✅ added
    content    = mapped_column(Text, nullable=False)                # ✅ Text
    created_at = mapped_column(DateTime, default=datetime.now)

    session = relationship("Session", back_populates="messages")    # ✅
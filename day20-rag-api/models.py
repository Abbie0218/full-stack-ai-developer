from sqlalchemy import String, Integer,DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import mapped_column
from database import Base
from datetime import datetime
from enum import Enum as PyEnum

class Status(str, PyEnum):
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"

class User(Base):
    __tablename__ = "users"
    id=mapped_column(Integer, primary_key=True)
    name=mapped_column(String(200), nullable=False)
    email=mapped_column(String(200),nullable=False)
    password=mapped_column(String(200),nullable=False)
    created_at=mapped_column(DateTime,default=datetime.now)


class UploadJob(Base):
    __tablename__ = "upload_jobs"
    id=mapped_column(Integer, primary_key=True)
   
    user_id=mapped_column(Integer, ForeignKey("users.id"))
    file_name = mapped_column(String(200),nullable=False)
    status = mapped_column(Enum(Status), default=Status.PROCESSING, nullable=False, server_default="processing")
   
    error = mapped_column(Text, nullable=True)
    created_at=mapped_column(DateTime,default=datetime.now)

class Conversation(Base):
    __tablename__ = "conversations"
    id=mapped_column(Integer, primary_key=True) 
    user_id=mapped_column(Integer, ForeignKey("users.id"))
    title=mapped_column(String(200), nullable=True)
    created_at=mapped_column(DateTime,default=datetime.now)

class Message(Base):
    __tablename__ = "messages"
    id=mapped_column(Integer, primary_key=True) 
    conversation_id=mapped_column(Integer, ForeignKey("conversations.id"))
    role = mapped_column(String(20), nullable=False)
    content=mapped_column(Text, nullable=False)
    created_at=mapped_column(DateTime,default=datetime.now)

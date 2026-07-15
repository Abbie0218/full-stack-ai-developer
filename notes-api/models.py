from database import Base
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey, Enum as SAEnum
from datetime import datetime
from enum import Enum as PyEnum

class UserRole(str, PyEnum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"

class Users(Base):
    __tablename__ = 'notes_users'
    id         = mapped_column(Integer, primary_key=True)
    name       = mapped_column(String(200), nullable=False)
    email      = mapped_column(String(200), nullable=False, unique=True)
    password   = mapped_column(String(200), nullable=False)
    role       = mapped_column(
                    SAEnum(UserRole),
                    default=UserRole.USER,
                    nullable=False,
                    server_default="USER"   # ✅ uppercase
                 )
    created_at = mapped_column(DateTime, default=datetime.now)

    notes = relationship('Notes', back_populates="user")  # ✅ plural

class Notes(Base):
    __tablename__ = 'notes'
    id         = mapped_column(Integer, primary_key=True)
    user_id    = mapped_column(Integer, ForeignKey("notes_users.id"))
    title      = mapped_column(String(200), nullable=False)
    content    = mapped_column(String(200), nullable=False)
    tag        = mapped_column(String(200), nullable=False)
    created_at = mapped_column(DateTime, default=datetime.now)
    updated_at = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    user = relationship('Users', back_populates="notes")  # ✅
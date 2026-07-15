from sqlalchemy import String, Integer, DateTime, Float, ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from database import Base
from datetime import datetime

class Python_User(Base):
    __tablename__ = "python_users"
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(100), nullable=False)
    email = mapped_column(String(250),nullable=False, unique=True)
    age = mapped_column(Integer,nullable=False)
    phone = mapped_column(String(20),nullable=False)
    created_at = mapped_column(DateTime,default=datetime.now)

    orders = relationship("Python_Order", back_populates="user")


class Python_Order(Base):
    __tablename__ = "python_orders"
    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer,ForeignKey("python_users.id"))
    product_name = mapped_column(String(250), nullable=False)
    price = mapped_column(Float,nullable=False)
    status = mapped_column(String(50), default="pending")
    created_at = mapped_column(DateTime, default=datetime.now)

    user = relationship("Python_User", back_populates="orders")
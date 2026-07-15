# Define User + Post + Comment models with relationship
from database import Base
from sqlalchemy import Integer, String,DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from datetime import datetime
class User(Base):
    __tablename__="post_user"
    id= mapped_column(Integer, primary_key=True)
    name= mapped_column(String, nullable=False)
    email= mapped_column(String, nullable=False,unique=True)
    password= mapped_column(String, nullable=False)
    created_at= mapped_column(DateTime, default=datetime.now)

    posts = relationship('Post', back_populates='user')
    comments = relationship('Comments', back_populates='user')

class Post(Base):
    __tablename__="posts"
    id= mapped_column(Integer, primary_key=True)
    title= mapped_column(String, nullable=False)
    description= mapped_column(String, nullable=False)
    created_at= mapped_column(DateTime, default=datetime.now)

    user_id= mapped_column(Integer, ForeignKey("post_user.id"))

    user = relationship('User', back_populates='posts')
    comments = relationship('Comments', back_populates='post')


class Comments(Base):
    __tablename__="comments"
    id= mapped_column(Integer, primary_key=True)
    content= mapped_column(String, nullable=False)
    created_at= mapped_column(DateTime, default=datetime.now)
    
    user_id= mapped_column(Integer, ForeignKey("post_user.id"))
    post_id= mapped_column(Integer, ForeignKey("posts.id"))

    user = relationship('User', back_populates='comments')
    post = relationship('Post', back_populates='comments')

    

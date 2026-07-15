from sqlalchemy.orm import Session
from models import User
from sqlalchemy import select

class UserRepository:
    def __init__(self, db:Session):
        self.db = db
    
    def create_new_user(self, user:User):
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_by_email(self,email:str):
        return self.db.execute(
            select(User).where(User.email == email)
            ).scalar_one_or_none()
    
    def get_by_id(self, user_id:int):
        return self.db.execute(
            select(User).where(User.id == user_id)
            ).scalar_one_or_none()
        
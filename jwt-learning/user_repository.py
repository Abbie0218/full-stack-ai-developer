from sqlalchemy import select
from sqlalchemy.orm import Session
from models import Users
class UserRepository:
    def __init__(self,db:Session):
        self.db=db
    
    def create_user(self,user:Users):
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_by_email(self,email:str):
        return self.db.execute(
            select(Users).where(Users.email == email)
            ).scalar_one_or_none()
    
    def get_by_id(self, user_id:int):
        return self.db.execute(
            select(Users).where(Users.id == user_id)
            ).scalar_one_or_none()
        
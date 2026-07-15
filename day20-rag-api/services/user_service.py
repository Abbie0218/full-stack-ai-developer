from repository.user_repository import UserRepository
from models import User
from fastapi import HTTPException
from auth import hash_pwd, verify, create_access_token, refresh_token

class UserService:
    def __init__(self, repo:UserRepository):
        self.repo = repo
    
    def register(self,user_data:User):
        existing = self.repo.get_by_email(user_data.email)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Email ID already exists"
            )
        
        # hash password
        hashed_pwd = hash_pwd(user_data.password)
        print(user_data)
        new_user = User(
            name=user_data.name,
            email=user_data.email,
            password=hashed_pwd
        )

        return self.repo.create_new_user(new_user)

    
    def login(self, email: str, password: str):
        user = self.repo.get_by_email(email)

        if not user or not verify(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid Credentials")

        token_data = {"user_id": user.id, "email": user.email}
        return {
            "access_token": create_access_token(token_data),
            "refresh_token": refresh_token(token_data),
            "token_type": "bearer"
        }
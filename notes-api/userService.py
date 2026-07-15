from user_repository import UserRepository
from models import Users
from fastapi import HTTPException
from auth import hash_pwd, verify, create_access_token, refresh_token

class UserService:
    def __init__(self, repo:UserRepository):
        self.repo = repo
    
    def register(self,user_data:Users):
        existing = self.repo.get_by_email(user_data.email)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Email ID already exists"
            )
        
        # hash password
        hashed_pwd = hash_pwd(user_data.password)
        print(user_data)
        new_user = Users(
            name=user_data.name,
            email=user_data.email,
            password=hashed_pwd
        )

        return self.repo.create_user(new_user)

    
    def login(self, email:str, password:str):

        user = self.repo.get_by_email(email)
        
        print(f"user found: {user}")           # ← check if user exists
        print(f"stored password: {user.password if user else 'NO USER'}")  # ← check hash
        print(f"password match: {verify(password, user.password) if user else 'NO USER'}")  # ← check verify

        if not user or not verify(password, user.password):
            raise HTTPException(
                status_code=401,
                detail="Invalid Credentials"
            )
        
        # create token

        token_data = {"user_id": user.id, "email": user.email,"role": user.role.value}
        return {
            "access_token" : create_access_token(token_data),
            "refresh_token" : refresh_token(token_data),
            "token_type": "bearer"
        }
            
from fastapi import APIRouter, Depends
from schemas import UserLogin,RegisterUserRequest,RefreshTokenRequest
from userService import UserService
from sqlalchemy.orm import Session
from database import get_db
from user_repository import UserRepository
from auth import verify_token,create_access_token,refresh_token


routers = APIRouter()

def get_user_service(db: Session = Depends(get_db))->UserService:
    return UserService(UserRepository(db))


@routers.post("/register",status_code=201)
async def register_user(payload:RegisterUserRequest,service:UserService=Depends(get_user_service)):
    return service.register(payload)

@routers.post("/login",status_code=200)
async def login(payload:UserLogin,service:UserService=Depends(get_user_service)):
    return service.login(payload.email,payload.password)

@routers.post("/refresh",status_code=200)
async def get_another_token(data:RefreshTokenRequest,service:UserService=Depends(get_user_service)):
   payload = verify_token(data.refresh_token)
   token_data = {"user_id":payload["user_id"],"email":payload["email"]}

   return {
    "access_token": create_access_token(token_data),
    "refresh_token": refresh_token(token_data),
    "token_type":"bearer"
   }
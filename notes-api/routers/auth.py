from fastapi import APIRouter, Depends, Request
from schemas import UserLogin,RegisterUserRequest,RefreshTokenRequest
from userService import UserService
from sqlalchemy.orm import Session
from database import get_db
from user_repository import UserRepository
from auth import verify_token,create_access_token,refresh_token
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter  = Limiter(key_func=get_remote_address)


router = APIRouter(prefix="/auth")
def get_user_service(db: Session = Depends(get_db))->UserService:
    return UserService(UserRepository(db))


@router.post("/register",status_code=201,tags=["Auth"])
async def register_user(payload:RegisterUserRequest,service:UserService=Depends(get_user_service)):
    return service.register(payload) 

@router.post("/login",status_code=200,tags=["Auth"])
@limiter.limit("5/minute")
async def login(request:Request,form_data:OAuth2PasswordRequestForm = Depends(),service:UserService=Depends(get_user_service)):
     return service.login(form_data.username, form_data.password)

@router.post("/refresh",status_code=200,tags=["Auth"])
async def get_another_token(data:RefreshTokenRequest,service:UserService=Depends(get_user_service)):
   payload = verify_token(data.refresh_token)
   token_data = {"user_id":payload["user_id"],"email":payload["email"]}

   return {
    "access_token": create_access_token(token_data),
    "refresh_token": refresh_token(token_data),
    "token_type":"bearer"
   }
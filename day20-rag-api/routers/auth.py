from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from repository.user_repository import UserRepository
from services.user_service import UserService
from schemas import RegisterUserRequest, TokenResponse, RefreshTokenRequest
from auth import verify_token, create_access_token, refresh_token

router = APIRouter(prefix="/auth", tags=["Auth"])

def get_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db))

@router.post("/register", status_code=201)
def register(
    payload: RegisterUserRequest,
    service: UserService = Depends(get_service)
):
    return service.register(payload)

@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(get_service)
):
    return service.login(form_data.username, form_data.password)

@router.post("/refresh", response_model=TokenResponse)
def get_new_token(data: RefreshTokenRequest):
    payload = verify_token(data.refresh_token)
    token_data = {"user_id": payload["user_id"], "email": payload["email"]}
    return {
        "access_token": create_access_token(token_data),
        "refresh_token": refresh_token(token_data),
        "token_type": "bearer"
    }
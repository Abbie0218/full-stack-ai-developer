from dotenv import load_dotenv
import os
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, Depends
from models import UserRole
load_dotenv()

secret_key = os.getenv("SECRET_KEY")
algorithm = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def hash_pwd(pwd:str)->str:
    return pwd_context.hash(pwd)

def verify(plain_pwd:str, hashed_pwd:str)->bool:
    return pwd_context.verify(plain_pwd, hashed_pwd)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) 
    to_encode.update({"exp": expire.timestamp()}) 
    return jwt.encode(to_encode,secret_key,algorithm=algorithm)

def refresh_token(data:dict)->str:
    to_encode=data.copy()
    expire=datetime.now()+timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire.timestamp()}) 
    return jwt.encode(to_encode,secret_key,algorithm)

def verify_token(token:str) -> dict:
    try:
        payload = jwt.decode(token,secret_key,algorithm)
        return payload
    except JWTError:
        raise HTTPException(
            status_code=404,
            detail="Invalid token"
        )

def get_current_user(token:str=Depends(oauth2_scheme)):
    return verify_token(token)

def require_role(*roles:UserRole):
    def role_checker(current_user:dict=Depends(get_current_user)):
        if current_user["role"] not in [r.value for r in roles]:
            raise HTTPException(
                status_code=403,
                detail=f"requires role:{[r.value for r in roles]}"
            )
        return current_user
    return role_checker
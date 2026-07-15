from pydantic import BaseModel

class RegisterUserRequest(BaseModel):
    name:str
    email:str
    password:str

class UserLogin(BaseModel):
    email:str
    password:str
    
class UserDetails(BaseModel):
    email:str

class RegisterUserResponse(BaseModel):
    user_details: UserDetails
    access_token:str
    refresh_token:str
    token_type:str='bearer'
    token_expires:int = 15

class RefreshTokenRequest(BaseModel):
    refresh_token:str

from pydantic import BaseModel

class UserRequest(BaseModel):
    name: str
    email:str
    password:str
    
class UserResponse(BaseModel):
    id:int
    name: str
    email:str

class Patch_UserRequest(BaseModel):
    name: str | None = None
    email:str | None = None
    password: str | None = None


    class Config:
        from_attributes = True


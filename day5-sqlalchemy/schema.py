from pydantic import BaseModel
from datetime import datetime

# request body
class UserCreate(BaseModel):
    name:str
    email:str
    age:int
class OrderRequest(BaseModel):
    product_name: str
    price: float
    status: str
class OrderResponse(BaseModel):
    id: int
    product_name: str
    price: float
    status: str
    created_at: str

# response body
class UserResponse(BaseModel):
    id:int
    name:str
    email:str
    age:int
    created_at:datetime
    orders: list[OrderResponse] = []

class UserUpdateRequest(BaseModel):
    id:int
    name:str
    email:str
    age:int
    
class UserPatchRequest(BaseModel):
    name:str | None = None
    email:str | None = None
    age:int | None = None

    class Config:
        from_attributes = True
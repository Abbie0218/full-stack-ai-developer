from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()
class UserCreate(BaseModel):
    name:str
    email:str
    password:str

class UserOut(BaseModel):
    name:str
    email:str

fake_users_db = [
    {"id": 1, "name": "Abinaya", "email": "abinaya@gmail.com", "password": "abi123"},
    {"id": 2, "name": "Priya",   "email": "priya@gmail.com",   "password": "priya456"},
    {"id": 3, "name": "Ram",     "email": "ram@gmail.com",     "password": "ram789"},
    {"id": 4, "name": "Karthik", "email": "karthik@gmail.com", "password": "karthik321"},
    {"id": 5, "name": "Divya",   "email": "divya@gmail.com",   "password": "divya654"},
]

@router.get("/users",status_code=200,response_model=list[UserOut])
def user_list(skip:int=0, limit:int=2):
    return fake_users_db[skip:skip+limit]
@router.post("/users",response_model=UserOut,status_code=201)
def create_user(user:UserCreate)->dict:
    return{
         "name":user.name,
         "email":user.email,
         "password": user.password
    }


def get_product_or_404(product_id:int):
    for item in fake_db:
        if item['id'] == product_id:
            return item
    raise HTTPException(
        status_code=404,
        detail=f"Product {product_id} is not found"
    )

from fastapi import APIRouter,Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from database import get_db
from schemas import UserResponse, UserRequest,Patch_UserRequest
import models
 
router = APIRouter()

@router.post("/users",response_model=UserResponse,status_code=201)
async def create_user(user:UserRequest,db:Session=Depends(get_db)):
    new_user = models.User(
        name = user.name,
        email = user.email,
        password = user.password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/users",response_model=list[UserResponse],status_code=200)
async def get_user_list(db:Session=Depends(get_db)):
    user_list = db.execute(select(models.User)).scalars().all()
    return user_list

@router.get("/users/{user_id}",response_model=UserResponse,status_code=200)
async def get_user_details_by_id(user_id:int, db:Session=Depends(get_db)):
    user_detail = db.get(models.User,user_id)
    if not user_detail:
        raise HTTPException(status_code=404, detail="User not found")
    return user_detail

@router.put("/users/{user_id}",response_model=UserResponse, status_code=201)
async def update_user(user_id:int, user:UserRequest, db:Session=Depends(get_db)):
    user_detail = db.get(models.User, user_id)
    if not user_detail:
        raise HTTPException(status_code=404, detail="User not found")
    user_detail.name = user.name,
    user_detail.email = user.email,
    user_detail.password = user.password
    
    db.commit()
    db.refresh(user_detail)
    return user_detail

@router.patch("/users/{user_id}",response_model=UserResponse, status_code=201)
async def path_user(user_id:int, user:Patch_UserRequest, db:Session=Depends(get_db)):
    user_detail = db.get(models.User, user_id)
    if not user_detail:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = user.model_dump(exclude_unset=True)
    for key, value in updated_user.items():
        setattr(user_detail,key,value)
    db.commit()
    db.refresh(user_detail)
    return user_detail


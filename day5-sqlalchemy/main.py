from database import engine, Base, get_db
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from schema import UserCreate, UserResponse,UserUpdateRequest,UserPatchRequest
from routers import orders
import models

# test connection
try:
    with engine.connect() as connection:
        from sqlalchemy import text
        connection.execute(text("SELECT 1"))
        print("✅ Database connected successfully!")
except Exception as e:
    print(f"❌ Connection failed: {e}")

app = FastAPI()

# create tables
Base.metadata.create_all(bind=engine)
print("✅ tables created")

app.include_router(orders.router)
# routes
@app.post('/users',response_model=UserResponse,status_code=201)
async def create_user(user:UserCreate,db:Session=Depends(get_db)):
    new_user = models.Python_User(
        name=user.name,
        email=user.email,
        age=user.age
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users",response_model=list[UserResponse],status_code=200)
async def list_user(db:Session=Depends(get_db)):
    users = db.execute(select(models.Python_User)).scalars().all()
    return users;

@app.get("/users/{user_id}",status_code=200)
async def get_user_by_id( user_id:int,db:Session=Depends(get_db)):
    user = db.get(models.Python_User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.delete("/users/{user_id}",status_code=204)
async def delete_user(user_id:int, db:Session=Depends(get_db)):
    user = db.get(models.Python_User,user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user);
    db.commit()
    return None

@app.put("/users/{user_id}",status_code=201)
async def update_user(user_id:int,data:UserUpdateRequest, db:Session=Depends(get_db)):
    user = db.get(models.Python_User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    user.name=data.name
    user.email=data.email
    user.age=data.age

    db.commit()
    db.refresh(user)
    return user

@app.patch("/users/{user_id}",response_model=UserResponse, status_code=200)
async def patch_user(user_id:int, data:UserPatchRequest,db:Session=Depends(get_db)):
    user = db.get(models.Python_User,user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    updated_user = data.model_dump(exclude_unset=True)
    for key, value in updated_user.items():
        setattr(user,key,value)
    db.commit()
    db.refresh(user)
    return user


@app.get("/users-with-orders")
def get_users_with_orders(db: Session = Depends(get_db)):
    users = db.execute(
        select(models.Python_User)
        .options(selectinload(models.Python_User.orders))  # ✅ load all orders in one query
    ).scalars().all()
    return users


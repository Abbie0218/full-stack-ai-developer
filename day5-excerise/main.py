import models
from database import Base, engine
from sqlalchemy import text
from fastapi import FastAPI
from routers import post_users
app = FastAPI()

# include other routes
app.include_router(post_users.router)

Base.metadata.create_all(bind=engine)

try: 
    with engine.connect() as connection:
        connection.execute(text("select 1"))
        print("Database Connected successfully")
except Exception as e:
    print(f"connection failed: {e}")



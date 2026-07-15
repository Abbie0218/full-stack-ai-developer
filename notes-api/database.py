from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL,echo=True)

LocalSession = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db=LocalSession()
    try:
        yield db
    finally:
        db.close()

# verify connection

try:
    with engine.connect() as connection:
        connection.execute(text("select 1"))
        print("Database connected successfully")

except Exception as e:
    print(f"Connection failed: {e}")
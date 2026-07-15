from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import create_engine,text
import os
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
localSession = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db=localSession()
    try:
        yield db
    finally:
        db.close()

try:
    with engine.connect() as connection:
        connection.execute(text('select 1'))
        print(f"Database connected")
except Exception as e:
    print(f"Connection failed",e)

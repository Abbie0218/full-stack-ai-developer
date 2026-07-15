from dotenv import load_dotenv
import os
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL, echo=True)
localSession = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db=localSession()
    try:
        yield db
    finally:
        db.close()

# test connection
try:
    with engine.connect() as connection:
        connection.execute(text("select 1"))
        print("database connected")
except Exception as e:
    print('Connection failed',e)
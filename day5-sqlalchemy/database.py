from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "postgresql://postgres:Thilak@localhost:5432/day4_practice"

engine = create_engine(DATABASE_URL);

localSession=sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass


def get_db():
    db = localSession()
    try:
        yield db
    finally:
        db.close()


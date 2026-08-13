import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://postgres:rootpassword@postgres-db:5432/articles_db")

engine = create_engine(POSTGRES_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_postgres_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

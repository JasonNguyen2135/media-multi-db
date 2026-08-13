import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

MYSQL_URL = os.getenv("MYSQL_URL", "mysql+pymysql://root:rootpassword@mysql-db:3306/auth_db")

engine = create_engine(MYSQL_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_mysql_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

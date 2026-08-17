from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from backend.core.db_mysql import get_mysql_db
from backend.core.security import create_access_token, get_current_user
from backend.models import user_mysql, schemas

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_mysql_db)):
    db_user = db.query(user_mysql.User).filter(user_mysql.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = user_mysql.User(username=user.username, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Trả về JWT Token thay vì trả thẳng thông tin user
    token = create_access_token(new_user.id, new_user.username, new_user.role)
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_mysql_db)):
    db_user = db.query(user_mysql.User).filter(user_mysql.User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    # Trả về JWT Token thay vì trả thẳng thông tin user
    token = create_access_token(db_user.id, db_user.username, db_user.role)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    """API để Frontend lấy thông tin user từ Token (thay vì bốc từ localStorage)."""
    return current_user

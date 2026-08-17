import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Secret key dùng để ký JWT — trong Production nên đặt trong biến môi trường
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "cmc-cloud-polyglot-secret-key-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

security_scheme = HTTPBearer()


def create_access_token(user_id: int, username: str, role: str) -> str:
    """Tạo JWT Token chứa thông tin user (mã hóa, không thể sửa từ F12)."""
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": str(user_id),       # subject = user ID
        "username": username,
        "role": role,
        "exp": expire,             # thời gian hết hạn
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> dict:
    """Dependency dùng trong các API cần xác thực. Giải mã Token từ Header Authorization."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        username = payload.get("username")
        role = payload.get("role")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token: missing user ID")
        return {"id": int(user_id), "username": username, "role": role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

from pydantic import BaseModel
from typing import List, Optional

# --- Auth Schemas ---
class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True

# --- Article Schemas ---
class ArticleCreate(BaseModel):
    title: str
    content: str
    author_id: int
    tags: Optional[List[str]] = []

class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    tags: Optional[List[str]] = []
    views: int = 0

    class Config:
        from_attributes = True

# --- Draft Schemas (MongoDB) ---
class DraftCreate(BaseModel):
    author_id: int
    draft_data: dict # Unstructured JSON data


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
    author_name: Optional[str] = None
    is_anonymous: bool = False
    tags: Optional[List[str]] = []
    image_id: Optional[str] = None

class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    author_name: Optional[str] = None
    is_anonymous: bool = False
    tags: Optional[List[str]] = []
    image_id: Optional[str] = None
    views: int = 0

    class Config:
        from_attributes = True

# --- Draft Schemas (MongoDB) ---
class DraftCreate(BaseModel):
    author_id: int
    draft_data: dict # Unstructured JSON data


# --- Comment Schemas (MongoDB) ---
class CommentCreate(BaseModel):
    article_id: int
    author_id: int
    author_name: str
    content: str

class CommentResponse(BaseModel):
    id: str
    article_id: int
    author_id: int
    author_name: str
    content: str
    created_at: str

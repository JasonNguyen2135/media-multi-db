from fastapi import APIRouter, Depends, BackgroundTasks, Request, UploadFile, File, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List
from bson import ObjectId
from backend.core.db_postgres import get_postgres_db
from backend.core.db_mongo import get_mongo_db, logs_collection, images_collection
from backend.core.db_redis import get_redis
from backend.models import article_postgres, schemas
from datetime import datetime

router = APIRouter()

# --- Helper: map Article ORM → dict with author display logic ---
def article_to_dict(art, views: int = 0) -> dict:
    return {
        "id": art.id,
        "title": art.title,
        "content": art.content,
        "author_id": art.author_id,
        # If anonymous, mask author_name to "Anonymous"
        "author_name": "Anonymous" if art.is_anonymous else (art.author_name or f"User #{art.author_id}"),
        "is_anonymous": art.is_anonymous,
        "tags": art.tags or [],
        "image_id": art.image_id,
        "views": views
    }

# --- Helper: Background task for MongoDB Logging ---
async def log_article_view(article_id: int, request: Request):
    ip_address = request.client.host if request.client else "unknown"
    log_data = {
        "article_id": article_id,
        "ip_address": ip_address,
        "timestamp": datetime.utcnow()
    }
    await logs_collection.insert_one(log_data)

@router.post("/", response_model=schemas.ArticleResponse)
def create_article(article: schemas.ArticleCreate, db: Session = Depends(get_postgres_db)):
    new_article = article_postgres.Article(**article.model_dump())
    db.add(new_article)
    db.commit()
    db.refresh(new_article)
    return article_to_dict(new_article)

@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    contents = await file.read()
    image_data = {
        "filename": file.filename,
        "content_type": file.content_type,
        "data": contents
    }
    result = await images_collection.insert_one(image_data)
    return {"image_id": str(result.inserted_id)}

@router.get("/image/{image_id}")
async def get_image(image_id: str):
    try:
        image = await images_collection.find_one({"_id": ObjectId(image_id)})
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        return Response(content=image["data"], media_type=image["content_type"])
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image ID")

@router.get("/", response_model=List[schemas.ArticleResponse])
def get_articles(search: str = None, db: Session = Depends(get_postgres_db), redis_client = Depends(get_redis)):
    query = db.query(article_postgres.Article)
    
    if search:
        query = query.filter(or_(
            article_postgres.Article.title.ilike(f"%{search}%"),
            article_postgres.Article.content.ilike(f"%{search}%")
        ))
    
    articles = query.order_by(article_postgres.Article.id.desc()).all()
    
    result = []
    for art in articles:
        view_count = redis_client.get(f"article_view:{art.id}")
        views = int(view_count) if view_count else 0
        result.append(article_to_dict(art, views))
        
    return result

@router.get("/{article_id}", response_model=schemas.ArticleResponse)
def get_article_by_id(
    article_id: int, 
    request: Request, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_postgres_db),
    redis_client = Depends(get_redis)
):
    article = db.query(article_postgres.Article).filter(article_postgres.Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Increment view count in Redis
    redis_client.incr(f"article_view:{article.id}")
    
    # Async Log view to MongoDB
    background_tasks.add_task(log_article_view, article.id, request)
    
    view_count = redis_client.get(f"article_view:{article.id}")
    views = int(view_count) if view_count else 0
    
    return article_to_dict(article, views)

@router.delete("/{article_id}")
def delete_article(
    article_id: int,
    author_id: int,  # passed from frontend to verify ownership
    db: Session = Depends(get_postgres_db),
    redis_client = Depends(get_redis)
):
    article = db.query(article_postgres.Article).filter(article_postgres.Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    if article.author_id != author_id:
        raise HTTPException(status_code=403, detail="You are not the author of this article")
    
    # Delete from Postgres
    db.delete(article)
    db.commit()
    
    # Clean up view count from Redis
    redis_client.delete(f"article_view:{article_id}")
    
    return {"message": "Article deleted successfully"}

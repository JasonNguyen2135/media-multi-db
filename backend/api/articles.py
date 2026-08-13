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
    return new_article

@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    # Read file content
    contents = await file.read()
    
    # Save to MongoDB
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
    
    # Text search on Postgres
    if search:
        query = query.filter(or_(
            article_postgres.Article.title.ilike(f"%{search}%"),
            article_postgres.Article.content.ilike(f"%{search}%")
        ))
    
    articles = query.order_by(article_postgres.Article.id.desc()).all()
    
    # Fetch view counts from Redis
    result = []
    for art in articles:
        view_count = redis_client.get(f"article_view:{art.id}")
        views = int(view_count) if view_count else 0
        
        art_dict = {
            "id": art.id,
            "title": art.title,
            "content": art.content,
            "author_id": art.author_id,
            "tags": art.tags,
            "image_id": art.image_id,
            "views": views
        }
        result.append(art_dict)
        
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
    
    if article:
        # Increment view count in Redis
        redis_client.incr(f"article_view:{article.id}")
        
        # Async Log view to MongoDB
        background_tasks.add_task(log_article_view, article.id, request)
        
        view_count = redis_client.get(f"article_view:{article.id}")
        views = int(view_count) if view_count else 0
        
        return {
            "id": article.id,
            "title": article.title,
            "content": article.content,
            "author_id": article.author_id,
            "tags": article.tags,
            "image_id": article.image_id,
            "views": views
        }
    return None

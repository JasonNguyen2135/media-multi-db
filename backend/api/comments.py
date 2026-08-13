from fastapi import APIRouter, HTTPException
from typing import List
from bson import ObjectId
from backend.core.db_mongo import comments_collection
from backend.models.schemas import CommentCreate, CommentResponse
from datetime import datetime

router = APIRouter()

@router.post("/{article_id}", response_model=CommentResponse)
async def add_comment(article_id: int, comment: CommentCreate):
    if article_id != comment.article_id:
        raise HTTPException(status_code=400, detail="article_id mismatch")
    
    doc = {
        "article_id": comment.article_id,
        "author_id": comment.author_id,
        "author_name": comment.author_name,
        "content": comment.content,
        "created_at": datetime.utcnow().isoformat()
    }
    result = await comments_collection.insert_one(doc)
    
    return CommentResponse(
        id=str(result.inserted_id),
        article_id=doc["article_id"],
        author_id=doc["author_id"],
        author_name=doc["author_name"],
        content=doc["content"],
        created_at=doc["created_at"]
    )

@router.get("/{article_id}", response_model=List[CommentResponse])
async def get_comments(article_id: int):
    cursor = comments_collection.find({"article_id": article_id}).sort("created_at", -1)
    comments = []
    async for doc in cursor:
        comments.append(CommentResponse(
            id=str(doc["_id"]),
            article_id=doc["article_id"],
            author_id=doc["author_id"],
            author_name=doc["author_name"],
            content=doc["content"],
            created_at=doc["created_at"]
        ))
    return comments

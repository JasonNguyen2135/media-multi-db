from fastapi import APIRouter
from backend.core.db_mongo import drafts_collection
from backend.models import schemas
from datetime import datetime

router = APIRouter()

@router.post("/")
async def save_draft(draft: schemas.DraftCreate):
    draft_dict = draft.model_dump()
    draft_dict["updated_at"] = datetime.utcnow()
    
    # Upsert logic based on author_id
    await drafts_collection.update_one(
        {"author_id": draft.author_id},
        {"$set": draft_dict},
        upsert=True
    )
    return {"message": "Draft saved successfully", "status": "ok"}

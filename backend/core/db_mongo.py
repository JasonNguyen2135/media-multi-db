from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb://admin:rootpassword@mongo-db:27017"

client = AsyncIOMotorClient(MONGO_URL)
db = client["drafts_logs_db"]
drafts_collection = db["drafts"]
logs_collection = db["logs"]
images_collection = db["images"]
comments_collection = db["comments"]

def get_mongo_db():
    return db

from sqlalchemy.orm import Session
from core.db_postgres import SessionLocal, engine
from models.article_postgres import Article
from pymongo import MongoClient
import random
import urllib.request
import urllib.error

dummy_data = [
    {
        "title": "Introduction to Microservices Architecture",
        "content": "Microservices are a software development technique—a variant of the structural style of the service-oriented architecture (SOA) architectural style that arranges an application as a collection of loosely coupled services.",
        "author_id": 1,
        "tags": ["Architecture", "Backend", "Tech"]
    },
    {
        "title": "Why Python is great for Data Science",
        "content": "Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability with the use of significant indentation. Python is dynamically typed and garbage-collected.",
        "author_id": 1,
        "tags": ["Python", "Data Science", "AI"]
    },
    {
        "title": "Mastering Docker and Containers",
        "content": "Docker is a set of platform as a service products that use OS-level virtualization to deliver software in packages called containers. Containers are isolated from one another and bundle their own software, libraries and configuration files.",
        "author_id": 1,
        "tags": ["Docker", "DevOps", "Containers"]
    },
    {
        "title": "The Rise of NoSQL Databases",
        "content": "A NoSQL originally referring to non SQL or non relational is a database that provides a mechanism for storage and retrieval of data. This data is modeled in means other than the tabular relations used in relational databases.",
        "author_id": 1,
        "tags": ["Database", "NoSQL", "MongoDB"]
    },
    {
        "title": "Understanding PostgreSQL Full-Text Search",
        "content": "PostgreSQL provides powerful full-text search capabilities right out of the box. It uses tsvector to parse documents into tokens and tsquery to match queries against those tokens, making it extremely fast with GIN indexes.",
        "author_id": 1,
        "tags": ["PostgreSQL", "Search", "Database"]
    }
]

def get_mongo_collection():
    client = MongoClient("mongodb://root:rootpassword@mongo-db:27017/")
    db = client["drafts_logs_db"]
    return db["images"]

def download_random_image():
    try:
        # Fetch a random 800x400 image
        url = "https://picsum.photos/800/400"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            image_data = response.read()
            return image_data
    except Exception as e:
        print(f"Failed to download image: {e}")
        return None

def seed_data():
    print("Connecting to database...")
    db: Session = SessionLocal()
    images_coll = get_mongo_collection()
    
    try:
        # Check if articles already exist
        count = db.query(Article).count()
        if count > 0:
            print(f"Database already has {count} articles. Skipping seed.")
            return

        print("Generating dummy articles with random images...")
        for i, data in enumerate(dummy_data):
            print(f"Downloading image for article {i+1}...")
            img_bytes = download_random_image()
            
            image_id = None
            if img_bytes:
                # Insert into Mongo
                mongo_res = images_coll.insert_one({
                    "filename": f"seed_image_{i}.jpg",
                    "content_type": "image/jpeg",
                    "data": img_bytes
                })
                image_id = str(mongo_res.inserted_id)
            
            data["image_id"] = image_id
            article = Article(**data)
            db.add(article)
        
        db.commit()
        print("Successfully added 5 dummy articles!")
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()

from sqlalchemy import Column, Integer, String, Text, JSON, Boolean
from backend.core.db_postgres import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, nullable=False)          # Refers to MySQL user id
    author_name = Column(String(100), nullable=True)     # Store username at publish time
    is_anonymous = Column(Boolean, default=False)        # Hide author identity
    tags = Column(JSON, default=[])
    image_id = Column(String(255), nullable=True)        # MongoDB image ID
    views = Column(Integer, default=0)                   # Sync from Redis ZSET

from sqlalchemy import Column, Integer, String, Text, JSON
from backend.core.db_postgres import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, nullable=False) # Refers to MySQL user id loosely
    tags = Column(JSON, default=[]) # Storing tags as JSON array for simplicity

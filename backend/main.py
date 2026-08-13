from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.api import auth, articles, drafts, comments
from backend.core.db_mysql import engine as mysql_engine, Base as mysql_base
from backend.core.db_postgres import engine as pg_engine, Base as pg_base

# Create tables for MySQL and Postgres
mysql_base.metadata.create_all(bind=mysql_engine)
pg_base.metadata.create_all(bind=pg_engine)

app = FastAPI(title="Polyglot Blog API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth (MySQL)"])
app.include_router(articles.router, prefix="/api/articles", tags=["Articles (Postgres & Redis)"])
app.include_router(drafts.router, prefix="/api/drafts", tags=["Drafts (MongoDB)"])
app.include_router(comments.router, prefix="/api/comments", tags=["Comments (MongoDB)"])

@app.get("/")
def root():
    return {"message": "Welcome to Polyglot Blog API! Visit /docs for Swagger UI or /static/index.html for Frontend."}

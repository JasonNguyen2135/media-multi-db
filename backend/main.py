import threading
import time
import urllib.request
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.api import auth, articles, drafts, comments
from backend.core.db_mysql import engine as mysql_engine, Base as mysql_base
from backend.core.db_postgres import engine as pg_engine, Base as pg_base

# Create tables for MySQL and Postgres
mysql_base.metadata.create_all(bind=mysql_engine)
pg_base.metadata.create_all(bind=pg_engine)

# --- Auto Sync Worker ---
def auto_sync_worker():
    while True:
        time.sleep(60) # Chạy mỗi 60 giây
        try:
            req = urllib.request.Request("http://127.0.0.1:8000/api/articles/admin/sync-views", method="POST")
            urllib.request.urlopen(req)
            print("Auto-sync views from Redis to Postgres successful.")
        except Exception as e:
            print(f"Auto-sync error: {e}")

sync_thread = threading.Thread(target=auto_sync_worker, daemon=True)
sync_thread.start()

app = FastAPI(title="Polyglot Blog API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Request
@app.middleware("http")
async def add_cache_control_header(request: Request, call_next):
    response = await call_next(request)
    # Cấm Cloudflare hoặc bất kỳ CDN nào cache API
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth (MySQL)"])
app.include_router(articles.router, prefix="/api/articles", tags=["Articles (Postgres & Redis)"])
app.include_router(drafts.router, prefix="/api/drafts", tags=["Drafts (MongoDB)"])
app.include_router(comments.router, prefix="/api/comments", tags=["Comments (MongoDB)"])

@app.get("/")
def root():
    return {"message": "Welcome to Polyglot Blog API! Visit /docs for Swagger UI or /static/index.html for Frontend."}

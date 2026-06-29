# -*- coding: utf-8 -*-
"""
Main FastAPI application for Travel Recommender System
"""
import sys
# Fix Windows console encoding issues for Vietnamese characters
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Load .env từ thư mục gốc dự án (1 cấp trên backend/)
from pathlib import Path
from dotenv import load_dotenv
_root_env = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=_root_env, override=True)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import uvicorn
from api.routes import router

class UTF8JSONResponse(JSONResponse):
    """Custom JSON response that ensures UTF-8 encoding for Vietnamese characters."""
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")

app = FastAPI(
    title="Travel Recommender API",
    description="He thong goi y du lich quoc te",
    version="1.0.0",
    default_response_class=UTF8JSONResponse,
)

# CORS configuration - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")

# Mount static directory for uploads
from fastapi.staticfiles import StaticFiles
import os
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
(static_dir / "uploads").mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
async def root():
    return {
        "message": "Travel Recommender API",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("[START] Starting Travel Recommender Backend...")
    print("[INFO] API: http://localhost:8000")
    print("[INFO] Docs: http://localhost:8000/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
# Trigger reload to load clean destinations (no duplicate names) - 2


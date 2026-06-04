# -*- coding: utf-8 -*-
"""
Main FastAPI application for Travel Recommender System
"""
import sys
# Fix Windows console encoding issues for Vietnamese characters
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

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

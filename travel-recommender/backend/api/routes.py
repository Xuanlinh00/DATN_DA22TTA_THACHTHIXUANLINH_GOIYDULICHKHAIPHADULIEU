# -*- coding: utf-8 -*-
"""
API Routes for Travel Recommender System
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict
import sys
from pathlib import Path

# Import recommender engine
sys.path.insert(0, str(Path(__file__).parent.parent))
from recommender_engine import engine

router = APIRouter()

# Request Models
class RecommendationRequest(BaseModel):
    season: Optional[str] = None
    budget: Optional[str] = None
    category: Optional[str] = None
    country: Optional[str] = None
    limit: Optional[int] = 10

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Dict]] = []

# Health check
@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Travel Recommender API"}

# Data summary
@router.get("/data/summary")
async def data_summary():
    """Get summary of available data"""
    try:
        df = engine.destinations
        return {
            "success": True,
            "data": {
                "total_destinations": len(df),
                "countries": df['Country'].unique().tolist() if not df.empty else [],
                "types": df['Type'].unique().tolist() if not df.empty else [],
                "seasons": df['Best Season'].unique().tolist() if not df.empty else []
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get recommendations
@router.post("/recommendations")
async def get_recommendations(request: RecommendationRequest):
    """Get travel recommendations based on filters"""
    try:
        filters = {
            'season': request.season,
            'budget': request.budget,
            'category': request.category,
            'country': request.country
        }
        
        filters = {k: v for k, v in filters.items() if v is not None}
        results = engine.get_recommendations(filters, limit=request.limit)
        
        return {
            "success": True,
            "count": len(results),
            "filters": filters,
            "recommendations": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get seasonal recommendations
@router.get("/recommendations/seasonal/{season}")
async def get_seasonal_recommendations(
    season: str,
    limit: int = Query(default=6, ge=1, le=20)
):
    """Get top recommendations for a specific season"""
    try:
        results = engine.get_recommendations({'season': season}, limit=limit)
        return {
            "success": True,
            "season": season,
            "count": len(results),
            "recommendations": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get similar destinations
@router.get("/destinations/{destination_name}/similar")
async def get_similar_destinations(
    destination_name: str,
    limit: int = Query(default=5, ge=1, le=10)
):
    """Find similar destinations"""
    try:
        results = engine.get_similar(destination_name, limit)
        return {
            "success": True,
            "destination": destination_name,
            "count": len(results),
            "similar": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Search destinations
@router.get("/destinations/search")
async def search_destinations(
    q: str = Query(..., min_length=1),
    limit: int = Query(default=10, ge=1, le=50)
):
    """Search destinations by name"""
    try:
        results = engine.search(q, limit)
        return {
            "success": True,
            "query": q,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get all destinations
@router.get("/destinations")
async def get_all_destinations(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0)
):
    """Get all destinations with pagination"""
    try:
        df = engine.destinations
        total = len(df)
        results = df.iloc[offset:offset+limit].to_dict('records')
        
        return {
            "success": True,
            "total": total,
            "limit": limit,
            "offset": offset,
            "count": len(results),
            "destinations": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get destination by name
@router.get("/destinations/{destination_name}")
async def get_destination_details(destination_name: str):
    """Get details of a specific destination"""
    try:
        df = engine.destinations
        dest = df[df['Destination Name'] == destination_name]
        
        if dest.empty:
            raise HTTPException(status_code=404, detail="Destination not found")
        
        return {
            "success": True,
            "destination": dest.iloc[0].to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chat endpoint
@router.post("/chat")
async def chat(request: ChatRequest):
    """Simple chat endpoint"""
    try:
        message = request.message.lower()
        filters = {}
        
        # Detect season
        seasons = ['spring', 'summer', 'autumn', 'fall', 'winter']
        for season in seasons:
            if season in message:
                filters['season'] = season.capitalize()
                break
        
        # Detect budget
        if any(word in message for word in ['cheap', 'budget', 'affordable']):
            filters['budget'] = 'Budget'
        elif any(word in message for word in ['luxury', 'expensive', 'premium']):
            filters['budget'] = 'Luxury'
        
        # Detect category
        categories = ['beach', 'mountain', 'cultural', 'nature', 'adventure', 'historical']
        for cat in categories:
            if cat in message:
                filters['category'] = cat.capitalize()
                break
        
        results = engine.get_recommendations(filters, limit=6)
        
        response_text = f"Toi tim thay {len(results)} diem den phu hop"
        if filters:
            filter_desc = ", ".join([f"{k}: {v}" for k, v in filters.items()])
            response_text += f" ({filter_desc})"
        
        return {
            "success": True,
            "response": response_text,
            "filters": filters,
            "recommendations": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get filter options
@router.get("/filters/options")
async def get_filter_options():
    """Get available filter options"""
    try:
        df = engine.destinations
        
        return {
            "success": True,
            "options": {
                "seasons": df['Best Season'].unique().tolist() if not df.empty else [],
                "budgets": df['Cost_Category'].unique().tolist() if not df.empty else [],
                "categories": df['Type'].unique().tolist() if not df.empty else [],
                "countries": df['Country'].unique().tolist() if not df.empty else []
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
    user_id: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    conversation_history: Optional[List[Dict]] = []
    recommendation_context: Optional[Dict] = None

class ChatSessionSaveRequest(BaseModel):
    session_id: str
    user_id: str
    title: str
    messages: List[Dict]

class RatingRequest(BaseModel):
    user_id: str
    rating: float  # 1.0 – 5.0

class RegisterRequest(BaseModel):
    username: str
    password: str
    full_name: str
    email: str

class LoginRequest(BaseModel):
    username: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    email: str
    token: str
    new_password: str

class PreferencesRequest(BaseModel):
    season: Optional[str] = None
    category: Optional[str] = None
    budget: Optional[str] = None

import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# User Authentication Endpoints
@router.post("/auth/register")
async def register_user(request: RegisterRequest):
    """Register a new user account"""
    try:
        from mining.mongodb_storage import db_storage
        if not db_storage.is_connected():
            raise HTTPException(status_code=503, detail="Database connection not available")
            
        username = request.username.strip().lower()
        email = request.email.strip().lower()
        if not username or not request.password or not email:
            raise HTTPException(status_code=400, detail="Vui lòng cung cấp đầy đủ tên đăng nhập, email và mật khẩu")
            
        # Check if user already exists
        existing_user = db_storage.db.users.find_one({"username": username})
        if existing_user:
            raise HTTPException(status_code=400, detail="Tên đăng nhập đã được sử dụng")
            
        # Check if email is already in use
        existing_email = db_storage.db.users.find_one({"email": email})
        if existing_email:
            raise HTTPException(status_code=400, detail="Email này đã được sử dụng để đăng ký tài khoản")
            
        # Save new user
        new_user = {
            "username": username,
            "email": email,
            "password_hash": hash_password(request.password),
            "full_name": request.full_name.strip() or username,
            "role": "user"
        }
        db_storage.db.users.insert_one(new_user)
        
        return {
            "success": True,
            "message": "Đăng ký tài khoản thành công!"
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auth/login")
async def login_user(request: LoginRequest):
    """Log in user and verify credentials"""
    try:
        from mining.mongodb_storage import db_storage
        if not db_storage.is_connected():
            raise HTTPException(status_code=503, detail="Database connection not available")
            
        username = request.username.strip().lower()
        # Find user
        user = db_storage.db.users.find_one({"username": username})
        if not user:
            raise HTTPException(status_code=400, detail="Tên đăng nhập hoặc mật khẩu không chính xác")
            
        # Verify password
        if user["password_hash"] != hash_password(request.password):
            raise HTTPException(status_code=400, detail="Tên đăng nhập hoặc mật khẩu không chính xác")
            
        return {
            "success": True,
            "message": "Đăng nhập thành công!",
            "user": {
                "id": str(user["_id"]) if "_id" in user else username,
                "username": user["username"],
                "fullName": user.get("full_name", username),
                "role": user.get("role", "user"),
                "preferences": user.get("preferences")
            }
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auth/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """Generate password reset token and send reset link to user's email"""
    try:
        from mining.mongodb_storage import db_storage
        from services.email_service import send_reset_password_email
        import secrets
        from datetime import datetime, timedelta, timezone
        import os
        
        if not db_storage.is_connected():
            raise HTTPException(status_code=503, detail="Database connection not available")
            
        email = request.email.strip().lower()
        if not email:
            raise HTTPException(status_code=400, detail="Vui lòng cung cấp email")
            
        user = db_storage.db.users.find_one({"email": email})
        if not user:
            # For security reasons, don't reveal that the email doesn't exist.
            # But let's log it internally or output success message.
            return {
                "success": True,
                "message": "Nếu email tồn tại trong hệ thống, liên kết đặt lại mật khẩu đã được gửi."
            }
            
        # Generate token and expiry (15 mins)
        token = secrets.token_hex(20)
        expiry = datetime.now(timezone.utc) + timedelta(minutes=15)
        
        # Save to user in db
        db_storage.db.users.update_one(
            {"email": email},
            {"$set": {
                "reset_token": token,
                "reset_expiry": expiry
            }}
        )
        
        # Construct reset link
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        reset_link = f"{frontend_url}/reset-password?token={token}&email={email}"
        
        # Send reset email
        send_reset_password_email(email, reset_link)
        
        return {
            "success": True,
            "message": "Liên kết đặt lại mật khẩu đã được gửi đến email của bạn."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auth/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Verify reset token and update password"""
    try:
        from mining.mongodb_storage import db_storage
        from datetime import datetime, timezone
        
        if not db_storage.is_connected():
            raise HTTPException(status_code=503, detail="Database connection not available")
            
        email = request.email.strip().lower()
        token = request.token.strip()
        new_password = request.new_password
        
        if not email or not token or not new_password:
            raise HTTPException(status_code=400, detail="Thiếu thông tin yêu cầu đặt lại mật khẩu")
            
        user = db_storage.db.users.find_one({
            "email": email,
            "reset_token": token
        })
        
        if not user:
            raise HTTPException(status_code=400, detail="Mã xác thực đặt lại mật khẩu không chính xác hoặc đã được sử dụng")
            
        # Check token expiry
        expiry = user.get("reset_expiry")
        if not expiry:
            raise HTTPException(status_code=400, detail="Mã xác thực không hợp lệ")
            
        # Handle timezone-aware conversion
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
            
        if datetime.now(timezone.utc) > expiry:
            raise HTTPException(status_code=400, detail="Mã xác thực đã hết hạn")
            
        # Update user's password, and clean up token fields
        hashed = hash_password(new_password)
        db_storage.db.users.update_one(
            {"email": email},
            {
                "$set": {"password_hash": hashed},
                "$unset": {"reset_token": "", "reset_expiry": ""}
            }
        )
        
        return {
            "success": True,
            "message": "Đặt lại mật khẩu thành công! Bạn có thể dùng mật khẩu mới để đăng nhập."
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/auth/preferences")
async def update_preferences(request: PreferencesRequest, username: str = Query(...)):
    """Update user's personal travel preferences"""
    try:
        from mining.mongodb_storage import db_storage
        if not db_storage.is_connected():
            raise HTTPException(status_code=503, detail="Database connection not available")
            
        username_clean = username.strip().lower()
        
        # Build preferences update object
        prefs = {}
        if request.season: prefs["season"] = request.season
        if request.category: prefs["category"] = request.category
        if request.budget: prefs["budget"] = request.budget
        
        # Update user in DB
        res = db_storage.db.users.update_one(
            {"username": username_clean},
            {"$set": {"preferences": prefs}}
        )
        
        # Get updated user info
        user = db_storage.db.users.find_one({"username": username_clean})
        if not user:
            raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
            
        return {
            "success": True,
            "message": "Cập nhật sở thích cá nhân thành công!",
            "user": {
                "id": str(user["_id"]) if "_id" in user else username_clean,
                "username": user["username"],
                "fullName": user.get("full_name", username_clean),
                "role": user.get("role", "user"),
                "preferences": user.get("preferences")
            }
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check
@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Travel Recommender API"}

# Global stats (used on HomePage counter widgets)
@router.get("/stats")
async def get_stats():
    """Returns global system statistics for homepage display"""
    try:
        from mining.mongodb_storage import db_storage
        df = engine.destinations
        total_destinations = len(df) if not df.empty else 0
        total_countries = int(df['Country'].nunique()) if not df.empty else 0

        # Count rules in MongoDB
        total_rules = 0
        if db_storage.is_connected():
            total_rules = db_storage.db.rules.count_documents({})

        return {
            "success": True,
            "data": {
                "total_destinations": total_destinations,
                "total_countries":    total_countries,
                "total_rules":        total_rules,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        results = engine.get_recommendations(filters, limit=request.limit, user_id=request.user_id)

        # Get matched Apriori rules for frontend explanation panel
        matched_rules_info = engine.get_matched_rules_info(filters)

        return {
            "success": True,
            "count": len(results),
            "filters": filters,
            "recommendations": results,
            "matched_rules": matched_rules_info,
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
    limit: int = Query(default=50, ge=1, le=200)
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
        
        # Clean NaN values
        import pandas as pd
        subset = df.iloc[offset:offset+limit].copy()
        subset = subset.astype(object).where(pd.notnull(subset), None)
        results = subset.to_dict('records')
        
        return {
            "success": True,
            "total": total,
            "limit": limit,
            "offset": offset,
            "count": len(results),
            "destinations": results
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Get weather for a destination
@router.get("/destinations/{destination_name}/weather")
async def get_destination_weather(destination_name: str):
    """Get current weather for a specific destination"""
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from weather_service import get_current_weather

        # Try to get country and coordinates from destination data
        df = engine.destinations
        country = ""
        lat = None
        lon = None
        if not df.empty:
            match = df[df['Destination Name'] == destination_name]
            if not match.empty:
                dest_row = match.iloc[0]
                country = str(dest_row.get('Country', ''))
                # Ưu tiên lấy tọa độ của nước để thời tiết và khí hậu chính xác với thực tế quốc gia đó
                lat = dest_row.get('country_latitude')
                lon = dest_row.get('country_longitude')
                
                import pandas as pd
                if pd.isna(lat) or pd.isna(lon):
                    lat = dest_row.get('destination_latitude')
                    lon = dest_row.get('destination_longitude')

        # Convert coordinates to float if present
        try:
            import pandas as pd
            latitude = float(lat) if lat is not None and not pd.isna(lat) else None
            longitude = float(lon) if lon is not None and not pd.isna(lon) else None
        except ValueError:
            latitude = None
            longitude = None

        # Use first word of destination name as city query fallback
        city = destination_name.split()[0] if destination_name else destination_name
        weather = get_current_weather(city_name=city, country_name=country, latitude=latitude, longitude=longitude)
        return {
            "success": True,
            "destination": destination_name,
            "country": country,
            "weather": weather
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Get historical climate data for a destination (Open-Meteo Archive API)
@router.get("/destinations/{destination_name}/climate")
async def get_destination_climate(destination_name: str):
    """
    Lấy dữ liệu khí hậu lịch sử (nhiệt độ TB và lượng mưa từng tháng)
    cho một điểm đến, sử dụng Open-Meteo Archive API miễn phí.
    Dùng để vẽ biểu đồ khí hậu (Climate Chart) trên trang chi tiết điểm đến.
    """
    try:
        from services.openmeteo_service import get_historical_climate, get_best_months_to_visit

        # Lấy tọa độ (lat/lon) của điểm đến từ dữ liệu
        df = engine.destinations
        if df.empty:
            raise HTTPException(status_code=404, detail="Không có dữ liệu điểm đến.")

        match = df[df['Destination Name'] == destination_name]
        if match.empty:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy điểm đến: {destination_name}")

        dest_row = match.iloc[0]
        # Lấy tọa độ của nước (hoặc điểm đến) từ dữ liệu để đảm bảo tính thực tế
        lat = dest_row.get('country_latitude')
        lon = dest_row.get('country_longitude')
        
        import pandas as pd
        if pd.isna(lat) or pd.isna(lon):
            lat = dest_row.get('destination_latitude')
            lon = dest_row.get('destination_longitude')

        if pd.isna(lat) or pd.isna(lon):
            raise HTTPException(
                status_code=422,
                detail=f"Điểm đến '{destination_name}' không có dữ liệu tọa độ (lat/lon)."
            )

        # Gọi Open-Meteo Archive API
        climate_result = get_historical_climate(
            latitude=float(lat),
            longitude=float(lon)
        )

        if not climate_result["success"]:
            raise HTTPException(
                status_code=502,
                detail=climate_result.get("error", "Lỗi không xác định từ Open-Meteo API.")
            )

        # Tính các tháng đẹp nhất để du lịch
        best_months = get_best_months_to_visit(
            climate_result["climate"]["temp_avg"],
            climate_result["climate"]["rainfall"]
        )

        return {
            "success":     True,
            "destination": destination_name,
            "latitude":    float(lat),
            "longitude":   float(lon),
            "climate":     climate_result["climate"],
            "year":        climate_result["year"],
            "best_months": best_months,
            "source":      climate_result["source"]
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Rate a destination (saves real user rating to MongoDB for Collaborative Filtering)
@router.post("/destinations/{destination_name}/rate")
async def rate_destination(destination_name: str, request: RatingRequest):
    """
    Saves a star rating (1–5) for a destination from an anonymous user.
    The rating is stored in MongoDB and immediately used to refresh the
    Collaborative Filtering item-similarity matrix.
    """
    try:
        if not (1.0 <= request.rating <= 5.0):
            raise HTTPException(status_code=422, detail="Rating phải nằm trong khoảng 1.0 đến 5.0")

        from mining.collaborative_filtering import collaborative_recommender
        success = collaborative_recommender.save_real_rating(
            user_id=request.user_id,
            destination_name=destination_name,
            rating=request.rating
        )

        if not success:
            raise HTTPException(status_code=500, detail="Không thể lưu đánh giá. Vui lòng thử lại.")

        return {
            "success":          True,
            "destination":      destination_name,
            "user_id":          request.user_id,
            "rating":           request.rating,
            "message":          f"Đã lưu đánh giá {request.rating}⭐ cho {destination_name}!"
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Get a user's own rating for a destination
@router.get("/destinations/{destination_name}/my-rating")
async def get_my_rating(destination_name: str, user_id: str = Query(...)):
    """
    Retrieves the authenticated (anonymous) user's rating for a destination.
    Used by the frontend to show the user's existing star selection.
    """
    try:
        from mining.collaborative_filtering import collaborative_recommender
        rating = collaborative_recommender.get_user_rating(
            user_id=user_id,
            destination_name=destination_name
        )
        return {
            "success":     True,
            "destination": destination_name,
            "user_id":     user_id,
            "rating":      rating,  # None if not rated yet
            "has_rated":   rating is not None,
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
        
        import pandas as pd
        dest_clean = dest.astype(object).where(pd.notnull(dest), None)
        
        return {
            "success": True,
            "destination": dest_clean.iloc[0].to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Chat endpoint
@router.post("/chat")
async def chat(request: ChatRequest):
    """Chat endpoint powered by Gemini NLP Chatbot Module"""
    try:
        from nlp.gemini_module import process_chat_query
        
        # Run NLP pipeline to parse intent, extract entities and generate response
        res = process_chat_query(
            request.message,
            session_id=request.session_id or "default",
            recommendation_context=request.recommendation_context,
            conversation_history=request.conversation_history
        )
        
        return {
            "success": True,
            "response": res["response"],
            "filters": res["preferences"],
            "recommendations": res["recommendations"]
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Chat Session Management Endpoints
@router.get("/chat/sessions")
async def get_chat_sessions(user_id: str = Query(...)):
    """Retrieve all chat sessions for a user"""
    try:
        from mining.mongodb_storage import db_storage
        if not db_storage.is_connected():
            raise HTTPException(status_code=503, detail="Database connection not available")
        sessions = db_storage.load_chat_sessions(user_id)
        return {"success": True, "sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/sessions/{session_id}")
async def get_chat_session(session_id: str):
    """Retrieve details of a single chat session"""
    try:
        from mining.mongodb_storage import db_storage
        if not db_storage.is_connected():
            raise HTTPException(status_code=503, detail="Database connection not available")
        session = db_storage.load_chat_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        return {"success": True, "session": session}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/sessions")
async def save_chat_session(request: ChatSessionSaveRequest):
    """Save or update a chat session"""
    try:
        from mining.mongodb_storage import db_storage
        if not db_storage.is_connected():
            raise HTTPException(status_code=503, detail="Database connection not available")
        success = db_storage.save_chat_session(
            session_id=request.session_id,
            user_id=request.user_id,
            title=request.title,
            messages=request.messages
        )
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save chat session")
        return {"success": True, "message": "Chat session saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/chat/sessions/{session_id}")
async def delete_chat_session(session_id: str):
    """Delete a chat session"""
    try:
        from mining.mongodb_storage import db_storage
        if not db_storage.is_connected():
            raise HTTPException(status_code=503, detail="Database connection not available")
        success = db_storage.delete_chat_session(session_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete chat session")
        return {"success": True, "message": "Chat session deleted successfully"}
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


# ==========================================
# ADMIN DASHBOARD ENDPOINTS
# ==========================================

class AprioriParams(BaseModel):
    min_support: Optional[float] = 0.01
    min_confidence: Optional[float] = 0.1
    min_lift: Optional[float] = 1.0

class ClusteringParams(BaseModel):
    n_clusters: Optional[int] = 5

@router.get("/admin/stats")
async def get_admin_stats():
    """Retrieves dashboard stats for admin panel"""
    try:
        from mining.mongodb_storage import db_storage
        df = engine.destinations
        total_destinations = len(df) if not df.empty else 0
        total_countries = int(df['Country'].nunique()) if not df.empty else 0
        
        total_rules = 0
        total_ratings = 0
        real_ratings = 0
        simulated_ratings = 0
        cluster_profiles = []
        
        if db_storage.is_connected():
            total_rules = db_storage.db.rules.count_documents({})
            total_ratings = db_storage.db.user_ratings.count_documents({})
            real_ratings = db_storage.db.user_ratings.count_documents({"is_real": True})
            simulated_ratings = total_ratings - real_ratings
            cluster_profiles = list(db_storage.db.cluster_profiles.find({}, {"_id": 0}))
            
        return {
            "success": True,
            "stats": {
                "total_destinations": total_destinations,
                "total_countries": total_countries,
                "total_rules": total_rules,
                "total_ratings": total_ratings,
                "real_ratings": real_ratings,
                "simulated_ratings": simulated_ratings
            },
            "cluster_profiles": cluster_profiles
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/ratings")
async def get_admin_ratings(limit: int = 150):
    """Retrieves all user ratings from database"""
    try:
        from mining.mongodb_storage import db_storage
        ratings = []
        if db_storage.is_connected():
            # Return real ratings first, then simulated, sorted descending by rating
            ratings = list(db_storage.db.user_ratings.find({}, {"_id": 0}).limit(limit))
            # Sort by rating or real ratings
            ratings.sort(key=lambda x: (x.get('is_real', False), x.get('rating', 0.0)), reverse=True)
        return {
            "success": True,
            "ratings": ratings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/rules")
async def get_admin_rules():
    """Retrieves all rules from database"""
    try:
        from mining.mongodb_storage import db_storage
        rules = []
        if db_storage.is_connected():
            rules = list(db_storage.db.rules.find({}, {"_id": 0}))
        return {
            "success": True,
            "rules": rules
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/admin/ratings")
async def delete_admin_rating(user_id: str, destination_name: str):
    """Deletes a rating and updates collaborative filtering matrix"""
    try:
        from mining.mongodb_storage import db_storage
        from mining.collaborative_filtering import collaborative_recommender
        if db_storage.is_connected():
            res = db_storage.db.user_ratings.delete_one({
                "user_id": user_id,
                "destination_name": destination_name
            })
            if res.deleted_count > 0:
                # Refresh CF matrix immediately
                collaborative_recommender.refresh_similarity_matrix()
                return {"success": True, "message": f"Đã xóa đánh giá của user {user_id} cho điểm đến {destination_name}."}
            else:
                raise HTTPException(status_code=404, detail="Không tìm thấy đánh giá cần xóa.")
        raise HTTPException(status_code=500, detail="Không kết nối được MongoDB.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/mine-apriori")
async def run_apriori_mining(params: AprioriParams):
    """Triggers Apriori rule mining from MongoDB transactions"""
    try:
        from mining.apriori_module import mine_association_rules
        rules = mine_association_rules(
            min_support=params.min_support,
            min_confidence=params.min_confidence,
            min_lift=params.min_lift
        )
        # Reload engine data to sync rules and updated info
        engine.load_data()
        return {
            "success": True,
            "count": len(rules),
            "message": f"Khai phá thành công! Tạo mới {len(rules)} luật kết hợp Apriori."
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/run-clustering")
async def run_kmeans_clustering(params: ClusteringParams):
    """Triggers K-Means clustering and updates cluster profiles"""
    try:
        from mining.clustering import run_clustering
        profiles = run_clustering(n_clusters=params.n_clusters)
        if profiles is None:
            raise HTTPException(status_code=500, detail="Lỗi trong quá trình phân cụm.")
        # Reload engine data to sync updated cluster labels
        engine.load_data()
        return {
            "success": True,
            "profiles": profiles,
            "message": f"Phân cụm K-Means thành công với k={params.n_clusters} cụm!"
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/refresh-cf")
async def refresh_cf_matrix():
    """Triggers manual re-computation of Collaborative Filtering item similarities"""
    try:
        from mining.collaborative_filtering import collaborative_recommender
        collaborative_recommender.refresh_similarity_matrix()
        # Reload engine data to sync destinations and rating updates
        engine.load_data()
        return {
            "success": True,
            "message": "Đã tính toán lại ma trận tương đồng Collaborative Filtering thành công!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


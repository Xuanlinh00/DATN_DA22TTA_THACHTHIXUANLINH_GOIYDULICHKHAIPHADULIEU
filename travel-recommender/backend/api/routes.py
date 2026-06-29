# -*- coding: utf-8 -*-
"""
API Routes for Travel Recommender System
"""
from fastapi import APIRouter, HTTPException, Query, Request, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List, Dict
import sys
from pathlib import Path

# Import recommender engine
sys.path.insert(0, str(Path(__file__).parent.parent))
from recommender_engine import engine
from services.image_service import get_image_service
from mining.mongodb_storage import db_storage
from datetime import datetime, timezone, timedelta

def get_cached_climate(destination_name: str) -> Optional[dict]:
    try:
        if not db_storage.is_connected():
            return None
        cached = db_storage.db.climate_cache.find_one({"destination_name": destination_name})
        if cached:
            created_at = cached.get("created_at")
            if created_at:
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
                if datetime.now(timezone.utc) - created_at < timedelta(days=30):
                    return cached.get("climate_data")
    except Exception as e:
        print(f"[CACHE] Error reading climate cache: {e}")
    return None

def save_cached_climate(destination_name: str, climate_data: dict):
    try:
        if not db_storage.is_connected():
            return
        db_storage.db.climate_cache.update_one(
            {"destination_name": destination_name},
            {"$set": {
                "destination_name": destination_name,
                "climate_data": climate_data,
                "created_at": datetime.now(timezone.utc)
            }},
            upsert=True
        )
    except Exception as e:
        print(f"[CACHE] Error writing climate cache: {e}")

def get_cached_weather(destination_name: str) -> Optional[dict]:
    try:
        if not db_storage.is_connected():
            return None
        cached = db_storage.db.weather_cache.find_one({"destination_name": destination_name})
        if cached:
            created_at = cached.get("created_at")
            if created_at:
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
                if datetime.now(timezone.utc) - created_at < timedelta(minutes=15):
                    return cached.get("weather_data")
    except Exception as e:
        print(f"[CACHE] Error reading weather cache: {e}")
    return None

def save_cached_weather(destination_name: str, weather_data: dict):
    try:
        if not db_storage.is_connected():
            return
        db_storage.db.weather_cache.update_one(
            {"destination_name": destination_name},
            {"$set": {
                "destination_name": destination_name,
                "weather_data": weather_data,
                "created_at": datetime.now(timezone.utc)
            }},
            upsert=True
        )
    except Exception as e:
        print(f"[CACHE] Error writing weather cache: {e}")

router = APIRouter()

# Request Models
class RecommendationRequest(BaseModel):
    season: Optional[str] = None
    budget: Optional[str] = None
    category: Optional[str] = None
    country: Optional[str] = None
    limit: Optional[int] = 10
    user_id: Optional[str] = None
    strict: Optional[bool] = False
    strict_country: Optional[bool] = False

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
    token: str          # raw token tu URL (se duoc hash SHA256 de tim trong DB)
    new_password: str

class ChangePasswordRequest(BaseModel):
    username: str
    current_password: str
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
def register_user(request: RegisterRequest):
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
def login_user(request: LoginRequest):
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
            
        # Check lock status
        if user.get("status") == "locked":
            raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa. Vui lòng liên hệ quản trị viên.")
            
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
def forgot_password(request: ForgotPasswordRequest):
    """
    Tao token reset (SHA256), luu hash vao DB, gui raw token qua email.
    Token het han sau 10 phut.
    """
    try:
        import hashlib, secrets, os
        from mining.mongodb_storage import db_storage
        from services.email_service import send_reset_password_email, _is_configured as email_is_configured
        from datetime import datetime, timedelta, timezone

        if not db_storage.is_connected():
            raise HTTPException(status_code=503, detail="Database connection not available")

        email = request.email.strip().lower()
        if not email:
            raise HTTPException(status_code=400, detail="Vui long cung cap email")

        user = db_storage.db.users.find_one({"email": email})
        if not user:
            # Bao mat: khong tiet lo email co ton tai khong
            return {
                "success": True,
                "email_configured": email_is_configured(),
                "message": "Neu email ton tai trong he thong, lien ket dat lai mat khau da duoc gui."
            }

        # 1. Tao raw token (20 bytes -> 40 hex chars)
        raw_token = secrets.token_hex(20)

        # 2. Hash bang SHA256 -> luu vao DB (khong luu raw token)
        hashed_token = hashlib.sha256(raw_token.encode()).hexdigest()

        # 3. Luu hash token + expiry (10 phut) vao DB
        expiry = datetime.now(timezone.utc) + timedelta(minutes=10)
        db_storage.db.users.update_one(
            {"email": email},
            {"$set": {
                "resetPasswordToken":  hashed_token,
                "resetPasswordExpire": expiry
            }}
        )

        # 4. Xay dung reset URL voi raw token trong path
        frontend_url = os.getenv("FRONTEND_URL", "http://127.0.0.1:3000")
        reset_url = f"{frontend_url}/reset-password/{raw_token}"

        # Log de dev kiem tra
        sep = "=" * 72
        print(f"\n{sep}")
        print(f"  [RESET TOKEN]")
        print(f"  Email     : {email}")
        print(f"  Raw token : {raw_token}")
        print(f"  Reset URL : {reset_url}")
        print(f"{sep}\n")

        # 5. Gui email (hoac in ra console neu chua cau hinh)
        send_reset_password_email(email, reset_url)

        email_ok = email_is_configured()
        response = {
            "success": True,
            "email_configured": email_ok,
            "message": (
                "Lien ket dat lai mat khau da duoc gui den email cua ban."
                if email_ok
                else "Email chua duoc cau hinh - lien ket duoc tao de dung truc tiep."
            )
        }

        # Neu email chua cau hinh -> tra link thang ve frontend de test
        if not email_ok:
            response["dev_reset_link"] = reset_url

        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auth/reset-password")
def reset_password(request: ResetPasswordRequest):
    """
    Nhan raw token tu frontend, hash SHA256, tim user trong DB.
    Dat lai mat khau neu token hop le va chua het han.
    Xoa token sau khi su dung.
    """
    try:
        import hashlib
        from mining.mongodb_storage import db_storage
        from datetime import datetime, timezone

        if not db_storage.is_connected():
            raise HTTPException(status_code=503, detail="Database connection not available")

        raw_token    = (request.token or "").strip()
        new_password = (request.new_password or "").strip()

        if not raw_token or not new_password:
            raise HTTPException(status_code=400, detail="Thieu thong tin yeu cau dat lai mat khau")

        if len(new_password) < 6:
            raise HTTPException(status_code=400, detail="Mat khau phai co it nhat 6 ky tu")

        # Hash raw token de so sanh voi DB
        hashed_token = hashlib.sha256(raw_token.encode()).hexdigest()

        # Tim user theo hashed token VA kiem tra chua het han
        user = db_storage.db.users.find_one({
            "resetPasswordToken": hashed_token
        })

        if not user:
            raise HTTPException(
                status_code=400,
                detail="Token khong hop le hoac da duoc su dung"
            )

        # Kiem tra thoi gian het han
        expiry = user.get("resetPasswordExpire")
        if not expiry:
            raise HTTPException(status_code=400, detail="Token khong hop le")

        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)

        if datetime.now(timezone.utc) > expiry:
            # Xoa token het han
            db_storage.db.users.update_one(
                {"_id": user["_id"]},
                {"$unset": {"resetPasswordToken": "", "resetPasswordExpire": ""}}
            )
            raise HTTPException(status_code=400, detail="Token da het han (10 phut). Vui long gui lai yeu cau.")

        # Cap nhat mat khau moi + xoa token (single use)
        db_storage.db.users.update_one(
            {"_id": user["_id"]},
            {
                "$set":   {"password_hash": hash_password(new_password)},
                "$unset": {"resetPasswordToken": "", "resetPasswordExpire": ""}
            }
        )

        return {
            "success": True,
            "message": "Doi mat khau thanh cong! Ban co the dung mat khau moi de dang nhap."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auth/change-password")
def change_password(request: ChangePasswordRequest):
    """Change password for an authenticated user (requires current password)"""
    try:
        from mining.mongodb_storage import db_storage
        if not db_storage.is_connected():
            raise HTTPException(status_code=503, detail="Database connection not available")

        username = request.username.strip().lower()
        if not username or not request.current_password or not request.new_password:
            raise HTTPException(status_code=400, detail="Vui lòng điền đầy đủ thông tin")

        if len(request.new_password) < 6:
            raise HTTPException(status_code=400, detail="Mật khẩu mới phải có ít nhất 6 ký tự")

        # Find user
        user = db_storage.db.users.find_one({"username": username})
        if not user:
            raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

        # Verify current password
        if user["password_hash"] != hash_password(request.current_password):
            raise HTTPException(status_code=400, detail="Mật khẩu hiện tại không chính xác")

        # Check new password is not same as old
        if hash_password(request.new_password) == user["password_hash"]:
            raise HTTPException(status_code=400, detail="Mật khẩu mới phải khác mật khẩu hiện tại")

        # Update password
        db_storage.db.users.update_one(
            {"username": username},
            {"$set": {"password_hash": hash_password(request.new_password)}}
        )

        return {
            "success": True,
            "message": "Đổi mật khẩu thành công!"
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/auth/preferences")
def update_preferences(request: PreferencesRequest, username: str = Query(...)):
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
def health_check():
    return {"status": "healthy", "service": "Travel Recommender API"}

# Global stats (used on HomePage counter widgets)
@router.get("/stats")
def get_stats():
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
def data_summary():
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
def get_recommendations(request: RecommendationRequest):
    """Get travel recommendations based on filters"""
    try:
        filters = {
            'season': request.season,
            'budget': request.budget,
            'category': request.category,
            'country': request.country
        }
        
        filters = {k: v for k, v in filters.items() if v is not None}
        results = engine.get_recommendations(
            filters,
            limit=request.limit,
            user_id=request.user_id,
            strict=request.strict,
            strict_country=request.strict_country
        )

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
def get_seasonal_recommendations(
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
def get_similar_destinations(
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
def search_destinations(
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
def get_all_destinations(
    limit: int = Query(default=50, ge=1, le=2000),
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
def get_destination_weather(destination_name: str):
    """Get current weather for a specific destination"""
    try:
        # Check cache first
        cached = get_cached_weather(destination_name)
        if cached:
            print(f"[CACHE] Serving weather for '{destination_name}' from MongoDB cache")
            return {
                "success": True,
                "destination": destination_name,
                "country": cached.get("country", ""),
                "weather": cached
            }

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
                # Ưu tiên tọa độ điểm đến cụ thể, fallback về tọa độ quốc gia nếu không có
                lat = dest_row.get('destination_latitude')
                lon = dest_row.get('destination_longitude')
                
                import pandas as pd
                if pd.isna(lat) or pd.isna(lon):
                    lat = dest_row.get('country_latitude')
                    lon = dest_row.get('country_longitude')

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
        
        # Save cache on success
        if weather and weather.get("success"):
            weather["country"] = country
            save_cached_weather(destination_name, weather)

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
def get_destination_climate(destination_name: str):
    """
    Lấy dữ liệu khí hậu lịch sử (nhiệt độ TB và lượng mưa từng tháng)
    cho một điểm đến, sử dụng Open-Meteo Archive API miễn phí.
    Dùng để vẽ biểu đồ khí hậu (Climate Chart) trên trang chi tiết điểm đến.
    """
    try:
        # Check cache first
        cached = get_cached_climate(destination_name)
        if cached:
            print(f"[CACHE] Serving climate for '{destination_name}' from MongoDB cache")
            return cached

        from services.openmeteo_service import get_historical_climate, get_best_months_to_visit

        # Lấy tọa độ (lat/lon) của điểm đến từ dữ liệu
        df = engine.destinations
        if df.empty:
            raise HTTPException(status_code=404, detail="Không có dữ liệu điểm đến.")

        match = df[df['Destination Name'] == destination_name]
        if match.empty:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy điểm đến: {destination_name}")

        dest_row = match.iloc[0]
        # Ưu tiên tọa độ điểm đến cụ thể, fallback về tọa độ quốc gia nếu không có
        lat = dest_row.get('destination_latitude')
        lon = dest_row.get('destination_longitude')
        
        import pandas as pd
        if pd.isna(lat) or pd.isna(lon):
            lat = dest_row.get('country_latitude')
            lon = dest_row.get('country_longitude')

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

        result_dict = {
            "success":     True,
            "destination": destination_name,
            "latitude":    float(lat),
            "longitude":   float(lon),
            "climate":     climate_result["climate"],
            "year":        climate_result["year"],
            "best_months": best_months,
            "source":      climate_result["source"]
        }

        # Save to cache
        save_cached_climate(destination_name, result_dict)

        return result_dict

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Rate a destination (saves real user rating to MongoDB for Collaborative Filtering)
@router.post("/destinations/{destination_name}/rate")
def rate_destination(destination_name: str, request: RatingRequest):
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
def get_my_rating(destination_name: str, user_id: str = Query(...)):
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
def get_destination_details(destination_name: str):
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
def chat(request: ChatRequest):
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
def get_chat_sessions(user_id: str = Query(...)):
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
def get_chat_session(session_id: str):
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
def save_chat_session(request: ChatSessionSaveRequest):
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
def delete_chat_session(session_id: str):
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
def get_filter_options():
    """Get available filter options — normalized to Title Case to deduplicate mixed-case data."""
    try:
        import pandas as pd
        df = engine.destinations

        def normalize_unique(series):
            """Normalize values to Title Case and return deduplicated sorted list."""
            vals = series.dropna().str.strip().str.title().unique().tolist()
            return sorted(set(vals))

        return {
            "success": True,
            "options": {
                "seasons":    normalize_unique(df['Best Season'])   if not df.empty else [],
                "budgets":    normalize_unique(df['Cost_Category']) if not df.empty else [],
                "categories": normalize_unique(df['Type'])          if not df.empty else [],
                "countries":  sorted(df['Country'].dropna().str.strip().unique().tolist()) if not df.empty else [],
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
def get_admin_stats():
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
        total_users = 0
        cluster_profiles = []
        
        if db_storage.is_connected():
            total_rules = db_storage.db.rules.count_documents({})
            total_ratings = db_storage.db.user_ratings.count_documents({})
            real_ratings = db_storage.db.user_ratings.count_documents({"is_real": True})
            simulated_ratings = total_ratings - real_ratings
            cluster_profiles = list(db_storage.db.cluster_profiles.find({}, {"_id": 0}))
            total_users = db_storage.db.users.count_documents({})
            
        return {
            "success": True,
            "stats": {
                "total_destinations": total_destinations,
                "total_countries": total_countries,
                "total_rules": total_rules,
                "total_ratings": total_ratings,
                "real_ratings": real_ratings,
                "simulated_ratings": simulated_ratings,
                "total_users": total_users
            },
            "cluster_profiles": cluster_profiles
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/users")
def get_admin_users():
    """Retrieve all users for admin dashboard with review counts and statuses"""
    try:
        from mining.mongodb_storage import db_storage
        if not db_storage.is_connected():
            raise HTTPException(status_code=503, detail="Database connection not available")
            
        raw_users = list(db_storage.db.users.find({}))
        users = []
        for u in raw_users:
            uid = str(u["_id"])
            username = u.get("username", "")
            
            # Extract creation date from ObjectId
            created_at = None
            if "_id" in u:
                created_at = u["_id"].generation_time.isoformat()
                
            # Count reviews in MongoDB user_ratings
            reviews_count = db_storage.db.user_ratings.count_documents({"user_id": username})
            
            users.append({
                "id": uid,
                "username": username,
                "email": u.get("email", ""),
                "full_name": u.get("full_name", ""),
                "role": u.get("role", "user"),
                "status": u.get("status", "active"),
                "created_at": created_at,
                "reviews_count": reviews_count
            })
            
        return {
            "success": True,
            "users": users
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/admin/users/{username}")
def delete_admin_user(username: str):
    """Delete a user account by username"""
    try:
        from mining.mongodb_storage import db_storage
        if not db_storage.is_connected():
            raise HTTPException(status_code=503, detail="Database connection not available")
        
        # Don't allow deleting the 'admin' account
        if username.lower() == 'admin':
            raise HTTPException(status_code=400, detail="Không thể xóa tài khoản Admin hệ thống.")
            
        res = db_storage.db.users.delete_one({"username": username})
        if res.deleted_count > 0:
            db_storage.db.user_ratings.delete_many({"user_id": username})
            db_storage.db.chat_sessions.delete_many({"user_id": username})
            return {"success": True, "message": f"Đã xóa tài khoản {username} thành công."}
        else:
            raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản cần xóa.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/ratings")
def get_admin_ratings(limit: int = 150):
    """Retrieves all user ratings from database"""
    try:
        from mining.mongodb_storage import db_storage
        ratings = []
        if db_storage.is_connected():
            limit = max(1, min(int(limit or 150), 2000))
            ratings = list(
                db_storage.db.user_ratings
                .find({}, {"_id": 0})
                .sort([("timestamp", -1), ("is_real", -1), ("rating", -1)])
                .limit(limit)
            )
        return {
            "success": True,
            "ratings": ratings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/rules")
def get_admin_rules():
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
def delete_admin_rating(user_id: str, destination_name: str):
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
def run_apriori_mining(params: AprioriParams):
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
def run_kmeans_clustering(params: ClusteringParams):
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
def refresh_cf_matrix():
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


@router.post("/admin/evaluate-system")
def evaluate_recommendation_system(k_values: Optional[str] = Query(default="5,10,20")):
    """
    Evaluate the hybrid recommendation system using standard metrics:
    - Precision@K, Recall@K, NDCG@K
    - MAP (Mean Average Precision)
    - RMSE, MAE (for rating prediction)
    - Coverage
    """
    try:
        from mining.evaluation_metrics import evaluator
        
        # Parse K values
        k_list = [int(k.strip()) for k in k_values.split(',')]
        
        # Split ratings into train/test
        split_success = evaluator.split_ratings(test_ratio=0.2, min_ratings_per_user=5)
        if not split_success:
            raise HTTPException(status_code=400, detail="Không đủ dữ liệu đánh giá để tính toán metrics")
        
        # Define recommendation function
        def get_recs(user_id, limit):
            return engine.get_recommendations(filters={}, limit=limit, user_id=user_id)
        
        # Run evaluation
        results = evaluator.evaluate_system(get_recs, k_values=k_list)
        
        return {
            "success": True,
            "metrics": results,
            "message": f"Đã đánh giá hệ thống với {results.get('users_evaluated', 0)} người dùng"
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/evaluation-metrics")
def get_current_evaluation_metrics():
    """
    Get cached evaluation metrics if available
    """
    try:
        from mining.mongodb_storage import db_storage
        
        # Try to get cached metrics from database
        if db_storage.is_connected():
            cached = db_storage.db.evaluation_metrics.find_one(
                {},
                sort=[("timestamp", -1)]
            )
            if cached:
                cached.pop('_id', None)
                return {
                    "success": True,
                    "metrics": cached,
                    "cached": True
                }
        
        return {
            "success": False,
            "message": "Chưa có metrics. Hãy chạy đánh giá hệ thống."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/reload-data")
def reload_engine_data():
    """Reload all data from MongoDB into the recommender engine"""
    try:
        engine.load_data()
        return {
            "success": True,
            "message": "Đã tải lại dữ liệu từ MongoDB thành công!",
            "destinations_count": len(engine.destinations)
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# IMAGE SERVICE ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/destinations/{destination_name}/fetch-image")
def fetch_destination_image(destination_name: str, country: str = Query(default=""), dest_type: str = Query(default="")):
    """Fetch real image for a destination from Unsplash/Wikimedia and update database"""
    try:
        image_service = get_image_service(db_storage)
        image_url = image_service.get_destination_image(destination_name, country, dest_type)
        
        if not image_url:
            raise HTTPException(status_code=404, detail="No image found for this destination")
        
        # Update in database
        collection = db_storage.db["destinations"]
        result = collection.update_one(
            {"Destination Name": destination_name},
            {"$set": {"image": image_url}}
        )
        
        return {
            "success": True,
            "destination": destination_name,
            "image_url": image_url,
            "updated": result.modified_count > 0
        }
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/update-all-images")
async def update_all_images(mode: str = Query(default="missing", regex="^(all|missing)$")):
    """
    Trigger batch update of destination images
    - mode='missing': Only update destinations without images
    - mode='all': Update all destinations
    """
    try:
        import asyncio
        from mining.update_destination_images import update_missing_images_only, update_all_destination_images
        
        # Run in background to avoid timeout
        if mode == "all":
            asyncio.create_task(asyncio.to_thread(update_all_destination_images))
            message = "Đang cập nhật hình ảnh cho tất cả địa điểm. Quá trình này có thể mất vài phút..."
        else:
            asyncio.create_task(asyncio.to_thread(update_missing_images_only))
            message = "Đang cập nhật hình ảnh cho các địa điểm chưa có hình. Quá trình này có thể mất vài phút..."
        
        return {
            "success": True,
            "message": message,
            "mode": mode
        }
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# ADDITIONAL ADMIN DASHBOARD CRUD & UTILITIES ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

class DestinationModel(BaseModel):
    destination_name: str
    country: str
    continent: Optional[str] = "Asia"
    type: str
    avg_cost: float
    best_season: str
    cost_category: str
    description: Optional[str] = ""
    image: Optional[str] = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None

@router.get("/admin/clustering/elbow")
def get_clustering_elbow():
    """Retrieve SSE values for K from 1 to 10 for the Elbow Method"""
    try:
        from mining.clustering import get_elbow_data
        sse_dict = get_elbow_data(max_k=10)
        return {
            "success": True,
            "sse": sse_dict
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/destinations")
def add_destination(dest: DestinationModel):
    """Add a new destination to MongoDB and reload engine"""
    try:
        from mining.mongodb_storage import db_storage
        if not db_storage.is_connected():
            raise HTTPException(status_code=503, detail="Database connection not available")
            
        dest_name = dest.destination_name.strip()
        if not dest_name:
            raise HTTPException(status_code=400, detail="Tên điểm đến không được để trống.")
            
        # Check if already exists
        existing = db_storage.db.destinations.find_one({"Destination Name": dest_name})
        if existing:
            raise HTTPException(status_code=400, detail=f"Điểm đến '{dest_name}' đã tồn tại trong hệ thống.")
            
        doc = {
            "Destination Name": dest_name,
            "Country": dest.country.strip(),
            "Continent": dest.continent.strip() if dest.continent else "Asia",
            "Type": dest.type.strip(),
            "Avg Cost (USD/day)": float(dest.avg_cost),
            "Best Season": dest.best_season.strip(),
            "Cost_Category": dest.cost_category.strip(),
            "Description": dest.description.strip() if dest.description else "",
            "image": dest.image.strip() if dest.image else "",
            "destination_latitude": float(dest.latitude) if dest.latitude is not None else None,
            "destination_longitude": float(dest.longitude) if dest.longitude is not None else None,
            "Avg Rating": 3.0,
            "Annual Visitors (M)": 1.0,
            "UNESCO Site": "No",
            "Cluster": 0
        }
        
        db_storage.db.destinations.insert_one(doc)
        engine.load_data()
        
        return {
            "success": True,
            "message": f"Đã thêm điểm đến '{dest_name}' thành công.",
            "destination": {k: v for k, v in doc.items() if k != "_id"}
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/admin/destinations/{original_name}")
def update_destination(original_name: str, dest: DestinationModel):
    """Update destination details and reload engine"""
    try:
        from mining.mongodb_storage import db_storage
        if not db_storage.is_connected():
            raise HTTPException(status_code=503, detail="Database connection not available")
            
        existing = db_storage.db.destinations.find_one({"Destination Name": original_name})
        if not existing:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy điểm đến '{original_name}' để cập nhật.")
            
        new_name = dest.destination_name.strip()
        if new_name != original_name:
            collide = db_storage.db.destinations.find_one({"Destination Name": new_name})
            if collide:
                raise HTTPException(status_code=400, detail=f"Tên điểm đến mới '{new_name}' đã tồn tại.")
                
        update_fields = {
            "Destination Name": new_name,
            "Country": dest.country.strip(),
            "Continent": dest.continent.strip() if dest.continent else "Asia",
            "Type": dest.type.strip(),
            "Avg Cost (USD/day)": float(dest.avg_cost),
            "Best Season": dest.best_season.strip(),
            "Cost_Category": dest.cost_category.strip(),
            "Description": dest.description.strip() if dest.description else "",
            "image": dest.image.strip() if dest.image else "",
            "destination_latitude": float(dest.latitude) if dest.latitude is not None else None,
            "destination_longitude": float(dest.longitude) if dest.longitude is not None else None
        }
        
        db_storage.db.destinations.update_one(
            {"Destination Name": original_name},
            {"$set": update_fields}
        )
        engine.load_data()
        
        return {
            "success": True,
            "message": f"Đã cập nhật điểm đến '{new_name}' thành công."
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/admin/destinations/{destination_name}")
def delete_destination(destination_name: str):
    """Delete a destination and reload engine"""
    try:
        from mining.mongodb_storage import db_storage
        if not db_storage.is_connected():
            raise HTTPException(status_code=503, detail="Database connection not available")
            
        res = db_storage.db.destinations.delete_one({"Destination Name": destination_name})
        if res.deleted_count > 0:
            engine.load_data()
            return {"success": True, "message": f"Đã xóa điểm đến '{destination_name}' thành công."}
        else:
            raise HTTPException(status_code=404, detail="Không tìm thấy điểm đến cần xóa.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/destinations/{destination_name}/upload-image")
async def upload_destination_image(destination_name: str, request: Request, file: UploadFile = File(...)):
    """Upload image for a destination, save locally under static/uploads/ and return absolute URL"""
    try:
        from mining.mongodb_storage import db_storage
        import uuid
        import shutil
        
        if not db_storage.is_connected():
            raise HTTPException(status_code=503, detail="Database connection not available")
            
        dest = db_storage.db.destinations.find_one({"Destination Name": destination_name})
        if not dest:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy điểm đến '{destination_name}'.")
            
        # Define upload directories relative to backend root
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        static_dir = os.path.join(backend_dir, "static")
        uploads_dir = os.path.join(static_dir, "uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Save file with unique filename
        file_ext = os.path.splitext(file.filename)[1] or ".jpg"
        safe_name = "".join([c if c.isalnum() else "_" for c in destination_name.lower()])
        new_filename = f"{safe_name}_{uuid.uuid4().hex[:8]}{file_ext}"
        file_path = os.path.join(uploads_dir, new_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Get absolute request URL
        base_url = str(request.base_url)
        image_url = f"{base_url}static/uploads/{new_filename}"
        
        db_storage.db.destinations.update_one(
            {"Destination Name": destination_name},
            {"$set": {"image": image_url}}
        )
        engine.load_data()
        
        return {
            "success": True,
            "message": "Upload hình ảnh thành công.",
            "image_url": image_url
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/admin/destinations/{destination_name}/image")
def delete_destination_image(destination_name: str):
    """Reset destination image field to empty"""
    try:
        from mining.mongodb_storage import db_storage
        if not db_storage.is_connected():
            raise HTTPException(status_code=503, detail="Database connection not available")
            
        dest = db_storage.db.destinations.find_one({"Destination Name": destination_name})
        if not dest:
            raise HTTPException(status_code=404, detail="Không tìm thấy điểm đến.")
            
        db_storage.db.destinations.update_one(
            {"Destination Name": destination_name},
            {"$set": {"image": ""}}
        )
        engine.load_data()
        
        return {
            "success": True,
            "message": "Đã xóa ảnh điểm đến."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/admin/users/{username}/toggle-lock")
def toggle_user_lock(username: str):
    """Toggle lock status of user account"""
    try:
        from mining.mongodb_storage import db_storage
        if not db_storage.is_connected():
            raise HTTPException(status_code=503, detail="Database connection not available")
            
        if username.lower() == 'admin':
            raise HTTPException(status_code=400, detail="Không thể khóa tài khoản Admin hệ thống.")
            
        user = db_storage.db.users.find_one({"username": username})
        if not user:
            raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
            
        current_status = user.get("status", "active")
        new_status = "locked" if current_status == "active" else "active"
        
        db_storage.db.users.update_one(
            {"username": username},
            {"$set": {"status": new_status}}
        )
        
        return {
            "success": True,
            "message": f"Đã {'khóa' if new_status == 'locked' else 'mở khóa'} tài khoản {username} thành công.",
            "status": new_status
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

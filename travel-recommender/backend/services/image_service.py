# -*- coding: utf-8 -*-
"""
image_service.py
================
Service để lấy hình ảnh cho các địa điểm du lịch từ:
1. Cache trong MongoDB
2. Fallback images (hardcoded URLs theo country + type)
"""

from typing import Optional
from .fallback_images import get_fallback_image


class ImageService:
    """Service lấy và cache hình ảnh cho địa điểm du lịch"""
    
    def __init__(self, db_storage=None):
        self.db_storage = db_storage
        self.cache = {}  # In-memory cache
    
    def get_destination_image(self, destination_name: str, country: str = "", dest_type: str = "") -> str:
        """
        Lấy URL hình ảnh cho địa điểm
        
        Args:
            destination_name: Tên địa điểm
            country: Tên quốc gia
            dest_type: Loại du lịch (Beach, Mountain, Cultural...)
            
        Returns:
            URL hình ảnh (luôn trả về URL)
        """
        # Check memory cache
        cache_key = f"{destination_name}_{country}_{dest_type}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Check MongoDB cache
        if self.db_storage:
            cached_image = self._get_from_db_cache(destination_name, country)
            if cached_image:
                self.cache[cache_key] = cached_image
                return cached_image
        
        # Sử dụng fallback image (hardcoded URL dựa trên country + type)
        image_url = get_fallback_image(country, dest_type, destination_name)
        
        # Cache result
        if image_url and self.db_storage:
            self._save_to_db_cache(destination_name, country, image_url)
            self.cache[cache_key] = image_url
        
        return image_url
    
    def _get_from_db_cache(self, destination_name: str, country: str) -> Optional[str]:
        """Lấy hình từ MongoDB cache"""
        try:
            if not self.db_storage or self.db_storage.db is None:
                return None
            
            cache_collection = self.db_storage.db["image_cache"]
            cached = cache_collection.find_one({
                "destination_name": destination_name,
                "country": country
            })
            
            if cached and cached.get("image_url"):
                return cached["image_url"]
        
        except Exception as e:
            print(f"[ERROR] DB cache read failed: {e}")
        
        return None
    
    def _save_to_db_cache(self, destination_name: str, country: str, image_url: str):
        """Lưu hình vào MongoDB cache"""
        try:
            if not self.db_storage or self.db_storage.db is None:
                return
            
            cache_collection = self.db_storage.db["image_cache"]
            cache_collection.update_one(
                {
                    "destination_name": destination_name,
                    "country": country
                },
                {
                    "$set": {
                        "destination_name": destination_name,
                        "country": country,
                        "image_url": image_url
                    }
                },
                upsert=True
            )
        
        except Exception as e:
            print(f"[ERROR] DB cache write failed: {e}")


# Singleton instance
_image_service_instance = None

def get_image_service(db_storage=None):
    """Get singleton instance of ImageService"""
    global _image_service_instance
    if _image_service_instance is None:
        _image_service_instance = ImageService(db_storage)
    return _image_service_instance

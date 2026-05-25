# -*- coding: utf-8 -*-
"""
Test if server can start
"""
import sys
from pathlib import Path

print("[TEST] Testing imports...")

try:
    from mining.hybrid_recommender import recommender
    print("[OK] Recommender imported")
except Exception as e:
    print(f"[ERROR] Failed to import recommender: {e}")
    sys.exit(1)

try:
    from api.routes import router
    print("[OK] API routes imported")
except Exception as e:
    print(f"[ERROR] Failed to import routes: {e}")
    sys.exit(1)

try:
    from fastapi import FastAPI
    print("[OK] FastAPI imported")
except Exception as e:
    print(f"[ERROR] Failed to import FastAPI: {e}")
    sys.exit(1)

print("\n[SUCCESS] All imports successful!")
print("[INFO] You can now run: python main.py")

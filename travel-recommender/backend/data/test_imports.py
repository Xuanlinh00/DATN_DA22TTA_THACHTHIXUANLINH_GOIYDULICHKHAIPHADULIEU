#!/usr/bin/env python3
"""Test imports cho notebook phân tích dữ liệu"""

print("Đang kiểm tra các thư viện...")
print("="*50)

try:
    import pandas as pd
    print("✅ pandas:", pd.__version__)
except ImportError as e:
    print("❌ pandas:", e)

try:
    import numpy as np
    print("✅ numpy:", np.__version__)
except ImportError as e:
    print("❌ numpy:", e)

try:
    import matplotlib
    print("✅ matplotlib:", matplotlib.__version__)
except ImportError as e:
    print("❌ matplotlib:", e)

try:
    import seaborn as sns
    print("✅ seaborn:", sns.__version__)
except ImportError as e:
    print("❌ seaborn:", e)

try:
    from sklearn import __version__ as sk_version
    print("✅ scikit-learn:", sk_version)
except ImportError as e:
    print("❌ scikit-learn:", e)

try:
    import mlxtend
    print("✅ mlxtend:", mlxtend.__version__)
except ImportError as e:
    print("❌ mlxtend:", e)

print("="*50)
print("Kiểm tra hoàn tất!")

# Kiểm tra Python path
import sys
print(f"\nPython executable: {sys.executable}")
print(f"Python version: {sys.version}")

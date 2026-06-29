import pandas as pd
from pathlib import Path
import sys

# Set encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

processed_dir = Path("c:/datn/travel-recommender/backend/data/processed")
csv_path = processed_dir / "poi_clean.csv"
xlsx_path = processed_dir / "poi_clean.xlsx"

if not csv_path.exists():
    print(f"[LỖI] Không tìm thấy file csv tại {csv_path}")
    sys.exit(1)

print("📂 Đang tải dữ liệu từ CSV...")
df = pd.read_csv(csv_path)

# Drop the index column if it's Unnamed: 0
if 'Unnamed: 0' in df.columns:
    df = df.drop(columns=['Unnamed: 0'])

print("💾 Đang xuất ra file Excel (.xlsx)...")
try:
    # Try using default openpyxl
    df.to_excel(xlsx_path, index=False)
    print(f"✅ Đã lưu file Excel thành công tại: {xlsx_path}")
except Exception as e:
    print(f"⚠️ Không thể lưu mặc định, có thể thiếu thư viện openpyxl. Đang thử cài đặt openpyxl...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "openpyxl"], capture_output=True)
    df.to_excel(xlsx_path, index=False)
    print(f"✅ Đã tự cài đặt thư viện và lưu file Excel thành công tại: {xlsx_path}")

import pandas as pd
import os
from pathlib import Path

processed_dir = Path("backend/data/processed")

for file in os.listdir(processed_dir):
    if file.endswith('.csv'):
        file_path = processed_dir / file
        try:
            df = pd.read_csv(file_path, nrows=3)
            full_df = pd.read_csv(file_path)
            print(f"\n==================================================")
            print(f"FILE: {file}")
            print(f"Shape: {full_df.shape}")
            print(f"Columns: {list(full_df.columns)}")
            print("Sample data (first row):")
            print(full_df.head(1).to_dict('records'))
        except Exception as e:
            print(f"Error reading {file}: {e}")

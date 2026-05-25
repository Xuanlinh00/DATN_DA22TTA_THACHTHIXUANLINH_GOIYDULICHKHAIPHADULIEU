# -*- coding: utf-8 -*-
"""
Data preprocessing module - loads and prepares data from CSV files
"""
import pandas as pd
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"

def load_destinations():
    """Load destinations from CSV"""
    try:
        df = pd.read_csv(DATA_DIR / "destinations_clustered.csv")
        print(f"[OK] Loaded {len(df)} destinations")
        return df
    except Exception as e:
        print(f"[ERROR] Error loading destinations: {e}")
        return pd.DataFrame()

def load_rules():
    """Load association rules from CSV"""
    try:
        df = pd.read_csv(DATA_DIR / "all_rules.csv")
        print(f"[OK] Loaded {len(df)} rules")
        return df
    except Exception as e:
        print(f"[ERROR] Error loading rules: {e}")
        return pd.DataFrame()

def load_cluster_profiles():
    """Load cluster profiles from CSV"""
    try:
        df = pd.read_csv(DATA_DIR / "cluster_profiles.csv")
        print(f"[OK] Loaded {len(df)} cluster profiles")
        return df
    except Exception as e:
        print(f"[ERROR] Error loading cluster profiles: {e}")
        return pd.DataFrame()

def get_data_summary():
    """Get summary of available data"""
    destinations = load_destinations()
    rules = load_rules()
    clusters = load_cluster_profiles()
    
    return {
        "destinations_count": len(destinations),
        "rules_count": len(rules),
        "clusters_count": len(clusters),
        "countries": destinations['Country'].unique().tolist() if not destinations.empty else [],
        "types": destinations['Type'].unique().tolist() if not destinations.empty else []
    }

if __name__ == "__main__":
    print("[INFO] Data Summary:")
    summary = get_data_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")

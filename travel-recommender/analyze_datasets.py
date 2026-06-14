
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import sys
import io

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def section(title):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)

# ========================================
# 1. TOURIST DESTINATIONS DATASET (Raw)
# ========================================
section("1. TOURIST DESTINATIONS DATASET (Raw)")
df_dest = pd.read_csv(r'backend\data\raw\Tourist_Destinations.csv')
print(f"Shape: {df_dest.shape}")
print(f"Columns: {list(df_dest.columns)}")
print(f"\nCountry count: {df_dest['Country'].nunique()}")
print(f"Continent count: {df_dest['Continent'].nunique()}")
print("\nContinent distribution:")
print(df_dest['Continent'].value_counts().to_string())
print("\nType distribution:")
print(df_dest['Type'].value_counts().to_string())
print("\nBest Season distribution:")
print(df_dest['Best Season'].value_counts().to_string())
print("\nUNESCO Site distribution:")
print(df_dest['UNESCO Site'].value_counts().to_string())
print("\nAvg Cost (USD/day) stats:")
print(df_dest['Avg Cost (USD/day)'].describe().to_string())
print("\nAvg Rating stats:")
print(df_dest['Avg Rating'].describe().to_string())
print("\nAnnual Visitors (M) stats:")
print(df_dest['Annual Visitors (M)'].describe().to_string())

# ========================================
# 2. DESTINATIONS CLEAN (PROCESSED)
# ========================================
section("2. DESTINATIONS CLEAN (PROCESSED)")
df_clean = pd.read_csv(r'backend\data\processed\destinations_clean.csv')
print(f"Shape: {df_clean.shape}")
print(f"Columns:")
for c in df_clean.columns:
    print(f"  - {c}")
print(f"\nNull counts:")
null_cols = df_clean.isnull().sum()
print(null_cols[null_cols > 0].to_string())
if 'Cluster' in df_clean.columns:
    print("\nCluster distribution:")
    print(df_clean['Cluster'].value_counts().to_string())
if 'Cost_Category' in df_clean.columns:
    print("\nCost_Category distribution:")
    print(df_clean['Cost_Category'].value_counts().to_string())
if 'destination_budget_level' in df_clean.columns:
    print("\ndestination_budget_level distribution:")
    print(df_clean['destination_budget_level'].value_counts().to_string())

# ========================================
# 3. GLOBAL HOLIDAYS DATASET
# ========================================
section("3. GLOBAL HOLIDAYS 2025-2035 DATASET")
df_hol = pd.read_csv(r'backend\data\raw\Global_Holidays_2025_2035.csv')
print(f"Shape: {df_hol.shape}")
print(f"Columns: {list(df_hol.columns)}")
print("\nNull counts:")
print(df_hol.isnull().sum().to_string())
for col in df_hol.columns:
    if df_hol[col].dtype == object:
        unique = df_hol[col].nunique()
        print(f"\n  Column '{col}': {unique} unique values, top 5:")
        print(df_hol[col].value_counts().head(5).to_string())
    else:
        print(f"\n  Column '{col}' (numeric): min={df_hol[col].min()}, max={df_hol[col].max()}")

# ========================================
# 4. POI CLEAN
# ========================================
section("4. POI CLEAN (Points of Interest)")
df_poi = pd.read_csv(r'backend\data\processed\poi_clean.csv')
print(f"Shape: {df_poi.shape}")
print(f"Columns: {list(df_poi.columns)}")
print("\nNull counts:")
null_poi = df_poi.isnull().sum()
print(null_poi[null_poi > 0].to_string())
for col in df_poi.columns:
    if df_poi[col].dtype == object:
        unique = df_poi[col].nunique()
        if unique < 50:
            print(f"\n  Column '{col}': {unique} unique values")
            print(df_poi[col].value_counts().head(10).to_string())
        else:
            print(f"\n  Column '{col}': {unique} unique values (high cardinality)")
    else:
        print(f"\n  Column '{col}' (numeric): {df_poi[col].describe().to_dict()}")

# ========================================
# 5. TRANSACTIONS (Apriori)
# ========================================
section("5. TRANSACTIONS DATASET (Apriori Mining)")
df_trans = pd.read_csv(r'backend\data\processed\transactions.csv')
print(f"Shape: {df_trans.shape}")
print(f"Columns: {list(df_trans.columns)}")
print("\nFirst 3 rows:")
for i, row in df_trans.head(3).iterrows():
    print(f"  Row {i}: {dict(row)}")
print("\nNull counts:")
print(df_trans.isnull().sum().to_string())

# ========================================
# 6. ASSOCIATION RULES
# ========================================
section("6. ASSOCIATION RULES (Apriori Results)")
df_rules = pd.read_csv(r'backend\data\processed\travel_rules.csv')
print(f"Shape: {df_rules.shape}")
print(f"Columns: {list(df_rules.columns)}")
print("\nFirst 5 rules:")
for i, row in df_rules.head(5).iterrows():
    print(f"  {dict(row)}")
print("\nNumeric stats:")
print(df_rules.describe().to_string())

# ========================================
# 7. CLUSTER PROFILES
# ========================================
section("7. CLUSTER PROFILES (K-Means)")
df_cl = pd.read_csv(r'backend\data\processed\cluster_profiles.csv')
print(f"Shape: {df_cl.shape}")
print(f"Columns: {list(df_cl.columns)}")
print("\nAll cluster data:")
for i, row in df_cl.iterrows():
    print(f"  {dict(row)}")

# ========================================
# 8. OFFERINGS (TripAdvisor Raw)
# ========================================
section("8. OFFERINGS DATASET (TripAdvisor)")
try:
    df_off = pd.read_csv(r'backend\data\raw\offerings.csv')
    print(f"Shape: {df_off.shape}")
    print(f"Columns: {list(df_off.columns)}")
    print("\nNull counts:")
    print(df_off.isnull().sum().to_string())
    for col in df_off.columns:
        if df_off[col].dtype == object:
            unique = df_off[col].nunique()
            if unique < 50:
                print(f"\n  Column '{col}': {unique} unique values")
                print(df_off[col].value_counts().head(10).to_string())
except Exception as e:
    print(f"Error: {e}")

# ========================================
# 9. REVIEWS (TripAdvisor) - Sample only
# ========================================
section("9. REVIEWS DATASET (TripAdvisor) - 1000 row sample")
try:
    df_rev = pd.read_csv(r'backend\data\raw\reviews.csv', nrows=1000)
    print(f"File size: ~968MB | Reading first 1000 rows for analysis")
    print(f"Columns: {list(df_rev.columns)}")
    print("\nNull counts (sample):")
    print(df_rev.isnull().sum().to_string())
    for col in df_rev.columns:
        if df_rev[col].dtype == object:
            unique = df_rev[col].nunique()
            print(f"\n  Column '{col}': {unique} unique values in sample")
            print(df_rev[col].value_counts().head(5).to_string())
        else:
            print(f"\n  Column '{col}' (numeric): {df_rev[col].describe().to_dict()}")
except Exception as e:
    print(f"Error reading reviews.csv: {e}")

# ========================================
# 10. COUNTRY-SPECIFIC CLEANED DATA
# ========================================
for country in ['India', 'Iran', 'USA']:
    section(f"10. CLEANED DATA - {country}")
    try:
        df_c = pd.read_csv(f'backend/data/raw/cleaned_data_{country}.csv')
        print(f"Shape: {df_c.shape}")
        print(f"Columns: {list(df_c.columns)}")
        print("\nNull counts:")
        null_c = df_c.isnull().sum()
        print(null_c[null_c > 0].to_string() if null_c.sum() > 0 else "No nulls")
        for col in df_c.columns:
            if df_c[col].dtype == object:
                unique = df_c[col].nunique()
                if unique < 30:
                    print(f"\n  Column '{col}': {unique} unique values")
                    print(df_c[col].value_counts().head(5).to_string())
                else:
                    print(f"\n  Column '{col}': {unique} unique values (high cardinality)")
            else:
                print(f"\n  Column '{col}' (numeric): min={df_c[col].min():.2f}, max={df_c[col].max():.2f}, mean={df_c[col].mean():.2f}")
    except Exception as e:
        print(f"Error: {e}")

print()
print("=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)

# -*- coding: utf-8 -*-
"""
Recommender Engine - Main recommendation logic
"""
import pandas as pd
from pathlib import Path

class RecommenderEngine:
    def __init__(self):
        self.data_dir = Path(__file__).parent / "data" / "processed"
        self.destinations = None
        self.load_data()
    
    def load_data(self):
        """Load destinations data"""
        try:
            csv_path = self.data_dir / "destinations_clustered.csv"
            self.destinations = pd.read_csv(csv_path)
            print(f"[OK] Loaded {len(self.destinations)} destinations")
        except Exception as e:
            print(f"[ERROR] Failed to load data: {e}")
            self.destinations = pd.DataFrame()
    
    def filter_destinations(self, season=None, budget=None, category=None, country=None):
        """Filter destinations by criteria"""
        if self.destinations is None or self.destinations.empty:
            return pd.DataFrame()
        
        df = self.destinations.copy()
        
        if season:
            df = df[df['Best Season'].str.contains(season, case=False, na=False)]
        
        if budget:
            df = df[df['Cost_Category'].str.contains(budget, case=False, na=False)]
        
        if category:
            df = df[df['Type'].str.contains(category, case=False, na=False)]
        
        if country:
            df = df[df['Country'].str.contains(country, case=False, na=False)]
        
        return df
    
    def get_recommendations(self, filters=None, limit=10):
        """Get recommendations"""
        if filters is None:
            filters = {}
        
        results = self.filter_destinations(
            season=filters.get('season'),
            budget=filters.get('budget'),
            category=filters.get('category'),
            country=filters.get('country')
        )
        
        if 'Avg Rating' in results.columns:
            results = results.sort_values('Avg Rating', ascending=False)
        
        # Replace NaN with None for JSON serialization
        results = results.fillna('')
        
        return results.head(limit).to_dict('records')
    
    def search(self, query, limit=10):
        """Search destinations"""
        if self.destinations is None or self.destinations.empty:
            return []
        
        df = self.destinations.copy()
        mask = df['Destination Name'].str.contains(query, case=False, na=False)
        results = df[mask]
        
        if 'Avg Rating' in results.columns:
            results = results.sort_values('Avg Rating', ascending=False)
        
        # Replace NaN with None for JSON serialization
        results = results.fillna('')
        
        return results.head(limit).to_dict('records')
    
    def get_similar(self, destination_name, limit=5):
        """Get similar destinations"""
        if self.destinations is None or self.destinations.empty:
            return []
        
        try:
            dest = self.destinations[self.destinations['Destination Name'] == destination_name]
            if dest.empty:
                return []
            
            cluster_id = dest.iloc[0]['Cluster']
            similar = self.destinations[
                (self.destinations['Cluster'] == cluster_id) &
                (self.destinations['Destination Name'] != destination_name)
            ]
            
            if 'Avg Rating' in similar.columns:
                similar = similar.sort_values('Avg Rating', ascending=False)
            
            # Replace NaN with None for JSON serialization
            similar = similar.fillna('')
            
            return similar.head(limit).to_dict('records')
        except Exception as e:
            print(f"[ERROR] get_similar failed: {e}")
            return []

# Create global instance
engine = RecommenderEngine()

if __name__ == "__main__":
    print("[TEST] Testing Recommender Engine...")
    results = engine.get_recommendations({'season': 'Spring'}, limit=3)
    print(f"[RESULT] Found {len(results)} destinations")
    for r in results:
        print(f"  - {r.get('Destination Name')} ({r.get('Country')})")

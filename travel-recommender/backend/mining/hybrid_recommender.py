# -*- coding: utf-8 -*-
"""
Hybrid Recommender System - combines multiple recommendation strategies
"""
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"

class HybridRecommender:
    def __init__(self):
        self.destinations = None
        self.rules = None
        self.clusters = None
        self.load_data()
    
    def load_data(self):
        """Load all necessary data"""
        try:
            self.destinations = pd.read_csv(DATA_DIR / "destinations_clustered.csv")
            self.rules = pd.read_csv(DATA_DIR / "all_rules.csv")
            self.clusters = pd.read_csv(DATA_DIR / "cluster_profiles.csv")
            print("[OK] Hybrid Recommender initialized")
        except Exception as e:
            print(f"[ERROR] Error loading data: {e}")
    
    def filter_by_preferences(self, season=None, budget=None, category=None, country=None):
        """Filter destinations by user preferences"""
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
        """Get recommendations based on filters"""
        if filters is None:
            filters = {}
        
        # Apply filters
        results = self.filter_by_preferences(
            season=filters.get('season'),
            budget=filters.get('budget'),
            category=filters.get('category'),
            country=filters.get('country')
        )
        
        # Sort by rating
        if 'Avg Rating' in results.columns:
            results = results.sort_values('Avg Rating', ascending=False)
        
        # Limit results
        results = results.head(limit)
        
        # Convert to dict
        return results.to_dict('records')
    
    def get_similar_destinations(self, destination_name, limit=5):
        """Find similar destinations based on cluster"""
        try:
            # Find the destination
            dest = self.destinations[self.destinations['Destination Name'] == destination_name]
            if dest.empty:
                return []
            
            cluster_id = dest.iloc[0]['Cluster']
            
            # Find destinations in same cluster
            similar = self.destinations[
                (self.destinations['Cluster'] == cluster_id) &
                (self.destinations['Destination Name'] != destination_name)
            ]
            
            # Sort by rating
            if 'Avg Rating' in similar.columns:
                similar = similar.sort_values('Avg Rating', ascending=False)
            
            return similar.head(limit).to_dict('records')
        except Exception as e:
            print(f"Error finding similar destinations: {e}")
            return []
    
    def get_seasonal_recommendations(self, season, limit=6):
        """Get top recommendations for a specific season"""
        results = self.filter_by_preferences(season=season)
        
        if 'Avg Rating' in results.columns:
            results = results.sort_values('Avg Rating', ascending=False)
        
        return results.head(limit).to_dict('records')
    
    def search_destinations(self, query, limit=10):
        """Search destinations by name"""
        df = self.destinations.copy()
        
        # Search in Destination Name column
        mask = df['Destination Name'].str.contains(query, case=False, na=False)
        results = df[mask]
        
        if 'Avg Rating' in results.columns:
            results = results.sort_values('Avg Rating', ascending=False)
        
        return results.head(limit).to_dict('records')

# Global instance
recommender = HybridRecommender()

if __name__ == "__main__":
    print("[TEST] Testing Hybrid Recommender...")
    
    # Test filtering
    results = recommender.get_recommendations({'season': 'Spring'}, limit=5)
    print(f"\n[RESULT] Spring destinations: {len(results)}")
    for r in results[:3]:
        print(f"  - {r.get('Destination Name', 'N/A')} ({r.get('Country', 'N/A')})")

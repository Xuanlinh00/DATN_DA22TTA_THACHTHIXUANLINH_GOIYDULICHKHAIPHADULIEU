# -*- coding: utf-8 -*-
"""
MongoDB Storage Module - Manages MongoDB connections and data persistence.
"""
import os
import sys
import pandas as pd
import numpy as np
from pymongo import MongoClient
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "travel_recommender")

class MongoDBStorage:
    def __init__(self, uri=MONGO_URI, db_name=DB_NAME):
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.db = None
        self.connect()

    def connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            # Force a connection check
            self.client.server_info()
            self.db = self.client[self.db_name]
            print(f"[OK] Connected to MongoDB at {self.uri}, Database: {self.db_name}")
        except Exception as e:
            print(f"[ERROR] Failed to connect to MongoDB: {e}")
            self.client = None
            self.db = None

    def is_connected(self):
        return self.db is not None

    def clean_records(self, df):
        """Convert DataFrame to list of dicts, replacing NaN values with None (null in MongoDB)"""
        # Replace NaN with None for BSON/JSON compliance
        clean_df = df.astype(object).where(pd.notnull(df), None)
        return clean_df.to_dict(orient="records")

    # Destination Operations
    def save_destinations(self, df_or_list):
        if not self.is_connected():
            return False
        try:
            self.db.destinations.drop()
            records = df_or_list if isinstance(df_or_list, list) else self.clean_records(df_or_list)
            if records:
                import copy
                self.db.destinations.insert_many(copy.deepcopy(records))
            print(f"[OK] Saved {len(records)} destinations to MongoDB")
            return True
        except Exception as e:
            print(f"[ERROR] save_destinations failed: {e}")
            return False

    def load_destinations(self):
        if not self.is_connected():
            return []
        try:
            return list(self.db.destinations.find({}, {"_id": 0}))
        except Exception as e:
            print(f"[ERROR] load_destinations failed: {e}")
            return []

    # Rules Operations
    def save_rules(self, df_or_list):
        if not self.is_connected():
            return False
        try:
            self.db.rules.drop()
            records = df_or_list if isinstance(df_or_list, list) else self.clean_records(df_or_list)
            if records:
                import copy
                self.db.rules.insert_many(copy.deepcopy(records))
            print(f"[OK] Saved {len(records)} association rules to MongoDB")
            return True
        except Exception as e:
            print(f"[ERROR] save_rules failed: {e}")
            return False

    def load_rules(self):
        if not self.is_connected():
            return []
        try:
            return list(self.db.rules.find({}, {"_id": 0}))
        except Exception as e:
            print(f"[ERROR] load_rules failed: {e}")
            return []

    # Cluster Profiles Operations
    def save_cluster_profiles(self, df_or_list):
        if not self.is_connected():
            return False
        try:
            self.db.cluster_profiles.drop()
            records = df_or_list if isinstance(df_or_list, list) else self.clean_records(df_or_list)
            if records:
                import copy
                self.db.cluster_profiles.insert_many(copy.deepcopy(records))
            print(f"[OK] Saved {len(records)} cluster profiles to MongoDB")
            return True
        except Exception as e:
            print(f"[ERROR] save_cluster_profiles failed: {e}")
            return False

    def load_cluster_profiles(self):
        if not self.is_connected():
            return []
        try:
            return list(self.db.cluster_profiles.find({}, {"_id": 0}))
        except Exception as e:
            print(f"[ERROR] load_cluster_profiles failed: {e}")
            return []

    # Transactions Operations
    def save_transactions(self, df_or_list):
        if not self.is_connected():
            return False
        try:
            self.db.transactions.drop()
            records = df_or_list if isinstance(df_or_list, list) else self.clean_records(df_or_list)
            if records:
                self.db.transactions.insert_many(records)
            print(f"[OK] Saved {len(records)} transactions to MongoDB")
            return True
        except Exception as e:
            print(f"[ERROR] save_transactions failed: {e}")
            return False

    def load_transactions(self):
        if not self.is_connected():
            return []
        try:
            return list(self.db.transactions.find({}, {"_id": 0}))
        except Exception as e:
            print(f"[ERROR] load_transactions failed: {e}")
            return []

    # Holidays Operations
    def save_holidays(self, df_or_list):
        if not self.is_connected():
            return False
        try:
            self.db.holidays.drop()
            records = df_or_list if isinstance(df_or_list, list) else self.clean_records(df_or_list)
            if records:
                self.db.holidays.insert_many(records)
            print(f"[OK] Saved {len(records)} holidays to MongoDB")
            return True
        except Exception as e:
            print(f"[ERROR] save_holidays failed: {e}")
            return False

    def load_holidays(self, country_code=None):
        if not self.is_connected():
            return []
        try:
            query = {"Country": country_code} if country_code else {}
            return list(self.db.holidays.find(query, {"_id": 0}))
        except Exception as e:
            print(f"[ERROR] load_holidays failed: {e}")
            return []

    # Points of Interest Operations
    def save_poi(self, df_or_list):
        if not self.is_connected():
            return False
        try:
            self.db.poi.drop()
            records = df_or_list if isinstance(df_or_list, list) else self.clean_records(df_or_list)
            if records:
                self.db.poi.insert_many(records)
            print(f"[OK] Saved {len(records)} POIs to MongoDB")
            return True
        except Exception as e:
            print(f"[ERROR] save_poi failed: {e}")
            return False

    def load_poi(self, city=None):
        if not self.is_connected():
            return []
        try:
            query = {"city": city} if city else {}
            return list(self.db.poi.find(query, {"_id": 0}))
        except Exception as e:
            print(f"[ERROR] load_poi failed: {e}")
            return []

    # Chat Sessions Operations
    def save_chat_session(self, session_id: str, user_id: str, title: str, messages: list):
        if not self.is_connected():
            return False
        try:
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            self.db.chat_sessions.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "session_id": session_id,
                        "user_id": user_id,
                        "title": title,
                        "messages": messages,
                        "updated_at": now
                    },
                    "$setOnInsert": {
                        "created_at": now
                    }
                },
                upsert=True
            )
            return True
        except Exception as e:
            print(f"[ERROR] save_chat_session failed: {e}")
            return False

    def load_chat_sessions(self, user_id: str):
        if not self.is_connected():
            return []
        try:
            # Sort by updated_at descending
            sessions = list(self.db.chat_sessions.find({"user_id": user_id}, {"_id": 0}).sort("updated_at", -1))
            return sessions
        except Exception as e:
            print(f"[ERROR] load_chat_sessions failed: {e}")
            return []

    def load_chat_session(self, session_id: str):
        if not self.is_connected():
            return None
        try:
            return self.db.chat_sessions.find_one({"session_id": session_id}, {"_id": 0})
        except Exception as e:
            print(f"[ERROR] load_chat_session failed: {e}")
            return None

    def delete_chat_session(self, session_id: str):
        if not self.is_connected():
            return False
        try:
            self.db.chat_sessions.delete_one({"session_id": session_id})
            return True
        except Exception as e:
            print(f"[ERROR] delete_chat_session failed: {e}")
            return False

    def seed_all(self):
        """Seed all processed CSV files into MongoDB"""
        print("[SEED] Starting database seeding from CSV files...")
        base_dir = Path(__file__).parent.parent
        data_dir = base_dir / "data" / "processed"

        if not data_dir.exists():
            print(f"[ERROR] Processed data directory not found at: {data_dir}")
            return False

        # Seed Destinations Clustered
        dest_path = data_dir / "destinations_clustered.csv"
        if dest_path.exists():
            df = pd.read_csv(dest_path)
            # Ensure coordinates columns exist and are clean
            self.save_destinations(df)
        else:
            print(f"[WARNING] {dest_path.name} not found, checking destinations_clean.csv")
            clean_path = data_dir / "destinations_clean.csv"
            if clean_path.exists():
                df = pd.read_csv(clean_path)
                self.save_destinations(df)

        # Seed Rules
        rules_path = data_dir / "travel_rules.csv"
        if not rules_path.exists():
            rules_path = data_dir / "all_rules.csv"
        if rules_path.exists():
            df = pd.read_csv(rules_path)
            self.save_rules(df)

        # Seed Cluster Profiles
        profiles_path = data_dir / "cluster_profiles.csv"
        if profiles_path.exists():
            df = pd.read_csv(profiles_path)
            self.save_cluster_profiles(df)

        # Seed Transactions
        trans_path = data_dir / "transactions.csv"
        if trans_path.exists():
            df = pd.read_csv(trans_path)
            self.save_transactions(df)

        # Seed Holidays
        holidays_path = data_dir / "holidays_clean.csv"
        if holidays_path.exists():
            df = pd.read_csv(holidays_path)
            self.save_holidays(df)

        # Seed POI
        poi_path = data_dir / "poi_clean.csv"
        if poi_path.exists():
            df = pd.read_csv(poi_path)
            self.save_poi(df)

        print("[SEED] Database seeding completed successfully!")
        return True

# Global MongoDB instance
db_storage = MongoDBStorage()

if __name__ == "__main__":
    print("[MAIN] MongoDB Storage test run...")
    if db_storage.is_connected():
        # Running seed
        db_storage.seed_all()
        # Test count
        count = db_storage.db.destinations.count_documents({})
        print(f"[TEST] Successfully seeded {count} destinations in MongoDB.")
    else:
        print("[ERROR] Database not connected. Make sure mongod is running.")

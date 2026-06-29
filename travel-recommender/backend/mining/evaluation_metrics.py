# -*- coding: utf-8 -*-
"""
Evaluation Metrics for Hybrid Recommendation System
Calculates: Precision@K, Recall@K, NDCG@K, MAP, RMSE, MAE
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
from mining.mongodb_storage import db_storage


class RecommendationEvaluator:
    """Evaluates recommendation quality using standard metrics"""
    
    def __init__(self):
        self.test_ratings = []
        self.train_ratings = []
        
    def split_ratings(self, test_ratio=0.2, min_ratings_per_user=5):
        """Split ratings into train/test sets"""
        if not db_storage.is_connected():
            print("[EVAL] Database not connected")
            return False
            
        # Get all ratings
        all_ratings = list(db_storage.db.user_ratings.find({}))
        
        if len(all_ratings) == 0:
            print("[EVAL] No ratings found")
            return False
            
        # Group by user
        user_ratings = {}
        for rating in all_ratings:
            user_id = rating['user_id']
            if user_id not in user_ratings:
                user_ratings[user_id] = []
            user_ratings[user_id].append(rating)
        
        # Split each user's ratings
        self.train_ratings = []
        self.test_ratings = []
        
        for user_id, ratings in user_ratings.items():
            if len(ratings) < min_ratings_per_user:
                # Not enough ratings, use all for training
                self.train_ratings.extend(ratings)
                continue
                
            # Sort by timestamp if available, otherwise random
            ratings_sorted = sorted(ratings, key=lambda x: x.get('timestamp', 0))
            
            # Split
            split_point = int(len(ratings_sorted) * (1 - test_ratio))
            self.train_ratings.extend(ratings_sorted[:split_point])
            self.test_ratings.extend(ratings_sorted[split_point:])
        
        print(f"[EVAL] Split: {len(self.train_ratings)} train, {len(self.test_ratings)} test")
        return True
    
    def precision_at_k(self, recommended: List[str], relevant: List[str], k: int) -> float:
        """
        Precision@K = |recommended ∩ relevant| / K
        """
        if k == 0:
            return 0.0
        recommended_k = recommended[:k]
        relevant_set = set(relevant)
        hits = len([dest for dest in recommended_k if dest in relevant_set])
        return hits / k
    
    def recall_at_k(self, recommended: List[str], relevant: List[str], k: int) -> float:
        """
        Recall@K = |recommended ∩ relevant| / |relevant|
        """
        if len(relevant) == 0:
            return 0.0
        recommended_k = recommended[:k]
        relevant_set = set(relevant)
        hits = len([dest for dest in recommended_k if dest in relevant_set])
        return hits / len(relevant)
    
    def ndcg_at_k(self, recommended: List[str], relevant_with_ratings: Dict[str, float], k: int) -> float:
        """
        NDCG@K (Normalized Discounted Cumulative Gain)
        DCG = Σ (2^rel - 1) / log2(i + 1)
        """
        if k == 0:
            return 0.0
            
        recommended_k = recommended[:k]
        
        # Calculate DCG
        dcg = 0.0
        for i, dest in enumerate(recommended_k):
            rel = relevant_with_ratings.get(dest, 0.0)
            dcg += (2**rel - 1) / np.log2(i + 2)  # i+2 because i starts at 0
        
        # Calculate Ideal DCG
        ideal_ratings = sorted(relevant_with_ratings.values(), reverse=True)[:k]
        idcg = 0.0
        for i, rel in enumerate(ideal_ratings):
            idcg += (2**rel - 1) / np.log2(i + 2)
        
        if idcg == 0:
            return 0.0
        
        return dcg / idcg
    
    def average_precision(self, recommended: List[str], relevant: List[str]) -> float:
        """
        Average Precision = Σ P(k) * rel(k) / |relevant|
        """
        if len(relevant) == 0:
            return 0.0
            
        relevant_set = set(relevant)
        score = 0.0
        num_hits = 0.0
        
        for i, dest in enumerate(recommended):
            if dest in relevant_set:
                num_hits += 1.0
                precision_at_i = num_hits / (i + 1.0)
                score += precision_at_i
        
        return score / len(relevant)
    
    def mean_average_precision(self, user_recommendations: Dict[str, List[str]], 
                               user_relevant: Dict[str, List[str]]) -> float:
        """
        MAP = Σ AP(u) / |users|
        """
        if len(user_relevant) == 0:
            return 0.0
            
        ap_sum = 0.0
        for user_id in user_relevant:
            recommended = user_recommendations.get(user_id, [])
            relevant = user_relevant[user_id]
            ap_sum += self.average_precision(recommended, relevant)
        
        return ap_sum / len(user_relevant)
    
    def rmse(self, predictions: List[Tuple[str, str, float]], 
            actuals: List[Tuple[str, str, float]]) -> float:
        """
        Root Mean Squared Error
        RMSE = sqrt(Σ(predicted - actual)² / n)
        """
        # Create lookup dict for actuals
        actual_dict = {(user, dest): rating for user, dest, rating in actuals}
        
        squared_errors = []
        for user, dest, pred_rating in predictions:
            actual_rating = actual_dict.get((user, dest))
            if actual_rating is not None:
                squared_errors.append((pred_rating - actual_rating) ** 2)
        
        if len(squared_errors) == 0:
            return 0.0
        
        return np.sqrt(np.mean(squared_errors))
    
    def mae(self, predictions: List[Tuple[str, str, float]], 
           actuals: List[Tuple[str, str, float]]) -> float:
        """
        Mean Absolute Error
        MAE = Σ|predicted - actual| / n
        """
        # Create lookup dict for actuals
        actual_dict = {(user, dest): rating for user, dest, rating in actuals}
        
        absolute_errors = []
        for user, dest, pred_rating in predictions:
            actual_rating = actual_dict.get((user, dest))
            if actual_rating is not None:
                absolute_errors.append(abs(pred_rating - actual_rating))
        
        if len(absolute_errors) == 0:
            return 0.0
        
        return np.mean(absolute_errors)
    
    def evaluate_system(self, recommender_func, k_values=[5, 10, 20]) -> Dict:
        """
        Full system evaluation using test set
        Returns comprehensive metrics dictionary
        """
        if len(self.test_ratings) == 0:
            print("[EVAL] No test data available")
            return {
                'error': 'No test data',
                'precision': {k: 0.0 for k in k_values},
                'recall': {k: 0.0 for k in k_values},
                'ndcg': {k: 0.0 for k in k_values},
                'map': 0.0,
                'rmse': 0.0,
                'mae': 0.0,
                'coverage': 0.0,
                'users_evaluated': 0,
                'test_ratings': 0
            }
        
        # Group test ratings by user (only ratings >= 4 are considered relevant)
        user_test_data = {}
        for rating in self.test_ratings:
            user_id = rating['user_id']
            dest_name = rating['destination_name']
            rating_val = rating['rating']
            
            if user_id not in user_test_data:
                user_test_data[user_id] = {'destinations': [], 'ratings': {}, 'all_destinations': []}
            
            # Store all for RMSE/MAE
            user_test_data[user_id]['all_destinations'].append(dest_name)
            user_test_data[user_id]['ratings'][dest_name] = rating_val
            
            # Only consider ratings >= 4.0 as "relevant" for Precision/Recall
            if rating_val >= 4.0:
                user_test_data[user_id]['destinations'].append(dest_name)
        
        # Calculate metrics for each K
        results = {
            'precision': {},
            'recall': {},
            'ndcg': {},
            'f1': {},
            'map': 0.0,
            'rmse': 0.0,
            'mae': 0.0,
            'coverage': 0.0,
            'users_evaluated': len(user_test_data),
            'test_ratings': len(self.test_ratings),
            'relevant_items_total': 0,
            'recommendations_made': 0
        }
        
        # Track for MAP calculation
        user_recommendations = {}
        user_relevant = {}
        
        # Track predictions for RMSE/MAE
        predictions = []
        actuals = []
        
        # Unique destinations recommended
        all_recommended = set()
        
        # Evaluate each user
        print(f"[EVAL] Evaluating {len(user_test_data)} users...")
        
        successful_users = 0
        
        for user_id, test_data in user_test_data.items():
            relevant_dests = test_data['destinations']  # Only ratings >= 4
            relevant_ratings = test_data['ratings']  # All ratings
            all_user_dests = test_data['all_destinations']
            
            # Skip users with no relevant items
            if len(relevant_dests) == 0:
                print(f"[EVAL] User {user_id} has no relevant items (rating >= 4), skipping")
                continue
            
            results['relevant_items_total'] += len(relevant_dests)
            
            # Get recommendations for this user
            try:
                recs = recommender_func(user_id=user_id, limit=max(k_values))
                recommended_dests = [r['Destination Name'] for r in recs if 'Destination Name' in r]
                
                if len(recommended_dests) > 0:
                    results['recommendations_made'] += len(recommended_dests)
                    successful_users += 1
                    print(f"[EVAL] User {user_id}: {len(recommended_dests)} recs, {len(relevant_dests)} relevant items")
            except Exception as e:
                print(f"[EVAL] Failed to get recs for user {user_id}: {e}")
                recommended_dests = []
            
            if len(recommended_dests) == 0:
                print(f"[EVAL] No recommendations for user {user_id}")
                continue
            
            all_recommended.update(recommended_dests)
            
            # Store for MAP
            user_recommendations[user_id] = recommended_dests
            user_relevant[user_id] = relevant_dests
            
            # Calculate Precision@K, Recall@K, NDCG@K
            for k in k_values:
                if k not in results['precision']:
                    results['precision'][k] = []
                    results['recall'][k] = []
                    results['ndcg'][k] = []
                    results['f1'][k] = []
                
                prec_k = self.precision_at_k(recommended_dests, relevant_dests, k)
                rec_k = self.recall_at_k(recommended_dests, relevant_dests, k)
                ndcg_k = self.ndcg_at_k(recommended_dests, relevant_ratings, k)
                
                # Calculate F1 Score
                f1_k = 0.0
                if prec_k + rec_k > 0:
                    f1_k = 2 * (prec_k * rec_k) / (prec_k + rec_k)
                
                results['precision'][k].append(prec_k)
                results['recall'][k].append(rec_k)
                results['ndcg'][k].append(ndcg_k)
                results['f1'][k].append(f1_k)
            
            # For RMSE/MAE: predict rating for test items
            for dest in all_user_dests:
                actual_rating = relevant_ratings.get(dest, 0.0)
                
                # Find if this destination was recommended
                rec_item = next((r for r in recs if r.get('Destination Name') == dest), None)
                
                if rec_item:
                    # Use final_score as predicted rating (scale 0-1 to 1-5)
                    predicted_rating = min(max(rec_item.get('final_score', 0.5) * 4 + 1, 1.0), 5.0)
                else:
                    # If not recommended, predict average rating (3.0)
                    predicted_rating = 3.0
                
                predictions.append((user_id, dest, predicted_rating))
                actuals.append((user_id, dest, actual_rating))
        
        print(f"[EVAL] Successfully evaluated {successful_users}/{len(user_test_data)} users")
        
        # Average metrics across users
        for k in k_values:
            if len(results['precision'][k]) > 0:
                results['precision'][k] = np.mean(results['precision'][k])
                results['recall'][k] = np.mean(results['recall'][k])
                results['ndcg'][k] = np.mean(results['ndcg'][k])
                results['f1'][k] = np.mean(results['f1'][k])
            else:
                results['precision'][k] = 0.0
                results['recall'][k] = 0.0
                results['ndcg'][k] = 0.0
                results['f1'][k] = 0.0
        
        # Calculate MAP
        if len(user_relevant) > 0:
            results['map'] = self.mean_average_precision(user_recommendations, user_relevant)
        
        # Calculate RMSE and MAE
        if len(predictions) > 0:
            results['rmse'] = self.rmse(predictions, actuals)
            results['mae'] = self.mae(predictions, actuals)
        
        # Calculate coverage
        if db_storage.is_connected():
            total_destinations = db_storage.db.destinations.count_documents({})
            results['coverage'] = len(all_recommended) / total_destinations if total_destinations > 0 else 0.0
        
        print(f"[EVAL] Evaluation complete!")
        print(f"[EVAL] Precision@5={results['precision'].get(5, 0):.4f}, Recall@5={results['recall'].get(5, 0):.4f}")
        print(f"[EVAL] MAP={results['map']:.4f}, RMSE={results['rmse']:.4f}, MAE={results['mae']:.4f}")
        
        return results


# Global evaluator instance
evaluator = RecommendationEvaluator()

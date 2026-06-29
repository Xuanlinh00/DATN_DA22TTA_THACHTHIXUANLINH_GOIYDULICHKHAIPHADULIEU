# -*- coding: utf-8 -*-
"""
Recommender Engine - Main recommendation logic combining MongoDB, rules, clusters, and hybrid ranking.

Hybrid scoring formula:
  final_score = 0.6 * content_score + 0.4 * apriori_score
  
Apriori score is derived from matching association rules where the antecedents
align with the user's stated preferences (season, budget, category).
The consequents (e.g. Country:France, Continent:Europe) are used to boost
candidates that match those consequents.
"""
import sys
import pandas as pd
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mining.mongodb_storage import db_storage
from mining.apriori_module import get_matching_rules
from mining.content_based import content_recommender
from mining.collaborative_filtering import collaborative_recommender


# ── Helper: parse Apriori consequent tokens ─────────────────────────────────

def _parse_consequent_boost(rules):
    """
    Extracts useful consequent signals from matching Apriori rules.

    Each rule consequent may contain tokens like:
      'Country:France', 'Continent:Europe', 'Type:Cultural', 'Cost:Budget'

    Returns a dict:
      {
        'countries':  {'France': 0.92, 'Italy': 0.75, ...},   # value = confidence * lift
        'continents': {'Europe': 0.88, ...},
        'types':      {'Cultural': 0.80, ...},
        'costs':      {'Budget': 0.70, ...},
      }
    """
    boosts = {
        'countries':  {},
        'continents': {},
        'types':      {},
        'costs':      {},
    }

    for rule in rules:
        score = rule.get('recommendation_score', 0.0)  # confidence * lift
        for consequent in rule.get('consequents', []):
            if ':' not in consequent:
                continue
            prefix, value = consequent.split(':', 1)
            prefix = prefix.strip().lower()
            value  = value.strip()

            if prefix == 'country':
                boosts['countries'][value] = max(boosts['countries'].get(value, 0.0), score)
            elif prefix == 'continent':
                boosts['continents'][value] = max(boosts['continents'].get(value, 0.0), score)
            elif prefix == 'type':
                boosts['types'][value] = max(boosts['types'].get(value, 0.0), score)
            elif prefix == 'cost':
                boosts['costs'][value] = max(boosts['costs'].get(value, 0.0), score)

    return boosts


def _compute_apriori_score(dest: dict, boosts: dict) -> float:
    """
    Given one destination record and the boost signals extracted from Apriori rules,
    compute a composite apriori_score in [0.0, 1.0].

    Matching priority (weighted):
      country   : 0.40
      continent : 0.25
      type      : 0.20
      cost      : 0.15
    """
    if not any(boosts.values()):
        return 0.0

    country   = str(dest.get('Country', ''))
    continent = str(dest.get('Continent', ''))
    d_type    = str(dest.get('Type', ''))
    cost      = str(dest.get('Cost_Category', ''))

    country_score   = boosts['countries'].get(country, 0.0)
    continent_score = boosts['continents'].get(continent, 0.0)
    type_score      = boosts['types'].get(d_type, 0.0)
    cost_score      = boosts['costs'].get(cost, 0.0)

    raw = (
        0.40 * country_score +
        0.25 * continent_score +
        0.20 * type_score +
        0.15 * cost_score
    )

    # Normalize to [0, 1] — max raw is 1.0 when all signals fire at confidence*lift = 1.0
    return min(raw, 1.0)


# ── Recommender Engine class ─────────────────────────────────────────────────

class RecommenderEngine:
    def __init__(self):
        self.destinations = pd.DataFrame()
        self.load_data()

    def load_data(self):
        """Load destinations data from MongoDB (fallback to CSV)"""
        try:
            records = db_storage.load_destinations()
            if records:
                self.destinations = pd.DataFrame(records)
                print(f"[ENGINE] Loaded {len(self.destinations)} destinations from MongoDB")
            else:
                # Fallback to CSV
                csv_path = Path(__file__).parent / "data" / "processed" / "destinations_clustered.csv"
                if csv_path.exists():
                    self.destinations = pd.read_csv(csv_path)
                    print(f"[ENGINE] Fallback loaded {len(self.destinations)} destinations from CSV")
                else:
                    print("[ERROR] Destinations dataset not found in MongoDB or CSV")
                    self.destinations = pd.DataFrame()
        except Exception as e:
            print(f"[ERROR] Failed to load data: {e}")
            self.destinations = pd.DataFrame()

    def filter_destinations(self, season=None, budget=None, category=None, country=None):
        """Filter destinations by criteria"""
        if self.destinations.empty:
            self.load_data()
            if self.destinations.empty:
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

    def get_recommendations(self, filters=None, limit=10, user_id=None, strict=False, strict_country=False):
        """
        Get recommendations using the FULL Hybrid approach:

        Step 1: Filter candidate destinations by hard constraints (season/budget/category/country).
        Step 2: Rank candidates using Content-Based TF-IDF cosine similarity.
        Step 3: Look up matching Apriori rules and compute apriori_score for each candidate.
        Step 4: Compute final_score = 0.6 * content_score + 0.4 * apriori_score.
        Step 5: Optionally boost with Collaborative Filtering if user_id is provided.
        Step 6: Prioritize destinations with real descriptions; return top-N.

        Returns list of destination dicts with fields:
          content_score, apriori_score, final_score, matched_rules (count)
        """
        if filters is None:
            filters = {}

        if self.destinations.empty:
            self.load_data()

        # ── Step 1: Filter with Soft Relaxation ───────────────────────
        candidates_df = self.filter_destinations(
            season=filters.get('season'),
            budget=filters.get('budget'),
            category=filters.get('category'),
            country=filters.get('country')
        )

        relaxed_by = []
        # strict=True: no relaxation at all
        # strict_country=True: country is locked, but season/budget/category may relax
        if strict:
            pass  # no relaxation
        elif candidates_df.empty:
            locked_country = filters.get('country') if strict_country else None

            # 1. Relax Country filter (only if not strict_country)
            if not strict_country and filters.get('country'):
                relaxed_by.append('country')
                print(f"[ENGINE] 0 candidates found. Relaxing filter: country='{filters.get('country')}'")
                candidates_df = self.filter_destinations(
                    season=filters.get('season'),
                    budget=filters.get('budget'),
                    category=filters.get('category'),
                    country=None
                )

            # 2. Relax Budget filter
            if candidates_df.empty and filters.get('budget'):
                relaxed_by.append('budget')
                print(f"[ENGINE] 0 candidates found. Relaxing filter: budget='{filters.get('budget')}'")
                candidates_df = self.filter_destinations(
                    season=filters.get('season'),
                    budget=None,
                    category=filters.get('category'),
                    country=locked_country or (None if 'country' in relaxed_by else filters.get('country'))
                )

            # 3. Relax Season filter
            if candidates_df.empty and filters.get('season'):
                relaxed_by.append('season')
                print(f"[ENGINE] 0 candidates found. Relaxing filter: season='{filters.get('season')}'")
                candidates_df = self.filter_destinations(
                    season=None,
                    budget=None if 'budget' in relaxed_by else filters.get('budget'),
                    category=filters.get('category'),
                    country=locked_country or (None if 'country' in relaxed_by else filters.get('country'))
                )

            # 4. Relax Category filter
            if candidates_df.empty and filters.get('category'):
                relaxed_by.append('category')
                print(f"[ENGINE] 0 candidates found. Relaxing filter: category='{filters.get('category')}'")
                candidates_df = self.filter_destinations(
                    season=None,
                    budget=None,
                    category=None,
                    country=locked_country
                )

            # 5. Final fallback: all destinations in country (or all if no country lock)
            if candidates_df.empty:
                candidates_df = self.filter_destinations(
                    season=None, budget=None, category=None, country=locked_country
                ) if locked_country else self.destinations.copy()

            print(f"[ENGINE] Soft Filtering activated. Relaxed filters: {relaxed_by}. Found {len(candidates_df)} candidates.")

        candidates = candidates_df.to_dict('records')

        # ── Step 2: Content-Based ranking ────────────────────────────
        ranked_candidates = content_recommender.rank_candidates(candidates, filters)

        # ── Step 3: Apriori rule-based scoring ───────────────────────
        matching_rules = []
        boosts = {}
        try:
            matching_rules = get_matching_rules(filters)
            boosts = _parse_consequent_boost(matching_rules)
        except Exception as e:
            print(f"[ENGINE] Apriori rule lookup failed (non-fatal): {e}")

        has_apriori = bool(matching_rules)

        for item in ranked_candidates:
            content_s = float(item.get('content_score', 0.0))
            apriori_s = _compute_apriori_score(item, boosts) if has_apriori else 0.0

            # Hybrid final score
            if has_apriori:
                final_s = 0.60 * content_s + 0.40 * apriori_s
            else:
                # No Apriori rules found → fall back to content-only
                final_s = content_s

            item['content_score']  = round(content_s, 4)
            item['apriori_score']  = round(apriori_s, 4)
            item['final_score']    = round(final_s, 4)
            item['matched_rules']  = len(matching_rules)

        # ── Step 4: Collaborative Filtering boost (if user_id provided) ──
        if user_id:
            try:
                user_recs = collaborative_recommender.get_user_recommendations(user_id, limit=50)
                if user_recs:
                    user_rec_names = {r['Destination Name'] for r in user_recs}
                    for item in ranked_candidates:
                        if item['Destination Name'] in user_rec_names:
                            item['final_score'] = min(item['final_score'] + 0.15, 1.0)
            except Exception as e:
                print(f"[ENGINE] Collaborative filtering boost failed (non-fatal): {e}")

        # ── Step 5: Sort — descriptions first, then final_score ──────
        def sort_key(item):
            desc = item.get('Description')
            has_desc = (
                desc is not None and
                str(desc).strip() != '' and
                str(desc).lower() != 'nan'
            )
            return (1 if has_desc else 0, item.get('final_score', 0.0))

        ranked_candidates.sort(key=sort_key, reverse=True)

        # ── Step 6: Serialize and return ─────────────────────────────
        df_result = pd.DataFrame(ranked_candidates).head(limit)
        if not df_result.empty:
            df_result = df_result.astype(object).where(pd.notnull(df_result), None)
            return df_result.to_dict('records')

        return []

    def get_matched_rules_info(self, filters):
        """
        Returns human-readable info about the Apriori rules that matched the given filters.
        Used by the frontend to display 'Why these recommendations?' explanations.
        """
        try:
            rules = get_matching_rules(filters)
            info = []
            for r in rules[:5]:  # top 5 rules
                antecedents = ' + '.join(r.get('antecedents', []))
                consequents = ' → '.join(r.get('consequents', []))
                info.append({
                    'rule':       f"{antecedents} ⟹ {consequents}",
                    'confidence': round(r.get('confidence', 0.0), 2),
                    'lift':       round(r.get('lift', 0.0), 2),
                    'score':      round(r.get('recommendation_score', 0.0), 2),
                })
            return info
        except Exception as e:
            print(f"[ENGINE] get_matched_rules_info failed: {e}")
            return []

    def search(self, query, limit=50):
        """
        Search destinations by keyword across multiple fields:
        - Destination Name (highest priority)
        - Country
        - Type / Broader_Type
        - Continent / country_subregion
        - Description
        Results are ranked by relevance score + avg rating.
        """
        if self.destinations.empty:
            self.load_data()

        if self.destinations.empty:
            return []

        df = self.destinations.copy()
        q = query.strip().lower()

        # Build relevance score for each row
        def relevance(row):
            score = 0
            name    = str(row.get('Destination Name', '')).lower()
            country = str(row.get('Country', '')).lower()
            dest_type = str(row.get('Type', '')).lower()
            broader  = str(row.get('Broader_Type', '')).lower()
            continent = str(row.get('Continent', '')).lower()
            subregion = str(row.get('country_subregion', '')).lower()
            desc    = str(row.get('Description', '')).lower()
            capital = str(row.get('country_capital', '')).lower()

            if q == name:              score += 100  # exact name match
            elif q in name:            score += 60   # partial name match
            if q == country:           score += 80   # exact country
            elif q in country:         score += 50   # partial country
            if q in capital:           score += 30   # capital city
            if q in dest_type:         score += 25   # type keyword (beach, mountain...)
            if q in broader:           score += 20
            if q in continent:         score += 15
            if q in subregion:         score += 15
            if q in desc:              score += 10   # description mention
            return score

        df['_rel_score'] = df.apply(relevance, axis=1)
        results = df[df['_rel_score'] > 0].copy()

        if results.empty:
            return []

        # Sort by relevance desc, then Avg Rating desc, then has_desc
        if 'Avg Rating' in results.columns:
            results['_has_desc'] = results['Description'].apply(
                lambda x: 1 if pd.notnull(x) and str(x).strip() not in ('', 'nan') else 0
            )
            results = results.sort_values(
                by=['_rel_score', '_has_desc', 'Avg Rating'],
                ascending=[False, False, False]
            )
            results = results.drop(columns=['_has_desc'])
        else:
            results = results.sort_values(by=['_rel_score'], ascending=False)

        results = results.drop(columns=['_rel_score'])
        results = results.head(limit)
        results = results.astype(object).where(pd.notnull(results), None)
        return results.to_dict('records')

    def get_similar(self, destination_name, limit=5):
        """Get similar destinations prioritizing same type and same country"""
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            
            # Get all destinations
            all_dests = content_recommender.destinations
            if all_dests.empty:
                return []
            
            # Find target index
            idx_list = all_dests[all_dests['Destination Name'].str.lower() == destination_name.lower()].index
            if len(idx_list) == 0:
                print(f"[WARNING] Destination '{destination_name}' not found for similarity matching.")
                return []
            idx = idx_list[0]
            target = all_dests.iloc[idx]
            
            # Compute base content-based similarity scores
            sim_scores = cosine_similarity(content_recommender.tfidf_matrix[idx], content_recommender.tfidf_matrix).flatten()
            
            # Try to get collaborative filtering similarity index
            collab_scores = {}
            if collaborative_recommender.item_similarity_df is not None and target['Destination Name'] in collaborative_recommender.item_similarity_df.index:
                collab_scores = collaborative_recommender.item_similarity_df[target['Destination Name']].to_dict()

            # Create a DataFrame to score and sort candidates
            df = all_dests.copy()
            df['sim_score'] = sim_scores
            
            # Exclude the target destination itself
            df = df[df.index != idx]
            
            target_country = str(target.get('Country', '')).lower().strip()
            target_type = str(target.get('Type', '')).lower().strip()
            
            def calculate_similarity_rank(row):
                # Start with TF-IDF similarity (0.0 to 1.0)
                score = row['sim_score']
                
                # Add collaborative filtering score if available
                row_name = row['Destination Name']
                if row_name in collab_scores:
                    score += collab_scores[row_name] * 0.5 # weight collaborative filtering
                
                row_country = str(row.get('Country', '')).lower().strip()
                row_type = str(row.get('Type', '')).lower().strip()
                
                # High boost for same country
                if row_country == target_country:
                    score += 5.0
                    
                # High boost for same type
                if row_type == target_type:
                    score += 3.0
                    
                return score
                
            df['final_score'] = df.apply(calculate_similarity_rank, axis=1)
            df = df.sort_values(by='final_score', ascending=False)
            
            # Select top limit
            results = df.head(limit).copy()
            results = results.astype(object).where(pd.notnull(results), None)
            return results.to_dict('records')
            
        except Exception as e:
            print(f"[ERROR] get_similar failed, falling back: {e}")
            return content_recommender.get_similar(destination_name, limit)


# Create global instance
engine = RecommenderEngine()


if __name__ == "__main__":
    print("[MAIN] Testing Hybrid Recommender Engine with Apriori scoring...")
    filters = {'season': 'Autumn', 'budget': 'Budget', 'category': 'Cultural'}
    results = engine.get_recommendations(filters, limit=5)
    print(f"[RESULT] Recommendations found: {len(results)}")
    for r in results:
        print(
            f"  - {r.get('Destination Name')} ({r.get('Country')}) | "
            f"content={r.get('content_score', 0):.3f} | "
            f"apriori={r.get('apriori_score', 0):.3f} | "
            f"final={r.get('final_score', 0):.3f} | "
            f"rules={r.get('matched_rules', 0)}"
        )
    print("\n[MAIN] Matched rule explanations:")
    rules_info = engine.get_matched_rules_info(filters)
    for ri in rules_info:
        print(f"  {ri['rule']}  (conf={ri['confidence']}, lift={ri['lift']})")

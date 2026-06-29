# Evaluation Metrics System - Complete Implementation

## Completed: June 27, 2026

### Overview
Added comprehensive evaluation metrics system to measure the quality of the Hybrid Recommendation System using industry-standard metrics.

---

## Backend Implementation

### 1. Evaluation Metrics Module (`backend/mining/evaluation_metrics.py`)

**Features:**
- ✅ **Precision@K** - Accuracy of recommendations in top K results
- ✅ **Recall@K** - Coverage of relevant items in top K results  
- ✅ **NDCG@K** - Normalized Discounted Cumulative Gain (ranking quality)
- ✅ **F1 Score@K** - Harmonic mean of Precision and Recall
- ✅ **MAP** - Mean Average Precision across all users
- ✅ **RMSE** - Root Mean Squared Error for rating prediction
- ✅ **MAE** - Mean Absolute Error for rating prediction
- ✅ **Coverage** - Percentage of items recommended

**Key Logic:**
```python
# Split ratings 80/20 train/test
split_ratings(test_ratio=0.2, min_ratings_per_user=5)

# Relevant items = ratings >= 4.0 (high quality)
if rating_val >= 4.0:
    user_relevant_items.append(destination)

# Calculate all metrics
evaluate_system(recommender_func, k_values=[5, 10, 20])
```

**Improvements Made:**
- Only considers ratings ≥ 4.0 as "relevant" for Precision/Recall
- Handles users with no recommendations gracefully
- Predicts ratings for all test items (not just recommended ones)
- Detailed logging for debugging
- Tracks additional stats: relevant_items_total, recommendations_made

---

## API Endpoints

### POST `/api/admin/evaluate-system`
**Query Parameters:**
- `k_values` (optional, default: "5,10,20")

**Response:**
```json
{
  "success": true,
  "metrics": {
    "precision": {
      "5": 0.15,
      "10": 0.12,
      "20": 0.08
    },
    "recall": {
      "5": 0.25,
      "10": 0.35,
      "20": 0.45
    },
    "ndcg": {
      "5": 0.18,
      "10": 0.16,
      "20": 0.14
    },
    "f1": {
      "5": 0.19,
      "10": 0.17,
      "20": 0.14
    },
    "map": 0.22,
    "rmse": 0.85,
    "mae": 0.67,
    "coverage": 0.133,
    "users_evaluated": 27,
    "test_ratings": 159,
    "relevant_items_total": 45,
    "recommendations_made": 540
  },
  "message": "Đã đánh giá hệ thống với 27 người dùng"
}
```

### GET `/api/admin/evaluation-metrics`
Returns cached metrics if available.

---

## Frontend Implementation

### Admin Page Section

**UI Components:**

1. **Explanation Box** - Educational content about each metric
   - Support, Confidence, Lift definitions
   - Precision, Recall, NDCG formulas
   - MAP, RMSE, MAE meanings

2. **Run Evaluation Button**
   - Shows total ratings available
   - Loading state during calculation
   - Success message with user count

3. **Overview Stats Cards**
   - Users Evaluated
   - Test Ratings
   - Items Liên Quan (rating ≥ 4.0)
   - Gợi Ý Đã Tạo
   - Coverage %

4. **Warning Alert**
   - Shows if relevant_items_total < 10
   - Warns about insufficient data quality

5. **Metrics @ K Cards** (one for each K value)
   - Precision@K with color coding
   - Recall@K with color coding
   - NDCG@K with color coding
   - F1 Score (if available)
   - Highlights values > 30% in green

6. **Aggregate Metrics**
   - MAP (overall quality)
   - RMSE (prediction error)
   - MAE (average error)

7. **Interpretation Guide**
   - Explains what good/bad values mean
   - Provides context for results

---

## How Metrics Are Calculated

### Precision@K
```
Precision@K = (Number of relevant items in top K) / K
```
- Example: If 3 out of top 10 recommendations are relevant → 30%
- Higher is better

### Recall@K
```
Recall@K = (Number of relevant items in top K) / (Total relevant items)
```
- Example: If user has 15 relevant items, and 5 are in top 10 → 33.3%
- Higher is better

### NDCG@K
```
DCG = Σ (2^relevance - 1) / log2(position + 1)
NDCG = DCG / Ideal DCG
```
- Rewards placing high-rated items at top positions
- Range: 0-1, higher is better

### MAP (Mean Average Precision)
```
AP = Σ (Precision@k × relevance(k)) / Total_relevant
MAP = Average of AP across all users
```
- Overall recommendation quality
- Higher is better

### RMSE (Root Mean Squared Error)
```
RMSE = sqrt(Σ (predicted_rating - actual_rating)² / n)
```
- Measures rating prediction accuracy
- Lower is better (0 = perfect)

### MAE (Mean Absolute Error)
```
MAE = Σ |predicted_rating - actual_rating| / n
```
- Average prediction error
- Lower is better (0 = perfect)

---

## Understanding Results

### Good vs Bad Metrics

**Precision/Recall/NDCG:**
- 🟢 Excellent: > 50%
- 🟡 Good: 30-50%
- 🟠 Fair: 10-30%
- 🔴 Poor: < 10%

**MAP:**
- 🟢 Excellent: > 0.5
- 🟡 Good: 0.3-0.5
- 🟠 Fair: 0.1-0.3
- 🔴 Poor: < 0.1

**RMSE/MAE:**
- 🟢 Excellent: < 0.5 (for 1-5 scale)
- 🟡 Good: 0.5-0.8
- 🟠 Fair: 0.8-1.2
- 🔴 Poor: > 1.2

**Coverage:**
- 🟢 Excellent: > 50%
- 🟡 Good: 20-50%
- 🟠 Fair: 10-20%
- 🔴 Poor: < 10%

---

## Why Metrics Might Be Zero or Low

1. **Not Enough High-Quality Ratings**
   - Need ratings ≥ 4.0 to be considered "relevant"
   - Solution: Add more high-quality user ratings

2. **Poor Train/Test Split**
   - Users need at least 5 ratings to be included
   - Solution: Ensure users have sufficient rating history

3. **Recommendation System Not Personalized**
   - System recommends same items to everyone
   - Solution: Improve collaborative filtering

4. **No Overlap Between Test and Recommendations**
   - Test items are never recommended
   - Solution: Check recommendation filters/logic

---

## Testing Recommendations

To get meaningful metrics:

1. **Ensure Quality Data:**
   - At least 50+ users with 5+ ratings each
   - Mix of ratings (1-5 stars)
   - At least 30% of ratings should be ≥ 4.0

2. **Run Algorithms First:**
   - Execute K-Means clustering
   - Run Apriori mining
   - Update CF matrix

3. **Run Evaluation:**
   - Click "Chạy Đánh Giá"
   - Wait for processing (may take 30s-2min)
   - Review results

4. **Iterate and Improve:**
   - Low Precision → Recommendations too broad
   - Low Recall → Missing relevant items
   - Low NDCG → Poor ranking quality
   - High RMSE/MAE → Bad rating predictions

---

## Files Modified

### Backend:
- `backend/mining/evaluation_metrics.py` ← NEW
- `backend/api/routes.py` (added `/admin/evaluate-system`, `/admin/evaluation-metrics`)
- `frontend/src/services/api.js` (added `evaluateSystem`, `getEvaluationMetrics`)

### Frontend:
- `frontend/src/pages/AdminPage.js` (added Evaluation Metrics section)
- Added state: `evaluationMetrics`, `actionLoading.evaluation`
- Added function: `handleEvaluateSystem()`

---

## Next Steps (Optional Enhancements)

1. **Cache Metrics in Database**
   - Save evaluation results to MongoDB
   - Show historical trends
   - Compare before/after algorithm changes

2. **A/B Testing Framework**
   - Test different algorithm parameters
   - Compare Hybrid vs Content-only vs CF-only

3. **Real-time Metrics Dashboard**
   - Live tracking of recommendation quality
   - Alert when metrics drop below threshold

4. **Per-Algorithm Breakdown**
   - Separate metrics for Content-Based, CF, Apriori
   - Show contribution of each algorithm

5. **User Segment Analysis**
   - Metrics by user demographics
   - Identify which user groups get better recommendations

---

## Usage in Thesis (Chapter 4)

This evaluation system provides concrete evidence for:

**4.1 Experimental Setup:**
- Train/test split methodology (80/20)
- Evaluation metrics selection
- Relevant item definition (rating ≥ 4.0)

**4.2 Results:**
- Precision@K, Recall@K, NDCG@K tables
- MAP for overall quality
- RMSE/MAE for rating prediction accuracy
- Coverage analysis

**4.3 Discussion:**
- Compare with baseline systems
- Justify hybrid approach benefits
- Show improvement over single algorithms

**4.4 Limitations:**
- Data sparsity issues
- Cold start problem
- Coverage vs Accuracy tradeoff

---

## Conclusion

The evaluation metrics system is now fully operational and provides comprehensive quality measurements for the Hybrid Recommendation System. All standard metrics (Precision, Recall, NDCG, MAP, RMSE, MAE) are calculated correctly with proper handling of edge cases.

Users can now quantitatively assess recommendation quality and make data-driven improvements to the system.

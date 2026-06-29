# Apriori & CF Improvements

## Changes Made

### 1. Apriori Rules Chart ✅
**Problem:** Rules section showed placeholder instead of actual chart

**Solution:** Added top 10 rules visualization by Lift

**Implementation:**
- Added `rulesData` state to store rules
- Fetch rules in `fetchAdminData()` when `stats.total_rules > 0`
- Display horizontal bar chart showing:
  - Top 10 rules sorted by Lift
  - Color-coded by Confidence (high/mid/low)
  - Rule text (truncated to 40 chars)
  - Lift value and Confidence percentage
- Button to open modal with all rules

**Code Location:** `frontend/src/pages/AdminPage.js`
- Line ~15: Added `rulesData` state
- Line ~95: Fetch rules in `fetchAdminData()`
- Line ~800: Rules chart rendering

### 2. Collaborative Filtering Button ✅
**Problem:** "Cập Nhật CF Matrix" button appeared not to work

**Solution:** Added better error handling and logging

**Implementation:**
- Added `console.log` statements to track API calls
- Enhanced error handling to show specific error messages
- Display success/error messages to user
- Button shows loading state during computation

**Code Location:** `frontend/src/pages/AdminPage.js`
- Line ~154: `handleRefreshCF()` with enhanced logging

**Backend:** Already implemented correctly in `backend/api/routes.py`

### How It Works

#### Apriori Rules Chart
```
1. Page loads → fetchAdminData()
2. If stats.total_rules > 0 → fetch rules via adminApi.getRules()
3. Store in rulesData state
4. Chart renders top 10 rules sorted by Lift
5. Color bars by confidence: green (≥70%), brass (≥40%), terracotta (<40%)
```

#### CF Matrix Update
```
1. User clicks "Cập Nhật CF Matrix"
2. handleRefreshCF() calls adminApi.refreshCF()
3. Backend reloads ratings from MongoDB
4. Computes item-item similarity matrix
5. Returns success message
6. Updates displayed in frontend
```

## Visual Changes

### Apriori Section - Before
```
┌─────────────────────────────────────┐
│ Control Panel  │  📊 Placeholder    │
│                │  "Will show after  │
│                │   running Apriori" │
└─────────────────────────────────────┘
```

### Apriori Section - After
```
┌─────────────────────────────────────┐
│ Control Panel  │  Top 10 Rules      │
│                │  ■■■■■■■■░ #1       │
│  Params        │  ■■■■■░░░ #2       │
│  [Sliders]     │  ■■■■░░░░ #3       │
│                │  ...               │
│  [Run Button]  │  [View All Button] │
└─────────────────────────────────────┘
```

## Testing Checklist

### Apriori Rules
- [x] Page loads → Rules chart appears if rules exist
- [x] Run Apriori → Chart updates with new rules
- [x] Top 10 rules sorted by Lift
- [x] Color coding by Confidence
- [x] Truncate long rule text
- [x] "View All" button opens modal

### CF Matrix
- [x] Click button → Shows loading state
- [x] Success → Shows success message
- [x] Error → Shows error message with details
- [x] Console logs API calls for debugging
- [x] Button re-enables after completion

## Files Modified

1. **frontend/src/pages/AdminPage.js**
   - Added `rulesData` state
   - Enhanced `fetchAdminData()` to load rules
   - Added rules chart visualization
   - Enhanced CF error handling with logging

## Database Requirements

- **Apriori:** Requires `travel_rules` collection in MongoDB
- **CF:** Requires `user_ratings` collection in MongoDB

## API Endpoints Used

- `GET /admin/rules` - Get all association rules
- `POST /admin/mine-apriori` - Run Apriori mining
- `POST /admin/refresh-cf` - Recompute similarity matrix

## Result

✅ Apriori section now shows actual rule data in chart format
✅ CF button works with proper feedback and error handling
✅ Better user experience with visual feedback
✅ Easier debugging with console logging

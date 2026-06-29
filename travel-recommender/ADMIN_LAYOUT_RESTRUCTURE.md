# Hướng Dẫn Tái Cấu Trúc Admin Layout

## 🎯 Mục Tiêu

1. **Đặt K-Means Control gần Cluster Visualization** để dễ quan sát kết quả
2. **Thêm biểu đồ** cho Countries, Rules, Users stats
3. **Đồng bộ màu sắc** với giao diện chính (pink theme)

## 📐 Layout Mới

```
┌─────────────────────────────────────────────────┐
│              HEADER + LOGOUT                     │
├─────────────────────────────────────────────────┤
│        STATS CARDS (4 columns)                   │
│  Destinations | Countries | Rules | Users        │
├─────────────────────────────────────────────────┤
│                                                   │
│  ┌─────────────────────────────────────────┐   │
│  │  K-MEANS CLUSTERING SECTION              │   │
│  │  ┌──────────────┐  ┌──────────────────┐ │   │
│  │  │   Control    │  │  Cluster Charts   │ │   │
│  │  │   Panel      │  │  - Bar Chart      │ │   │
│  │  │   - K Slider │  │  - Cost Cards     │ │   │
│  │  │   - Run Btn  │  │                   │ │   │
│  │  └──────────────┘  └──────────────────┘ │   │
│  └─────────────────────────────────────────┘   │
│                                                   │
│  ┌─────────────────────────────────────────┐   │
│  │  RATINGS DASHBOARD (3 columns)           │   │
│  │  Distribution | Top Dests | User Activity│   │
│  └─────────────────────────────────────────┘   │
│                                                   │
│  ┌─────────────────────────────────────────┐   │
│  │  APRIORI RULES VISUALIZATION             │   │
│  │  ┌──────────────┐  ┌──────────────────┐ │   │
│  │  │   Control    │  │  Rules Charts     │ │   │
│  │  │   Panel      │  │  - Top Rules      │ │   │
│  │  │   - Params   │  │  - Confidence     │ │   │
│  │  │   - Run Btn  │  │                   │ │   │
│  │  └──────────────┘  └──────────────────┘ │   │
│  └─────────────────────────────────────────┘   │
│                                                   │
│  ┌─────────────────────────────────────────┐   │
│  │  SYSTEM STATISTICS                       │   │
│  │  ┌──────────────┐  ┌──────────────────┐ │   │
│  │  │  Countries   │  │   Users Chart     │ │   │
│  │  │  Pie Chart   │  │   - Activity      │ │   │
│  │  │              │  │   - Growth        │ │   │
│  │  └──────────────┘  └──────────────────┘ │   │
│  └─────────────────────────────────────────┘   │
│                                                   │
│  ┌─────────────────────────────────────────┐   │
│  │  COLLABORATIVE FILTERING                 │   │
│  │  - Matrix Status + Update Button         │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

## 🎨 Color Scheme (Đồng Bộ)

### Primary Colors (từ index.css)
```css
--accent-primary: #c24482;     /* Pink chính */
--accent-secondary: #fd662f;   /* Orange phụ */
--grad-hero: linear-gradient(135deg, #fffbff 0%, #fbe4f2 100%);
--grad-primary: linear-gradient(135deg, #c24482 0%, #f4a4c6 100%);
```

### Chart Colors
```css
/* Thay đổi từ */
background: #4CAF50; /* Green */
background: #2196F3; /* Blue */
background: #FF9800; /* Orange */

/* Sang */
background: linear-gradient(135deg, #c24482, #f4a4c6); /* Pink gradient */
background: linear-gradient(135deg, #fd662f, #ff9472); /* Orange gradient */
background: linear-gradient(135deg, #e91e63, #f48fb1); /* Deep pink */
```

### Button Colors
```css
.btn-primary {
  background: var(--grad-primary);
  /* Pink gradient */
}

.bg-purple → .bg-pink-deep {
  background: linear-gradient(135deg, #e91e63, #f06292);
}

.bg-cyan → .bg-pink-light {
  background: linear-gradient(135deg, #f48fb1, #fce4ec);
}
```

## 📊 Charts Mới Cần Thêm

### 1. Countries Distribution (Pie Chart)
```javascript
// Top 10 countries by destination count
const countryStats = {};
destinations.forEach(d => {
  const country = d.Country;
  countryStats[country] = (countryStats[country] || 0) + 1;
});

const topCountries = Object.entries(countryStats)
  .sort((a, b) => b[1] - a[1])
  .slice(0, 10);

// SVG Pie Chart với màu pink shades
```

### 2. Rules Confidence Chart
```javascript
// Top 10 rules by confidence
const topRules = rules
  .sort((a, b) => b.confidence - a.confidence)
  .slice(0, 10);

// Horizontal bar chart với gradient pink
```

### 3. Users Growth/Activity
```javascript
// Nếu có timestamp, show growth over time
// Nếu không, show activity distribution

// Line chart hoặc bar chart với pink theme
```

## 🔧 Implementation Steps

### Step 1: Tái cấu trúc Layout Container

Trong `AdminPage.js`, thay đổi phần visualization:

```jsx
{/* K-Means + Cluster Section */}
<div className="clustering-section admin-card glass-panel">
  <h2 className="section-title font-heading">
    Phân Cụm Địa Điểm (K-Means Clustering)
  </h2>
  
  <div className="clustering-grid">
    {/* Left: Control Panel */}
    <div className="control-panel">
      <div className="param-group">
        <label>Số lượng Cụm (K): <code>{nClusters}</code></label>
        <input type="range" min="3" max="8" value={nClusters} 
          onChange={(e) => setNClusters(parseInt(e.target.value))} />
      </div>
      <button className="btn-primary" onClick={handleRunClustering}>
        {actionLoading.clustering ? 'Đang chạy...' : 'Chạy K-Means'}
      </button>
    </div>
    
    {/* Right: Visualization */}
    <div className="cluster-visualization">
      {/* Bar charts + Cost cards */}
    </div>
  </div>
</div>
```

### Step 2: Thêm Countries Chart

```jsx
<div className="countries-section admin-card glass-panel">
  <h2 className="section-title">Phân Bố Quốc Gia</h2>
  <div className="countries-chart">
    {/* Pie chart showing top countries */}
    <svg viewBox="0 0 200 200">
      {/* Render pie segments with pink shades */}
    </svg>
    <div className="countries-legend">
      {/* Legend items */}
    </div>
  </div>
</div>
```

### Step 3: Thêm Rules Visualization

```jsx
<div className="apriori-section admin-card glass-panel">
  <h2 className="section-title">Khai Phá Luật Kết Hợp (Apriori)</h2>
  
  <div className="apriori-grid">
    {/* Left: Control Panel */}
    <div className="control-panel">
      {/* Parameters sliders */}
      <button className="btn-primary" onClick={handleRunApriori}>
        Chạy Apriori
      </button>
    </div>
    
    {/* Right: Top Rules Chart */}
    <div className="rules-chart">
      {/* Horizontal bars showing confidence/lift */}
    </div>
  </div>
</div>
```

### Step 4: Update CSS Colors

In `AdminPage.css`, replace hardcoded colors:

```css
/* Old */
background: #4CAF50;
background: #2196F3;
border-left: 3px solid #9C27B0;

/* New */
background: linear-gradient(135deg, var(--accent-primary), #f4a4c6);
background: linear-gradient(135deg, #fd662f, #ff9472);
border-left: 3px solid var(--accent-primary);
```

Search and replace:
- `#4CAF50` → `var(--accent-primary)` (green to pink)
- `#2196F3` → `var(--accent-secondary)` (blue to orange)
- `#9C27B0` → `var(--accent-primary)` (purple to pink)
- `#FF5722` → `var(--accent-secondary)` (red to orange)

## 📝 Detailed CSS Classes

### New Layout Classes

```css
/* Clustering section with side-by-side layout */
.clustering-section {
  margin-bottom: 30px;
}

.clustering-grid {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 30px;
  margin-top: 20px;
}

.control-panel {
  background: var(--grad-hero);
  padding: 24px;
  border-radius: 16px;
  border: 1px solid rgba(194, 68, 130, 0.1);
}

.cluster-visualization {
  /* Charts go here */
}

/* Apriori section */
.apriori-section {
  margin-bottom: 30px;
}

.apriori-grid {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 30px;
  margin-top: 20px;
}

/* Countries + Users section */
.system-stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-bottom: 30px;
}

/* Responsive */
@media (max-width: 1100px) {
  .clustering-grid,
  .apriori-grid {
    grid-template-columns: 1fr;
  }
  
  .system-stats-grid {
    grid-template-columns: 1fr;
  }
}
```

### Updated Button Styles

```css
.btn-primary {
  background: var(--grad-primary);
  border: none;
  color: white;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(194, 68, 130, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}
```

## 🎯 Expected Outcome

### Visual Consistency
✅ Tất cả màu sắc theo pink theme
✅ Gradient buttons đồng bộ
✅ Chart colors harmonious

### Better UX
✅ K-Means control + visualization cùng screen
✅ Immediate feedback khi chạy algorithm
✅ Data visualization thay vì tables

### Information Architecture
✅ Grouped by function (clustering, rules, stats, CF)
✅ Progressive disclosure (overview → details)
✅ Clear visual hierarchy

## ✅ Checklist

- [ ] Move K-Means control next to cluster charts
- [ ] Add Countries pie chart
- [ ] Add Rules bar chart
- [ ] Add Users activity chart
- [ ] Replace all green/blue with pink/orange
- [ ] Update button styles
- [ ] Update border colors
- [ ] Update gradient backgrounds
- [ ] Test responsive breakpoints
- [ ] Verify all charts render correctly
- [ ] Check color contrast for accessibility

## 🚀 Quick Start

1. **Backup current file**: `cp AdminPage.js AdminPage.js.backup`
2. **Update layout structure** theo diagram trên
3. **Add chart components** cho Countries/Rules
4. **Replace colors** trong CSS
5. **Test** trên các breakpoints
6. **Polish** animations và transitions

Good luck! 🎨✨

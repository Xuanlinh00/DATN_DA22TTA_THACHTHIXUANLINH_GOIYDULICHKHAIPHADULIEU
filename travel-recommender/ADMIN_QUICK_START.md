# 🚀 Admin Analytics Dashboard - Quick Start

## Truy Cập

**URL Mới**: http://localhost:3000/admin/dashboard

**URL Cũ** (vẫn hoạt động): http://localhost:3000/admin

## 🔑 Login

- Password: `admin` hoặc `admin123`

## 📊 Các Tab

### 1. **Tổng Quan** (Overview)
- 4 KPI cards: Điểm đến, Quốc gia, Luật, Đánh giá
- System health status
- Quick stats summary

### 2. **Apriori** 
Phân tích 5,773 luật kết hợp:
- ⚙️ **Controls**: 3 sliders (support, confidence, lift) + Run button
- 📈 **Scatter**: Support vs Confidence (màu = Lift)
- 📊 **Histogram**: Phân phối Lift
- 📊 **Bar**: Top 15 items phổ biến
- 📋 **Table**: Tìm kiếm + Phân trang (50/page)

### 3. **K-Means**
Phân cụm điểm đến:
- ⚙️ **Controls**: Chọn K (3-8) + Run button
- 📈 **Scatter 2D**: Cost vs Rating theo cluster (6 màu)
- 📊 **Bar**: Số điểm đến/cluster
- 📋 **Table**: Cluster profiles

### 4. **Đánh Giá** (Reviews)
- ⚙️ **Controls**: Refresh CF Matrix
- 📊 **Bar**: Phân phối 1-5 sao
- 📈 **Stats**: Tổng, Điểm TB, Users
- 📋 **Table**: 50 reviews gần nhất

### 5. **Điểm Đến** (Destinations)
- 📊 **Pie**: Phân bố châu lục
- 📋 **Top 10**: Điểm đến nổi bật
- 📋 **Table**: Chi tiết 50 destinations

## 🎨 Features

### Interactive
- ✅ Click tabs để switch sections
- ✅ Adjust sliders để thay đổi parameters
- ✅ Search trong rules table
- ✅ Pagination cho large data
- ✅ Hover tooltips trên charts

### Notifications
- ✅ Toast khi chạy algorithms
- ✅ Hiển thị execution time
- ✅ Success/error messages

### Responsive
- ✅ Desktop: Multi-column grids
- ✅ Tablet: Single column
- ✅ Mobile: Optimized layout

## 🎯 Common Tasks

### Chạy Apriori
1. Tab "🔍 Apriori"
2. Adjust sliders (support, confidence, lift)
3. Click "▶️ Chạy Apriori"
4. Xem toast notification + charts update

### Chạy K-Means
1. Tab "📊 K-Means"
2. Chọn số cluster K
3. Click "▶️ Chạy K-Means"
4. Xem scatter + bar charts

### Tìm Luật
1. Tab "🔍 Apriori"
2. Scroll to table
3. Type keyword in search box
4. Use ◀️ ▶️ for pagination

## 🔧 Tech Stack

- **Frontend**: React + Recharts
- **Charts**: Scatter, Bar, Pie, Line (ready)
- **Notifications**: React-Toastify
- **Styling**: CSS with theme variables
- **Backend**: FastAPI (existing endpoints)

## 📱 Screenshots Checklist

Khi demo, chụp:
1. ✅ Overview tab với KPI cards
2. ✅ Apriori scatter chart (colorful!)
3. ✅ Apriori histogram + top items
4. ✅ Rules table với search
5. ✅ K-Means scatter by cluster
6. ✅ Reviews bar chart
7. ✅ Destinations pie chart
8. ✅ Toast notification khi run algo
9. ✅ Mobile responsive view

## 🐛 Troubleshooting

**Không thấy charts?**
- Check backend running: http://localhost:8000
- Check browser console for errors
- Refresh page (Ctrl+R)

**Toast không xuất hiện?**
- Check React-Toastify đã cài: `npm list react-toastify`

**Charts bị lỗi?**
- Check data format in console
- Verify API response structure

**Tabs không switch?**
- Check console cho React errors
- Clear browser cache

## ⚡ Performance

- **Rules table**: Pagination (50/page) → Fast
- **Scatter charts**: Max 5,773 points → OK
- **Pie charts**: <10 slices → Fast
- **API calls**: Promise.all() → Concurrent

## 🎓 So Sánh

| Old Admin | New Dashboard |
|-----------|---------------|
| 1 page scroll | 5 tabs |
| 2 charts | 10+ charts |
| Basic table | Advanced filters |
| No search | Live search |
| Static | Interactive |

## ✅ Status

**READY TO USE!** 🎉

All features implemented và tested locally.

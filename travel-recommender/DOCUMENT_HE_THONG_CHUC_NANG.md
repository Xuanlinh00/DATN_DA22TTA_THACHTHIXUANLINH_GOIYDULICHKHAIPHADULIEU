# TÀI LIỆU CHỨC NĂNG HỆ THỐNG KẾ HỆ THỐNG THỐNG GỢI Ý DU LỊCH

> **Đồ án**: Khai phá Dữ liệu Du lịch  
> **Giảng viên hướng dẫn**: ThS. Phạm Thị Trúc Mai  
> **Sinh viên thực hiện**: Thạch Thị Xuân Linh - DA22TTA - 110122013

---

## MỤC LỤC

1. [Tổng Quan Hệ Thống](#1-tổng-quan-hệ-thống)
2. [Giao Diện Người Dùng](#2-giao-diện-người-dùng)
3. [Giao Diện Quản Trị](#3-giao-diện-quản-trị)
4. [Thành Phần Chung](#4-thành-phần-chung)
5. [Tính Năng Đặc Biệt](#5-tính-năng-đặc-biệt)

---

## 1. TỔNG QUAN HỆ THỐNG

### 1.1. Kiến trúc ứng dụng
- **Frontend**: React.js với Material Design 3
- **Backend**: Python FastAPI
- **Database**: MongoDB
- **AI/ML**: Gemini AI, Apriori, K-Means, Collaborative Filtering
- **Maps**: Leaflet.js
- **Charts**: Recharts

### 1.2. Các route chính

| Route | Mô tả |
|-------|-------|
| `/` | Trang chủ với gợi ý cá nhân hóa |
| `/destinations` | Danh sách điểm đến |
| `/destinations/:name` | Chi tiết điểm đến |
| `/map` | Bản đồ tương tác |
| `/recommend` | Wizard gợi ý 3 bước |
| `/login` | Đăng nhập |
| `/register` | Đăng ký tài khoản |
| `/forgot-password` | Quên mật khẩu |
| `/reset-password/:token` | Đặt lại mật khẩu |
| `/change-password` | Đổi mật khẩu |
| `/admin` | Dashboard quản trị cũ |
| `/admin/dashboard` | Dashboard quản trị mới |

---

## 2. GIAO DIỆN NGƯỜI DÙNG

### 2.1. **TRANG CHỦ** (`HomePage.js`)

#### 2.1.1. Header & Navigation
- **Logo thương hiệu**: Nâu Travel với hình ảnh đặc trưng
- **Menu điều hướng**:
  - Trang chủ
  - Điểm Đến
  - Bản Đồ
  - Gợi Ý
- **Chuyển đổi ngôn ngữ**: Hỗ trợ 3 ngôn ngữ (VI/EN/中文)
- **Dropdown tài khoản**:
  - Hiển thị tên người dùng khi đăng nhập
  - Menu: Gợi Ý Của Tôi, Đổi Mật Khẩu, Thống Kê Hệ Thống, Đăng Xuất
  - Khi chưa đăng nhập: Đăng Nhập, Đăng Ký

#### 2.1.2. Hero Section (Phần giới thiệu)

- **Bố cục Split Screen**:
  - **Bên trái**: Nội dung text với hiệu ứng glass morphism
    - Tiêu đề gradient: "Gợi ý điểm đến du lịch quốc tế"
    - Phụ đề giải thích hệ thống AI
    - Nút CTA: "Gợi ý cá nhân hóa ✨"
  - **Bên phải**: Hình ảnh blob-shape với các floating cards
    - Card AI Insight: Hiển thị điểm đến hot nhất theo mùa
    - Card điểm đến nổi bật: Tên + quốc gia
    - Card avatar người dùng: Hiển thị cộng đồng

#### 2.1.3. Recommendations Section
- **Gợi ý cá nhân hóa** (khi đăng nhập):
  - Sử dụng Collaborative Filtering
  - Badge: "🤖 Gợi ý dành riêng cho bạn"
  - Lời chào cá nhân: "👋 Xin chào, [Tên người dùng]!"
  - Mô tả: Dựa trên sở thích và lịch sử

- **Gợi ý theo mùa** (khi chưa đăng nhập):
  - Badge: "⭐ Gợi ý theo mùa"
  - Tiêu đề: Mùa hiện tại (Xuân/Hạ/Thu/Đông)
  - Mô tả: Điểm đến lý tưởng cho thời điểm hiện tại

- **Masonry Grid Layout**:
  - Hiển thị tối đa 8 điểm đến
  - Mỗi card có rank, hình ảnh, tên, quốc gia
  - Nút "Xem tất cả điểm đến" để chuyển sang `/destinations`

#### 2.1.4. Live Stats Counter
- **3 KPI Cards**:
  - 🗺️ Tổng số điểm đến
  - 🌍 Tổng số quốc gia
  - 📋 Tổng số luật Apriori
- Hiển thị số liệu thực từ database

#### 2.1.5. CTA Banner
- Kêu gọi hành động: "Bắt đầu hành trình của bạn"
- Mô tả: "Chỉ mất 30 giây trả lời 3 câu hỏi..."
- 2 nút:
  - "✨ Nhận gợi ý ngay" → chuyển đến `/recommend`
  - "🗺️ Khám phá bản đồ" → chuyển đến `/destinations`

#### 2.1.6. Footer
- Logo Nâu Travel
- Links: Bảo mật, Điều khoản, Hỗ trợ, Điểm đến
- Thông tin sinh viên và giảng viên

---

### 2.2. **TRANG ĐIỂM ĐẾN** (`DestinationsPage.js`)

#### 2.2.1. Header Section

- **Tiêu đề chính**: "Hành Trình Độc Bản"
- **Phụ đề**: Giới thiệu về bộ sưu tập điểm đến được chọn lọc

#### 2.2.2. Tìm kiếm Live Search
- **Thanh tìm kiếm**:
  - Icon search
  - Placeholder: "Tìm kiếm điểm đến, quốc gia..."
  - Debounce 400ms để tránh spam API
  - Nút clear (X) khi có nội dung
- **Tính năng**:
  - Dịch tự động từ tiếng Việt sang tiếng Anh (translateSearchQuery)
  - Tìm kiếm song song nhiều terms
  - Merge và dedupe kết quả
  - Highlight từ khóa đang tìm

#### 2.2.3. Bộ lọc FilterPanel (sidebar)
- **Layout**: Sticky sidebar bên phải (desktop), drawer trên mobile
- **Các bộ lọc**:
  - **Mùa du lịch**: Spring/Summer/Autumn/Winter
  - **Ngân sách**: Budget/Moderate/Expensive/Luxury
  - **Loại hình**: Beach, Mountain, Cultural, City, Adventure, Wellness, Nature, Theme Park
  - **Quốc gia**: Dropdown danh sách quốc gia
- **Tính năng**:
  - Real-time filtering
  - Reset all filters button
  - Hiển thị số lượng active filters

#### 2.2.4. Danh sách điểm đến
- **Layout**: Masonry grid responsive
- **Destination Card** hiển thị:
  - Hình ảnh chất lượng cao
  - Tên điểm đến (stripped display name)
  - Quốc gia (có dịch)
  - Type badge
  - Rating sao
  - Chi phí trung bình
  - Mùa tốt nhất
- **Pagination**: Load 50 items đầu tiên
- **Empty state**: Hiển thị khi không có kết quả

#### 2.2.5. Desktop vs Mobile
- **Desktop**: 
  - Sidebar cố định
  - Grid 3-4 cột
- **Mobile**:
  - Floating drawer filter
  - Grid 1-2 cột
  - Hamburger menu

---

### 2.3. **CHI TIẾT ĐIỂM ĐẾN** (`DestinationDetailPage.js`)

#### 2.3.1. Hero Image Section

- **Large Hero Image**: Full-width với gradient overlay
- **Breadcrumb navigation**: Điểm Đến > [Quốc gia] > [Tên điểm đến]
- **Title overlay**:
  - Tên điểm đến lớn
  - Quốc gia + cờ
  - Type badge

#### 2.3.2. Thông tin chi tiết
- **Overview section**:
  - **Mô tả chi tiết**: Paragraph dài, có thể expand/collapse
  - **Quick facts grid**:
    - ⭐ Rating trung bình
    - 💵 Chi phí mỗi ngày (USD)
    - 🗓️ Mùa tốt nhất
    - 🌍 Châu lục
    - 🏷️ Budget category
    - 🏅 UNESCO badge (nếu có)
  - **Latitude/Longitude**: Tọa độ chính xác

#### 2.3.3. Interactive Elements
- **Nút hành động**:
  - "📍 Xem trên Bản Đồ" → chuyển đến `/map` và focus vào điểm đó
  - "✨ Tìm điểm đến tương tự"
  - "💬 Hỏi AI về điểm này" → mở chatbot với context

#### 2.3.4. Climate Chart
- **ClimateChart Component**: 
  - Biểu đồ nhiệt độ và lượng mưa theo tháng
  - Line chart + Bar chart kết hợp
  - Responsive với Recharts

#### 2.3.5. Related Destinations
- **Carousel/Grid**: 4-6 điểm đến tương tự
- **Tiêu chí**:
  - Cùng quốc gia
  - Cùng type
  - Cùng cluster (K-Means)
  - Xuất phát từ Apriori rules

#### 2.3.6. Reviews Section (nếu có)
- Hiển thị rating distribution
- User reviews list
- Form đánh giá (khi đăng nhập)

---

### 2.4. **BẢN ĐỒ TƯƠNG TÁC** (`WorldMapPage.js`)

#### 2.4.1. Fullscreen Map
- **MapContainer (Leaflet)**:
  - Tile layer: Carto Light theme
  - Zoom controls
  - Custom pink pulsing markers
  - Popup on marker click

#### 2.4.2. Filter Sidebar (bên trái)
- **Header section**:
  - Icon 🔍
  - Title: "Lọc Điểm Đến"
  - Active filter chips (removable)
- **Filter controls**:
  - **Mùa du lịch**: Dropdown với emoji
  - **Ngân sách**: Dropdown
  - **Loại hình du lịch**: Dropdown
  - **Quốc gia**: Dropdown
- **Results footer**:
  - Số điểm đến hiển thị trên bản đồ
  - Loading indicator
  - "Xóa tất cả bộ lọc" button

#### 2.4.3. Interactive Markers

- **Custom Icon**: Pink pulsing marker với animation
- **Selected marker**: Larger với stronger pulse
- **Click event**: 
  - Pan + zoom to marker
  - Show destination card (bottom)

#### 2.4.4. Destination Card (bottom overlay)
- **Hiển thị khi click marker**:
  - Hình ảnh thumbnail (180px width)
  - Type badge
  - Tên + quốc gia
  - Meta info: Mùa, rating, chi phí
  - Mô tả ngắn (2 dòng)
- **Action buttons**:
  - "Xem Chi Tiết" → navigate to detail page
  - "Chỉ Đường" → open Google Maps directions
- **Close button**: X ở góc trên bên phải

#### 2.4.5. MapFlyTo Component
- Smooth pan/zoom animation khi selected destination thay đổi
- Duration: 1.2s
- Zoom level: 6

#### 2.4.6. Real-time Filter
- Load 150 items đầu tiên
- Filter client-side trước khi render markers
- Auto-select first result và fly to it
- Loading overlay khi đang fetch data

---

### 2.5. **WIZARD GỢI Ý** (`RecommendPage.js`)

#### 2.5.1. Progress Bar
- **4 Steps indicator**:
  - Mùa (🗓️)
  - Phong cách (🎒)
  - Ngân sách (💰)
  - Kết quả (✨)
- **Visual states**: 
  - Completed (✓)
  - Active (số step)
  - Pending (số step mờ)

#### 2.5.2. Step 1: Chọn Mùa
- **Title**: "Bạn muốn đi du lịch vào mùa nào?"
- **4 Option Cards**:
  - Spring (🌸): Xuân - Tháng 1-3, Tết, lễ hội
  - Summer (☀️): Hạ - Tháng 4-6, Biển, nghỉ hạ
  - Autumn (🍂): Thu - Tháng 7-9, Lúa vàng
  - Winter (❄️): Đông - Tháng 10-12, Giáng Sinh
- **Navigation**: 
  - "Tiếp theo →" button (disabled nếu chưa chọn)

#### 2.5.3. Step 2: Chọn Phong Cách
- **Title**: "Bạn thích phong cách du lịch nào?"
- **8 Option Cards**:
  - 🏖️ Biển & Đảo
  - 🏔️ Núi & Rừng
  - 🏛️ Văn Hoá & Lịch Sử
  - 🏙️ Thành Phố
  - 🪂 Phiêu Lưu
  - 🧘 Nghỉ Dưỡng
  - 🌿 Thiên Nhiên
  - 🎡 Vui Chơi
- **Navigation**: 
  - "← Quay lại" button
  - "Tiếp theo →" button

#### 2.5.4. Step 3: Chọn Ngân Sách
- **Title**: "Ngân sách mỗi ngày của bạn là bao nhiêu?"
- **4 Budget Options**:
  - 💚 Tiết Kiệm: < $50/ngày
  - 💛 Bình Dân: $50-$150/ngày
  - 🧡 Cao Cấp: $150-$300/ngày
  - 💎 Sang Trọng: > $300/ngày
- **Navigation**: 
  - "← Quay lại" button
  - "✨ Tìm điểm đến phù hợp" button

#### 2.5.5. Step 4: Kết Quả

- **Results Header**:
  - Emoji ✈️
  - Title: "X Điểm Đến Dành Riêng Cho Bạn"
  - Subtitle: Giải thích về selection
  - **Selection Pills**: Hiển thị các lựa chọn (mùa, phong cách, ngân sách)

- **Results Grid**:
  - Layout: 2-3 cột responsive
  - **Destination Result Card**:
    - Hình ảnh với rank badge (🥇🥈🥉)
    - Rating badge
    - Type chip
    - Tên + quốc gia
    - Chi phí/ngày
    - **Emotional Tagline**: Câu gợi ý cảm xúc được tạo động theo:
      - Destination type (beach/mountain/cultural...)
      - User preferences (season/budget)
      - Stable seed (tên điểm đến) để luôn nhất quán
    - Info pills: Mùa tốt nhất, UNESCO badge

- **Loading State**: 
  - Spinner
  - Text: "Đang phân tích với thuật toán Hybrid Recommender..."

- **Empty State**:
  - Icon 🔍
  - "Không tìm thấy điểm đến phù hợp"
  - Gợi ý thay đổi tiêu chí

- **Navigation**:
  - "🔄 Tìm kiếm lại với tiêu chí khác" button

#### 2.5.6. Context Update
- **Recommendation Context**: 
  - Cập nhật RecommendationContext khi có kết quả
  - Lưu user preferences (nếu đăng nhập)
  - Chatbot sẽ nhận được context này để trả lời chính xác hơn

#### 2.5.7. Backend Integration
- **API Call**: `/api/recommendations/filtered`
- **Payload**: 
  - season, category, budget, limit=12
- **Response**: 
  - recommendations: Danh sách điểm đến
  - matched_rules: Apriori rules đã match
  - success flag

---

### 2.6. **XÁC THỰC & TÀI KHOẢN**

#### 2.6.1. Đăng Nhập (`LoginPage.js`)
- **Form fields**:
  - Tên đăng nhập (với icon person)
  - Mật khẩu (với icon lock)
- **Links**:
  - "Quên mật khẩu?" → `/forgot-password`
  - "Đăng ký ngay" → `/register`
- **Error handling**:
  - Alert với animation shake
  - Gợi ý đăng ký nếu tài khoản không tồn tại
- **Loading state**: Spinner trong button
- **Success**: Navigate về trang chủ

#### 2.6.2. Đăng Ký (`RegisterPage.js`)
- **Form fields**:
  - Họ tên đầy đủ
  - Tên đăng nhập (unique)
  - Email
  - Mật khẩu
  - Xác nhận mật khẩu
- **Validation**:
  - Password strength indicator
  - Email format check
  - Username availability check
  - Password match
- **Success**: Navigate to login

#### 2.6.3. Quên Mật Khẩu (`ForgotPasswordPage.js`)

- **Form fields**:
  - Email address
- **Process**:
  - Gửi email với reset token
  - Hiển thị success message
  - Link trong email → `/reset-password/:token`

#### 2.6.4. Đặt Lại Mật Khẩu (`ResetPasswordPage.js`)
- **Form fields**:
  - Mật khẩu mới
  - Xác nhận mật khẩu
- **Token validation**: 
  - Kiểm tra token từ URL params
  - Hiển thị lỗi nếu token hết hạn/không hợp lệ
- **Success**: Navigate to login

#### 2.6.5. Đổi Mật Khẩu (`ChangePasswordPage.js`)
- **Yêu cầu**: Phải đăng nhập
- **Form fields**:
  - Mật khẩu hiện tại
  - Mật khẩu mới
  - Xác nhận mật khẩu mới
- **Validation**: Kiểm tra mật khẩu cũ
- **Success**: Toast notification

---

## 3. GIAO DIỆN QUẢN TRỊ

### 3.1. **ADMIN PAGE** (`AdminPage.js`)

#### 3.1.1. Xác thực Admin
- **Login screen**:
  - Password input (admin / admin123)
  - Glass panel design
  - Session storage để duy trì phiên
- **Logout**: Xóa session và quay về login

#### 3.1.2. Header Dashboard
- **Title**: "Hệ Thống Thống Kê & Khai Phá Dữ Liệu"
- **Subtitle**: Giới thiệu các thuật toán
- **Logout button**: Góc trên bên phải

#### 3.1.3. KPI Cards (4 cards)
- **1. Điểm Đến**: 
  - Icon 🗺️
  - Số lượng total_destinations
  - Click để mở modal danh sách
- **2. Quốc Gia**:
  - Icon 🌍
  - Số lượng total_countries
  - Click để mở modal danh sách countries
- **3. Luật Apriori**:
  - Icon 📋
  - Số lượng rules
  - Click để mở modal danh sách rules
- **4. Người Dùng / Đánh Giá**:
  - Icon ⭐
  - Format: "X U / Y R"
  - Click để mở modal users + ratings

#### 3.1.4. Tabs Navigation
- **📊 Thống kê Tổng Quan** (overview)
- **🔍 Luật Kết Hợp Apriori** (apriori)
- **🗂️ Phân Cụm K-Means** (kmeans)
- **⭐ Đánh Giá** (reviews)
- **📍 Quản Lý Điểm Đến** (destinations)
- **👥 Quản Lý Tài Khoản** (users)

---

### 3.2. **TAB THỐNG KÊ TỔNG QUAN**

#### 3.2.1. Biểu đồ Phân Bố
- **Phân Bố Châu Lục** (PieChart):
  - Asia, Europe, Americas, Africa, Oceania
  - Màu sắc riêng biệt cho mỗi châu lục
  - Label với phần trăm
- **Phân Bố Theo Mức Chi Phí** (BarChart):
  - Budget (💚), Moderate (💙), Expensive (🧡), Luxury (💎)
  - Tooltip hiển thị số lượng

#### 3.2.2. Trạng Thái Thuật Toán
- **Health Indicators**:
  - Luật kết hợp Apriori: Badge "Hoạt động (X luật)"
  - Phân cụm K-Means: Badge "Đã chia X cụm"
  - Lọc cộng tác (CF): Badge "Đã tạo ma trận"

#### 3.2.3. Dữ Liệu Đánh Giá
- Đánh giá thực tế: Số lượng
- Đánh giá mô phỏng: Số lượng
- Người dùng đã đăng ký: Số lượng

---

### 3.3. **TAB LUẬT APRIORI**

#### 3.3.1. Control Panel

- **Sliders để điều chỉnh tham số**:
  - **Min Support**: 0.005 - 0.05 (step 0.005)
  - **Min Confidence**: 0.05 - 0.5 (step 0.05)
  - **Min Lift**: 0.5 - 2.0 (step 0.1)
- **Button "▶️ Chạy Apriori"**: 
  - Loading state khi đang chạy
  - Hiển thị duration (giây)
  - Toast notification với kết quả
  - So sánh với lần chạy trước (+/- X luật)

#### 3.3.2. Biểu Đồ Phân Tích
- **Support vs Confidence (ScatterChart)**:
  - X-axis: Support %
  - Y-axis: Confidence %
  - Color: Lift value
  - Tooltip: Chi tiết rule

- **Phân Phối Lift (BarChart)**:
  - Bins: 0-0.5, 0.5-1, 1-1.5, ... 5-10
  - Y-axis: Số lượng rules
  - Màu gradient theo lift value

- **Top 15 Items Phổ Biến (BarChart horizontal)**:
  - Các item xuất hiện nhiều nhất trong rules
  - X-axis: Số lần xuất hiện
  - Y-axis: Tên item (150px width)

#### 3.3.3. Rules Table
- **Search bar**: Tìm kiếm rules theo text
- **Sort controls**:
  - Sortable columns: Support, Confidence, Lift, Recommendation Score
  - Asc/Desc toggle
- **Pagination**:
  - 15 rules per page
  - Previous/Next buttons
  - Page indicator
- **Table columns**:
  - # (STT)
  - Luật (monospace font)
  - Support (%)
  - Confidence (%)
  - Lift (rounded 2 decimals)

#### 3.3.4. Run Comparison
- Hiển thị thời gian chạy
- So sánh số luật với lần trước
- Timestamp

---

### 3.4. **TAB PHÂN CỤM K-MEANS**

#### 3.4.1. Control Panel
- **Slider chọn K**: 3-8 clusters
- **Button "▶️ Chạy K-Means"**:
  - Loading state
  - Toast notification kết quả
  - Refresh cluster profiles

#### 3.4.2. Elbow Chart (nếu có dữ liệu)
- **LineChart**: SSE vs K
- Giúp xác định K tối ưu
- X-axis: Số cụm (K)
- Y-axis: SSE (Sum of Squared Errors)

#### 3.4.3. Biểu Đồ Phân Tích
- **Cost vs Rating theo Cluster (ScatterChart)**:
  - X-axis: Chi phí (USD/day)
  - Y-axis: Rating
  - Color: Cluster ID
  - Tooltip: Destination name
  - Legend: Cluster 0, Cluster 1, ...

- **Số Điểm Đến theo Cluster (BarChart)**:
  - X-axis: Cluster name (Cost_Level)
  - Y-axis: Số lượng
  - Màu tím

#### 3.4.4. Cluster Profiles Table
- **Columns**:
  - Cluster # (ID)
  - Loại (Cost_Level badge)
  - Số Điểm (Size)
  - Chi Phí TB (Avg_Cost_Per_Day)
- **Data source**: cluster_profiles từ stats API

---

### 3.5. **TAB ĐÁNH GIÁ**

#### 3.5.1. Control Panel
- **Button "🔄 Refresh CF Matrix"**:
  - Cập nhật Collaborative Filtering matrix
  - Toast notification
  - Reload stats

#### 3.5.2. Biểu Đồ Phân Tích
- **Phân Phối Rating (BarChart)**:
  - X-axis: 1⭐, 2⭐, 3⭐, 4⭐, 5⭐
  - Y-axis: Số lượng đánh giá
  - Màu xanh lá

- **Đánh Giá Thực vs Mô phỏng (PieChart)**:
  - Real ratings (màu hồng)
  - Simulated ratings (màu cam)
  - Legend + Tooltip

- **Timeline Đánh Giá Theo Tháng (LineChart)**:
  - X-axis: Tháng (YYYY-MM)
  - Y-axis: Số đánh giá
  - Line smooth

#### 3.5.3. Ratings Table
- **Columns**:
  - User ID
  - Destination Name
  - Rating (⭐)
  - Timestamp
  - Action: Delete button (⚠️ với confirm)
- **Pagination**: 50 items per view
- **Filter**: By user_id, destination

---

### 3.6. **TAB QUẢN LÝ ĐIỂM ĐẾN**

#### 3.6.1. Toolbar
- **Button "➕ Thêm Điểm Đến Mới"**: Mở modal thêm
- **Search bar**: Tìm theo tên, quốc gia, type

#### 3.6.2. Destinations Table
- **Columns**:
  - Thumbnail (hình ảnh)
  - Tên Điểm Đến
  - Quốc Gia
  - Châu Lục
  - Type
  - Mùa Tốt Nhất
  - Chi Phí (USD/day)
  - Budget Category
  - Rating
  - Cluster
  - Actions: Edit (✏️), Delete (🗑️)
- **Pagination**: 10 items per page
- **Sort**: By name, country, cost, rating

#### 3.6.3. Add/Edit Destination Modal
- **Form fields**:
  - Tên điểm đến (required)
  - Quốc gia (required)
  - Châu lục (dropdown: Asia, Europe, ...)
  - Type (dropdown: Beach, Mountain, ...)
  - Mùa tốt nhất (dropdown)
  - Chi phí trung bình (number input)
  - Budget category (dropdown)
  - Mô tả (textarea)
  - Latitude (number, optional)
  - Longitude (number, optional)
  
- **Image Upload Section**:
  - **Upload file**: File input cho upload local
  - **Auto-fetch button**: Tự động lấy ảnh từ Unsplash/Wikimedia
    - Dựa trên destination_name, country, type
  - **Preview**: Hiển thị ảnh hiện tại
  - **Delete image button**: Xóa ảnh

- **Actions**:
  - Save (Add hoặc Update)
  - Cancel

#### 3.6.4. Delete Destination
- Confirm dialog: "Bạn có chắc chắn muốn xóa điểm đến này?"
- Xóa tất cả references liên quan
- Toast notification

---

### 3.7. **TAB QUẢN LÝ TÀI KHOẢN**

#### 3.7.1. Users Table
- **Columns**:
  - Username
  - Full Name
  - Email
  - Trạng thái (Active / Locked badge)
  - Ngày đăng ký
  - Preferences (JSON compact view)
  - Actions:
    - Lock/Unlock (🔒/🔓)
    - Delete (🗑️)
- **Filter**: By username, email
- **Sort**: By date, username

#### 3.7.2. Lock/Unlock User
- Toggle button
- Confirm dialog
- Update database
- Toast notification
- Reload users list

#### 3.7.3. Delete User
- Confirm dialog: "Bạn có chắc chắn muốn xóa vĩnh viễn tài khoản này?"
- Cascade delete:
  - User record
  - User ratings
  - User preferences
  - Chat sessions
- Toast notification

---

### 3.8. **MODAL OVERLAYS**

#### 3.8.1. Destinations Modal
- Triggered by KPI card click
- **Search bar**: Filter destinations
- **List view**: Scrollable, virtualized
- Each item: Name, Country, Type
- Click item → Navigate to detail page

#### 3.8.2. Countries Modal
- Triggered by KPI card click
- **Search bar**: Filter countries
- **List view**: Unique countries sorted
- Click item → Filter destinations by country

#### 3.8.3. Rules Modal
- Triggered by KPI card click
- **Search bar**: Filter rules by text
- **List view**: Scrollable with pagination
- Each item: Rule string, Support, Confidence, Lift

#### 3.8.4. Users/Ratings Modal
- Triggered by KPI card click
- **Tabs**: Users / Ratings
- Users tab: List users with details
- Ratings tab: List ratings with filters

---

## 4. THÀNH PHẦN CHUNG

### 4.1. **NAVBAR** (`Navbar.js`)

#### 4.1.1. Desktop Layout
- **Logo**: Nâu Travel (trái)
- **Menu links** (giữa):
  - Trang chủ
  - Điểm Đến
  - Bản Đồ
  - Gợi Ý
- **Account dropdown** (phải):
  - Avatar chữ cái đầu (khi đăng nhập)
  - Dropdown menu:
    - Gợi Ý Của Tôi
    - Đổi Mật Khẩu
    - Thống Kê Hệ Thống
    - Đăng Xuất (màu đỏ)
  - Khi chưa đăng nhập:
    - Đăng Nhập
    - Đăng Ký
    - Thống Kê Hệ Thống

#### 4.1.2. Mobile Layout
- **Hamburger menu button**: Toggle mobile menu
- **Mobile drawer**: Slide-in từ trên xuống
  - Tất cả menu items
  - Account info
  - Logout button

#### 4.1.3. Scroll Effect
- Transparent → Solid background khi scroll > 50px
- Shadow effect
- Smooth transition

---

### 4.2. **CHATBOT WIDGET** (`ChatbotWidget.js`)

#### 4.2.1. Floating Button
- Fixed bottom-right
- Pink gradient background
- Icon: auto_awesome
- Pulse animation khi có thông báo
- Badge count (nếu có unread)

#### 4.2.2. Chat Window
- **Header**:
  - Avatar (chữ cái đầu nếu đăng nhập, AI icon nếu guest)
  - Title: Session title hoặc "NÂU AI"
  - Status: "Online" badge (green dot)
  - Actions:
    - New chat button (➕)
    - History button (📜)
    - Size selector (S/M/L)
    - Close button (✕)

- **Messages Area**:
  - Scrollable container
  - User messages: Right-aligned, blue background
  - Bot messages: Left-aligned, gray background
  - **Message types**:
    - Text message (supports **bold** and *italic* markdown)
    - Recommendations cards (horizontal scroll)
    - Context message (auto-injected với badge)
  - Auto-scroll to bottom

- **Recommendations Cards**:
  - Horizontal scroll container
  - Each card:
    - Thumbnail image
    - Destination name
    - Country
    - Type badge
    - Rating + Cost
    - Click → Navigate to detail page

- **Input Area**:
  - Textarea (auto-resize)
  - Placeholder: "Hãy hỏi tôi về chuyến đi của bạn..."
  - Send button (disabled khi empty)
  - Loading state: Spinner trong input

- **Quick Prompts** (below input):
  - Pills layout, horizontal scroll
  - **Personalized prompts** (khi đăng nhập):
    - Dựa trên user preferences
    - Ví dụ: "✨ Gợi ý biển mùa hè cho tôi"
  - **Context-aware prompts** (khi viewing destination):
    - "🌤 Thời tiết tại [Destination]"
    - "🍜 Đặc sản ẩm thực tại [Destination]"
    - "🚌 Cách di chuyển đến [Destination]"
    - "📋 Lịch trình gợi ý đi [Destination]"
    - "💰 Chi phí du lịch tại [Destination]"
  - **Base prompts**:
    - "🗺 Gợi ý đi biển mùa hè, chi phí tiết kiệm"
    - "🏔 Tôi muốn đi du lịch núi..."
    - "⚖️ So sánh du lịch Thái Lan và Singapore"
    - ...
  - Click prompt → Auto-send

#### 4.2.3. Resize Handle
- Top-left corner drag handle
- Min size: 340x440
- Max size: 720x820 (hoặc viewport - 32px)
- Save size to localStorage
- Preset sizes: S (360x500), M (440x580), L (560x700)

#### 4.2.4. History Panel
- Overlay trên chat window
- **Header**: "Lịch sử trò chuyện", "Mới" button
- **Sessions list**:
  - Each session: Title, Timestamp, Active indicator
  - Click session → Switch active session
  - Hover: Delete button (🗑️)
- **Auto-generate title**: Từ first user message

#### 4.2.5. Session Management
- **Đăng nhập**: Sync sessions to MongoDB
- **Guest**: Store sessions in localStorage
- **Active session**: Persist in localStorage
- **Create new session**: Auto-generate ID
- **Delete session**: Confirm dialog

#### 4.2.6. Context Injection
- **Recommendation context**:
  - Auto-inject khi chatbot mở và có criteria từ RecommendPage
  - Hiển thị tiêu chí đã chọn
  - Danh sách điểm đến đã gợi ý
  - Badge: "Ngữ cảnh gợi ý"
  
- **Viewing destination context**:
  - Auto-inject khi chatbot mở và đang xem detail page
  - Gợi ý hỏi về điểm đến đó
  - Quick prompts cá nhân hóa

- **Fingerprint check**: Chỉ inject 1 lần cho mỗi context unique

#### 4.2.7. Backend Integration
- **API**: `/api/chat/message`
- **Payload**:
  - message: User text
  - history: Previous messages (filter bỏ context messages)
  - recommendation_context: {
    - criteria: { season, category, budget }
    - destinations: [...] (top 8)
    - matched_rules: [...]
    - currentViewingDestination: "..."
    - user_profile: { name, username, preferences }
  }
  - session_id: Current session ID
- **Response**:
  - response: Bot text (Gemini AI)
  - recommendations: [...] (nếu có)
  - success flag

---

### 4.3. **DESTINATION CARD** (`DestinationCard.js`)

#### 4.3.1. Card Layout
- **Hình ảnh**:
  - Full-width, aspect ratio 4:3
  - Gradient overlay
  - Rank badge (top-left nếu có)
  - Rating badge (top-right)

- **Content**:
  - Type chip (màu tương ứng)
  - Destination name (bold, large)
  - Country + flag
  - Description (2 dòng, ellipsis)
  - Info pills:
    - Mùa tốt nhất
    - UNESCO badge (nếu có)
    - Chi phí/ngày

- **Hover effect**:
  - Scale 1.02
  - Shadow increase
  - Brightness increase

- **Click**: Navigate to `/destinations/:name`

#### 4.3.2. Image Handling
- Sử dụng `imageService.js`:
  - `getDestinationImage(name, type, country)`
  - Fallback chain: Real landmarks → Category types → Country generic
- onError: `getFallbackImage(name, type)`

---

### 4.4. **FILTER PANEL** (`FilterPanel.js`)

#### 4.4.1. Inline Mode (Desktop)
- Sticky sidebar, glass morphism
- **Header**: "Lọc Điểm Đến"
- **Filters**: Dropdowns cho Season, Budget, Category, Country
- **Active filters chips**: Removable
- **Clear all button**: Khi có filters

#### 4.4.2. Drawer Mode (Mobile)
- Floating action button: "🔍 Lọc"
- Slide-in drawer từ bottom
- Same filter controls
- Apply button

#### 4.4.3. Real-time Update
- onChange: Call `onFilterChange(newFilters)`
- Parent component fetch data mới
- Loading state

---

### 4.5. **THEME SWITCHER** (`ThemeSwitcher.js`)

#### 4.5.1. Floating Button
- Fixed bottom-left
- Icon: light_mode / dark_mode
- Toggle onClick

#### 4.5.2. Theme Modes
- **Light mode**: Default
- **Dark mode**: 
  - Dark background
  - Light text
  - Adjusted colors
- Save preference to localStorage
- Apply CSS variables

---

### 4.6. **CLIMATE CHART** (`ClimateChart.js`)

#### 4.6.1. Data Source
- Monthly temperature (°C)
- Monthly rainfall (mm)
- Average values

#### 4.6.2. Chart Types
- **Line Chart**: Temperature trend
- **Bar Chart**: Rainfall
- **ComposedChart**: Combine both

#### 4.6.3. Responsive
- ResponsiveContainer
- Adjust height based on screen size
- Tooltip with formatted data

---

## 5. TÍNH NĂNG ĐẶC BIỆT

### 5.1. **ĐA NGÔN NGỮ**

#### 5.1.1. Ngôn ngữ hỗ trợ
- **Tiếng Việt** (VI): Default
- **English** (EN)
- **中文** (ZH): Tiếng Trung

#### 5.1.2. Translation Service
- `translator.js`:
  - `translateCountry(country)`: Dịch tên quốc gia
  - `translateCategory(category)`: Dịch loại hình du lịch
  - `translateSeason(season)`: Dịch mùa
  - `translateSearchQuery(query)`: Dịch từ khóa tìm kiếm (VI → EN)
  - `stripDisplayName(name)`: Loại bỏ số thứ tự trong tên
  - `fixDescription(desc, name)`: Sửa mô tả NaN hoặc không hợp lệ

#### 5.1.3. Language Switcher
- Dropdown trong header (HomePage)
- Save preference to localStorage key: `Nau_home_language`
- Apply translations cho:
  - UI labels
  - Seasons, Categories, Budgets
  - CTA buttons
  - Footer links

#### 5.1.4. Copy Object
- `HOME_COPY`: Object chứa tất cả text strings cho 3 ngôn ngữ
- Truy cập: `HOME_COPY[language]`

---

### 5.2. **RECOMMENDATION CONTEXT**

#### 5.2.1. Context Provider
- `RecommendationContext.js`:
  - `criteria`: { season, category, budget }
  - `results`: Danh sách điểm đến
  - `matchedRules`: Apriori rules
  - `updateRecommendation(criteria, results, rules)`
  - `clearRecommendation()`

#### 5.2.2. Usage
- **RecommendPage**: Update context khi có kết quả wizard
- **ChatbotWidget**: Read context để inject vào conversation
- **HomePage**: Read context để hiểu user journey

---

### 5.3. **AUTH CONTEXT**

#### 5.3.1. Auth Provider
- `AuthContext.js`:
  - `user`: { username, fullName, email, preferences }
  - `isAuthenticated`: Boolean
  - `login(username, password)`
  - `logout()`
  - `register(data)`
  - `updatePreferences(preferences)`

#### 5.3.2. Persistence
- Token lưu trong localStorage
- Auto-refresh token
- Protected routes

---

### 5.4. **IMAGE SERVICE**

#### 5.4.1. Image Sources
- **Real Landmarks**: `real_landmarks_mapping.json`
- **Category Types**: `country_type_photo_ids.json`
- **Country Generic**: `country_type_image_pools.json`

#### 5.4.2. Functions
- `getDestinationImage(name, type, country)`: Primary function
- `getFallbackImage(name, type)`: Fallback chain
- `resolveCategoryKey(type, name)`: Normalize type string

#### 5.4.3. CDN
- Wikimedia Commons
- Format: 800px width optimized

---

### 5.5. **AI CHATBOT**

#### 5.5.1. Gemini Integration
- Model: `gemini-2.5-flash`
- Temperature: 0.7
- Top_p: 0.95
- Max tokens: 4096

#### 5.5.2. System Prompt
- Vai trò: Trợ lý gợi ý du lịch AI chuyên nghiệp
- Style: Thân thiện, nhiệt tình, emoji
- Khả năng:
  - Gợi ý điểm đến
  - So sánh địa điểm
  - Lên lịch trình
  - Tư vấn chi phí
  - Hỗ trợ visa, thời tiết, ẩm thực

#### 5.5.3. Context-Aware
- **Recommendation context**: Biết user đã chọn gì ở wizard
- **Viewing destination context**: Biết user đang xem điểm đến nào
- **User profile context**: Biết tên, preferences của user
- **Conversation history**: Multi-turn conversation

#### 5.5.4. Destination Recommendations
- Backend trả về danh sách điểm đến kèm response
- Frontend render cards horizontal scroll
- Click card → Navigate to detail page

---

### 5.6. **RESPONSIVE DESIGN**

#### 5.6.1. Breakpoints
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

#### 5.6.2. Mobile Optimizations
- Hamburger menu
- Drawer filters
- Single column grid
- Touch-friendly buttons
- Swipe gestures

#### 5.6.3. Desktop Optimizations
- Multi-column grids
- Sticky sidebars
- Hover effects
- Keyboard shortcuts

---

### 5.7. **PERFORMANCE**

#### 5.7.1. Lazy Loading
- Images: onError fallback
- Routes: React.lazy
- Components: Dynamic import

#### 5.7.2. Caching
- LocalStorage: Preferences, sessions, size
- SessionStorage: Admin auth
- API cache: Browser cache headers

#### 5.7.3. Optimization
- Debounce search: 400ms
- Pagination: Limit results
- Virtual scrolling: Long lists
- Memoization: React.memo, useMemo

---

### 5.8. **DATA MINING ALGORITHMS**

#### 5.8.1. Apriori
- **Input**: Transactions (user history)
- **Output**: Association rules
- **Parameters**: min_support, min_confidence, min_lift
- **Usage**: Tìm luật kết hợp giữa các điểm đến

#### 5.8.2. K-Means
- **Input**: Destinations features (cost, rating, ...)
- **Output**: Cluster assignments
- **Parameters**: n_clusters (K)
- **Usage**: Phân nhóm điểm đến tương tự

#### 5.8.3. Collaborative Filtering
- **Input**: User-item rating matrix
- **Output**: Predicted ratings
- **Method**: Matrix factorization (SVD)
- **Usage**: Gợi ý cá nhân hóa cho user

#### 5.8.4. Hybrid Recommender
- **Combine**:
  - Content-based (Apriori rules)
  - Collaborative filtering (CF matrix)
  - Cluster-based (K-Means)
- **Weight**: Dynamically adjust
- **Output**: Top-N recommendations

---

### 5.9. **ANALYTICS & TRACKING**

#### 5.9.1. User Events
- Page views
- Search queries
- Filter interactions
- Chatbot messages
- Recommendation clicks

#### 5.9.2. Admin Dashboard
- Total destinations
- Total countries
- Total rules
- Total users
- Total ratings
- Algorithm run history

#### 5.9.3. Charts & Visualizations
- ScatterChart: Support vs Confidence
- BarChart: Lift distribution, Top items
- PieChart: Continent, Cost category
- LineChart: Reviews timeline, Elbow method

---

## KẾT LUẬN

Hệ thống đã được xây dựng với đầy đủ các chức năng:

### Người dùng:
✅ Trang chủ với gợi ý cá nhân hóa  
✅ Tìm kiếm và lọc điểm đến  
✅ Chi tiết điểm đến với đầy đủ thông tin  
✅ Bản đồ tương tác với filter  
✅ Wizard gợi ý 3 bước  
✅ Chatbot AI hỗ trợ 24/7  
✅ Xác thực và quản lý tài khoản  
✅ Đa ngôn ngữ (VI/EN/ZH)  

### Quản trị:
✅ Dashboard thống kê tổng quan  
✅ Quản lý thuật toán Apriori  
✅ Quản lý phân cụm K-Means  
✅ Quản lý đánh giá và CF  
✅ CRUD điểm đến  
✅ Quản lý tài khoản người dùng  
✅ Biểu đồ phân tích chi tiết  

### Kỹ thuật:
✅ AI/ML: Apriori, K-Means, CF, Gemini AI  
✅ Responsive design toàn bộ  
✅ Real-time updates  
✅ Context-aware chatbot  
✅ Performance optimization  
✅ Image handling & fallback  
✅ Multi-language support  

---

**Ngày tạo**: 2024  
**Phiên bản**: 1.0  
**Sinh viên**: Thạch Thị Xuân Linh - DA22TTA - 110122013

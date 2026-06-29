# 📊 Hướng Dẫn Thêm Biểu Đồ Elbow Method vào Notebook

## ✅ Đã Hoàn Thành

1. **Script Python độc lập**: `draw_elbow_chart.py`
   - Vẽ 4 biểu đồ phân tích Elbow Method chi tiết
   - Tự động lưu vào `chart_exports/elbow_method_analysis.png`

2. **Biểu đồ được tạo**: `chart_exports/elbow_method_analysis.png`
   - Kích thước: 290KB
   - Độ phân giải: 150 DPI
   - Format: PNG

## 📋 Nội Dung Biểu Đồ Elbow Method

Biểu đồ bao gồm 4 phần:

### 1. **SSE (Elbow Chart)** 🔵
- Hiển thị SSE (Sum of Squared Errors) theo số cluster K
- Đánh dấu điểm K=5 (được chọn) bằng đường đứt màu đỏ
- Annotation chỉ rõ giá trị SSE tại K=5

### 2. **Tỷ lệ giảm SSE** 🟢  
- Biểu đồ tỷ lệ phần trăm giảm SSE khi tăng K
- Giúp xác định "khuỷu tay" (elbow point) rõ ràng hơn
- Highlight tại K=5

### 3. **Silhouette Score** 🟣
- Đo độ tách biệt giữa các cluster
- Giá trị từ 0 đến 1 (càng cao càng tốt)
- Chỉ tính cho K >= 2

### 4. **Bảng Tổng Hợp** 📋
- Tổng hợp các metrics cho K từ 1 đến 10
- Bao gồm: K, SSE, Giảm SSE (%), Silhouette Score
- Highlight dòng K=5 bằng màu vàng

## 🎯 Kết Quả Phân Tích

```
Số cluster được đề xuất: K=5
SSE tại K=5: 71.73
Silhouette Score tại K=5: 0.3207
```

### Lý do chọn K=5:
✓ Có "khuỷu tay" rõ ràng trên biểu đồ SSE  
✓ Silhouette score > 0.3 (chất lượng cluster chấp nhận được)  
✓ Cân bằng giữa độ phức tạp và hiệu quả  

## 📝 Cách Thêm vào Notebook

### Phương án 1: Mở notebook và thêm cell mới (Khuyến nghị)

1. Mở file `phan_tich_du_lieu.ipynb` trong Jupyter Notebook/JupyterLab
2. Tìm đến **Phần 5: Phân Cụm K-Means**
3. Thêm một cell Markdown mới sau phần giới thiệu:

```markdown
---
### 🔍 Phân Tích Elbow Method - Xác Định K Tối Ưu

Trước khi áp dụng K-Means với K=5, chúng ta cần xác định số cluster tối ưu thông qua Elbow Method.
```

4. Thêm cell Code mới:

```python
# ─── Chạy script phân tích Elbow Method ───
%run draw_elbow_chart.py
```

HOẶC nếu muốn nhúng trực tiếp:

```python
from IPython.display import Image, display
display(Image('chart_exports/elbow_method_analysis.png'))
```

### Phương án 2: Chạy script độc lập

Chỉ cần chạy:
```bash
cd backend/data
python draw_elbow_chart.py
```

Biểu đồ sẽ được lưu vào `chart_exports/elbow_method_analysis.png` và tự động hiển thị.

## 📊 Giải Thích Các Metrics

### SSE (Sum of Squared Errors)
- **Định nghĩa**: Tổng bình phương khoảng cách từ mỗi điểm đến tâm cluster của nó
- **Công thức**: SSE = Σ ||xi - centroid||²
- **Ý nghĩa**: Càng nhỏ càng tốt, nhưng sẽ giảm dần khi K tăng

### Elbow Point (Điểm Khuỷu Tay)
- **Định nghĩa**: Điểm mà SSE bắt đầu giảm chậm lại đáng kể
- **Cách xác định**: Tìm điểm "bẻ cong" trên đồ thị SSE
- **Ý nghĩa**: Số cluster tối ưu cân bằng giữa độ phức tạp và chất lượng

### Silhouette Score
- **Định nghĩa**: Đo độ tách biệt giữa các cluster
- **Giá trị**: Từ -1 đến 1
  - > 0.7: Cấu trúc cluster xuất sắc
  - > 0.5: Cấu trúc cluster tốt
  - > 0.3: Cấu trúc cluster chấp nhận được
  - < 0.3: Cấu trúc cluster yếu
- **Công thức**: s(i) = (b(i) - a(i)) / max(a(i), b(i))
  - a(i): Khoảng cách trung bình trong cluster
  - b(i): Khoảng cách trung bình đến cluster gần nhất

## 🔄 Cách Chạy Lại Phân Tích

Nếu bạn thay đổi dữ liệu hoặc muốn thử K khác:

1. Mở `draw_elbow_chart.py`
2. Sửa dòng: `K_range = range(1, 11)` (ví dụ: `range(1, 15)` để test đến K=14)
3. Chạy lại: `python draw_elbow_chart.py`

## 📌 Lưu Ý

- File biểu đồ được ghi đè mỗi lần chạy script
- Notebook hiện tại đã có một biểu đồ Elbow đơn giản, biểu đồ mới này chi tiết hơn nhiều
- Có thể dùng cả hai: giữ biểu đồ đơn giản trong notebook, và tham khảo biểu đồ chi tiết khi cần

## 🎨 Tùy Chỉnh Biểu Đồ

Bạn có thể tùy chỉnh trong file `draw_elbow_chart.py`:

- **Màu sắc**: Sửa các tham số `color=` trong các lệnh `plot()`
- **Kích thước**: Sửa `figsize=(14, 10)` 
- **DPI**: Sửa `dpi=150` trong `savefig()`
- **Font size**: Sửa các tham số `fontsize=`
- **Grid**: Thêm/bớt `grid()` parameters

## ✨ Tóm Tắt

✅ Script `draw_elbow_chart.py` đã được tạo  
✅ Biểu đồ phân tích chi tiết đã được vẽ  
✅ File được lưu tại `chart_exports/elbow_method_analysis.png`  
✅ Kết quả phân tích xác nhận K=5 là lựa chọn tốt  

Bạn có thể tích hợp vào notebook theo một trong hai phương án trên!

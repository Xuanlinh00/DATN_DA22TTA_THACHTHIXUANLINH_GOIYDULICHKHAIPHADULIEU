# 📊 Thư Mục Biểu Đồ Phân Tích Dữ Liệu

Thư mục này chứa các biểu đồ được tạo ra từ quá trình phân tích dữ liệu trong notebook `phan_tich_du_lieu.ipynb`.

## 📁 Danh Sách Biểu Đồ

### 1. **elbow_method_analysis.png** (MỚI ✨)
**Biểu đồ Phân Tích Elbow Method - Xác Định Số Cluster Tối Ưu**

Bao gồm 4 biểu đồ con:
- 🔵 **SSE theo K**: Đồ thị Elbow Method cổ điển
- 🟢 **Tỷ lệ giảm SSE**: Phần trăm giảm SSE khi tăng K  
- 🟣 **Silhouette Score**: Đo độ tách biệt cluster
- 📋 **Bảng Tổng Hợp**: Metrics chi tiết cho K=1..10

**Kích thước**: 290KB  
**Độ phân giải**: 150 DPI  
**Được tạo bởi**: `draw_elbow_chart.py`

**Kết luận**: Chọn **K=5** dựa trên:
- SSE có "khuỷu tay" rõ ràng tại K=5
- Silhouette Score = 0.3207 (chấp nhận được)
- Cân bằng giữa độ phức tạp và hiệu quả

---

### 2. **chart_00_cell9.png** đến **chart_04_cell29.png**
**Các biểu đồ khác từ notebook phân tích**

Được export tự động khi chạy notebook với magic command:
```python
plt.savefig('chart_exports/chart_XX_cellYY.png')
```

## 🔄 Cách Tạo Lại Biểu Đồ

### Elbow Method Analysis:
```bash
cd backend/data
python draw_elbow_chart.py
```

### Các biểu đồ từ notebook:
1. Mở `phan_tich_du_lieu.ipynb` trong Jupyter
2. Chạy các cell có chứa `plt.savefig()`
3. Biểu đồ sẽ được lưu tự động vào thư mục này

## 📝 Lưu Ý

- Các file trong thư mục này có thể được ghi đè khi chạy lại script/notebook
- Nên backup các biểu đồ quan trọng trước khi chạy lại phân tích
- Format: PNG với DPI cao để đảm bảo chất lượng in ấn

## 🎯 Mục Đích

Các biểu đồ này được sử dụng để:
- Trình bày kết quả phân tích dữ liệu
- Hỗ trợ báo cáo và tài liệu
- Minh họa cho bài thuyết trình
- Kiểm tra và đánh giá chất lượng clustering

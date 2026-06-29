# Tóm tắt sửa lỗi Bản đồ và Hình ảnh

## Vấn đề đã phát hiện

1. **Bản đồ hiển thị sai vị trí**: 
   - Backend API ưu tiên `country_latitude/longitude` thay vì `destination_latitude/longitude`
   - Dẫn đến marker hiển thị ở tọa độ trung tâm quốc gia thay vì địa điểm thực tế

2. **Hình ảnh không đúng với địa điểm**:
   - Image service tìm kiếm quá chung chung, rút gọn tên địa điểm
   - Không sử dụng đầy đủ thông tin (country, type) để tìm hình chính xác

## Các thay đổi đã thực hiện

### 1. Sửa Backend API (backend/api/routes.py)

**Trước:**
```python
# Ưu tiên tọa độ quốc gia
lat = dest_row.get('country_latitude')
lon = dest_row.get('country_longitude')

if pd.isna(lat) or pd.isna(lon):
    lat = dest_row.get('destination_latitude')
    lon = dest_row.get('destination_longitude')
```

**Sau:**
```python
# Ưu tiên tọa độ điểm đến cụ thể
lat = dest_row.get('destination_latitude')
lon = dest_row.get('destination_longitude')

if pd.isna(lat) or pd.isna(lon):
    lat = dest_row.get('country_latitude')
    lon = dest_row.get('country_longitude')
```

Thay đổi này áp dụng cho:
- `/destinations/{destination_name}/weather` endpoint (line 649-657)
- `/destinations/{destination_name}/climate` endpoint (line 716-723)

### 2. Cải thiện Image Service (backend/services/image_service.py)

**Unsplash API:**
- Sử dụng tên đầy đủ thay vì rút gọn 3 từ đầu
- Thêm `country` và `dest_type` vào query để tìm kiếm chính xác hơn
- Query cũ: `"Oslo Norway"` (3 từ đầu)
- Query mới: `"Oslo Fjords Museum Peninsula Norway Cultural"` (đầy đủ)

**Wikimedia API:**
- Tương tự, sử dụng tên đầy đủ để tìm kiếm Wikipedia page chính xác hơn

### 3. Script sửa dữ liệu (backend/fix_destinations_data.py)

Tạo script tiện ích để:
- Kiểm tra và sửa tọa độ thiếu
- Cập nhật lại hình ảnh cho các địa điểm

Cách dùng:
```bash
cd backend
python fix_destinations_data.py --coordinates  # Sửa tọa độ
python fix_destinations_data.py --images       # Cập nhật hình
python fix_destinations_data.py --all          # Cả hai
```

### 4. Script sửa địa điểm cụ thể (backend/fix_specific_destinations.py)

Sửa các địa điểm có dữ liệu sai:
- "Lush Pagoda (Thailand)" → Đã cập nhật:
  - Tọa độ: (7.7407, 98.7784) - Phi Phi Islands thực tế
  - Hình ảnh: Từ Unsplash với query "Phi Phi Islands Thailand"

## Kết quả

### Trước khi sửa:
- Marker hiển thị ở trung tâm Thailand (15.9581, 101.1304)
- Hình ảnh từ Cambodia Museum (không liên quan)

### Sau khi sửa:
- Marker hiển thị đúng tại Phi Phi Islands (7.7407, 98.7784)
- Hình ảnh beach đẹp từ Unsplash
- Bản đồ zoom chính xác vào địa điểm

## Cách test

1. **Khởi động lại backend** (nếu đang chạy):
   ```bash
   cd backend
   python main.py
   ```

2. **Mở trình duyệt và truy cập**:
   - Trang bản đồ: `http://localhost:3000/world-map`
   - Chọn quốc gia "Thái Lan" trong bộ lọc
   - Tìm "Lush Pagoda (Thailand)"
   - Click vào marker để xem thông tin

3. **Kiểm tra**:
   - ✅ Marker nên hiển thị ở vùng biển phía Nam Thailand (Phi Phi Islands)
   - ✅ Hình ảnh nên là cảnh biển đẹp với nước xanh trong
   - ✅ Khi click "Chỉ Đường" sẽ tính đường đến đúng vị trí

## Các địa điểm khác cần sửa

Nếu phát hiện địa điểm khác có vấn đề tương tự:

1. Thêm vào `FIXES` dictionary trong `backend/fix_specific_destinations.py`:
```python
FIXES = {
    "Tên địa điểm": {
        "search_name": "Tên thực tế để tìm hình",
        "latitude": xxx,
        "longitude": yyy,
        "description": "Mô tả mới..."
    }
}
```

2. Chạy lại: `python fix_specific_destinations.py`

## Lưu ý

- **Dữ liệu giả lập**: Một số địa điểm trong database là dữ liệu giả lập nên không có tọa độ chính xác
- **Geocoding tự động**: Có thể dùng `backend/mining/auto_geocode.py` để tự động lấy tọa độ cho địa điểm mới
- **Image API limits**: Unsplash có giới hạn 50 requests/giờ cho development, nên cập nhật hình từ từ

## Script tiện ích đã tạo

1. `backend/fix_destinations_data.py` - Sửa tọa độ và hình ảnh hàng loạt
2. `backend/fix_specific_destinations.py` - Sửa địa điểm cụ thể
3. `backend/check_destination.py` - Kiểm tra thông tin địa điểm

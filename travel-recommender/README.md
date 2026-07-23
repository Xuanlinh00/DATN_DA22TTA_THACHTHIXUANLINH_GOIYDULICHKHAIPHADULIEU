# Travel Recommender

Hệ thống gợi ý địa điểm du lịch đa nguồn dữ liệu, gồm backend FastAPI, frontend React và bộ tài liệu đồ án ở thư mục `docs`.

## Mục tiêu

- Gợi ý điểm đến phù hợp theo nhu cầu người dùng.
- Kết hợp dữ liệu điểm đến, thời tiết, hành vi và luật kết hợp để tăng độ phù hợp của đề xuất.
- Cung cấp giao diện web để tìm kiếm, xem gợi ý và quản trị dữ liệu.

## Kiến trúc

- `backend/`: API FastAPI, các module gợi ý, xử lý dữ liệu, dịch vụ thời tiết và NLP.
- `frontend/`: Ứng dụng React hiển thị giao diện người dùng.
- `docs/`: Tài liệu đồ án gồm báo cáo, slide, poster và các file thuyết minh.

## Yêu cầu triển khai

- Python 3.10+ cho backend.
- Node.js 18+ và npm cho frontend.
- Các thư viện backend được liệt kê trong `backend/requirements.txt`.

## Cách chạy chương trình

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Backend mặc định chạy tại `http://localhost:8000`.

### 2. Frontend

```bash
cd frontend
npm install
npm start
```

Frontend mặc định chạy tại `http://localhost:3000`.

## Tài liệu đồ án

Thư mục `docs` chứa các file phục vụ nộp và bảo vệ đồ án, bao gồm:

- File quyển đồ án định dạng `.docx`.
- File quyển đồ án định dạng `.pdf`.
- Slide bảo vệ định dạng `.pptx`.
- Poster giới thiệu đồ án khổ A1 định dạng `.pdf`.

## Ghi chú

- Một số chức năng cần cấu hình thêm biến môi trường hoặc dữ liệu đầu vào trong thư mục `backend/data`.
- Nếu bạn thay đổi dữ liệu hoặc luật gợi ý, nên kiểm tra lại các luồng gọi trong backend trước khi chạy lại giao diện.
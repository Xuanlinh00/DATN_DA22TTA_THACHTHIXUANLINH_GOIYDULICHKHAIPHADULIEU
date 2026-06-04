# -*- coding: utf-8 -*-
"""
Open-Meteo Archive Service Module
Retrieves historical climate data (temperature, rainfall) by geographic coordinates
using the free Open-Meteo Archive API (no API key required).

API Docs: https://open-meteo.com/en/docs/historical-weather-api
"""

import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

OPEN_METEO_BASE_URL = os.getenv(
    "OPEN_METEO_BASE_URL",
    "https://archive-api.open-meteo.com/v1/archive"
)

# Tên tháng hiển thị theo tiếng Anh viết tắt (trả về frontend)
MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _get_last_full_year_range():
    """
    Trả về khoảng thời gian 1 năm đầy đủ gần nhất (năm ngoái) 
    để tránh lấy dữ liệu của năm hiện tại chưa hoàn chỉnh.
    """
    today = datetime.now()
    # Năm ngoái đảm bảo đủ 12 tháng
    year = today.year - 1
    start_date = f"{year}-01-01"
    end_date   = f"{year}-12-31"
    return start_date, end_date


def _aggregate_monthly(daily_dates, daily_values):
    """
    Tổng hợp dữ liệu ngày → trung bình theo từng tháng.
    
    Args:
        daily_dates  (list[str]): Danh sách ngày dạng "YYYY-MM-DD"
        daily_values (list[float|None]): Giá trị tương ứng mỗi ngày
    
    Returns:
        list[float]: 12 giá trị trung bình cho Jan → Dec (làm tròn 1 chữ số)
    """
    monthly_sums   = [0.0] * 12
    monthly_counts = [0]   * 12

    for date_str, value in zip(daily_dates, daily_values):
        if value is None:
            continue
        try:
            month_idx = int(date_str[5:7]) - 1  # "YYYY-MM-DD" → tháng (0-indexed)
            monthly_sums[month_idx]   += float(value)
            monthly_counts[month_idx] += 1
        except (ValueError, IndexError):
            continue

    result = []
    for s, c in zip(monthly_sums, monthly_counts):
        if c > 0:
            result.append(round(s / c, 1))
        else:
            result.append(None)
    return result


def _aggregate_monthly_sum(daily_dates, daily_values):
    """
    Tổng hợp dữ liệu ngày → TỔNG theo từng tháng (dùng cho lượng mưa tích lũy).
    
    Returns:
        list[float]: 12 giá trị tổng cho Jan → Dec (làm tròn 1 chữ số)
    """
    monthly_sums = [0.0] * 12

    for date_str, value in zip(daily_dates, daily_values):
        if value is None:
            continue
        try:
            month_idx = int(date_str[5:7]) - 1
            monthly_sums[month_idx] += float(value)
        except (ValueError, IndexError):
            continue

    return [round(v, 1) for v in monthly_sums]


def get_historical_climate(latitude: float, longitude: float):
    """
    Lấy dữ liệu khí hậu lịch sử (1 năm gần nhất đầy đủ) cho một tọa độ địa lý.

    Trả về:
        {
            "success": True,
            "climate": {
                "months":   ["Jan", "Feb", ..., "Dec"],  # 12 nhãn tháng
                "temp_avg": [18.2, 20.1, ..., 16.5],    # Nhiệt độ TB (°C)
                "temp_max": [24.1, 26.3, ..., 22.0],    # Nhiệt độ cao TB (°C)
                "temp_min": [12.0, 14.2, ..., 10.8],    # Nhiệt độ thấp TB (°C)
                "rainfall": [45.2, 22.0, ..., 80.1],    # Lượng mưa tổng (mm)
            },
            "year":    2024,      # Năm dữ liệu được lấy
            "source":  "Open-Meteo Archive API"
        }
    
    Raises:
        Nếu gọi API thất bại, trả về dict với "success": False và thông báo lỗi.
    """
    start_date, end_date = _get_last_full_year_range()
    year = int(start_date[:4])

    params = {
        "latitude":  round(float(latitude), 4),
        "longitude": round(float(longitude), 4),
        "start_date": start_date,
        "end_date":   end_date,
        # Các chỉ số cần lấy theo ngày
        "daily": [
            "temperature_2m_mean",   # Nhiệt độ trung bình ngày (°C)
            "temperature_2m_max",    # Nhiệt độ cao nhất ngày (°C)
            "temperature_2m_min",    # Nhiệt độ thấp nhất ngày (°C)
            "precipitation_sum",     # Lượng mưa tổng ngày (mm)
        ],
        "timezone": "auto",          # Tự động xác định múi giờ theo tọa độ
        "wind_speed_unit": "ms",
    }

    try:
        print(f"[Open-Meteo] Fetching climate for lat={latitude}, lon={longitude}, year={year}")
        response = requests.get(
            OPEN_METEO_BASE_URL,
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        daily = data.get("daily", {})
        dates      = daily.get("time", [])
        temp_mean  = daily.get("temperature_2m_mean", [])
        temp_max   = daily.get("temperature_2m_max", [])
        temp_min   = daily.get("temperature_2m_min", [])
        precip     = daily.get("precipitation_sum", [])

        if not dates:
            return {
                "success": False,
                "error": "Open-Meteo trả về dữ liệu rỗng cho tọa độ này."
            }

        # Tổng hợp theo tháng
        temp_avg_monthly = _aggregate_monthly(dates, temp_mean)
        temp_max_monthly = _aggregate_monthly(dates, temp_max)
        temp_min_monthly = _aggregate_monthly(dates, temp_min)
        rainfall_monthly = _aggregate_monthly_sum(dates, precip)

        print(f"[Open-Meteo] ✅ Climate data retrieved successfully for year {year}.")

        return {
            "success": True,
            "climate": {
                "months":   MONTH_LABELS,
                "temp_avg": temp_avg_monthly,
                "temp_max": temp_max_monthly,
                "temp_min": temp_min_monthly,
                "rainfall": rainfall_monthly,
            },
            "year":   year,
            "source": "Dữ liệu Khí hậu Thực tế"
        }

    except requests.exceptions.Timeout:
        print("[Open-Meteo] ❌ Request timed out.")
        return {
            "success": False,
            "error": "Yêu cầu đến Open-Meteo API bị hết thời gian chờ (timeout)."
        }
    except requests.exceptions.HTTPError as e:
        print(f"[Open-Meteo] ❌ HTTP error: {e}")
        return {
            "success": False,
            "error": f"Lỗi HTTP từ Open-Meteo API: {e}"
        }
    except Exception as e:
        print(f"[Open-Meteo] ❌ Unexpected error: {e}")
        return {
            "success": False,
            "error": f"Lỗi không xác định khi gọi Open-Meteo API: {str(e)}"
        }


def get_best_months_to_visit(temp_avg, rainfall, target_temp_range=(18, 28), max_rainfall_mm=80):
    """
    Phân tích dữ liệu khí hậu và đề xuất các tháng đẹp nhất để du lịch.

    Args:
        temp_avg (list[float]):     Nhiệt độ trung bình 12 tháng (°C)
        rainfall (list[float]):     Lượng mưa tổng 12 tháng (mm)
        target_temp_range (tuple):  Khoảng nhiệt độ lý tưởng (mặc định 18–28°C)
        max_rainfall_mm (float):    Ngưỡng lượng mưa tối đa coi là "khô ráo" (mm/tháng)

    Returns:
        list[str]: Danh sách tháng được đề xuất (ví dụ: ["Mar", "Apr", "Oct"])
    """
    best = []
    for i, (temp, rain) in enumerate(zip(temp_avg, rainfall)):
        if temp is None or rain is None:
            continue
        temp_ok  = target_temp_range[0] <= temp <= target_temp_range[1]
        rain_ok  = rain <= max_rainfall_mm
        if temp_ok and rain_ok:
            best.append(MONTH_LABELS[i])
    return best


# ─── Kiểm thử nhanh khi chạy trực tiếp ──────────────────────────────────────
if __name__ == "__main__":
    import json

    print("=" * 60)
    print("[TEST] Open-Meteo Service - Kiểm thử với Paris, France")
    print("       (Vĩ độ: 48.8566, Kinh độ: 2.3522)")
    print("=" * 60)

    result = get_historical_climate(latitude=48.8566, longitude=2.3522)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    if result["success"]:
        best = get_best_months_to_visit(
            result["climate"]["temp_avg"],
            result["climate"]["rainfall"]
        )
        print(f"\n🌟 Các tháng đẹp nhất để thăm Paris: {best}")

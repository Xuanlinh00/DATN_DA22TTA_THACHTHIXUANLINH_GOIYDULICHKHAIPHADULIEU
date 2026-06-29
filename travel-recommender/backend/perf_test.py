import time
import requests

def test_endpoint(name, url, method="GET", json_data=None):
    start = time.time()
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        else:
            response = requests.post(url, json=json_data, timeout=10)
        elapsed = time.time() - start
        print(f"[{name}] {method} {url} -> Status: {response.status_code} | Time: {elapsed:.3f}s")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                print(f"      Keys: {list(data.keys())}")
                if "recommendations" in data:
                    print(f"      Recommendations count: {len(data['recommendations'])}")
                if "destinations" in data:
                    print(f"      Destinations count: {len(data['destinations'])}")
            elif isinstance(data, list):
                print(f"      List length: {len(data)}")
    except Exception as e:
        print(f"[{name}] {method} {url} -> FAILED: {e}")

print("--- Testing API Endpoints Performance ---")
test_endpoint("Root", "http://127.0.0.1:8000/")
test_endpoint("Stats", "http://127.0.0.1:8000/api/stats")
test_endpoint("Filters Options", "http://127.0.0.1:8000/api/filters/options")
test_endpoint("Get Destinations (limit 50)", "http://127.0.0.1:8000/api/destinations?limit=50")
test_endpoint("Seasonal recommendations", "http://127.0.0.1:8000/api/recommendations/seasonal/Summer?limit=8")
test_endpoint("Filtered recommendations", "http://127.0.0.1:8000/api/recommendations", method="POST", json_data={"season": "Summer", "budget": "Budget", "category": "Beach"})
test_endpoint("Destination Detail (Santorini)", "http://127.0.0.1:8000/api/destinations/Santorini%20Island%20Sunsets")
test_endpoint("Destination Weather (Santorini)", "http://127.0.0.1:8000/api/destinations/Santorini%20Island%20Sunsets/weather")
test_endpoint("Destination Climate (Santorini)", "http://127.0.0.1:8000/api/destinations/Santorini%20Island%20Sunsets/climate")
test_endpoint("Destination Similar (Santorini)", "http://127.0.0.1:8000/api/destinations/Santorini%20Island%20Sunsets/similar")

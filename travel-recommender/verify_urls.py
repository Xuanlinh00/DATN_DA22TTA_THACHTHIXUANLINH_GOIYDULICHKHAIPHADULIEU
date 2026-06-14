"""Verify one URL with GET request and proper browser User-Agent"""
import requests

# Test with a known working URL from the CSV first
test_urls = [
    # Known working image from CSV
    ('Existing OK', 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Marina_Bays_Sands_Hotel_from_the_bridge_connecting_to_the_Gardens_By_The_Bay_in_Singapore.jpg/960px-Marina_Bays_Sands_Hotel_from_the_bridge_connecting_to_the_Gardens_By_The_Bay_in_Singapore.jpg'),
    # One of our new URLs
    ('New Interlaken', 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Interlaken_-_Interlaken_Ost_-_Unterseen.jpg/960px-Interlaken_-_Interlaken_Ost_-_Unterseen.jpg'),
    ('New Times Square', 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/New_york_times_square-terabass.jpg/960px-New_york_times_square-terabass.jpg'),
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

for name, url in test_urls:
    try:
        resp = requests.get(url, timeout=10, allow_redirects=True, headers=headers, stream=True)
        ct = resp.headers.get('Content-Type', '')
        cl = resp.headers.get('Content-Length', '?')
        print(f"  [{resp.status_code}] [{ct}] [size={cl}] {name}")
        resp.close()
    except Exception as e:
        print(f"  ERROR: {name} - {e}")

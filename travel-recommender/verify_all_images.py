# -*- coding: utf-8 -*-
"""Verify all image URLs in imageService.js return valid HTTP responses."""
import re, sys, time, urllib.request, urllib.error
sys.stdout.reconfigure(encoding='utf-8')

JS_FILE = r"frontend\src\services\imageService.js"

UA = 'TravelRecommenderVerifier/1.0 (educational project; datn@student.com)'

def check_url(url):
    """Check if URL returns a valid image. Returns (ok, code, detail)."""
    # Try HEAD first
    try:
        req = urllib.request.Request(url, method='HEAD')
        req.add_header('User-Agent', UA)
        resp = urllib.request.urlopen(req, timeout=15)
        code = resp.getcode()
        ct = resp.headers.get('Content-Type', '')
        if code == 200 and 'image' in ct.lower():
            return True, code, ''
        return False, code, f'content-type: {ct}'
    except urllib.error.HTTPError as e:
        if e.code == 403 or e.code == 429:
            return None, e.code, 'rate limited'
        return False, e.code, e.reason
    except Exception as e:
        return False, 0, str(e)

def main():
    with open(JS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract destination name + URL pairs
    pattern = r"'([^']+)':\s*'(https://[^']+)'"
    matches = re.findall(pattern, content)
    
    print(f"Found {len(matches)} image URLs to verify")
    print()
    
    broken = []
    ok_count = 0
    skip_count = 0
    
    for i, (dest_name, url) in enumerate(matches):
        result, code, detail = check_url(url)
        if result is True:
            ok_count += 1
            print(f"  [{i+1}/{len(matches)}] OK  [{code}] {dest_name}")
        elif result is None:
            skip_count += 1
            print(f"  [{i+1}/{len(matches)}] SKIP [{code}] {dest_name} (rate limited)")
        else:
            print(f"  [{i+1}/{len(matches)}] FAIL [{code}] {dest_name} -> {detail}")
            broken.append((dest_name, url, f"[{code}] {detail}"))
        
        time.sleep(2)  # Rate limit - be polite to Wikimedia
    
    print()
    print(f"Results: {ok_count} OK, {len(broken)} broken, {skip_count} skipped (rate limited) out of {len(matches)}")
    
    if broken:
        print("\nBroken URLs:")
        for name, url, reason in broken:
            print(f"  {name}: {reason}")
            print(f"    {url}")

if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""
inspect_images.py
=================
Kiểm tra trạng thái hình ảnh trong database
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mining.mongodb_storage import db_storage

def inspect_images():
    """Kiểm tra trạng thái hình ảnh"""
    print("=" * 80)
    print("INSPECTING IMAGE STATUS")
    print("=" * 80)
    
    if not db_storage.is_connected():
        print("[ERROR] Database not connected")
        return
    
    destinations = db_storage.load_destinations()
    
    if not destinations:
        print("[ERROR] No destinations found")
        return
    
    print(f"\nTotal destinations: {len(destinations)}")
    
    # Categorize images
    has_http = 0
    has_value = 0
    is_empty = 0
    is_none = 0
    
    samples = {
        "http": [],
        "value": [],
        "empty": [],
        "none": []
    }
    
    for dest in destinations:
        image = dest.get("image")
        name = dest.get("Destination Name", "")
        country = dest.get("Country", "")
        
        if image is None:
            is_none += 1
            if len(samples["none"]) < 5:
                samples["none"].append(f"{name} ({country})")
        elif isinstance(image, str) and image.startswith("http"):
            has_http += 1
            if len(samples["http"]) < 5:
                samples["http"].append(f"{name} ({country}): {image[:50]}...")
        elif image == "" or (isinstance(image, str) and not image.strip()):
            is_empty += 1
            if len(samples["empty"]) < 5:
                samples["empty"].append(f"{name} ({country})")
        else:
            has_value += 1
            if len(samples["value"]) < 5:
                samples["value"].append(f"{name} ({country}): {str(image)[:50]}...")
    
    # Show results
    print("\n" + "=" * 80)
    print("IMAGE STATUS BREAKDOWN")
    print("=" * 80)
    print(f"Valid HTTP URLs:    {has_http}")
    print(f"Non-HTTP values:    {has_value}")
    print(f"Empty strings:      {is_empty}")
    print(f"None/missing:       {is_none}")
    print("=" * 80)
    
    # Show samples
    if samples["http"]:
        print("\nSample destinations WITH valid images:")
        for s in samples["http"]:
            print(f"  • {s}")
    
    if samples["none"]:
        print("\nSample destinations WITHOUT images (None):")
        for s in samples["none"]:
            print(f"  • {s}")
    
    if samples["empty"]:
        print("\nSample destinations WITH empty images:")
        for s in samples["empty"]:
            print(f"  • {s}")
    
    if samples["value"]:
        print("\nSample destinations WITH non-HTTP values:")
        for s in samples["value"]:
            print(f"  • {s}")


if __name__ == "__main__":
    inspect_images()

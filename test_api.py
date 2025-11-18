#!/usr/bin/env python3
"""
Test script for WLED Icons API v0.5.8
Tests brightness control and extended automation endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8234"
WLED_HOST = "192.168.1.100"  # Change to your WLED IP

def test_brightness_control():
    """Test POST /api/wled/brightness"""
    print("\n🧪 Testing brightness control...")
    
    url = f"{BASE_URL}/api/wled/brightness"
    for brightness in [50, 128, 255]:
        payload = {"host": WLED_HOST, "brightness": brightness}
        try:
            r = requests.post(url, json=payload, timeout=5)
            if r.ok:
                print(f"  ✅ Brightness set to {brightness}: {r.json()}")
            else:
                print(f"  ❌ Failed {brightness}: {r.status_code}")
        except Exception as e:
            print(f"  ❌ Exception: {e}")
        time.sleep(1)


def test_wled_state():
    """Test POST /api/wled/state"""
    print("\n🧪 Testing WLED state retrieval...")
    
    url = f"{BASE_URL}/api/wled/state"
    payload = {"host": WLED_HOST}
    try:
        r = requests.post(url, json=payload, timeout=5)
        if r.ok:
            state = r.json()
            print(f"  ✅ WLED State:")
            print(f"     - On: {state.get('on')}")
            print(f"     - Brightness: {state.get('bri')}")
            print(f"     - Segments: {len(state.get('seg', []))}")
        else:
            print(f"  ❌ Failed: {r.status_code}")
    except Exception as e:
        print(f"  ❌ Exception: {e}")


def test_wled_power():
    """Test POST /api/wled/on and /api/wled/off"""
    print("\n🧪 Testing WLED power control...")
    
    # Turn off
    url_off = f"{BASE_URL}/api/wled/off"
    payload = {"host": WLED_HOST}
    try:
        r = requests.post(url_off, json=payload, timeout=5)
        if r.ok:
            print(f"  ✅ WLED turned OFF")
        else:
            print(f"  ❌ Failed to turn off: {r.status_code}")
    except Exception as e:
        print(f"  ❌ Exception: {e}")
    
    time.sleep(1)
    
    # Turn on
    url_on = f"{BASE_URL}/api/wled/on"
    try:
        r = requests.post(url_on, json=payload, timeout=5)
        if r.ok:
            print(f"  ✅ WLED turned ON")
        else:
            print(f"  ❌ Failed to turn on: {r.status_code}")
    except Exception as e:
        print(f"  ❌ Exception: {e}")


def test_icon_search():
    """Test GET /api/icons/search"""
    print("\n🧪 Testing icon search...")
    
    # First create a test icon
    create_url = f"{BASE_URL}/api/icons"
    test_icon = {
        "id": "WI1731932400999999",
        "name": "Test Search Icon",
        "grid": [["#FF0000"] * 8 for _ in range(8)]
    }
    
    try:
        r = requests.post(create_url, json=test_icon, timeout=5)
        if r.ok:
            print(f"  ✅ Test icon created: {r.json()}")
        
        # Search for it
        search_url = f"{BASE_URL}/api/icons/search?q=test&limit=5"
        r = requests.get(search_url, timeout=5)
        if r.ok:
            results = r.json()
            print(f"  ✅ Search results: {results['count']} icons found")
            for icon in results['icons']:
                print(f"     - {icon['id']}: {icon['name']}")
        else:
            print(f"  ❌ Search failed: {r.status_code}")
    except Exception as e:
        print(f"  ❌ Exception: {e}")


def test_bulk_display():
    """Test POST /api/icons/bulk-display"""
    print("\n🧪 Testing bulk display...")
    
    # Create test icons
    icons_to_create = []
    for i in range(3):
        icon_id = f"WI173193240000000{i}"
        color = ["#FF0000", "#00FF00", "#0000FF"][i]
        icons_to_create.append({
            "id": icon_id,
            "name": f"Test Bulk {i}",
            "grid": [[color] * 8 for _ in range(8)]
        })
    
    create_url = f"{BASE_URL}/api/icons"
    created_ids = []
    
    for icon in icons_to_create:
        try:
            r = requests.post(create_url, json=icon, timeout=5)
            if r.ok:
                created_ids.append(icon["id"])
                print(f"  ✅ Created icon: {icon['id']}")
        except Exception as e:
            print(f"  ❌ Exception creating icon: {e}")
    
    # Test bulk display
    if created_ids:
        bulk_url = f"{BASE_URL}/api/icons/bulk-display"
        payload = {
            "icons": created_ids,
            "host": WLED_HOST,
            "duration": 1.0,
            "brightness": 150,
            "rotate": 0,
            "flip_h": False,
            "flip_v": False
        }
        
        try:
            r = requests.post(bulk_url, json=payload, timeout=15)
            if r.ok:
                result = r.json()
                print(f"  ✅ Bulk display success: {result['count']} icons shown")
            else:
                print(f"  ❌ Bulk display failed: {r.status_code}")
        except Exception as e:
            print(f"  ❌ Exception: {e}")


def main():
    print("=" * 60)
    print("WLED Icons API v0.5.8 - Test Suite")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print(f"WLED Host: {WLED_HOST}")
    
    # Check if add-on is running
    try:
        r = requests.get(f"{BASE_URL}/api/icons", timeout=5)
        if r.ok:
            print("✅ Add-on is accessible")
        else:
            print(f"⚠️  Add-on responded with {r.status_code}")
    except Exception as e:
        print(f"❌ Cannot reach add-on: {e}")
        print("Make sure the add-on is running!")
        return
    
    # Run tests
    test_brightness_control()
    test_wled_state()
    test_wled_power()
    test_icon_search()
    test_bulk_display()
    
    print("\n" + "=" * 60)
    print("✅ Test suite completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

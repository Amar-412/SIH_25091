#!/usr/bin/env python3
"""
Quick test to check if data is loading properly in the web app.
"""

import requests
import json

def test_data_loading():
    """Test if data is loading properly."""
    base_url = "http://localhost:5000"
    
    print("🔍 Testing Vicharak Data Loading...")
    print("=" * 40)
    
    try:
        # Test debug endpoint
        response = requests.get(f"{base_url}/api/debug")
        if response.status_code == 200:
            debug_info = response.json()
            print("📊 Data Loading Status:")
            print(f"  Students: {debug_info['students_count']} records")
            print(f"  Faculty: {debug_info['faculty_count']} records")
            print(f"  Courses: {debug_info['courses_count']} records")
            print(f"  Rooms: {debug_info['rooms_count']} records")
            print(f"  Constraints: {'✅ Loaded' if debug_info['constraints_loaded'] else '❌ Not loaded'}")
            
            if debug_info['students_empty'] or debug_info['courses_empty'] or debug_info['rooms_empty'] or debug_info['faculty_empty']:
                print("\n❌ Some datasets are empty!")
                print("💡 Solution: Restart the web app to reload data")
            else:
                print("\n✅ All datasets loaded successfully!")
                
        else:
            print(f"❌ Debug endpoint failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to web app.")
        print("💡 Make sure the web app is running:")
        print("   python start_web.py")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_data_loading()

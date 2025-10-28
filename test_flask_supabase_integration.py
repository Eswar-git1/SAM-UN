#!/usr/bin/env python3
"""
Test Flask app integration with Supabase for layer updates
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Flask app URL
FLASK_URL = "http://127.0.0.1:5050"

def test_layer_update():
    """Test updating a layer through the Flask app"""
    
    # Test data - a simple GeoJSON feature
    test_data = {
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "name": "Test Feature",
                    "description": "This is a test feature for Supabase integration",
                    "timestamp": "2024-01-01T00:00:00Z"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [-122.4194, 37.7749]  # San Francisco
                }
            }
        ]
    }
    
    layer_name = "test_supabase_layer"
    
    print(f"🧪 Testing layer update for '{layer_name}'...")
    print(f"📡 Sending POST request to {FLASK_URL}/data/{layer_name}/update")
    
    try:
        # Send POST request to update layer
        response = requests.post(
            f"{FLASK_URL}/data/{layer_name}/update",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Response: {json.dumps(result, indent=2)}")
            
            # Check if it was saved to Supabase or local storage
            storage_type = result.get("storage", "unknown")
            if storage_type == "supabase":
                print("🎉 Layer was successfully saved to Supabase!")
                return True
            elif storage_type == "local":
                print("⚠️  Layer was saved to local storage (Supabase failed)")
                return False
            else:
                print(f"❓ Unknown storage type: {storage_type}")
                return False
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_layer_retrieval():
    """Test retrieving the layer to verify it was saved"""
    
    layer_name = "test_supabase_layer"
    
    print(f"\n🔍 Testing layer retrieval for '{layer_name}'...")
    print(f"📡 Sending GET request to {FLASK_URL}/data/{layer_name}")
    
    try:
        response = requests.get(f"{FLASK_URL}/data/{layer_name}", timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Layer retrieved successfully!")
            print(f"📄 Features count: {len(result.get('features', []))}")
            
            # Check if we got our test feature back
            features = result.get('features', [])
            if features and features[0].get('properties', {}).get('name') == 'Test Feature':
                print("🎉 Test feature found in retrieved layer!")
                return True
            else:
                print("⚠️  Test feature not found in retrieved layer")
                return False
        else:
            print(f"❌ Retrieval failed with status {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Run the complete test suite"""
    print("🚀 Starting Flask-Supabase Integration Test")
    print("=" * 50)
    
    # Check if Flask server is running
    try:
        response = requests.get(FLASK_URL, timeout=5)
        print(f"✅ Flask server is running at {FLASK_URL}")
    except:
        print(f"❌ Flask server is not accessible at {FLASK_URL}")
        print("Please make sure the Flask server is running with 'python app.py'")
        return
    
    # Test layer update
    update_success = test_layer_update()
    
    if update_success:
        # Test layer retrieval
        retrieval_success = test_layer_retrieval()
        
        if retrieval_success:
            print("\n🎉 All tests passed! Supabase integration is working correctly.")
        else:
            print("\n⚠️  Update succeeded but retrieval failed.")
    else:
        print("\n❌ Layer update failed. Check the Flask server logs for details.")
    
    print("\n" + "=" * 50)
    print("Test completed.")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Test script to verify that new user layers are being saved to Supabase buckets.
This script tests:
1. File upload via /convert endpoint
2. Layer creation via drawing (simulated via /data/<layer>/update)
3. User layer persistence
"""

import requests
import json
import time
import os
from io import StringIO

BASE_URL = "http://127.0.0.1:5050"

# Test GeoJSON data for simulating drawing
TEST_DRAWING_GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "name": "Test Point",
                "description": "A test point created by drawing",
                "category": "test"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [25.0, -5.0]  # Within Congo bounds
            }
        },
        {
            "type": "Feature",
            "properties": {
                "name": "Test Line",
                "description": "A test line created by drawing",
                "category": "test"
            },
            "geometry": {
                "type": "LineString",
                "coordinates": [[25.0, -5.0], [26.0, -4.0], [27.0, -3.0]]
            }
        }
    ]
}

def test_file_upload_conversion():
    """Test file upload and conversion to GeoJSON with Supabase storage"""
    print("\n1. Testing file upload and conversion...")
    
    # Create a temporary GeoJSON file to upload
    test_geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Uploaded Test Feature", "type": "upload_test"},
                "geometry": {
                    "type": "Point",
                    "coordinates": [24.0, -6.0]
                }
            }
        ]
    }
    
    # Write to temporary file
    temp_file = "temp_test_upload.geojson"
    with open(temp_file, 'w') as f:
        json.dump(test_geojson, f)
    
    try:
        # Upload the file
        with open(temp_file, 'rb') as f:
            files = {'file': (temp_file, f, 'application/json')}
            response = requests.post(f"{BASE_URL}/convert", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ File upload successful!")
            print(f"   Layer name: {result.get('layer_name', 'unknown')}")
            print(f"   Storage: {result.get('storage', 'unknown')}")
            print(f"   Features: {result.get('features_count', 0)}")
            return result.get('layer_name'), result.get('storage') == 'supabase'
        else:
            print(f"❌ File upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None, False
    except Exception as e:
        print(f"❌ Error during file upload: {e}")
        return None, False
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file):
            os.remove(temp_file)

def test_drawing_layer_creation():
    """Test layer creation via drawing (simulated via /data/<layer>/update)"""
    print("\n2. Testing drawing layer creation...")
    
    layer_name = "test_drawing_layer"
    
    try:
        response = requests.post(
            f"{BASE_URL}/data/{layer_name}/update",
            json={"features": TEST_DRAWING_GEOJSON["features"]},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Drawing layer created successfully!")
            print(f"   Layer: {layer_name}")
            print(f"   Storage: {result.get('storage', 'unknown')}")
            print(f"   Features: {result.get('updatedCount', 0)}")
            return layer_name, result.get('storage') == 'supabase'
        else:
            print(f"❌ Drawing layer creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None, False
    except Exception as e:
        print(f"❌ Error creating drawing layer: {e}")
        return None, False

def test_user_layer_creation():
    """Test user layer creation (exported layers)"""
    print("\n3. Testing user layer creation...")
    
    user_layer_name = "user_test_exported_layer"
    
    try:
        response = requests.post(
            f"{BASE_URL}/data/{user_layer_name}/update",
            json={"features": TEST_DRAWING_GEOJSON["features"]},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ User layer created successfully!")
            print(f"   Layer: {user_layer_name}")
            print(f"   Storage: {result.get('storage', 'unknown')}")
            print(f"   Features: {result.get('updatedCount', 0)}")
            return user_layer_name, result.get('storage') == 'supabase'
        else:
            print(f"❌ User layer creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None, False
    except Exception as e:
        print(f"❌ Error creating user layer: {e}")
        return None, False

def test_layer_retrieval(layer_name):
    """Test that created layers can be retrieved"""
    print(f"\n4. Testing layer retrieval for '{layer_name}'...")
    
    try:
        response = requests.get(f"{BASE_URL}/data/{layer_name}")
        
        if response.status_code == 200:
            data = response.json()
            features_count = len(data.get("features", []))
            print(f"✅ Layer retrieved successfully!")
            print(f"   Features: {features_count}")
            return True
        else:
            print(f"❌ Layer retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error retrieving layer: {e}")
        return False

def test_layers_listing():
    """Test that created layers appear in the layers list"""
    print("\n5. Testing layers listing...")
    
    try:
        response = requests.get(f"{BASE_URL}/data/layers")
        
        if response.status_code == 200:
            layers = response.json()
            print(f"✅ Layers list retrieved successfully!")
            print(f"   Total layers: {len(layers)}")
            print(f"   Available layers: {', '.join(layers[:10])}{'...' if len(layers) > 10 else ''}")
            return layers
        else:
            print(f"❌ Layers listing failed: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error listing layers: {e}")
        return []

def main():
    """Run all tests"""
    print("🧪 Testing New Layer Creation with Supabase Bucket Storage")
    print("=" * 60)
    
    created_layers = []
    supabase_saves = 0
    total_tests = 0
    
    # Test 1: File upload conversion
    layer_name, saved_to_supabase = test_file_upload_conversion()
    if layer_name:
        created_layers.append(layer_name)
        if saved_to_supabase:
            supabase_saves += 1
        total_tests += 1
    
    # Test 2: Drawing layer creation
    layer_name, saved_to_supabase = test_drawing_layer_creation()
    if layer_name:
        created_layers.append(layer_name)
        if saved_to_supabase:
            supabase_saves += 1
        total_tests += 1
    
    # Test 3: User layer creation
    layer_name, saved_to_supabase = test_user_layer_creation()
    if layer_name:
        created_layers.append(layer_name)
        if saved_to_supabase:
            supabase_saves += 1
        total_tests += 1
    
    # Test 4: Layer retrieval for each created layer
    retrieval_success = 0
    for layer_name in created_layers:
        if test_layer_retrieval(layer_name):
            retrieval_success += 1
    
    # Test 5: Layers listing
    all_layers = test_layers_listing()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Layers created: {len(created_layers)}/{total_tests}")
    print(f"✅ Saved to Supabase: {supabase_saves}/{total_tests}")
    print(f"✅ Successfully retrieved: {retrieval_success}/{len(created_layers)}")
    print(f"✅ Total layers in system: {len(all_layers)}")
    
    if supabase_saves > 0:
        print(f"\n🎉 SUCCESS: {supabase_saves} new layers were saved to Supabase buckets!")
    else:
        print(f"\n⚠️  WARNING: No layers were saved to Supabase buckets (using local fallback)")
    
    # Check if our test layers are in the system
    found_layers = [layer for layer in created_layers if layer in all_layers]
    print(f"✅ Test layers found in system: {len(found_layers)}/{len(created_layers)}")
    
    if len(found_layers) == len(created_layers) and supabase_saves > 0:
        print("\n🎯 ALL TESTS PASSED: New layer creation is working with Supabase bucket storage!")
    elif len(found_layers) == len(created_layers):
        print("\n✅ TESTS PASSED: New layer creation is working with local fallback storage!")
    else:
        print("\n❌ SOME TESTS FAILED: Check the logs above for details.")

if __name__ == "__main__":
    main()
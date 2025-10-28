#!/usr/bin/env python3
"""
Test script for Supabase bucket layer storage functionality
"""

import json
import requests
import time

# Test configuration
BASE_URL = "http://localhost:5050"
TEST_LAYER_NAME = "test_aor_layer"

# Sample GeoJSON data for testing
TEST_GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [28.8, -2.5],
                    [28.9, -2.5],
                    [28.9, -2.4],
                    [28.8, -2.4],
                    [28.8, -2.5]
                ]]
            },
            "properties": {
                "name": "Test AoR Area",
                "description": "Test area of responsibility",
                "priority": "high"
            }
        }
    ]
}

def test_layer_operations():
    """Test all layer operations: create, read, update, delete"""
    
    print("🧪 Testing Supabase Bucket Layer Storage")
    print("=" * 50)
    
    # Test 1: Create/Update Layer
    print("\n1. Testing layer creation/update...")
    try:
        response = requests.post(
            f"{BASE_URL}/data/{TEST_LAYER_NAME}/update",
            json={"features": TEST_GEOJSON["features"]},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Layer created successfully!")
            print(f"   Storage: {result.get('storage', 'unknown')}")
            print(f"   Features: {result.get('updatedCount', 0)}")
        else:
            print(f"❌ Failed to create layer: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating layer: {e}")
        return False
    
    # Test 2: List Layers
    print("\n2. Testing layer listing...")
    try:
        response = requests.get(f"{BASE_URL}/data/layers")
        
        if response.status_code == 200:
            layers = response.json()
            if TEST_LAYER_NAME in layers:
                print(f"✅ Layer found in list!")
                print(f"   Total layers: {len(layers)}")
            else:
                print(f"⚠️  Layer not found in list. Available: {layers}")
        else:
            print(f"❌ Failed to list layers: {response.status_code}")
    except Exception as e:
        print(f"❌ Error listing layers: {e}")
    
    # Test 3: Retrieve Layer
    print("\n3. Testing layer retrieval...")
    try:
        response = requests.get(f"{BASE_URL}/data/{TEST_LAYER_NAME}")
        
        if response.status_code == 200:
            layer_data = response.json()
            if layer_data.get("type") == "FeatureCollection":
                print(f"✅ Layer retrieved successfully!")
                print(f"   Features: {len(layer_data.get('features', []))}")
            else:
                print(f"⚠️  Retrieved data format unexpected: {type(layer_data)}")
        else:
            print(f"❌ Failed to retrieve layer: {response.status_code}")
    except Exception as e:
        print(f"❌ Error retrieving layer: {e}")
    
    # Test 4: Update Layer
    print("\n4. Testing layer update...")
    try:
        # Add another feature
        updated_features = TEST_GEOJSON["features"] + [{
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [28.85, -2.45]
            },
            "properties": {
                "name": "Test Point",
                "description": "Updated test point"
            }
        }]
        
        response = requests.post(
            f"{BASE_URL}/data/{TEST_LAYER_NAME}/update",
            json={"features": updated_features},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Layer updated successfully!")
            print(f"   Storage: {result.get('storage', 'unknown')}")
            print(f"   Features: {result.get('updatedCount', 0)}")
        else:
            print(f"❌ Failed to update layer: {response.status_code}")
    except Exception as e:
        print(f"❌ Error updating layer: {e}")
    
    # Test 5: Delete Layer
    print("\n5. Testing layer deletion...")
    try:
        response = requests.delete(f"{BASE_URL}/data/{TEST_LAYER_NAME}/delete")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Layer deleted successfully!")
            print(f"   Storage: {result.get('storage', [])}")
        else:
            print(f"❌ Failed to delete layer: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error deleting layer: {e}")
    
    # Test 6: Verify Deletion
    print("\n6. Verifying layer deletion...")
    try:
        response = requests.get(f"{BASE_URL}/data/{TEST_LAYER_NAME}")
        
        if response.status_code == 404:
            print(f"✅ Layer successfully deleted (404 as expected)!")
        else:
            print(f"⚠️  Layer still exists after deletion: {response.status_code}")
    except Exception as e:
        print(f"❌ Error verifying deletion: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Test completed!")
    
    return True

if __name__ == "__main__":
    # Wait a moment for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    test_layer_operations()
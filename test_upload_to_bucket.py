#!/usr/bin/env python3
"""
Test script to verify upload functionality to Geojson bucket
"""
import json
from dotenv import load_dotenv
from supabase_client import upload_layer_to_bucket, download_layer_from_bucket, ensure_layers_bucket

# Load environment variables
load_dotenv(override=True)

def test_upload_functionality():
    """Test uploading a layer to the Geojson bucket"""
    print("🧪 Testing Upload to Geojson Bucket")
    print("=" * 50)
    
    # Check bucket accessibility
    print("1. Checking bucket accessibility...")
    bucket_exists = ensure_layers_bucket()
    print(f"   Bucket accessible: {'✅ Yes' if bucket_exists else '❌ No'}")
    print()
    
    if not bucket_exists:
        print("❌ Cannot proceed without bucket access")
        return
    
    # Create test GeoJSON data
    test_geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [0, 0]
                },
                "properties": {
                    "name": "Test Point",
                    "description": "Test upload to bucket"
                }
            }
        ]
    }
    
    test_layer_name = "test_upload_layer"
    
    # Test upload
    print("2. Testing layer upload...")
    upload_result = upload_layer_to_bucket(test_layer_name, test_geojson)
    
    if upload_result.get("success"):
        print(f"   ✅ Upload successful!")
        print(f"   Message: {upload_result.get('message')}")
    else:
        print(f"   ❌ Upload failed: {upload_result.get('error')}")
        return
    
    print()
    
    # Test download to verify upload
    print("3. Testing layer download to verify upload...")
    download_result = download_layer_from_bucket(test_layer_name)
    
    if download_result.get("success"):
        print(f"   ✅ Download successful!")
        downloaded_data = download_result.get("data")
        if downloaded_data:
            features_count = len(downloaded_data.get("features", []))
            print(f"   Features in downloaded layer: {features_count}")
        else:
            print("   ⚠️  Downloaded data is empty")
    else:
        print(f"   ❌ Download failed: {download_result.get('error')}")
    
    print()
    print("=" * 50)
    print("Upload test completed!")

if __name__ == "__main__":
    test_upload_functionality()
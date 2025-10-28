#!/usr/bin/env python3
"""
Final test for upload functionality with service role key
"""
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

def test_final_upload():
    """Test upload functionality"""
    print("🚀 Final Upload Test with Service Role Key")
    print("=" * 50)
    
    # Verify environment variables
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not service_key:
        print("❌ Service role key not found!")
        return
    
    print(f"✅ Service role key loaded: {service_key[:20]}...")
    
    try:
        from supabase_client import upload_layer_to_bucket
        
        # Create test GeoJSON data
        test_geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Final Test Layer",
                        "description": "Testing service role key upload"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [77.2090, 28.6139]  # New Delhi
                    }
                }
            ]
        }
        
        # Convert to JSON string
        geojson_content = json.dumps(test_geojson, indent=2)
        
        # Test upload
        layer_name = "final_test_layer"
        print(f"\n📤 Uploading layer: {layer_name}")
        
        result = upload_layer_to_bucket(layer_name, geojson_content)
        
        print(f"\n📋 Upload Result:")
        print(f"   Success: {result.get('success', False)}")
        
        if result.get('success'):
            print("   ✅ UPLOAD SUCCESSFUL!")
            print(f"   Message: {result.get('message', 'No message')}")
            if 'url' in result:
                print(f"   URL: {result['url']}")
        else:
            print("   ❌ Upload failed")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_final_upload()
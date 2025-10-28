#!/usr/bin/env python3
"""
Comprehensive test for service role key upload functionality
"""
import os
import json
from dotenv import load_dotenv

# Load environment variables with override
load_dotenv(override=True)

def test_service_role_upload():
    """Test upload functionality with service role key"""
    print("🧪 Testing Service Role Key Upload Functionality")
    print("=" * 60)
    
    # Check environment variables
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_anon_key = os.environ.get("SUPABASE_ANON_KEY")
    supabase_service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    
    print("1. Environment Variables Check:")
    print(f"   SUPABASE_URL: {'✅ Set' if supabase_url else '❌ Not set'}")
    print(f"   SUPABASE_ANON_KEY: {'✅ Set' if supabase_anon_key else '❌ Not set'}")
    print(f"   SUPABASE_SERVICE_ROLE_KEY: {'✅ Set' if supabase_service_key else '❌ Not set'}")
    
    if not all([supabase_url, supabase_anon_key, supabase_service_key]):
        print("❌ Missing required environment variables!")
        return
    
    print()
    
    # Test client creation
    print("2. Client Creation Test:")
    try:
        from supabase_client import get_supabase_client, get_admin_supabase_client
        
        # Test clients
        anon_client = get_supabase_client()
        admin_client = get_admin_supabase_client()
        
        print(f"   ✅ Anonymous client created")
        print(f"   ✅ Admin client created")
        
        # Check if they use different keys
        anon_auth = getattr(anon_client, 'auth', None)
        admin_auth = getattr(admin_client, 'auth', None)
        
        if anon_auth and admin_auth:
            anon_token = getattr(anon_auth, 'session', {}).get('access_token', 'none')
            admin_token = getattr(admin_auth, 'session', {}).get('access_token', 'none')
            
            if anon_token != admin_token:
                print(f"   ✅ Clients use different authentication tokens")
            else:
                print(f"   ⚠️  Clients may be using same authentication")
        
    except Exception as e:
        print(f"   ❌ Client creation failed: {e}")
        return
    
    print()
    
    # Test bucket access
    print("3. Bucket Access Test:")
    try:
        from supabase_client import ensure_layers_bucket
        
        bucket_result = ensure_layers_bucket()
        print(f"   Bucket check result: {bucket_result}")
        
        if bucket_result.get('success'):
            print("   ✅ Bucket is accessible")
        else:
            print("   ❌ Bucket access failed")
            
    except Exception as e:
        print(f"   ❌ Bucket access test failed: {e}")
        return
    
    print()
    
    # Test upload functionality
    print("4. Upload Test:")
    try:
        from supabase_client import upload_layer_to_bucket
        
        # Create test GeoJSON data
        test_geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"name": "Service Role Test"},
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
        layer_name = "service_role_test_layer"
        print(f"   Attempting to upload layer: {layer_name}")
        
        result = upload_layer_to_bucket(layer_name, geojson_content)
        
        if result.get('success'):
            print("   ✅ Upload successful!")
            print(f"   Upload result: {result}")
        else:
            print("   ❌ Upload failed!")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"   ❌ Upload test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    test_service_role_upload()
#!/usr/bin/env python3
"""
Test script to verify Geojson bucket accessibility
"""
import os
from dotenv import load_dotenv
from supabase_client import get_storage_client, list_layers_in_bucket, ensure_layers_bucket

# Load environment variables
load_dotenv()

def test_bucket_access():
    """Test if we can access the Geojson bucket"""
    print("🧪 Testing Geojson Bucket Access")
    print("=" * 50)
    
    # Check environment variables
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_ANON_KEY")
    
    print(f"SUPABASE_URL: {'✅ Set' if supabase_url else '❌ Not set'}")
    print(f"SUPABASE_ANON_KEY: {'✅ Set' if supabase_key else '❌ Not set'}")
    print()
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials in environment variables")
        return
    
    # Test bucket existence
    print("1. Testing bucket existence...")
    bucket_exists = ensure_layers_bucket()
    print(f"   Bucket 'Geojson' exists: {'✅ Yes' if bucket_exists else '❌ No'}")
    print()
    
    # Test listing files in bucket
    print("2. Testing file listing...")
    try:
        result = list_layers_in_bucket()
        if result.get("success"):
            layers = result.get("layers", [])
            print(f"   ✅ Successfully listed {len(layers)} layers")
            if layers:
                print("   Available layers:")
                for layer in layers[:10]:  # Show first 10
                    print(f"     - {layer}")
                if len(layers) > 10:
                    print(f"     ... and {len(layers) - 10} more")
        else:
            print(f"   ❌ Failed to list layers: {result.get('error')}")
    except Exception as e:
        print(f"   ❌ Exception during listing: {e}")
    
    print()
    
    # Test storage client directly
    print("3. Testing storage client directly...")
    try:
        storage = get_storage_client()
        bucket_info = storage.get_bucket("Geojson")
        print(f"   ✅ Bucket info retrieved: {bucket_info}")
    except Exception as e:
        print(f"   ❌ Direct bucket access failed: {e}")
    
    print()
    print("=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_bucket_access()
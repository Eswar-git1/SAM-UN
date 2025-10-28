#!/usr/bin/env python3
"""
Migration script to move existing layers from local storage to Supabase buckets
"""

import os
import json
from supabase_client import upload_layer_to_bucket, ensure_layers_bucket

def migrate_layers():
    """
    Migrate all existing GeoJSON layers from local storage to Supabase buckets
    """
    
    print("🚀 Starting layer migration to Supabase buckets")
    print("=" * 60)
    
    # Define the local GeoJSON directory
    geojson_dir = os.path.join(os.path.dirname(__file__), "Assignment", "GeoJSON Output")
    
    if not os.path.exists(geojson_dir):
        print(f"❌ GeoJSON directory not found: {geojson_dir}")
        return False
    
    # Ensure the Supabase bucket exists
    print("\n1. Ensuring Supabase bucket exists...")
    if ensure_layers_bucket():
        print("✅ Bucket is ready!")
    else:
        print("❌ Failed to ensure bucket exists. Check Supabase configuration.")
        return False
    
    # Get list of GeoJSON files
    geojson_files = [f for f in os.listdir(geojson_dir) if f.endswith('.geojson')]
    
    if not geojson_files:
        print(f"ℹ️  No GeoJSON files found in {geojson_dir}")
        return True
    
    print(f"\n2. Found {len(geojson_files)} layers to migrate:")
    for file in geojson_files:
        print(f"   - {file}")
    
    # Migrate each layer
    print(f"\n3. Starting migration...")
    
    migrated_count = 0
    failed_count = 0
    
    for filename in geojson_files:
        layer_name = filename[:-8]  # Remove .geojson extension
        file_path = os.path.join(geojson_dir, filename)
        
        print(f"\n   Migrating: {layer_name}")
        
        try:
            # Read the local GeoJSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                geojson_data = json.load(f)
            
            # Validate GeoJSON structure
            if not isinstance(geojson_data, dict) or geojson_data.get("type") != "FeatureCollection":
                print(f"   ⚠️  Skipping {layer_name}: Invalid GeoJSON structure")
                failed_count += 1
                continue
            
            # Upload to Supabase bucket
            result = upload_layer_to_bucket(layer_name, geojson_data)
            
            if result.get("success"):
                print(f"   ✅ Successfully migrated {layer_name}")
                migrated_count += 1
            else:
                print(f"   ❌ Failed to migrate {layer_name}: {result.get('error', 'Unknown error')}")
                failed_count += 1
                
        except Exception as e:
            print(f"   ❌ Error migrating {layer_name}: {str(e)}")
            failed_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Migration Summary:")
    print(f"   ✅ Successfully migrated: {migrated_count} layers")
    print(f"   ❌ Failed migrations: {failed_count} layers")
    print(f"   📁 Total processed: {len(geojson_files)} layers")
    
    if migrated_count > 0:
        print(f"\n🎉 Migration completed! {migrated_count} layers are now available in Supabase buckets.")
        print("   New user layers will automatically be stored in Supabase buckets.")
    
    if failed_count > 0:
        print(f"\n⚠️  {failed_count} layers failed to migrate. They will remain in local storage as fallback.")
    
    return migrated_count > 0

def verify_migration():
    """
    Verify that migrated layers can be retrieved from Supabase
    """
    from supabase_client import list_layers_in_bucket, download_layer_from_bucket
    
    print("\n🔍 Verifying migration...")
    
    try:
        # List layers in bucket
        result = list_layers_in_bucket()
        if result.get("success"):
            layers = result["layers"]
            print(f"✅ Found {len(layers)} layers in Supabase bucket")
            
            # Test downloading a few layers
            test_count = min(3, len(layers))
            for i, layer_name in enumerate(layers[:test_count]):
                download_result = download_layer_from_bucket(layer_name)
                if download_result.get("success"):
                    print(f"   ✅ {layer_name}: Download successful")
                else:
                    print(f"   ❌ {layer_name}: Download failed")
                    
        else:
            print(f"❌ Failed to list layers: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check if Supabase is configured
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        print("⚠️  Supabase environment variables not configured.")
        print("   Please set SUPABASE_URL and SUPABASE_ANON_KEY in your .env file.")
        print("   Migration will be skipped, but the system will work with local storage fallback.")
        exit(1)
    
    # Run migration
    success = migrate_layers()
    
    if success:
        verify_migration()
    
    print("\n🏁 Migration process completed!")
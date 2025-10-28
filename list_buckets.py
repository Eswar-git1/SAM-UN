#!/usr/bin/env python3
"""
List all available buckets in Supabase storage
"""
import os
from dotenv import load_dotenv
from supabase_client import get_storage_client

# Load environment variables
load_dotenv()

def list_all_buckets():
    """List all available buckets"""
    print("🗂️  Listing All Supabase Storage Buckets")
    print("=" * 50)
    
    try:
        storage = get_storage_client()
        buckets = storage.list_buckets()
        
        print(f"Found {len(buckets)} bucket(s):")
        print()
        
        for i, bucket in enumerate(buckets, 1):
            print(f"{i}. Bucket: '{bucket.name}'")
            print(f"   ID: {bucket.id}")
            print(f"   Public: {bucket.public}")
            print(f"   Created: {bucket.created_at}")
            print()
            
            # Try to list files in this bucket
            try:
                files = storage.from_(bucket.name).list()
                print(f"   Files in bucket: {len(files)}")
                if files:
                    print("   Sample files:")
                    for file in files[:5]:  # Show first 5 files
                        print(f"     - {file.get('name', 'Unknown')}")
                    if len(files) > 5:
                        print(f"     ... and {len(files) - 5} more")
                print()
            except Exception as e:
                print(f"   ❌ Could not list files: {e}")
                print()
        
    except Exception as e:
        print(f"❌ Failed to list buckets: {e}")

if __name__ == "__main__":
    list_all_buckets()
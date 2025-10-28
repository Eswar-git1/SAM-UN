#!/usr/bin/env python3
"""
Debug dotenv loading
"""
import os
from dotenv import load_dotenv, dotenv_values

def debug_dotenv():
    """Debug dotenv loading"""
    print("🔍 Debugging dotenv loading")
    print("=" * 50)
    
    # Check current environment before loading
    print("1. Environment before loading:")
    service_key_before = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    print(f"   SUPABASE_SERVICE_ROLE_KEY: {service_key_before or 'Not set'}")
    
    # Load dotenv values without setting environment
    print("\n2. Reading .env file directly:")
    try:
        env_values = dotenv_values(".env")
        service_key_in_file = env_values.get("SUPABASE_SERVICE_ROLE_KEY")
        print(f"   SUPABASE_SERVICE_ROLE_KEY in file: {'Found' if service_key_in_file else 'Not found'}")
        if service_key_in_file:
            print(f"   Value starts with: {service_key_in_file[:20]}...")
    except Exception as e:
        print(f"   Error reading .env file: {e}")
    
    # Load dotenv with override
    print("\n3. Loading with override=True:")
    try:
        result = load_dotenv(override=True)
        print(f"   load_dotenv result: {result}")
        
        service_key_after = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        print(f"   SUPABASE_SERVICE_ROLE_KEY after loading: {'Set' if service_key_after else 'Not set'}")
        if service_key_after:
            print(f"   Value starts with: {service_key_after[:20]}...")
            
    except Exception as e:
        print(f"   Error loading .env: {e}")
    
    # Check all environment variables that start with SUPABASE
    print("\n4. All SUPABASE environment variables:")
    for key, value in os.environ.items():
        if key.startswith("SUPABASE"):
            print(f"   {key}: {value[:20] if value else 'Empty'}...")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    debug_dotenv()
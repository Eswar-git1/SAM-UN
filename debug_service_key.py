#!/usr/bin/env python3
"""
Debug script to check service role key configuration
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

def debug_service_key():
    """Debug service role key configuration"""
    print("🔍 Debugging Service Role Key Configuration")
    print("=" * 60)
    
    # Check environment variables
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_anon_key = os.environ.get("SUPABASE_ANON_KEY")
    supabase_service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    
    print("Environment Variables:")
    print(f"  SUPABASE_URL: {'✅ Set' if supabase_url else '❌ Not set'}")
    if supabase_url:
        print(f"    Value: {supabase_url[:30]}...")
    
    print(f"  SUPABASE_ANON_KEY: {'✅ Set' if supabase_anon_key else '❌ Not set'}")
    if supabase_anon_key:
        print(f"    Value: {supabase_anon_key[:20]}...")
    
    print(f"  SUPABASE_SERVICE_ROLE_KEY: {'✅ Set' if supabase_service_key else '❌ Not set'}")
    if supabase_service_key:
        print(f"    Value: {supabase_service_key[:20]}...")
    
    print()
    
    # Test client creation
    print("Client Creation Test:")
    try:
        from supabase_client import get_supabase_client, get_admin_supabase_client
        
        # Test anonymous client
        anon_client = get_supabase_client()
        print(f"  ✅ Anonymous client created successfully")
        
        # Test admin client
        admin_client = get_admin_supabase_client()
        print(f"  ✅ Admin client created successfully")
        
        # Check if they're different
        if anon_client == admin_client:
            print("  ⚠️  WARNING: Admin client is same as anonymous client (service key not used)")
        else:
            print("  ✅ Admin client is different from anonymous client (service key being used)")
            
    except Exception as e:
        print(f"  ❌ Client creation failed: {e}")
    
    print()
    
    # Recommendations
    print("Recommendations:")
    if not supabase_service_key:
        print("  1. ❌ Add SUPABASE_SERVICE_ROLE_KEY to your .env file")
        print("     - Go to Supabase Dashboard → Settings → API")
        print("     - Copy the 'service_role' key (not the anon key)")
        print("     - Add to .env: SUPABASE_SERVICE_ROLE_KEY=your-service-key-here")
    else:
        print("  1. ✅ Service role key is configured")
        
    print("  2. Ensure the service role key has proper permissions")
    print("  3. Check that storage policies allow service role operations")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    debug_service_key()
#!/usr/bin/env python3
"""
Debug script to test authentication and identify login issues
"""
import os
from dotenv import load_dotenv
from supabase_client import get_admin_supabase_client, authenticate_user

# Load environment variables
load_dotenv()

def check_users_table():
    """Check what users exist in the database"""
    print("Checking users table...")
    try:
        supabase = get_admin_supabase_client()
        response = supabase.table("users").select("id, username, password, email, role, created_at").execute()
        
        if response.data:
            print(f"Found {len(response.data)} users in database:")
            for user in response.data:
                print(f"  ID: {user['id']}")
                print(f"  Username: '{user['username']}'")
                print(f"  Password: '{user['password']}'")
                print(f"  Email: {user.get('email', 'None')}")
                print(f"  Role: {user.get('role', 'None')}")
                print(f"  Created: {user.get('created_at', 'None')}")
                print("-" * 40)
        else:
            print("No users found in the database!")
        return response.data
    except Exception as e:
        print(f"Error checking users table: {e}")
        return None

def test_authentication():
    """Test authentication with known credentials"""
    print("\nTesting authentication...")
    
    # Test credentials
    test_users = [
        ("admin", "admin123"),
        ("analyst", "analyst123"),
        ("observer", "observer123"),
        ("adjt_sam_un_bn1", "asdf1234ASDF!@#$"),
        ("adjt_sam_un_bn2", "asdf1234ASDF!@#$"),
        ("gso1_sam_un_bde1", "asdf1234ASDF!@#$")
    ]
    
    for username, password in test_users:
        print(f"\nTesting: '{username}' with password: '{password}'")
        try:
            user = authenticate_user(username, password)
            if user:
                print(f"  ✓ SUCCESS - User authenticated: {user}")
            else:
                print(f"  ✗ FAILED - Authentication returned None")
        except Exception as e:
            print(f"  ✗ ERROR - Exception during authentication: {e}")

def test_direct_query():
    """Test direct database query to see what's happening"""
    print("\nTesting direct database queries...")
    
    supabase = get_admin_supabase_client()
    
    # Test specific user lookup
    test_username = "admin"
    test_password = "admin123"
    
    print(f"Looking for user: '{test_username}' with password: '{test_password}'")
    
    try:
        # First, check if user exists
        response1 = supabase.table("users").select("*").eq("username", test_username).execute()
        print(f"User lookup result: {response1.data}")
        
        # Then check with password
        response2 = supabase.table("users").select("*").eq("username", test_username).eq("password", test_password).execute()
        print(f"User + password lookup result: {response2.data}")
        
    except Exception as e:
        print(f"Direct query error: {e}")

def main():
    print("SAM UN - Login Debug Tool")
    print("=" * 50)
    
    # Check database connection
    try:
        supabase = get_admin_supabase_client()
        print("✓ Database connection successful")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return
    
    # Check users table
    users = check_users_table()
    
    if users:
        # Test authentication
        test_authentication()
        
        # Test direct queries
        test_direct_query()
    else:
        print("Cannot proceed with authentication tests - no users found!")

if __name__ == "__main__":
    main()
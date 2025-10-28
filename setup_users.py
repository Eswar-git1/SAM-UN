#!/usr/bin/env python3
"""
Script to create test users in Supabase
Note: The users table must be created manually in Supabase SQL editor first
"""
import os
from dotenv import load_dotenv
from supabase_client import get_admin_supabase_client

# Load environment variables
load_dotenv()

def create_test_users_direct():
    """Create three test users using direct table insertion"""
    supabase = get_admin_supabase_client()
    
    test_users = [
        {
            "username": "admin",
            "password": "admin123",
            "email": "admin@un.org",
            "role": "admin"
        },
        {
            "username": "analyst",
            "password": "analyst123",
            "email": "analyst@un.org",
            "role": "analyst"
        },
        {
            "username": "observer",
            "password": "observer123",
            "email": "observer@un.org",
            "role": "observer"
        }
    ]
    
    print("Creating test users...")
    for user_data in test_users:
        try:
            # Try to insert user directly into the table
            response = supabase.table("users").insert(user_data).execute()
            if response.data:
                print(f"✓ Created user: {user_data['username']} (password: {user_data['password']})")
            else:
                print(f"✗ Failed to create user: {user_data['username']}")
        except Exception as e:
            if "duplicate key" in str(e).lower() or "already exists" in str(e).lower():
                print(f"⚠ User {user_data['username']} already exists")
            else:
                print(f"✗ Error creating user {user_data['username']}: {e}")

def check_users_table():
    """Check if users table exists and show existing users"""
    supabase = get_admin_supabase_client()
    
    try:
        response = supabase.table("users").select("username, email, role, created_at").execute()
        if response.data:
            print(f"Found {len(response.data)} existing users:")
            for user in response.data:
                print(f"  - {user['username']} ({user['role']}) - {user['email']}")
        else:
            print("No users found in the table")
        return True
    except Exception as e:
        print(f"Error checking users table: {e}")
        print("The users table may not exist. Please create it using the SQL in create_users_table.sql")
        return False

def main():
    print("Setting up users for SAM UN application...")
    print("=" * 50)
    
    # Check if users table exists
    print("1. Checking users table...")
    if not check_users_table():
        print("\nPlease run the SQL from create_users_table.sql in your Supabase SQL editor first.")
        return
    
    print("\n2. Creating test users...")
    create_test_users_direct()
    
    print("\n3. Final user list:")
    check_users_table()
    
    print("\n" + "=" * 50)
    print("Setup complete!")
    print("\nTest user credentials:")
    print("1. Username: admin     | Password: admin123     | Role: admin")
    print("2. Username: analyst   | Password: analyst123   | Role: analyst")
    print("3. Username: observer  | Password: observer123  | Role: observer")
    print("\nYou can now use these credentials to log into the application.")

if __name__ == "__main__":
    main()
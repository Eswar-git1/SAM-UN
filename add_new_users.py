#!/usr/bin/env python3
"""
Script to add three new users to the SAM UN application
"""
import os
from dotenv import load_dotenv
from supabase_client import get_admin_supabase_client

# Load environment variables
load_dotenv()

def add_new_users():
    """Add the three new users to the database"""
    supabase = get_admin_supabase_client()
    
    # New users with specified credentials
    new_users = [
        {
            "username": "adjt_sam_un_bn1",
            "password": "asdf1234ASDF!@#$",
            "role": "user"
        },
        {
            "username": "adjt_sam_un_bn2", 
            "password": "asdf1234ASDF!@#$",
            "role": "user"
        },
        {
            "username": "gso1_sam_un_bde1",
            "password": "asdf1234ASDF!@#$",
            "role": "user"
        }
    ]
    
    print("Adding new users to SAM UN application...")
    print("=" * 50)
    
    success_count = 0
    
    for user_data in new_users:
        try:
            # Insert the user
            response = supabase.table("users").insert(user_data).execute()
            if response.data:
                print(f"✓ Created user: {user_data['username']}")
                success_count += 1
            else:
                print(f"✗ Failed to create user: {user_data['username']}")
        except Exception as e:
            error_msg = str(e).lower()
            if "duplicate" in error_msg or "already exists" in error_msg:
                print(f"⚠ User {user_data['username']} already exists")
                success_count += 1
            else:
                print(f"✗ Error creating user {user_data['username']}: {e}")
    
    print("\n" + "=" * 50)
    print(f"User creation completed! ({success_count}/3 users processed)")
    
    if success_count > 0:
        print("\nNew user credentials:")
        print("Username: adjt_sam_un_bn1   | Password: asdf1234ASDF!@#$")
        print("Username: adjt_sam_un_bn2   | Password: asdf1234ASDF!@#$")
        print("Username: gso1_sam_un_bde1  | Password: asdf1234ASDF!@#$")
        print("\nAll users can now log into the application.")
    
    return success_count > 0

def test_new_users():
    """Test authentication for the new users"""
    from supabase_client import authenticate_user
    
    test_credentials = [
        ("adjt_sam_un_bn1", "asdf1234ASDF!@#$"),
        ("adjt_sam_un_bn2", "asdf1234ASDF!@#$"),
        ("gso1_sam_un_bde1", "asdf1234ASDF!@#$")
    ]
    
    print("\nTesting authentication for new users...")
    for username, password in test_credentials:
        try:
            user = authenticate_user(username, password)
            if user:
                print(f"✓ Authentication successful for {username}")
            else:
                print(f"✗ Authentication failed for {username}")
        except Exception as e:
            print(f"✗ Authentication error for {username}: {e}")

if __name__ == "__main__":
    print("SAM UN - Adding New Users")
    print("=" * 30)
    
    if add_new_users():
        test_new_users()
    else:
        print("\nUser creation failed. Please check your database connection.")
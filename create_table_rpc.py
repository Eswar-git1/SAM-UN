#!/usr/bin/env python3
"""
Script to create users table using Supabase RPC
"""
import os
from dotenv import load_dotenv
from supabase_client import get_admin_supabase_client

# Load environment variables
load_dotenv()

def create_users_table_rpc():
    """Create users table using RPC function"""
    supabase = get_admin_supabase_client()
    
    # First, let's try to create a simple RPC function to execute SQL
    try:
        # Try to call a simple function to test RPC
        response = supabase.rpc('version').execute()
        print(f"Supabase connection successful: {response.data}")
    except Exception as e:
        print(f"RPC test failed: {e}")
    
    # Let's try to create the table using a different approach
    # We'll use the storage client to check if we can access the database
    try:
        # Check if we can access any existing tables
        response = supabase.table('sitreps').select('id').limit(1).execute()
        print("Database connection successful - can access sitreps table")
        
        # Now try to create users table by inserting a test record
        # This will fail if the table doesn't exist, which will tell us we need to create it
        try:
            test_response = supabase.table('users').select('id').limit(1).execute()
            print("Users table already exists!")
            return True
        except Exception as table_error:
            print(f"Users table doesn't exist: {table_error}")
            print("Please create the users table manually using the SQL in create_users_table.sql")
            return False
            
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

if __name__ == "__main__":
    create_users_table_rpc()
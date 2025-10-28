#!/usr/bin/env python3
"""
Test script to verify session timeout functionality
"""
import requests
import time
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:5050"
TEST_USERNAME = "adjt_sam_un_bn1"
TEST_PASSWORD = "asdf1234ASDF!@#$"

def test_session_timeout():
    """Test session timeout functionality"""
    print("=== Session Timeout Test ===")
    print(f"Testing with user: {TEST_USERNAME}")
    print(f"Base URL: {BASE_URL}")
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Step 1: Login
    print("\n1. Logging in...")
    login_data = {
        'username': TEST_USERNAME,
        'password': TEST_PASSWORD
    }
    
    login_response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
    
    if login_response.status_code == 302:  # Redirect after successful login
        print("✓ Login successful")
        print(f"  Redirected to: {login_response.headers.get('Location', 'Unknown')}")
    else:
        print(f"✗ Login failed with status: {login_response.status_code}")
        print(f"  Response: {login_response.text[:200]}...")
        return
    
    # Step 2: Access protected page
    print("\n2. Accessing protected page...")
    index_response = session.get(f"{BASE_URL}/")
    
    if index_response.status_code == 200:
        print("✓ Successfully accessed protected page")
    else:
        print(f"✗ Failed to access protected page: {index_response.status_code}")
        return
    
    # Step 3: Check session info
    print("\n3. Session information:")
    cookies = session.cookies.get_dict()
    if 'session' in cookies:
        print(f"  Session cookie present: {len(cookies['session'])} characters")
    else:
        print("  No session cookie found")
    
    print(f"  Current time: {datetime.now().strftime('%H:%M:%S')}")
    
    # Step 4: Wait and test session refresh
    print("\n4. Testing session refresh (waiting 5 seconds)...")
    time.sleep(5)
    
    refresh_response = session.get(f"{BASE_URL}/")
    if refresh_response.status_code == 200:
        print("✓ Session still valid after activity")
        print(f"  Time after refresh: {datetime.now().strftime('%H:%M:%S')}")
    else:
        print(f"✗ Session expired unexpectedly: {refresh_response.status_code}")
    
    # Step 5: Information about timeout
    print("\n5. Session timeout configuration:")
    print("  Default timeout: 30 minutes")
    print("  Session refreshes on each request")
    print("  To test actual timeout, wait 30+ minutes without activity")
    
    # Step 6: Logout
    print("\n6. Logging out...")
    logout_response = session.get(f"{BASE_URL}/logout", allow_redirects=False)
    
    if logout_response.status_code == 302:
        print("✓ Logout successful")
    else:
        print(f"✗ Logout failed: {logout_response.status_code}")
    
    # Step 7: Verify logout
    print("\n7. Verifying logout...")
    protected_response = session.get(f"{BASE_URL}/", allow_redirects=False)
    
    if protected_response.status_code == 302:  # Should redirect to login
        print("✓ Successfully logged out - redirected to login")
    else:
        print(f"✗ Still logged in: {protected_response.status_code}")

if __name__ == "__main__":
    try:
        test_session_timeout()
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to the Flask application")
        print("  Make sure the app is running on http://127.0.0.1:5050")
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
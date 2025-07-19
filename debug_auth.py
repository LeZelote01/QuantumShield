#!/usr/bin/env python3
"""
Debug authentication issue
"""

import requests
import json

def debug_auth():
    base_url = "http://localhost:8001/api"
    
    print("🔍 Debugging authentication...")
    
    # Test login
    login_data = {
        "username": "quantum_user_2025",
        "password": "QuantumSecure2025!"
    }
    
    print("1. Testing login...")
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Response keys: {list(data.keys())}")
        
        auth_token = data.get("access_token") or data.get("token")
        print(f"   Token received: {bool(auth_token)}")
        
        if auth_token:
            print(f"   Token (first 20 chars): {auth_token[:20]}...")
            
            # Test token verification
            print("\n2. Testing token verification...")
            headers = {"Authorization": f"Bearer {auth_token}"}
            verify_response = requests.get(f"{base_url}/auth/verify-token", headers=headers)
            print(f"   Verify status: {verify_response.status_code}")
            
            if verify_response.status_code != 200:
                print(f"   Verify error: {verify_response.text}")
            else:
                print("   Token is valid!")
                
                # Test MFA setup
                print("\n3. Testing MFA setup...")
                mfa_response = requests.post(f"{base_url}/auth/mfa/setup", headers=headers)
                print(f"   MFA status: {mfa_response.status_code}")
                
                if mfa_response.status_code == 200:
                    print("   ✅ MFA setup working!")
                else:
                    print(f"   ❌ MFA error: {mfa_response.text}")
    else:
        print(f"   Login failed: {response.text}")

if __name__ == "__main__":
    debug_auth()
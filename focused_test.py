#!/usr/bin/env python3
"""
Focused test for the specific endpoints mentioned in the review request
"""

import requests
import json

def test_specific_endpoints():
    base_url = "http://localhost:8001/api"
    
    # First get auth token
    login_data = {
        "username": "quantum_user_2025",
        "password": "QuantumSecure2025!"
    }
    
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    if response.status_code == 200:
        auth_token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {auth_token}"}
    else:
        print("❌ Failed to get auth token")
        return
    
    print("🔍 Testing specific endpoints mentioned in review request:")
    print("=" * 60)
    
    # Test the endpoints that were supposed to be fixed
    endpoints_to_test = [
        ("POST", "/auth/mfa/setup", None),
        ("POST", "/advanced-crypto/generate-keypair", {"algorithm": "kyber-768", "key_size": 2048}),
        ("GET", "/advanced-blockchain/validators", None),
        ("POST", "/advanced-blockchain/stake", {"validator_address": "0x1234567890abcdef1234567890abcdef12345678", "amount": 1000.0, "duration": 30}),
        ("GET", "/security/alerts", None),
        ("GET", "/ai-analytics/anomaly-detection", None),
        ("GET", "/ai-analytics/predictions", None),
        ("GET", "/advanced-blockchain/smart-contracts/templates", None)
    ]
    
    results = []
    
    for method, endpoint, data in endpoints_to_test:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=10)
            else:
                response = requests.post(f"{base_url}{endpoint}", json=data, headers=headers, timeout=10)
            
            status = "✅ WORKING" if response.status_code in [200, 201] else f"❌ HTTP {response.status_code}"
            print(f"{status} - {method} {endpoint}")
            
            if response.status_code not in [200, 201]:
                try:
                    error_detail = response.json().get("detail", response.text)
                    print(f"    Error: {error_detail}")
                except:
                    print(f"    Error: {response.text}")
            
            results.append({
                "endpoint": endpoint,
                "method": method,
                "status_code": response.status_code,
                "working": response.status_code in [200, 201]
            })
            
        except Exception as e:
            print(f"❌ EXCEPTION - {method} {endpoint}: {str(e)}")
            results.append({
                "endpoint": endpoint,
                "method": method,
                "status_code": None,
                "working": False,
                "error": str(e)
            })
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY:")
    working = sum(1 for r in results if r["working"])
    total = len(results)
    print(f"Working: {working}/{total} ({working/total*100:.1f}%)")
    
    print("\n✅ WORKING ENDPOINTS:")
    for r in results:
        if r["working"]:
            print(f"  - {r['method']} {r['endpoint']}")
    
    print("\n❌ FAILING ENDPOINTS:")
    for r in results:
        if not r["working"]:
            print(f"  - {r['method']} {r['endpoint']} (HTTP {r['status_code']})")

if __name__ == "__main__":
    test_specific_endpoints()
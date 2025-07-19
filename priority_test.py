#!/usr/bin/env python3
"""
Priority Test for the 3 specific endpoints mentioned in the review request
"""

import requests
import json
from datetime import datetime

class PriorityTester:
    def __init__(self):
        self.base_url = "http://localhost:8001/api"
        self.session = requests.Session()
        self.auth_token = None
        
    def authenticate(self):
        """Get authentication token"""
        try:
            login_data = {
                "username": "quantum_user_2025",
                "password": "QuantumSecure2025!"
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/login", 
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("token")
                print(f"✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_security_alerts(self):
        """Test /api/security/alerts - was HTTP 500, should now be HTTP 200"""
        print("\n🔍 Testing Security Alerts (Priority Endpoint 1/3)")
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = self.session.get(
                f"{self.base_url}/security/alerts",
                headers=headers,
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                alerts = data.get("alerts", [])
                print(f"✅ SUCCESS: Retrieved {len(alerts)} security alerts")
                print(f"Response: {json.dumps(data, indent=2, default=str)[:500]}...")
                return True
            else:
                print(f"❌ FAILED: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ FAILED: Exception {str(e)}")
            return False
    
    def test_token_staking(self):
        """Test /api/advanced-blockchain/stake - was HTTP 400, validation corrected"""
        print("\n🔍 Testing Token Staking (Priority Endpoint 2/3)")
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test with amount above minimum (1000.0 based on code inspection)
            stake_data = {
                "validator_address": "0x1234567890abcdef1234567890abcdef12345678",
                "amount": 1500.0,  # Above minimum 1000.0
                "duration": 30
            }
            
            response = self.session.post(
                f"{self.base_url}/advanced-blockchain/stake",
                json=stake_data,
                headers=headers,
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS: Staking completed")
                print(f"Response: {json.dumps(data, indent=2, default=str)}")
                return True
            else:
                print(f"❌ FAILED: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                
                # Try with lower amount to confirm minimum validation
                print("\n🔍 Testing with lower amount to confirm validation...")
                stake_data["amount"] = 10.0
                response2 = self.session.post(
                    f"{self.base_url}/advanced-blockchain/stake",
                    json=stake_data,
                    headers=headers,
                    timeout=30
                )
                print(f"Lower amount test - Status: {response2.status_code}")
                print(f"Lower amount test - Response: {response2.text}")
                return False
                
        except Exception as e:
            print(f"❌ FAILED: Exception {str(e)}")
            return False
    
    def test_smart_contract_templates(self):
        """Test /api/advanced-blockchain/templates - was HTTP 404, alias added"""
        print("\n🔍 Testing Smart Contract Templates (Priority Endpoint 3/3)")
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test the new alias endpoint
            response = self.session.get(
                f"{self.base_url}/advanced-blockchain/templates",
                headers=headers,
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                templates = data if isinstance(data, list) else data.get("templates", [])
                print(f"✅ SUCCESS: Retrieved {len(templates)} contract templates")
                print(f"Response: {json.dumps(data, indent=2, default=str)[:500]}...")
                return True
            else:
                print(f"❌ FAILED: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                
                # Also test the original endpoint
                print("\n🔍 Testing original endpoint...")
                response2 = self.session.get(
                    f"{self.base_url}/advanced-blockchain/smart-contracts/templates",
                    headers=headers,
                    timeout=30
                )
                print(f"Original endpoint - Status: {response2.status_code}")
                print(f"Original endpoint - Response: {response2.text[:200]}...")
                return False
                
        except Exception as e:
            print(f"❌ FAILED: Exception {str(e)}")
            return False
    
    def run_priority_tests(self):
        """Run the 3 priority tests"""
        print("🚀 Starting Priority Endpoint Testing")
        print("=" * 60)
        
        if not self.authenticate():
            print("❌ Cannot proceed without authentication")
            return
        
        results = []
        
        # Test the 3 priority endpoints
        results.append(self.test_security_alerts())
        results.append(self.test_token_staking())
        results.append(self.test_smart_contract_templates())
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 PRIORITY TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(results)
        total = len(results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Priority Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {total - passed} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL PRIORITY ENDPOINTS WORKING!")
        else:
            print(f"\n⚠️  {total - passed} priority endpoints still need fixes")
        
        return success_rate

if __name__ == "__main__":
    tester = PriorityTester()
    tester.run_priority_tests()
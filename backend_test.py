#!/usr/bin/env python3
"""
QuantumShield Backend Testing Suite
Tests critical backend functionalities for MVP validation
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

class QuantumShieldTester:
    def __init__(self):
        # Use the production URL from frontend/.env
        self.base_url = "https://fa71b110-641f-4998-92bb-6968bae54ec8.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}: {details}")
        
    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> requests.Response:
        """Make HTTP request with proper error handling"""
        url = f"{self.base_url}{endpoint}"
        request_headers = {"Content-Type": "application/json"}
        
        if self.auth_token:
            request_headers["Authorization"] = f"Bearer {self.auth_token}"
            
        if headers:
            request_headers.update(headers)
            
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=request_headers, timeout=30)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=request_headers, timeout=30)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=request_headers, timeout=30)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=request_headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed for {endpoint}: {str(e)}")
            raise

    def test_health_check(self):
        """Test 1: Global Health Check - Verify all services (21 services expected)"""
        try:
            response = self.make_request("GET", "/health")
            
            if response.status_code == 200:
                data = response.json()
                services = data.get("services", {})
                total_services = len(services)
                healthy_services = sum(1 for status in services.values() if status)
                
                self.log_test(
                    "Global Health Check",
                    healthy_services >= 20,  # Allow for 1-2 services to be down
                    f"Services: {healthy_services}/{total_services} healthy. Services: {list(services.keys())}",
                    {"total": total_services, "healthy": healthy_services, "services": services}
                )
            else:
                self.log_test("Global Health Check", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Global Health Check", False, f"Exception: {str(e)}")

    def test_authentication_flow(self):
        """Test 2: Authentication Flow - Register, Login, MFA"""
        # Test User Registration
        try:
            register_data = {
                "username": "quantum_user_2025",
                "email": "quantum.test@quantumshield.com",
                "password": "QuantumSecure2025!",
                "full_name": "Quantum Test User"
            }
            
            response = self.make_request("POST", "/auth/register", register_data)
            
            if response.status_code == 201:
                data = response.json()
                self.user_id = data.get("user_id")
                self.log_test("User Registration", True, f"User registered with ID: {self.user_id}")
            else:
                self.log_test("User Registration", False, f"HTTP {response.status_code}: {response.text}")
                return
                
        except Exception as e:
            self.log_test("User Registration", False, f"Exception: {str(e)}")
            return

        # Test User Login
        try:
            login_data = {
                "username": "quantum_user_2025",
                "password": "QuantumSecure2025!"
            }
            
            response = self.make_request("POST", "/auth/login", login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.log_test("User Login", True, f"Login successful, token received")
            else:
                self.log_test("User Login", False, f"HTTP {response.status_code}: {response.text}")
                return
                
        except Exception as e:
            self.log_test("User Login", False, f"Exception: {str(e)}")
            return

        # Test MFA Setup
        try:
            response = self.make_request("POST", "/auth/mfa/setup")
            
            if response.status_code == 200:
                data = response.json()
                secret = data.get("secret")
                self.log_test("MFA Setup", True, f"MFA setup successful, secret generated")
            else:
                self.log_test("MFA Setup", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("MFA Setup", False, f"Exception: {str(e)}")

    def test_advanced_cryptography(self):
        """Test 3: Advanced Cryptography - Key generation, encryption, ZK-proofs"""
        if not self.auth_token:
            self.log_test("Advanced Cryptography", False, "No auth token available")
            return

        # Test Key Generation
        try:
            key_data = {
                "algorithm": "kyber-768",
                "key_size": 2048
            }
            
            response = self.make_request("POST", "/advanced-crypto/generate-keypair", key_data)
            
            if response.status_code == 200:
                data = response.json()
                public_key = data.get("public_key")
                self.log_test("Advanced Key Generation", True, f"Kyber-768 keypair generated successfully")
            else:
                self.log_test("Advanced Key Generation", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Advanced Key Generation", False, f"Exception: {str(e)}")

        # Test Batch Encryption
        try:
            encrypt_data = {
                "messages": ["Quantum message 1", "Quantum message 2", "Quantum message 3"],
                "algorithm": "kyber-768"
            }
            
            response = self.make_request("POST", "/advanced-crypto/batch-encrypt", encrypt_data)
            
            if response.status_code == 200:
                data = response.json()
                encrypted_messages = data.get("encrypted_messages", [])
                self.log_test("Batch Encryption", True, f"Successfully encrypted {len(encrypted_messages)} messages")
            else:
                self.log_test("Batch Encryption", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Batch Encryption", False, f"Exception: {str(e)}")

        # Test ZK-Proofs Generation (Known issue from test_result.md)
        try:
            zk_data = {
                "proof_type": "membership",
                "secret": "quantum_secret_2025",
                "public_parameters": {"modulus": 2048, "generator": 2},
                "statement": "I know the secret value"
            }
            
            response = self.make_request("POST", "/advanced-crypto/generate-zk-proof", zk_data)
            
            if response.status_code == 200:
                data = response.json()
                proof = data.get("proof")
                self.log_test("ZK-Proofs Generation", True, f"ZK-proof generated successfully")
            else:
                self.log_test("ZK-Proofs Generation", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("ZK-Proofs Generation", False, f"Exception: {str(e)}")

    def test_advanced_blockchain(self):
        """Test 4: Advanced Blockchain - Overview, metrics, validators"""
        if not self.auth_token:
            self.log_test("Advanced Blockchain", False, "No auth token available")
            return

        # Test Blockchain Overview
        try:
            response = self.make_request("GET", "/advanced-blockchain/overview")
            
            if response.status_code == 200:
                data = response.json()
                validators = data.get("validators", 0)
                bridges = data.get("cross_chain_bridges", 0)
                self.log_test("Blockchain Overview", True, f"Overview retrieved: {validators} validators, {bridges} bridges")
            else:
                self.log_test("Blockchain Overview", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Blockchain Overview", False, f"Exception: {str(e)}")

        # Test Network Metrics
        try:
            response = self.make_request("GET", "/advanced-blockchain/metrics")
            
            if response.status_code == 200:
                data = response.json()
                hash_rate = data.get("hash_rate")
                block_time = data.get("average_block_time")
                self.log_test("Network Metrics", True, f"Metrics retrieved: Hash rate {hash_rate}, Block time {block_time}s")
            else:
                self.log_test("Network Metrics", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Network Metrics", False, f"Exception: {str(e)}")

        # Test Validators
        try:
            response = self.make_request("GET", "/advanced-blockchain/validators")
            
            if response.status_code == 200:
                data = response.json()
                validators = data.get("validators", [])
                self.log_test("Validators List", True, f"Retrieved {len(validators)} validators")
            else:
                self.log_test("Validators List", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Validators List", False, f"Exception: {str(e)}")

        # Test Staking (Known issue from test_result.md)
        try:
            stake_data = {
                "validator_address": "0x1234567890abcdef1234567890abcdef12345678",
                "amount": 100.0,
                "duration": 30
            }
            
            response = self.make_request("POST", "/advanced-blockchain/stake", stake_data)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Token Staking", True, f"Staking successful")
            else:
                self.log_test("Token Staking", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Token Staking", False, f"Exception: {str(e)}")

    def test_security_features(self):
        """Test 5: Security Features - Dashboard, alerts"""
        if not self.auth_token:
            self.log_test("Security Features", False, "No auth token available")
            return

        # Test Security Dashboard
        try:
            response = self.make_request("GET", "/security/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                threats = data.get("active_threats", 0)
                security_score = data.get("security_score", 0)
                self.log_test("Security Dashboard", True, f"Dashboard loaded: {threats} threats, score {security_score}")
            else:
                self.log_test("Security Dashboard", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Security Dashboard", False, f"Exception: {str(e)}")

        # Test Security Alerts
        try:
            response = self.make_request("GET", "/security/alerts")
            
            if response.status_code == 200:
                data = response.json()
                alerts = data.get("alerts", [])
                self.log_test("Security Alerts", True, f"Retrieved {len(alerts)} security alerts")
            else:
                self.log_test("Security Alerts", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Security Alerts", False, f"Exception: {str(e)}")

    def test_ai_analytics(self):
        """Test 6: AI Analytics - Anomaly detection, predictions"""
        if not self.auth_token:
            self.log_test("AI Analytics", False, "No auth token available")
            return

        # Test Anomaly Detection
        try:
            response = self.make_request("GET", "/ai-analytics/anomaly-detection")
            
            if response.status_code == 200:
                data = response.json()
                anomalies = data.get("anomalies", [])
                models = data.get("models_loaded", 0)
                self.log_test("Anomaly Detection", True, f"Detection active: {len(anomalies)} anomalies, {models} models loaded")
            else:
                self.log_test("Anomaly Detection", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Anomaly Detection", False, f"Exception: {str(e)}")

        # Test Predictions
        try:
            response = self.make_request("GET", "/ai-analytics/predictions")
            
            if response.status_code == 200:
                data = response.json()
                predictions = data.get("predictions", [])
                self.log_test("AI Predictions", True, f"Retrieved {len(predictions)} predictions")
            else:
                self.log_test("AI Predictions", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("AI Predictions", False, f"Exception: {str(e)}")

        # Test AI Dashboard
        try:
            response = self.make_request("GET", "/ai-analytics/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                active_anomalies = data.get("active_anomalies", 0)
                service_status = data.get("service_status")
                self.log_test("AI Dashboard", True, f"Dashboard loaded: {active_anomalies} active anomalies, status: {service_status}")
            else:
                self.log_test("AI Dashboard", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("AI Dashboard", False, f"Exception: {str(e)}")

    def test_smart_contracts_governance(self):
        """Test 7: Smart Contracts and Governance (Known issues from test_result.md)"""
        if not self.auth_token:
            self.log_test("Smart Contracts & Governance", False, "No auth token available")
            return

        # Test Smart Contract Templates
        try:
            response = self.make_request("GET", "/advanced-blockchain/smart-contracts/templates")
            
            if response.status_code == 200:
                data = response.json()
                templates = data.get("templates", [])
                self.log_test("Smart Contract Templates", True, f"Retrieved {len(templates)} templates")
            else:
                self.log_test("Smart Contract Templates", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Smart Contract Templates", False, f"Exception: {str(e)}")

        # Test Governance Proposals
        try:
            proposal_data = {
                "title": "Quantum Security Enhancement Proposal",
                "description": "Enhance quantum cryptography algorithms",
                "proposal_type": "upgrade",
                "voting_period": 7,
                "execution_delay": 2
            }
            
            response = self.make_request("POST", "/advanced-blockchain/governance/proposals", proposal_data)
            
            if response.status_code == 201:
                data = response.json()
                proposal_id = data.get("proposal_id")
                self.log_test("Governance Proposals", True, f"Proposal created with ID: {proposal_id}")
            else:
                self.log_test("Governance Proposals", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Governance Proposals", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all critical backend tests"""
        print("🚀 Starting QuantumShield Backend Testing Suite")
        print(f"🔗 Testing against: {self.base_url}")
        print("=" * 80)
        
        # Run tests in order of priority
        self.test_health_check()
        print()
        
        self.test_authentication_flow()
        print()
        
        self.test_advanced_cryptography()
        print()
        
        self.test_advanced_blockchain()
        print()
        
        self.test_security_features()
        print()
        
        self.test_ai_analytics()
        print()
        
        self.test_smart_contracts_governance()
        print()
        
        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
            print()
        
        print("✅ PASSED TESTS:")
        for result in self.test_results:
            if result["success"]:
                print(f"  - {result['test']}: {result['details']}")
        
        print("=" * 80)
        
        # Save detailed results to file
        with open("/app/backend_test_results.json", "w") as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "success_rate": success_rate,
                    "timestamp": datetime.now().isoformat()
                },
                "detailed_results": self.test_results
            }, f, indent=2)
        
        print(f"📄 Detailed results saved to: /app/backend_test_results.json")

if __name__ == "__main__":
    tester = QuantumShieldTester()
    tester.run_all_tests()
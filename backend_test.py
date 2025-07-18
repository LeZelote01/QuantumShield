#!/usr/bin/env python3
"""
Test complet du backend QuantumShield
Tests tous les services et endpoints API
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Configuration des tests
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

class QuantumShieldTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user = {
            "username": "quantum_tester",
            "email": "tester@quantumshield.com",
            "password": "SecurePassword123!"
        }
        self.test_results = {
            "health_check": False,
            "auth_register": False,
            "auth_login": False,
            "auth_verify": False,
            "crypto_generate_keys": False,
            "crypto_encrypt": False,
            "crypto_decrypt": False,
            "devices_register": False,
            "blockchain_stats": False,
            "tokens_balance": False,
            "mining_stats": False,
            "dashboard_overview": False,
            # Advanced Crypto Tests
            "advanced_crypto_supported_algorithms": False,
            "advanced_crypto_generate_keypair": False,
            "advanced_crypto_hybrid_encrypt": False,
            "advanced_crypto_hybrid_decrypt": False,
            "advanced_crypto_batch_encrypt": False,
            "advanced_crypto_batch_decrypt": False,
            "advanced_crypto_sign_dilithium": False,
            "advanced_crypto_verify_dilithium": False,
            "advanced_crypto_setup_key_rotation": False,
            "advanced_crypto_rotate_keys": False,
            "advanced_crypto_key_rotation_status": False,
            "advanced_crypto_performance_comparison": False,
            "advanced_crypto_algorithm_recommendations": False,
            # Security Service Tests
            "security_mfa_setup": False,
            "security_mfa_status": False,
            "security_behavior_analysis": False,
            "security_dashboard": False,
            "security_recommendations": False,
            "security_health": False,
            # AI Analytics Service Tests
            "ai_analytics_device_anomalies": False,
            "ai_analytics_network_anomalies": False,
            "ai_analytics_energy_anomalies": False,
            "ai_analytics_device_failure_prediction": False,
            "ai_analytics_energy_prediction": False,
            "ai_analytics_energy_optimization": False,
            "ai_analytics_dashboard": False,
            "ai_analytics_models_status": False,
            "ai_analytics_summary": False,
            "ai_analytics_recommendations": False,
            "ai_analytics_health": False,
            # IoT Protocol Service Tests
            "iot_protocol_health": False,
            "iot_protocol_status": False,
            "iot_protocol_statistics": False,
            "iot_protocol_mqtt_start": False,
            "iot_protocol_mqtt_publish": False,
            "iot_protocol_coap_start": False,
            "iot_protocol_lorawan_start": False,
            "iot_protocol_device_command": False,
            "iot_protocol_sensor_data": False,
            "iot_protocol_config": False,
            # OTA Update Service Tests
            "ota_health": False,
            "ota_statistics": False,
            "ota_firmware_register": False,
            "ota_firmware_list": False,
            "ota_update_schedule": False,
            "ota_update_queue": False,
            "ota_config": False,
            # New Advanced Crypto Features Tests
            "advanced_crypto_generate_zk_proof": False,
            "advanced_crypto_verify_zk_proof": False,
            "advanced_crypto_setup_threshold_signature": False,
            "advanced_crypto_threshold_sign": False,
            "advanced_crypto_verify_threshold_signature": False,
            "advanced_crypto_audit_trail": False,
            "advanced_crypto_verify_audit_integrity": False,
            "advanced_crypto_crypto_statistics": False
        }
        self.test_data = {}

    async def setup(self):
        """Initialise la session HTTP"""
        self.session = aiohttp.ClientSession()
        print("🔧 Session HTTP initialisée")

    async def cleanup(self):
        """Nettoie les ressources"""
        if self.session:
            await self.session.close()
        print("🧹 Nettoyage terminé")

    async def make_request(self, method: str, endpoint: str, data: Dict = None, 
                          headers: Dict = None, auth_required: bool = False) -> Dict:
        """Effectue une requête HTTP avec gestion d'erreurs"""
        url = f"{API_BASE}{endpoint}"
        
        # Headers par défaut
        request_headers = {"Content-Type": "application/json"}
        if headers:
            request_headers.update(headers)
        
        # Ajouter l'authentification si nécessaire
        if auth_required and self.auth_token:
            request_headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, headers=request_headers) as response:
                    result = await response.json()
                    return {"status": response.status, "data": result}
            elif method.upper() == "POST":
                async with self.session.post(url, json=data, headers=request_headers) as response:
                    result = await response.json()
                    return {"status": response.status, "data": result}
            elif method.upper() == "PUT":
                async with self.session.put(url, json=data, headers=request_headers) as response:
                    result = await response.json()
                    return {"status": response.status, "data": result}
        except Exception as e:
            return {"status": 500, "error": str(e)}

    async def test_health_check(self):
        """Test du health check API"""
        print("\n🏥 Test Health Check...")
        
        try:
            response = await self.make_request("GET", "/health")
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("status") == "healthy":
                    print("✅ Health check OK")
                    print(f"   Services: {data.get('services', {})}")
                    self.test_results["health_check"] = True
                    return True
                else:
                    print(f"❌ Health check failed: {data}")
            else:
                print(f"❌ Health check HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Health check exception: {e}")
        
        return False

    async def test_auth_register(self):
        """Test d'enregistrement utilisateur"""
        print("\n👤 Test Auth Register...")
        
        try:
            response = await self.make_request("POST", "/auth/register", self.test_user)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("username") == self.test_user["username"]:
                    print("✅ Registration successful")
                    print(f"   User ID: {data.get('id')}")
                    print(f"   Wallet: {data.get('wallet_address')}")
                    self.test_data["user_id"] = data.get("id")
                    self.test_data["wallet_address"] = data.get("wallet_address")
                    self.test_results["auth_register"] = True
                    return True
                else:
                    print(f"❌ Registration failed: {data}")
            else:
                print(f"❌ Registration HTTP error: {response['status']} - {response.get('data', {})}")
        except Exception as e:
            print(f"❌ Registration exception: {e}")
        
        return False

    async def test_auth_login(self):
        """Test de connexion utilisateur"""
        print("\n🔐 Test Auth Login...")
        
        try:
            login_data = {
                "username": self.test_user["username"],
                "password": self.test_user["password"]
            }
            response = await self.make_request("POST", "/auth/login", login_data)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("token"):
                    print("✅ Login successful")
                    print(f"   Token: {data.get('token')[:20]}...")
                    print(f"   User: {data.get('user', {}).get('username')}")
                    self.auth_token = data.get("token")
                    self.test_results["auth_login"] = True
                    return True
                else:
                    print(f"❌ Login failed: {data}")
            else:
                print(f"❌ Login HTTP error: {response['status']} - {response.get('data', {})}")
        except Exception as e:
            print(f"❌ Login exception: {e}")
        
        return False

    async def test_auth_verify(self):
        """Test de vérification du token"""
        print("\n🔍 Test Auth Verify Token...")
        
        try:
            response = await self.make_request("GET", "/auth/verify-token", auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("valid"):
                    print("✅ Token verification successful")
                    print(f"   User: {data.get('user', {}).get('username')}")
                    self.test_results["auth_verify"] = True
                    return True
                else:
                    print(f"❌ Token verification failed: {data}")
            else:
                print(f"❌ Token verification HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Token verification exception: {e}")
        
        return False

    async def test_crypto_generate_keys(self):
        """Test de génération de clés NTRU++"""
        print("\n🔑 Test Crypto Generate Keys...")
        
        try:
            key_request = {"key_size": 2048}
            response = await self.make_request("POST", "/crypto/generate-keys", key_request, auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("public_key") and data.get("private_key"):
                    print("✅ Key generation successful")
                    print(f"   Key size: {data.get('key_size')}")
                    print(f"   Public key: {data.get('public_key')[:30]}...")
                    self.test_data["public_key"] = data.get("public_key")
                    self.test_data["private_key"] = data.get("private_key")
                    self.test_results["crypto_generate_keys"] = True
                    return True
                else:
                    print(f"❌ Key generation failed: {data}")
            else:
                print(f"❌ Key generation HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Key generation exception: {e}")
        
        return False

    async def test_crypto_encrypt(self):
        """Test de chiffrement NTRU++"""
        print("\n🔒 Test Crypto Encrypt...")
        
        if not self.test_data.get("public_key"):
            print("❌ No public key available for encryption test")
            return False
        
        try:
            encrypt_request = {
                "data": "Hello QuantumShield! This is a test message for NTRU++ encryption.",
                "public_key": self.test_data["public_key"]
            }
            response = await self.make_request("POST", "/crypto/encrypt", encrypt_request, auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("encrypted_data"):
                    print("✅ Encryption successful")
                    print(f"   Algorithm: {data.get('algorithm', 'NTRU++')}")
                    print(f"   Encrypted data: {data.get('encrypted_data')[:50]}...")
                    self.test_data["encrypted_data"] = data.get("encrypted_data")
                    self.test_results["crypto_encrypt"] = True
                    return True
                else:
                    print(f"❌ Encryption failed: {data}")
            else:
                print(f"❌ Encryption HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Encryption exception: {e}")
        
        return False

    async def test_crypto_decrypt(self):
        """Test de déchiffrement NTRU++"""
        print("\n🔓 Test Crypto Decrypt...")
        
        if not self.test_data.get("encrypted_data") or not self.test_data.get("private_key"):
            print("❌ No encrypted data or private key available for decryption test")
            return False
        
        try:
            decrypt_request = {
                "encrypted_data": self.test_data["encrypted_data"],
                "private_key": self.test_data["private_key"]
            }
            response = await self.make_request("POST", "/crypto/decrypt", decrypt_request, auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("decrypted_data"):
                    print("✅ Decryption successful")
                    print(f"   Decrypted: {data.get('decrypted_data')}")
                    print(f"   Verification: {data.get('verification_status')}")
                    self.test_results["crypto_decrypt"] = True
                    return True
                else:
                    print(f"❌ Decryption failed: {data}")
            else:
                print(f"❌ Decryption HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Decryption exception: {e}")
        
        return False

    async def test_devices_register(self):
        """Test d'enregistrement de device IoT"""
        print("\n📱 Test Device Register...")
        
        try:
            device_data = {
                "device_id": "test_sensor_001",
                "device_name": "Test Smart Sensor",
                "device_type": "Smart Sensor",
                "location": "Test Lab",
                "capabilities": ["temperature", "humidity", "motion"]
            }
            response = await self.make_request("POST", "/devices/register", device_data, auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("device_id") == device_data["device_id"]:
                    print("✅ Device registration successful")
                    print(f"   Device ID: {data.get('device_id')}")
                    print(f"   Device Name: {data.get('device_name')}")
                    print(f"   Status: {data.get('status')}")
                    self.test_data["device_id"] = data.get("device_id")
                    self.test_results["devices_register"] = True
                    return True
                else:
                    print(f"❌ Device registration failed: {data}")
            else:
                print(f"❌ Device registration HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Device registration exception: {e}")
        
        return False

    async def test_blockchain_stats(self):
        """Test des statistiques blockchain"""
        print("\n⛓️ Test Blockchain Stats...")
        
        try:
            response = await self.make_request("GET", "/blockchain/stats", auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if "total_blocks" in data and "total_transactions" in data:
                    print("✅ Blockchain stats retrieved")
                    print(f"   Total blocks: {data.get('total_blocks')}")
                    print(f"   Total transactions: {data.get('total_transactions')}")
                    print(f"   Pending transactions: {data.get('pending_transactions')}")
                    print(f"   Current difficulty: {data.get('current_difficulty')}")
                    self.test_results["blockchain_stats"] = True
                    return True
                else:
                    print(f"❌ Blockchain stats incomplete: {data}")
            else:
                print(f"❌ Blockchain stats HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Blockchain stats exception: {e}")
        
        return False

    async def test_tokens_balance(self):
        """Test du solde de tokens $QS"""
        print("\n💰 Test Tokens Balance...")
        
        try:
            response = await self.make_request("GET", "/tokens/balance", auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if "balance" in data and "symbol" in data:
                    print("✅ Token balance retrieved")
                    print(f"   Balance: {data.get('balance')} {data.get('symbol')}")
                    print(f"   Wallet: {data.get('wallet_address')}")
                    print(f"   Decimals: {data.get('decimals')}")
                    self.test_results["tokens_balance"] = True
                    return True
                else:
                    print(f"❌ Token balance incomplete: {data}")
            else:
                print(f"❌ Token balance HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Token balance exception: {e}")
        
        return False

    async def test_mining_stats(self):
        """Test des statistiques de mining"""
        print("\n⛏️ Test Mining Stats...")
        
        try:
            response = await self.make_request("GET", "/mining/stats", auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if "current_difficulty" in data or "total_miners" in data:
                    print("✅ Mining stats retrieved")
                    print(f"   Current difficulty: {data.get('current_difficulty', 'N/A')}")
                    print(f"   Total miners: {data.get('total_miners', 'N/A')}")
                    print(f"   Active miners: {data.get('active_miners', 'N/A')}")
                    print(f"   Hash rate: {data.get('estimated_hash_rate', 'N/A')}")
                    self.test_results["mining_stats"] = True
                    return True
                else:
                    print(f"❌ Mining stats incomplete: {data}")
            else:
                print(f"❌ Mining stats HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Mining stats exception: {e}")
        
        return False

    async def test_dashboard_overview(self):
        """Test de l'aperçu du dashboard"""
        print("\n📊 Test Dashboard Overview...")
        
        try:
            response = await self.make_request("GET", "/dashboard/overview", auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if "user_info" in data and "device_stats" in data:
                    print("✅ Dashboard overview retrieved")
                    print(f"   User: {data.get('user_info', {}).get('username')}")
                    print(f"   Total devices: {data.get('device_stats', {}).get('total_devices')}")
                    print(f"   Token balance: {data.get('token_stats', {}).get('balance')}")
                    print(f"   Network blocks: {data.get('network_stats', {}).get('total_blocks')}")
                    self.test_results["dashboard_overview"] = True
                    return True
                else:
                    print(f"❌ Dashboard overview incomplete: {data}")
            else:
                print(f"❌ Dashboard overview HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Dashboard overview exception: {e}")
        
        return False

    async def test_advanced_crypto_supported_algorithms(self):
        """Test des algorithmes supportés par le service de cryptographie avancée"""
        print("\n🔬 Test Advanced Crypto Supported Algorithms...")
        
        try:
            response = await self.make_request("GET", "/advanced-crypto/supported-algorithms")
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("algorithms") and data.get("status") == "success":
                    print("✅ Supported algorithms retrieved")
                    algorithms = data["algorithms"]
                    print(f"   Available algorithms: {len(algorithms)}")
                    for alg_name, alg_info in algorithms.items():
                        print(f"   - {alg_name}: {alg_info.get('description', 'N/A')}")
                    self.test_results["advanced_crypto_supported_algorithms"] = True
                    return True
                else:
                    print(f"❌ Supported algorithms incomplete: {data}")
            else:
                print(f"❌ Supported algorithms HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Supported algorithms exception: {e}")
        
        return False

    async def test_advanced_crypto_generate_keypair(self):
        """Test de génération de paire de clés multi-algorithmes"""
        print("\n🔑 Test Advanced Crypto Generate Multi-Algorithm Keypair...")
        
        try:
            keypair_request = {
                "encryption_algorithm": "Kyber-768",
                "signature_algorithm": "Dilithium-3"
            }
            response = await self.make_request("POST", "/advanced-crypto/generate-multi-algorithm-keypair", 
                                             keypair_request, auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("keypair") and data.get("status") == "success":
                    keypair = data["keypair"]
                    print("✅ Multi-algorithm keypair generation successful")
                    print(f"   Keypair ID: {keypair.get('keypair_id')}")
                    print(f"   Encryption Algorithm: {keypair.get('encryption_algorithm')}")
                    print(f"   Signature Algorithm: {keypair.get('signature_algorithm')}")
                    print(f"   Encryption Public Key: {keypair.get('encryption_public_key')[:30]}...")
                    print(f"   Signature Public Key: {keypair.get('signature_public_key')[:30]}...")
                    
                    # Store keypair ID for other tests
                    self.test_data["advanced_keypair_id"] = keypair.get("keypair_id")
                    self.test_results["advanced_crypto_generate_keypair"] = True
                    return True
                else:
                    print(f"❌ Multi-algorithm keypair generation failed: {data}")
            else:
                print(f"❌ Multi-algorithm keypair generation HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Multi-algorithm keypair generation exception: {e}")
        
        return False

    async def test_advanced_crypto_hybrid_encrypt(self):
        """Test de chiffrement hybride"""
        print("\n🔒 Test Advanced Crypto Hybrid Encrypt...")
        
        if not self.test_data.get("advanced_keypair_id"):
            print("❌ No advanced keypair ID available for hybrid encryption test")
            return False
        
        try:
            encrypt_request = {
                "message": "Hello QuantumShield! This is a test message for hybrid encryption with Kyber KEM and AES.",
                "keypair_id": self.test_data["advanced_keypair_id"]
            }
            response = await self.make_request("POST", "/advanced-crypto/hybrid-encrypt", 
                                             encrypt_request, auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("encrypted_data") and data.get("status") == "success":
                    encrypted_data = data["encrypted_data"]
                    print("✅ Hybrid encryption successful")
                    print(f"   Algorithm: {encrypted_data.get('algorithm')}")
                    print(f"   KEM Ciphertext: {encrypted_data.get('kem_ciphertext')[:50]}...")
                    print(f"   AES IV: {encrypted_data.get('aes_iv')}")
                    print(f"   Encrypted Message: {encrypted_data.get('encrypted_message')[:50]}...")
                    
                    # Store encrypted data for decryption test
                    self.test_data["hybrid_encrypted_data"] = encrypted_data
                    self.test_results["advanced_crypto_hybrid_encrypt"] = True
                    return True
                else:
                    print(f"❌ Hybrid encryption failed: {data}")
            else:
                print(f"❌ Hybrid encryption HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Hybrid encryption exception: {e}")
        
        return False

    async def test_advanced_crypto_hybrid_decrypt(self):
        """Test de déchiffrement hybride"""
        print("\n🔓 Test Advanced Crypto Hybrid Decrypt...")
        
        if not self.test_data.get("hybrid_encrypted_data") or not self.test_data.get("advanced_keypair_id"):
            print("❌ No hybrid encrypted data or keypair ID available for decryption test")
            return False
        
        try:
            decrypt_request = {
                "encrypted_data": self.test_data["hybrid_encrypted_data"],
                "keypair_id": self.test_data["advanced_keypair_id"]
            }
            response = await self.make_request("POST", "/advanced-crypto/hybrid-decrypt", 
                                             decrypt_request, auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("decrypted_message") and data.get("status") == "success":
                    print("✅ Hybrid decryption successful")
                    print(f"   Decrypted Message: {data.get('decrypted_message')}")
                    self.test_results["advanced_crypto_hybrid_decrypt"] = True
                    return True
                else:
                    print(f"❌ Hybrid decryption failed: {data}")
            else:
                print(f"❌ Hybrid decryption HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Hybrid decryption exception: {e}")
        
        return False

    async def test_advanced_crypto_batch_encrypt(self):
        """Test de chiffrement par lots"""
        print("\n📦 Test Advanced Crypto Batch Encrypt...")
        
        if not self.test_data.get("advanced_keypair_id"):
            print("❌ No advanced keypair ID available for batch encryption test")
            return False
        
        try:
            batch_request = {
                "messages": [
                    "Message 1: IoT sensor data encryption test",
                    "Message 2: Blockchain transaction data",
                    "Message 3: Device authentication token"
                ],
                "keypair_id": self.test_data["advanced_keypair_id"]
            }
            response = await self.make_request("POST", "/advanced-crypto/batch-encrypt", 
                                             batch_request, auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("results") and data.get("status") == "success":
                    results = data["results"]
                    summary = data["summary"]
                    print("✅ Batch encryption successful")
                    print(f"   Total messages: {summary.get('total')}")
                    print(f"   Successful: {summary.get('successful')}")
                    print(f"   Failed: {summary.get('failed')}")
                    
                    # Store batch encrypted data for decryption test
                    successful_encryptions = [r["data"] for r in results if r["success"]]
                    self.test_data["batch_encrypted_data"] = successful_encryptions
                    self.test_results["advanced_crypto_batch_encrypt"] = True
                    return True
                else:
                    print(f"❌ Batch encryption failed: {data}")
            else:
                print(f"❌ Batch encryption HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Batch encryption exception: {e}")
        
        return False

    async def test_advanced_crypto_batch_decrypt(self):
        """Test de déchiffrement par lots"""
        print("\n📦 Test Advanced Crypto Batch Decrypt...")
        
        if not self.test_data.get("batch_encrypted_data") or not self.test_data.get("advanced_keypair_id"):
            print("❌ No batch encrypted data or keypair ID available for batch decryption test")
            return False
        
        try:
            batch_request = {
                "encrypted_messages": self.test_data["batch_encrypted_data"],
                "keypair_id": self.test_data["advanced_keypair_id"]
            }
            response = await self.make_request("POST", "/advanced-crypto/batch-decrypt", 
                                             batch_request, auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("results") and data.get("status") == "success":
                    results = data["results"]
                    summary = data["summary"]
                    print("✅ Batch decryption successful")
                    print(f"   Total messages: {summary.get('total')}")
                    print(f"   Successful: {summary.get('successful')}")
                    print(f"   Failed: {summary.get('failed')}")
                    
                    # Show decrypted messages
                    for i, result in enumerate(results):
                        if result["success"]:
                            print(f"   Message {i+1}: {result['data']}")
                    
                    self.test_results["advanced_crypto_batch_decrypt"] = True
                    return True
                else:
                    print(f"❌ Batch decryption failed: {data}")
            else:
                print(f"❌ Batch decryption HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Batch decryption exception: {e}")
        
        return False

    async def test_advanced_crypto_sign_dilithium(self):
        """Test de signature avec Dilithium"""
        print("\n✍️ Test Advanced Crypto Sign with Dilithium...")
        
        if not self.test_data.get("advanced_keypair_id"):
            print("❌ No advanced keypair ID available for Dilithium signing test")
            return False
        
        try:
            sign_request = {
                "message": "This is a test message for Dilithium digital signature verification.",
                "keypair_id": self.test_data["advanced_keypair_id"]
            }
            response = await self.make_request("POST", "/advanced-crypto/sign-dilithium", 
                                             sign_request, auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("signature_data") and data.get("status") == "success":
                    signature_data = data["signature_data"]
                    print("✅ Dilithium signing successful")
                    print(f"   Algorithm: {signature_data.get('algorithm')}")
                    print(f"   Message: {signature_data.get('message')}")
                    print(f"   Signature: {signature_data.get('signature')[:50]}...")
                    print(f"   Keypair ID: {signature_data.get('keypair_id')}")
                    
                    # Store signature for verification test
                    self.test_data["dilithium_signature"] = signature_data["signature"]
                    self.test_data["signed_message"] = signature_data["message"]
                    self.test_results["advanced_crypto_sign_dilithium"] = True
                    return True
                else:
                    print(f"❌ Dilithium signing failed: {data}")
            else:
                print(f"❌ Dilithium signing HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Dilithium signing exception: {e}")
        
        return False

    async def test_advanced_crypto_verify_dilithium(self):
        """Test de vérification de signature Dilithium"""
        print("\n✅ Test Advanced Crypto Verify Dilithium Signature...")
        
        if not self.test_data.get("dilithium_signature") or not self.test_data.get("advanced_keypair_id"):
            print("❌ No Dilithium signature or keypair ID available for verification test")
            return False
        
        try:
            verify_request = {
                "message": self.test_data["signed_message"],
                "signature": self.test_data["dilithium_signature"],
                "keypair_id": self.test_data["advanced_keypair_id"]
            }
            response = await self.make_request("POST", "/advanced-crypto/verify-dilithium", 
                                             verify_request, auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if "is_valid" in data and data.get("status") == "success":
                    print("✅ Dilithium signature verification successful")
                    print(f"   Signature Valid: {data.get('is_valid')}")
                    print(f"   Message: {data.get('message')}")
                    print(f"   Verification Time: {data.get('verification_time')}")
                    self.test_results["advanced_crypto_verify_dilithium"] = True
                    return True
                else:
                    print(f"❌ Dilithium signature verification failed: {data}")
            else:
                print(f"❌ Dilithium signature verification HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Dilithium signature verification exception: {e}")
        
        return False

    async def test_advanced_crypto_setup_key_rotation(self):
        """Test de configuration de rotation des clés"""
        print("\n🔄 Test Advanced Crypto Setup Key Rotation...")
        
        if not self.test_data.get("advanced_keypair_id"):
            print("❌ No advanced keypair ID available for key rotation setup test")
            return False
        
        try:
            rotation_request = {
                "keypair_id": self.test_data["advanced_keypair_id"],
                "policy": "time_based",
                "rotation_interval": 24
            }
            response = await self.make_request("POST", "/advanced-crypto/setup-key-rotation", 
                                             rotation_request, auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("rotation_config") and data.get("status") == "success":
                    config = data["rotation_config"]
                    print("✅ Key rotation setup successful")
                    print(f"   Keypair ID: {config.get('keypair_id')}")
                    print(f"   Policy: {config.get('policy')}")
                    print(f"   Next Rotation: {config.get('next_rotation')}")
                    print(f"   Status: {config.get('status')}")
                    self.test_results["advanced_crypto_setup_key_rotation"] = True
                    return True
                else:
                    print(f"❌ Key rotation setup failed: {data}")
            else:
                print(f"❌ Key rotation setup HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Key rotation setup exception: {e}")
        
        return False

    async def test_advanced_crypto_rotate_keys(self):
        """Test de rotation des clés"""
        print("\n🔄 Test Advanced Crypto Rotate Keys...")
        
        if not self.test_data.get("advanced_keypair_id"):
            print("❌ No advanced keypair ID available for key rotation test")
            return False
        
        try:
            rotation_request = {
                "keypair_id": self.test_data["advanced_keypair_id"]
            }
            response = await self.make_request("POST", "/advanced-crypto/rotate-keys", 
                                             rotation_request, auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("rotation_result") and data.get("status") == "success":
                    result = data["rotation_result"]
                    print("✅ Key rotation successful")
                    print(f"   Old Keypair ID: {result.get('old_keypair_id')}")
                    print(f"   New Keypair ID: {result.get('new_keypair_id')}")
                    print(f"   Rotation Time: {result.get('rotation_time')}")
                    print(f"   Status: {result.get('status')}")
                    
                    # Update keypair ID for status check
                    self.test_data["rotated_keypair_id"] = result.get("old_keypair_id")
                    self.test_results["advanced_crypto_rotate_keys"] = True
                    return True
                else:
                    print(f"❌ Key rotation failed: {data}")
            else:
                print(f"❌ Key rotation HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Key rotation exception: {e}")
        
        return False

    async def test_advanced_crypto_key_rotation_status(self):
        """Test de récupération du statut de rotation des clés"""
        print("\n📊 Test Advanced Crypto Key Rotation Status...")
        
        keypair_id = self.test_data.get("rotated_keypair_id") or self.test_data.get("advanced_keypair_id")
        if not keypair_id:
            print("❌ No keypair ID available for key rotation status test")
            return False
        
        try:
            response = await self.make_request("GET", f"/advanced-crypto/key-rotation-status/{keypair_id}", 
                                             auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("rotation_status") and data.get("status") == "success":
                    status = data["rotation_status"]
                    print("✅ Key rotation status retrieved")
                    print(f"   Keypair ID: {status.get('keypair_id')}")
                    print(f"   Status: {status.get('status')}")
                    if status.get("status") == "configured":
                        print(f"   Policy: {status.get('policy')}")
                        print(f"   Last Rotation: {status.get('last_rotation')}")
                        print(f"   Next Rotation: {status.get('next_rotation')}")
                        print(f"   Time to Rotation (hours): {status.get('time_to_rotation_hours')}")
                        print(f"   Rotation Needed: {status.get('rotation_needed')}")
                    self.test_results["advanced_crypto_key_rotation_status"] = True
                    return True
                else:
                    print(f"❌ Key rotation status retrieval failed: {data}")
            else:
                print(f"❌ Key rotation status HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Key rotation status exception: {e}")
        
        return False

    async def test_advanced_crypto_performance_comparison(self):
        """Test de comparaison des performances des algorithmes"""
        print("\n📈 Test Advanced Crypto Performance Comparison...")
        
        try:
            response = await self.make_request("GET", "/advanced-crypto/performance-comparison")
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("performance_comparison") and data.get("status") == "success":
                    comparison = data["performance_comparison"]
                    print("✅ Performance comparison retrieved")
                    print(f"   Available algorithms: {len(comparison.get('algorithms', {}))}")
                    print(f"   Recommended combinations: {len(comparison.get('recommended_combinations', []))}")
                    
                    # Show some algorithm performance info
                    algorithms = comparison.get("algorithms", {})
                    for alg_name, alg_perf in list(algorithms.items())[:3]:  # Show first 3
                        print(f"   - {alg_name}: {alg_perf.get('memory_usage')} memory, Quantum Resistant: {alg_perf.get('quantum_resistant')}")
                    
                    self.test_results["advanced_crypto_performance_comparison"] = True
                    return True
                else:
                    print(f"❌ Performance comparison failed: {data}")
            else:
                print(f"❌ Performance comparison HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Performance comparison exception: {e}")
        
        return False

    async def test_advanced_crypto_algorithm_recommendations(self):
        """Test de récupération des recommandations d'algorithmes"""
        print("\n💡 Test Advanced Crypto Algorithm Recommendations...")
        
        try:
            response = await self.make_request("GET", "/advanced-crypto/algorithm-recommendations")
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("recommendations") and data.get("status") == "success":
                    recommendations = data["recommendations"]
                    print("✅ Algorithm recommendations retrieved")
                    print(f"   Available recommendations: {len(recommendations)}")
                    
                    # Show recommendations
                    for use_case, rec in recommendations.items():
                        print(f"   - {use_case}: {rec.get('encryption')} + {rec.get('signature')}")
                        print(f"     Description: {rec.get('description')}")
                    
                    selection_criteria = data.get("selection_criteria", {})
                    print(f"   Selection criteria: {len(selection_criteria)} factors")
                    
                    self.test_results["advanced_crypto_algorithm_recommendations"] = True
                    return True
                else:
                    print(f"❌ Algorithm recommendations failed: {data}")
            else:
                print(f"❌ Algorithm recommendations HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Algorithm recommendations exception: {e}")
        
        return False

    # ===== SECURITY SERVICE TESTS =====
    
    async def test_security_mfa_setup(self):
        """Test de configuration MFA TOTP"""
        print("\n🔐 Test Security MFA Setup...")
        
        try:
            setup_request = {
                "service_name": "QuantumShield"
            }
            response = await self.make_request("POST", "/security/mfa/setup-totp", 
                                             setup_request, auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("setup_data") and data.get("status") == "success":
                    setup_data = data["setup_data"]
                    print("✅ MFA TOTP setup successful")
                    print(f"   Status: {setup_data.get('status')}")
                    print(f"   QR Code: {'Present' if setup_data.get('qr_code') else 'Missing'}")
                    print(f"   Backup Codes: {len(setup_data.get('backup_codes', []))}")
                    
                    # Store setup data for verification test
                    self.test_data["mfa_secret"] = setup_data.get("secret")
                    self.test_results["security_mfa_setup"] = True
                    return True
                else:
                    print(f"❌ MFA setup failed: {data}")
            else:
                print(f"❌ MFA setup HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ MFA setup exception: {e}")
        
        return False
    
    async def test_security_mfa_status(self):
        """Test de récupération du statut MFA"""
        print("\n📊 Test Security MFA Status...")
        
        try:
            response = await self.make_request("GET", "/security/mfa/status", auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("mfa_status") and data.get("status") == "success":
                    mfa_status = data["mfa_status"]
                    print("✅ MFA status retrieved")
                    print(f"   User ID: {mfa_status.get('user_id')}")
                    print(f"   MFA Enabled: {mfa_status.get('mfa_enabled')}")
                    print(f"   Methods: {len(mfa_status.get('methods', []))}")
                    self.test_results["security_mfa_status"] = True
                    return True
                else:
                    print(f"❌ MFA status failed: {data}")
            else:
                print(f"❌ MFA status HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ MFA status exception: {e}")
        
        return False
    
    async def test_security_behavior_analysis(self):
        """Test d'analyse comportementale"""
        print("\n🧠 Test Security Behavior Analysis...")
        
        try:
            analysis_request = {
                "action": "login",
                "context": {
                    "ip_address": "192.168.1.100",
                    "user_agent": "QuantumShield-Test/1.0",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            response = await self.make_request("POST", "/security/behavior/analyze", 
                                             analysis_request, auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("analysis") and data.get("status") == "success":
                    analysis = data["analysis"]
                    print("✅ Behavior analysis successful")
                    print(f"   Risk Score: {analysis.get('risk_score')}")
                    print(f"   Security Level: {analysis.get('security_level')}")
                    print(f"   Anomalies: {len(analysis.get('anomalies', []))}")
                    print(f"   Recommendations: {len(analysis.get('recommendations', []))}")
                    self.test_results["security_behavior_analysis"] = True
                    return True
                else:
                    print(f"❌ Behavior analysis failed: {data}")
            else:
                print(f"❌ Behavior analysis HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Behavior analysis exception: {e}")
        
        return False
    
    async def test_security_dashboard(self):
        """Test du tableau de bord sécurité"""
        print("\n📊 Test Security Dashboard...")
        
        try:
            response = await self.make_request("GET", "/security/dashboard", auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("dashboard") and data.get("status") == "success":
                    dashboard = data["dashboard"]
                    print("✅ Security dashboard retrieved")
                    overview = dashboard.get("overview", {})
                    print(f"   Events (24h): {overview.get('events_last_24h', 0)}")
                    print(f"   Active Alerts: {overview.get('active_alerts', 0)}")
                    print(f"   MFA Users: {overview.get('mfa_enabled_users', 0)}")
                    print(f"   Security Score: {dashboard.get('security_score', 0)}")
                    self.test_results["security_dashboard"] = True
                    return True
                else:
                    print(f"❌ Security dashboard failed: {data}")
            else:
                print(f"❌ Security dashboard HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Security dashboard exception: {e}")
        
        return False
    
    async def test_security_recommendations(self):
        """Test des recommandations de sécurité"""
        print("\n💡 Test Security Recommendations...")
        
        try:
            response = await self.make_request("GET", "/security/recommendations", auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("recommendations") and data.get("status") == "success":
                    recommendations = data["recommendations"]
                    print("✅ Security recommendations retrieved")
                    print(f"   Total Recommendations: {len(recommendations)}")
                    for rec in recommendations[:3]:  # Show first 3
                        print(f"   - {rec.get('title')} (Priority: {rec.get('priority')})")
                    self.test_results["security_recommendations"] = True
                    return True
                else:
                    print(f"❌ Security recommendations failed: {data}")
            else:
                print(f"❌ Security recommendations HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Security recommendations exception: {e}")
        
        return False
    
    async def test_security_health(self):
        """Test de santé du service de sécurité"""
        print("\n🏥 Test Security Health Check...")
        
        try:
            response = await self.make_request("GET", "/security/health")
            
            if response["status"] == 200:
                data = response["data"]
                if "service_ready" in data:
                    print("✅ Security health check successful")
                    print(f"   Service Ready: {data.get('service_ready')}")
                    print(f"   Status: {data.get('status')}")
                    self.test_results["security_health"] = True
                    return True
                else:
                    print(f"❌ Security health check failed: {data}")
            else:
                print(f"❌ Security health check HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Security health check exception: {e}")
        
        return False

    # ===== IOT PROTOCOL SERVICE TESTS =====
    
    async def test_iot_protocol_health(self):
        """Test de santé du service IoT Protocol"""
        print("\n🌐 Test IoT Protocol Health Check...")
        
        try:
            response = await self.make_request("GET", "/iot-protocol/health")
            
            if response["status"] == 200:
                data = response["data"]
                if "service" in data and data.get("status") in ["healthy", "unhealthy"]:
                    print("✅ IoT Protocol health check successful")
                    print(f"   Status: {data.get('status')}")
                    print(f"   Service: {data.get('service')}")
                    print(f"   Protocols Available: {data.get('protocols_available', 0)}")
                    self.test_results["iot_protocol_health"] = True
                    return True
                else:
                    print(f"❌ IoT Protocol health check failed: {data}")
            else:
                print(f"❌ IoT Protocol health check HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ IoT Protocol health check exception: {e}")
        
        return False
    
    async def test_iot_protocol_status(self):
        """Test du statut des protocoles IoT"""
        print("\n📡 Test IoT Protocol Status...")
        
        try:
            response = await self.make_request("GET", "/iot-protocol/protocols/status")
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("success") and "protocols" in data:
                    protocols = data["protocols"]
                    print("✅ IoT Protocol status retrieved")
                    print(f"   Available protocols: {len(protocols)}")
                    for protocol, status in protocols.items():
                        print(f"   - {protocol}: enabled={status.get('enabled', False)}")
                    self.test_results["iot_protocol_status"] = True
                    return True
                else:
                    print(f"❌ IoT Protocol status failed: {data}")
            else:
                print(f"❌ IoT Protocol status HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ IoT Protocol status exception: {e}")
        
        return False
    
    async def test_iot_protocol_statistics(self):
        """Test des statistiques des messages IoT"""
        print("\n📊 Test IoT Protocol Statistics...")
        
        try:
            response = await self.make_request("GET", "/iot-protocol/protocols/statistics")
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("success") and "statistics" in data:
                    stats = data["statistics"]
                    print("✅ IoT Protocol statistics retrieved")
                    print(f"   Total messages: {stats.get('total_messages', 0)}")
                    print(f"   Message types: {len(stats.get('by_type', {}))}")
                    print(f"   Protocol breakdown: {len(stats.get('by_protocol', {}))}")
                    self.test_results["iot_protocol_statistics"] = True
                    return True
                else:
                    print(f"❌ IoT Protocol statistics failed: {data}")
            else:
                print(f"❌ IoT Protocol statistics HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ IoT Protocol statistics exception: {e}")
        
        return False

    # ===== AI ANALYTICS SERVICE TESTS =====
    
    async def test_ai_analytics_device_anomalies(self):
        """Test de détection d'anomalies de dispositifs"""
        print("\n🤖 Test AI Analytics Device Anomalies...")
        
        if not self.test_data.get("device_id"):
            print("❌ No device ID available for anomaly detection test")
            return False
        
        try:
            anomaly_request = {
                "device_id": self.test_data["device_id"],
                "time_window_hours": 24
            }
            response = await self.make_request("POST", "/ai-analytics/anomalies/device", 
                                             anomaly_request, auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("anomaly_detection") and data.get("status") == "success":
                    detection = data["anomaly_detection"]
                    print("✅ Device anomaly detection successful")
                    print(f"   Device ID: {detection.get('device_id')}")
                    print(f"   Anomalies Detected: {detection.get('anomalies_detected')}")
                    print(f"   Anomaly Count: {detection.get('anomaly_count', 0)}")
                    print(f"   Data Points: {detection.get('total_data_points', 0)}")
                    self.test_results["ai_analytics_device_anomalies"] = True
                    return True
                else:
                    print(f"❌ Device anomaly detection failed: {data}")
            else:
                print(f"❌ Device anomaly detection HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Device anomaly detection exception: {e}")
        
        return False
    
    async def test_ai_analytics_network_anomalies(self):
        """Test de détection d'anomalies réseau"""
        print("\n🌐 Test AI Analytics Network Anomalies...")
        
        try:
            anomaly_request = {
                "time_window_hours": 6
            }
            response = await self.make_request("POST", "/ai-analytics/anomalies/network", 
                                             anomaly_request, auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("anomaly_detection") and data.get("status") == "success":
                    detection = data["anomaly_detection"]
                    print("✅ Network anomaly detection successful")
                    print(f"   Anomalies Detected: {detection.get('anomalies_detected')}")
                    print(f"   Anomaly Count: {detection.get('anomaly_count', 0)}")
                    if detection.get('reason'):
                        print(f"   Reason: {detection.get('reason')}")
                    self.test_results["ai_analytics_network_anomalies"] = True
                    return True
                else:
                    print(f"❌ Network anomaly detection failed: {data}")
            else:
                print(f"❌ Network anomaly detection HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Network anomaly detection exception: {e}")
        
        return False
    
    async def test_ai_analytics_energy_anomalies(self):
        """Test de détection d'anomalies énergétiques"""
        print("\n⚡ Test AI Analytics Energy Anomalies...")
        
        try:
            anomaly_request = {
                "time_window_hours": 12
            }
            response = await self.make_request("POST", "/ai-analytics/anomalies/energy", 
                                             anomaly_request, auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("anomaly_detection") and data.get("status") == "success":
                    detection = data["anomaly_detection"]
                    print("✅ Energy anomaly detection successful")
                    print(f"   Anomalies Detected: {detection.get('anomalies_detected')}")
                    print(f"   Anomaly Count: {detection.get('anomaly_count', 0)}")
                    if detection.get('reason'):
                        print(f"   Reason: {detection.get('reason')}")
                    self.test_results["ai_analytics_energy_anomalies"] = True
                    return True
                else:
                    print(f"❌ Energy anomaly detection failed: {data}")
            else:
                print(f"❌ Energy anomaly detection HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Energy anomaly detection exception: {e}")
        
        return False
    
    async def test_ai_analytics_device_failure_prediction(self):
        """Test de prédiction de panne de dispositif"""
        print("\n🔮 Test AI Analytics Device Failure Prediction...")
        
        if not self.test_data.get("device_id"):
            print("❌ No device ID available for failure prediction test")
            return False
        
        try:
            prediction_request = {
                "device_id": self.test_data["device_id"],
                "prediction_horizon_days": 7
            }
            response = await self.make_request("POST", "/ai-analytics/predictions/device-failure", 
                                             prediction_request, auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("failure_prediction") and data.get("status") == "success":
                    prediction = data["failure_prediction"]
                    print("✅ Device failure prediction successful")
                    print(f"   Device ID: {prediction.get('device_id')}")
                    print(f"   Prediction Available: {prediction.get('prediction_available')}")
                    if prediction.get('prediction_available'):
                        print(f"   Failure Probability: {prediction.get('failure_probability', 0):.2f}")
                        print(f"   Risk Level: {prediction.get('risk_level')}")
                        print(f"   Confidence: {prediction.get('confidence', 0):.2f}")
                    else:
                        print(f"   Reason: {prediction.get('reason')}")
                    self.test_results["ai_analytics_device_failure_prediction"] = True
                    return True
                else:
                    print(f"❌ Device failure prediction failed: {data}")
            else:
                print(f"❌ Device failure prediction HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Device failure prediction exception: {e}")
        
        return False
    
    async def test_ai_analytics_energy_prediction(self):
        """Test de prédiction énergétique"""
        print("\n⚡ Test AI Analytics Energy Prediction...")
        
        try:
            prediction_request = {
                "prediction_horizon_days": 1
            }
            response = await self.make_request("POST", "/ai-analytics/predictions/energy-usage", 
                                             prediction_request, auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("energy_prediction") and data.get("status") == "success":
                    prediction = data["energy_prediction"]
                    print("✅ Energy prediction successful")
                    print(f"   Prediction Available: {prediction.get('prediction_available')}")
                    if prediction.get('prediction_available'):
                        summary = prediction.get('summary', {})
                        print(f"   Total Predicted: {summary.get('total_predicted_consumption', 0):.2f}")
                        print(f"   Average Hourly: {summary.get('average_hourly_consumption', 0):.2f}")
                        print(f"   Peak: {summary.get('peak_consumption', 0):.2f}")
                    else:
                        print(f"   Reason: {prediction.get('reason')}")
                    self.test_results["ai_analytics_energy_prediction"] = True
                    return True
                else:
                    print(f"❌ Energy prediction failed: {data}")
            else:
                print(f"❌ Energy prediction HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Energy prediction exception: {e}")
        
        return False
    
    async def test_ai_analytics_energy_optimization(self):
        """Test d'optimisation énergétique"""
        print("\n🔧 Test AI Analytics Energy Optimization...")
        
        try:
            optimization_request = {
                "target_reduction": 0.15
            }
            response = await self.make_request("POST", "/ai-analytics/optimization/energy", 
                                             optimization_request, auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("optimization") and data.get("status") == "success":
                    optimization = data["optimization"]
                    print("✅ Energy optimization successful")
                    print(f"   Optimization Available: {optimization.get('optimization_available')}")
                    if optimization.get('optimization_available'):
                        print(f"   Current Consumption: {optimization.get('current_consumption', 0):.2f}")
                        print(f"   Potential Savings: {optimization.get('potential_savings', 0):.2f}")
                        print(f"   Savings Percentage: {optimization.get('savings_percentage', 0):.1f}%")
                        print(f"   Meets Target: {optimization.get('meets_target')}")
                    else:
                        print(f"   Reason: {optimization.get('reason')}")
                    self.test_results["ai_analytics_energy_optimization"] = True
                    return True
                else:
                    print(f"❌ Energy optimization failed: {data}")
            else:
                print(f"❌ Energy optimization HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Energy optimization exception: {e}")
        
        return False
    
    async def test_ai_analytics_dashboard(self):
        """Test du tableau de bord AI Analytics"""
        print("\n📊 Test AI Analytics Dashboard...")
        
        try:
            response = await self.make_request("GET", "/ai-analytics/dashboard", auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("dashboard") and data.get("status") == "success":
                    dashboard = data["dashboard"]
                    print("✅ AI Analytics dashboard retrieved")
                    overview = dashboard.get("overview", {})
                    print(f"   Active Anomalies: {overview.get('active_anomalies', 0)}")
                    print(f"   Total Predictions: {overview.get('total_predictions', 0)}")
                    print(f"   Models Active: {overview.get('models_active', 0)}")
                    print(f"   Service Health: {overview.get('service_health')}")
                    self.test_results["ai_analytics_dashboard"] = True
                    return True
                else:
                    print(f"❌ AI Analytics dashboard failed: {data}")
            else:
                print(f"❌ AI Analytics dashboard HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ AI Analytics dashboard exception: {e}")
        
        return False
    
    async def test_ai_analytics_models_status(self):
        """Test du statut des modèles ML"""
        print("\n🧠 Test AI Analytics Models Status...")
        
        try:
            response = await self.make_request("GET", "/ai-analytics/models/status", auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("models_info") and data.get("status") == "success":
                    models_info = data["models_info"]
                    print("✅ AI Analytics models status retrieved")
                    print(f"   Models Available: {len(models_info.get('models_available', []))}")
                    print(f"   Scalers Available: {len(models_info.get('scalers_available', []))}")
                    print(f"   Service Initialized: {models_info.get('service_initialized')}")
                    model_types = models_info.get('model_types', {})
                    print(f"   Anomaly Detection Models: {len(model_types.get('anomaly_detection', []))}")
                    print(f"   Prediction Models: {len(model_types.get('prediction', []))}")
                    self.test_results["ai_analytics_models_status"] = True
                    return True
                else:
                    print(f"❌ AI Analytics models status failed: {data}")
            else:
                print(f"❌ AI Analytics models status HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ AI Analytics models status exception: {e}")
        
        return False
    
    async def test_ai_analytics_summary(self):
        """Test du résumé des analyses"""
        print("\n📈 Test AI Analytics Summary...")
        
        try:
            response = await self.make_request("GET", "/ai-analytics/analytics/summary", auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("summary") and data.get("status") == "success":
                    summary = data["summary"]
                    print("✅ AI Analytics summary retrieved")
                    print(f"   Analysis Period: {summary.get('analysis_period', {}).get('duration_days')} days")
                    print(f"   Total Anomalies: {summary.get('total_anomalies', 0)}")
                    print(f"   Total Predictions: {summary.get('total_predictions', 0)}")
                    print(f"   Service Health: {summary.get('service_health')}")
                    anomaly_stats = summary.get('anomaly_statistics', {})
                    if anomaly_stats:
                        print(f"   Anomaly Types: {list(anomaly_stats.keys())}")
                    self.test_results["ai_analytics_summary"] = True
                    return True
                else:
                    print(f"❌ AI Analytics summary failed: {data}")
            else:
                print(f"❌ AI Analytics summary HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ AI Analytics summary exception: {e}")
        
        return False
    
    async def test_ai_analytics_recommendations(self):
        """Test des recommandations IA"""
        print("\n💡 Test AI Analytics Recommendations...")
        
        try:
            response = await self.make_request("GET", "/ai-analytics/recommendations", auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("recommendations") and data.get("status") == "success":
                    recommendations = data["recommendations"]
                    print("✅ AI Analytics recommendations retrieved")
                    print(f"   Total Recommendations: {len(recommendations)}")
                    print(f"   Based on Anomalies: {data.get('based_on_anomalies', 0)}")
                    for rec in recommendations[:3]:  # Show first 3
                        print(f"   - {rec.get('title')} (Priority: {rec.get('priority')})")
                    self.test_results["ai_analytics_recommendations"] = True
                    return True
                else:
                    print(f"❌ AI Analytics recommendations failed: {data}")
            else:
                print(f"❌ AI Analytics recommendations HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ AI Analytics recommendations exception: {e}")
        
        return False
    
    async def test_ai_analytics_health(self):
        """Test de santé du service AI Analytics"""
        print("\n🏥 Test AI Analytics Health Check...")
        
        try:
            response = await self.make_request("GET", "/ai-analytics/health")
            
            if response["status"] == 200:
                data = response["data"]
                if "service_ready" in data:
                    print("✅ AI Analytics health check successful")
                    print(f"   Service Ready: {data.get('service_ready')}")
                    print(f"   Models Loaded: {data.get('models_loaded', 0)}")
                    print(f"   Status: {data.get('status')}")
                    self.test_results["ai_analytics_health"] = True
                    return True
                else:
                    print(f"❌ AI Analytics health check failed: {data}")
            else:
                print(f"❌ AI Analytics health check HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ AI Analytics health check exception: {e}")
        
        return False

    # ===== NEW ADVANCED CRYPTO FEATURES TESTS =====
    
    async def test_advanced_crypto_generate_zk_proof(self):
        """Test de génération de preuve zero-knowledge"""
        print("\n🔐 Test Advanced Crypto Generate ZK Proof...")
        
        try:
            # Test IDENTITY proof
            zk_request = {
                "proof_type": "identity",
                "secret_value": "secret_identity_123",
                "public_parameters": {"domain": "QuantumShield"}
            }
            response = await self.make_request("POST", "/advanced-crypto/generate-zk-proof", 
                                             zk_request, auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("proof") and data.get("status") == "success":
                    proof = data["proof"]
                    print("✅ ZK Proof generation successful")
                    print(f"   Proof ID: {proof.get('proof_id')}")
                    print(f"   Proof Type: {proof.get('proof_type')}")
                    print(f"   Challenge: {proof.get('challenge', 'N/A')[:20]}...")
                    
                    # Store proof ID for verification test
                    self.test_data["zk_proof_id"] = proof.get("proof_id")
                    self.test_results["advanced_crypto_generate_zk_proof"] = True
                    return True
                else:
                    print(f"❌ ZK Proof generation failed: {data}")
            else:
                print(f"❌ ZK Proof generation HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ ZK Proof generation exception: {e}")
        
        return False
    
    async def test_advanced_crypto_verify_zk_proof(self):
        """Test de vérification de preuve zero-knowledge"""
        print("\n🔍 Test Advanced Crypto Verify ZK Proof...")
        
        if not self.test_data.get("zk_proof_id"):
            print("❌ No ZK proof ID available for verification test")
            return False
        
        try:
            verify_request = {
                "proof_id": self.test_data["zk_proof_id"]
            }
            response = await self.make_request("POST", "/advanced-crypto/verify-zk-proof", 
                                             verify_request, auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("verification_result") and data.get("status") == "success":
                    result = data["verification_result"]
                    print("✅ ZK Proof verification successful")
                    print(f"   Proof Valid: {result.get('valid')}")
                    print(f"   Proof ID: {result.get('proof_id')}")
                    print(f"   Proof Type: {result.get('proof_type')}")
                    self.test_results["advanced_crypto_verify_zk_proof"] = True
                    return True
                else:
                    print(f"❌ ZK Proof verification failed: {data}")
            else:
                print(f"❌ ZK Proof verification HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ ZK Proof verification exception: {e}")
        
        return False
    
    async def test_advanced_crypto_setup_threshold_signature(self):
        """Test de configuration de signature à seuil"""
        print("\n🔑 Test Advanced Crypto Setup Threshold Signature...")
        
        try:
            threshold_request = {
                "threshold": 2,
                "total_parties": 3
            }
            response = await self.make_request("POST", "/advanced-crypto/setup-threshold-signature", 
                                             threshold_request, auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("scheme") and data.get("status") == "success":
                    scheme = data["scheme"]
                    print("✅ Threshold signature setup successful")
                    print(f"   Scheme ID: {scheme.get('scheme_id')}")
                    print(f"   Threshold: {scheme.get('threshold')}")
                    print(f"   Total Parties: {scheme.get('total_parties')}")
                    print(f"   Parties: {len(scheme.get('parties', []))}")
                    
                    # Store scheme data for signing test
                    self.test_data["threshold_scheme_id"] = scheme.get("scheme_id")
                    self.test_data["threshold_parties"] = scheme.get("parties", [])
                    self.test_results["advanced_crypto_setup_threshold_signature"] = True
                    return True
                else:
                    print(f"❌ Threshold signature setup failed: {data}")
            else:
                print(f"❌ Threshold signature setup HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Threshold signature setup exception: {e}")
        
        return False
    
    async def test_advanced_crypto_threshold_sign(self):
        """Test de signature à seuil"""
        print("\n✍️ Test Advanced Crypto Threshold Sign...")
        
        if not self.test_data.get("threshold_scheme_id") or not self.test_data.get("threshold_parties"):
            print("❌ No threshold scheme data available for signing test")
            return False
        
        try:
            # Use first 2 parties (meets threshold of 2)
            parties = self.test_data["threshold_parties"]
            signing_parties = [p["party_id"] for p in parties[:2]]
            
            sign_request = {
                "scheme_id": self.test_data["threshold_scheme_id"],
                "message": "Test message for threshold signature verification",
                "signing_parties": signing_parties
            }
            response = await self.make_request("POST", "/advanced-crypto/threshold-sign", 
                                             sign_request, auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("signature") and data.get("status") == "success":
                    signature = data["signature"]
                    print("✅ Threshold signing successful")
                    print(f"   Signature ID: {signature.get('signature_id')}")
                    print(f"   Combined Signature: {signature.get('combined_signature')[:20]}...")
                    print(f"   Threshold Met: {signature.get('threshold_met')}")
                    print(f"   Signing Parties: {signature.get('signing_parties_count')}")
                    
                    # Store signature ID for verification test
                    self.test_data["threshold_signature_id"] = signature.get("signature_id")
                    self.test_results["advanced_crypto_threshold_sign"] = True
                    return True
                else:
                    print(f"❌ Threshold signing failed: {data}")
            else:
                print(f"❌ Threshold signing HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Threshold signing exception: {e}")
        
        return False
    
    async def test_advanced_crypto_verify_threshold_signature(self):
        """Test de vérification de signature à seuil"""
        print("\n✅ Test Advanced Crypto Verify Threshold Signature...")
        
        if not self.test_data.get("threshold_signature_id"):
            print("❌ No threshold signature ID available for verification test")
            return False
        
        try:
            verify_request = {
                "signature_id": self.test_data["threshold_signature_id"]
            }
            response = await self.make_request("POST", "/advanced-crypto/verify-threshold-signature", 
                                             verify_request, auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("verification_result") and data.get("status") == "success":
                    result = data["verification_result"]
                    print("✅ Threshold signature verification successful")
                    print(f"   Signature Valid: {result.get('valid')}")
                    print(f"   Signature ID: {result.get('signature_id')}")
                    print(f"   Scheme ID: {result.get('scheme_id')}")
                    print(f"   Threshold Met: {result.get('threshold_met')}")
                    self.test_results["advanced_crypto_verify_threshold_signature"] = True
                    return True
                else:
                    print(f"❌ Threshold signature verification failed: {data}")
            else:
                print(f"❌ Threshold signature verification HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Threshold signature verification exception: {e}")
        
        return False
    
    async def test_advanced_crypto_audit_trail(self):
        """Test de récupération du trail d'audit"""
        print("\n📋 Test Advanced Crypto Audit Trail...")
        
        try:
            response = await self.make_request("GET", "/advanced-crypto/audit-trail?limit=50", 
                                             auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("audit_trail") and data.get("status") == "success":
                    audit_trail = data["audit_trail"]
                    print("✅ Audit trail retrieved successfully")
                    print(f"   Total Events: {data.get('count', 0)}")
                    print(f"   Events Retrieved: {len(audit_trail)}")
                    
                    # Show some event types
                    event_types = set()
                    for event in audit_trail[:5]:  # First 5 events
                        event_types.add(event.get("event_type", "unknown"))
                    print(f"   Event Types: {', '.join(event_types)}")
                    
                    # Store first audit ID for integrity test
                    if audit_trail:
                        self.test_data["audit_id"] = audit_trail[0].get("audit_id")
                    
                    self.test_results["advanced_crypto_audit_trail"] = True
                    return True
                else:
                    print(f"❌ Audit trail retrieval failed: {data}")
            else:
                print(f"❌ Audit trail HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Audit trail exception: {e}")
        
        return False
    
    async def test_advanced_crypto_verify_audit_integrity(self):
        """Test de vérification d'intégrité d'audit"""
        print("\n🔍 Test Advanced Crypto Verify Audit Integrity...")
        
        if not self.test_data.get("audit_id"):
            print("❌ No audit ID available for integrity verification test")
            return False
        
        try:
            audit_id = self.test_data["audit_id"]
            response = await self.make_request("GET", f"/advanced-crypto/verify-audit-integrity/{audit_id}", 
                                             auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if "integrity_valid" in data and data.get("status") == "success":
                    print("✅ Audit integrity verification successful")
                    print(f"   Audit ID: {data.get('audit_id')}")
                    print(f"   Integrity Valid: {data.get('integrity_valid')}")
                    print(f"   Verified At: {data.get('verified_at')}")
                    self.test_results["advanced_crypto_verify_audit_integrity"] = True
                    return True
                else:
                    print(f"❌ Audit integrity verification failed: {data}")
            else:
                print(f"❌ Audit integrity verification HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Audit integrity verification exception: {e}")
        
        return False
    
    async def test_advanced_crypto_crypto_statistics(self):
        """Test de récupération des statistiques cryptographiques"""
        print("\n📊 Test Advanced Crypto Statistics...")
        
        try:
            response = await self.make_request("GET", "/advanced-crypto/crypto-statistics", 
                                             auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("statistics") and data.get("status") == "success":
                    stats = data["statistics"]
                    print("✅ Crypto statistics retrieved successfully")
                    print(f"   User ID: {stats.get('user_id')}")
                    print(f"   Keypairs Count: {stats.get('keypairs_count', 0)}")
                    print(f"   ZK Proofs Count: {stats.get('zk_proofs_count', 0)}")
                    print(f"   Threshold Schemes Count: {stats.get('threshold_schemes_count', 0)}")
                    
                    # Show audit events summary
                    audit_events = stats.get("audit_events", {})
                    total_events = sum(audit_events.values())
                    print(f"   Total Audit Events: {total_events}")
                    
                    self.test_results["advanced_crypto_crypto_statistics"] = True
                    return True
                else:
                    print(f"❌ Crypto statistics retrieval failed: {data}")
            else:
                print(f"❌ Crypto statistics HTTP error: {response['status']}")
        except Exception as e:
            print(f"❌ Crypto statistics exception: {e}")
        
        return False

    async def run_all_tests(self):
        """Exécute tous les tests dans l'ordre"""
        print("🚀 Démarrage des tests QuantumShield Backend")
        print("=" * 60)
        
        await self.setup()
        
        # Tests dans l'ordre logique
        test_functions = [
            self.test_health_check,
            self.test_auth_register,
            self.test_auth_login,
            self.test_auth_verify,
            self.test_crypto_generate_keys,
            self.test_crypto_encrypt,
            self.test_crypto_decrypt,
            self.test_devices_register,
            self.test_blockchain_stats,
            self.test_tokens_balance,
            self.test_mining_stats,
            self.test_dashboard_overview,
            # Advanced Crypto Tests
            self.test_advanced_crypto_supported_algorithms,
            self.test_advanced_crypto_generate_keypair,
            self.test_advanced_crypto_hybrid_encrypt,
            self.test_advanced_crypto_hybrid_decrypt,
            self.test_advanced_crypto_batch_encrypt,
            self.test_advanced_crypto_batch_decrypt,
            self.test_advanced_crypto_sign_dilithium,
            self.test_advanced_crypto_verify_dilithium,
            self.test_advanced_crypto_setup_key_rotation,
            self.test_advanced_crypto_rotate_keys,
            self.test_advanced_crypto_key_rotation_status,
            self.test_advanced_crypto_performance_comparison,
            self.test_advanced_crypto_algorithm_recommendations,
            # Security Service Tests
            self.test_security_mfa_setup,
            self.test_security_mfa_status,
            self.test_security_behavior_analysis,
            self.test_security_dashboard,
            self.test_security_recommendations,
            self.test_security_health,
            # AI Analytics Service Tests
            self.test_ai_analytics_device_anomalies,
            self.test_ai_analytics_network_anomalies,
            self.test_ai_analytics_energy_anomalies,
            self.test_ai_analytics_device_failure_prediction,
            self.test_ai_analytics_energy_prediction,
            self.test_ai_analytics_energy_optimization,
            self.test_ai_analytics_dashboard,
            self.test_ai_analytics_models_status,
            self.test_ai_analytics_summary,
            self.test_ai_analytics_recommendations,
            self.test_ai_analytics_health,
            # IoT Protocol Service Tests
            self.test_iot_protocol_health,
            self.test_iot_protocol_status,
            self.test_iot_protocol_statistics,
            # New Advanced Crypto Features Tests
            self.test_advanced_crypto_generate_zk_proof,
            self.test_advanced_crypto_verify_zk_proof,
            self.test_advanced_crypto_setup_threshold_signature,
            self.test_advanced_crypto_threshold_sign,
            self.test_advanced_crypto_verify_threshold_signature,
            self.test_advanced_crypto_audit_trail,
            self.test_advanced_crypto_verify_audit_integrity,
            self.test_advanced_crypto_crypto_statistics
        ]
        
        for test_func in test_functions:
            try:
                await test_func()
                await asyncio.sleep(0.5)  # Pause entre les tests
            except Exception as e:
                print(f"❌ Test {test_func.__name__} failed with exception: {e}")
        
        await self.cleanup()
        
        # Résumé des résultats
        self.print_summary()

    def print_summary(self):
        """Affiche le résumé des tests"""
        print("\n" + "=" * 60)
        print("📋 RÉSUMÉ DES TESTS")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results.values() if result)
        total = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:25} {status}")
        
        print("-" * 60)
        print(f"TOTAL: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        
        if passed == total:
            print("🎉 Tous les tests sont passés avec succès!")
        else:
            print("⚠️  Certains tests ont échoué. Vérifiez les logs ci-dessus.")
        
        return passed == total

async def main():
    """Point d'entrée principal"""
    tester = QuantumShieldTester()
    success = await tester.run_all_tests()
    
    # Code de sortie
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
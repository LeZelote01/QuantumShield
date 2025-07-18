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
from datetime import datetime
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
            "advanced_crypto_algorithm_recommendations": False
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
            self.test_dashboard_overview
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
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
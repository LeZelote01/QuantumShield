#!/usr/bin/env python3
"""
Test complet pour QuantumShield - Avec données de validation correctes
Focus sur les endpoints avec erreurs de validation et méthodes incorrectes
"""

import asyncio
import aiohttp
import json
import os
import sys
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Configuration des tests
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

class ComprehensiveQuantumShieldTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user = {
            "username": f"comprehensive_tester_{uuid.uuid4().hex[:8]}",
            "email": f"comprehensive_tester_{uuid.uuid4().hex[:8]}@quantumshield.com",
            "password": "SecurePassword123!"
        }
        self.test_data = {}
        self.comprehensive_results = {}

    async def setup(self):
        """Initialise la session HTTP"""
        self.session = aiohttp.ClientSession()
        print("🔧 Session HTTP initialisée pour tests complets")

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
                    try:
                        result = await response.json()
                    except:
                        result = {"error": "Invalid JSON response", "text": await response.text()}
                    return {"status": response.status, "data": result}
            elif method.upper() == "POST":
                async with self.session.post(url, json=data, headers=request_headers) as response:
                    try:
                        result = await response.json()
                    except:
                        result = {"error": "Invalid JSON response", "text": await response.text()}
                    return {"status": response.status, "data": result}
            elif method.upper() == "PUT":
                async with self.session.put(url, json=data, headers=request_headers) as response:
                    try:
                        result = await response.json()
                    except:
                        result = {"error": "Invalid JSON response", "text": await response.text()}
                    return {"status": response.status, "data": result}
        except Exception as e:
            return {"status": 500, "error": str(e)}

    async def setup_auth(self):
        """Configure l'authentification pour les tests"""
        print("\n🔐 Configuration de l'authentification...")
        
        # Enregistrement
        response = await self.make_request("POST", "/auth/register", self.test_user)
        if response["status"] != 200:
            print(f"❌ Échec de l'enregistrement: {response}")
            return False
        
        # Connexion
        login_data = {
            "username": self.test_user["username"],
            "password": self.test_user["password"]
        }
        response = await self.make_request("POST", "/auth/login", login_data)
        if response["status"] == 200 and response["data"].get("token"):
            self.auth_token = response["data"]["token"]
            print("✅ Authentification configurée")
            return True
        
        print(f"❌ Échec de la connexion: {response}")
        return False

    # ===== TESTS AVEC DONNÉES CORRECTES =====
    
    async def test_advanced_crypto_generate_zk_proof_corrected(self):
        """Test de génération ZK-proofs avec données correctes"""
        print("\n🔬 Test Advanced Crypto Generate ZK-Proof (Corrected)...")
        
        # Données correctes selon l'erreur de validation
        zk_request = {
            "proof_type": "membership",
            "statement": "test_statement",
            "witness": "test_witness",
            "secret_value": "test_secret_value_123",  # Champ manquant ajouté
            "public_parameters": {"test": "params"}
        }
        
        response = await self.make_request("POST", "/advanced-crypto/generate-zk-proof", 
                                         zk_request, auth_required=True)
        
        print(f"   Status: {response['status']}")
        print(f"   Response: {response['data']}")
        
        self.comprehensive_results["generate_zk_proof_corrected"] = {
            "status": response["status"],
            "working": response["status"] == 200,
            "error": response.get("error") or response["data"] if response["status"] != 200 else None
        }
        
        if response["status"] == 200:
            print("✅ ZK-proof generation working with correct data")
            return True
        else:
            print(f"❌ ZK-proof generation still failing with status {response['status']}")
            return False

    async def test_smart_contracts_templates_authenticated(self):
        """Test des templates smart contracts avec authentification"""
        print("\n📋 Test Smart Contracts Templates (Authenticated)...")
        
        response = await self.make_request("GET", "/advanced-blockchain/smart-contracts/templates", 
                                         auth_required=True)
        
        print(f"   Status: {response['status']}")
        print(f"   Response: {response['data']}")
        
        self.comprehensive_results["smart_contracts_templates"] = {
            "status": response["status"],
            "working": response["status"] == 200,
            "error": response.get("error") or response["data"] if response["status"] != 200 else None
        }
        
        if response["status"] == 200:
            print("✅ Smart contracts templates working")
            return True
        else:
            print(f"❌ Smart contracts templates failed with status {response['status']}")
            return False

    async def test_consensus_stake_corrected(self):
        """Test de staking avec données correctes"""
        print("\n💰 Test Consensus Stake (Corrected)...")
        
        # Données correctes selon l'erreur de validation
        stake_request = {
            "amount": 100.0,
            "validator_id": "validator_1",
            "validator_address": "0x1234567890abcdef1234567890abcdef12345678",  # Champ manquant ajouté
            "lock_period_days": 30
        }
        
        response = await self.make_request("POST", "/advanced-blockchain/consensus/stake", 
                                         stake_request, auth_required=True)
        
        print(f"   Status: {response['status']}")
        print(f"   Response: {response['data']}")
        
        self.comprehensive_results["consensus_stake_corrected"] = {
            "status": response["status"],
            "working": response["status"] == 200,
            "error": response.get("error") or response["data"] if response["status"] != 200 else None
        }
        
        if response["status"] == 200:
            print("✅ Consensus stake working with correct data")
            return True
        else:
            print(f"❌ Consensus stake still failing with status {response['status']}")
            return False

    async def test_ota_firmware_register_corrected(self):
        """Test d'enregistrement firmware OTA avec données correctes"""
        print("\n📦 Test OTA Firmware Register (Corrected)...")
        
        # Données correctes selon l'erreur de validation
        firmware_data = {
            "firmware_info": {
                "firmware_id": "test_firmware_v1.0.0",
                "version": "1.0.0",
                "device_type": "smart_sensor",
                "file_size": 1024000,
                "checksum": "sha256:abcd1234567890",
                "description": "Test firmware for smart sensors"
            },
            "firmware_file": {
                "filename": "test_firmware.bin",
                "content_type": "application/octet-stream",
                "size": 1024000
            }
        }
        
        response = await self.make_request("POST", "/ota/firmware/register", 
                                         firmware_data, auth_required=True)
        
        print(f"   Status: {response['status']}")
        print(f"   Response: {response['data']}")
        
        self.comprehensive_results["ota_firmware_register_corrected"] = {
            "status": response["status"],
            "working": response["status"] == 200,
            "error": response.get("error") or response["data"] if response["status"] != 200 else None
        }
        
        if response["status"] == 200:
            print("✅ OTA firmware register working with correct data")
            return True
        else:
            print(f"❌ OTA firmware register still failing with status {response['status']}")
            return False

    # ===== TESTS DES MÉTHODES HTTP CORRECTES =====
    
    async def test_smart_contracts_deploy_get_method(self):
        """Test de déploiement smart contracts avec méthode GET (si c'est un endpoint de liste)"""
        print("\n🚀 Test Smart Contracts Deploy (GET method)...")
        
        response = await self.make_request("GET", "/advanced-blockchain/smart-contracts/deploy", 
                                         auth_required=True)
        
        print(f"   Status: {response['status']}")
        print(f"   Response: {response['data']}")
        
        self.comprehensive_results["smart_contracts_deploy_get"] = {
            "status": response["status"],
            "working": response["status"] == 200,
            "error": response.get("error") or response["data"] if response["status"] != 200 else None
        }
        
        if response["status"] == 200:
            print("✅ Smart contracts deploy (GET) working")
            return True
        else:
            print(f"❌ Smart contracts deploy (GET) failed with status {response['status']}")
            return False

    async def test_security_gdpr_report_get_method(self):
        """Test de rapport GDPR avec méthode GET"""
        print("\n📋 Test Security GDPR Report (GET method)...")
        
        response = await self.make_request("GET", "/security/gdpr/report", auth_required=True)
        
        print(f"   Status: {response['status']}")
        print(f"   Response: {response['data']}")
        
        self.comprehensive_results["security_gdpr_report_get"] = {
            "status": response["status"],
            "working": response["status"] == 200,
            "error": response.get("error") or response["data"] if response["status"] != 200 else None
        }
        
        if response["status"] == 200:
            print("✅ Security GDPR report (GET) working")
            return True
        else:
            print(f"❌ Security GDPR report (GET) failed with status {response['status']}")
            return False

    # ===== TESTS D'EXPLORATION D'ENDPOINTS =====
    
    async def test_ota_endpoints_exploration(self):
        """Exploration des endpoints OTA disponibles"""
        print("\n📦 Test OTA Endpoints Exploration...")
        
        ota_endpoints = [
            "/ota/health",
            "/ota/statistics",
            "/ota/firmware",
            "/ota/updates",
            "/ota/config"
        ]
        
        working_endpoints = []
        for endpoint in ota_endpoints:
            response = await self.make_request("GET", endpoint, auth_required=True)
            if response["status"] == 200:
                working_endpoints.append(endpoint)
                print(f"   ✅ {endpoint}: Working")
            else:
                print(f"   ❌ {endpoint}: {response['status']}")
        
        self.comprehensive_results["ota_endpoints_exploration"] = {
            "working_endpoints": working_endpoints,
            "total_tested": len(ota_endpoints),
            "working_count": len(working_endpoints)
        }
        
        return len(working_endpoints) > 0

    async def test_security_endpoints_exploration(self):
        """Exploration des endpoints de sécurité disponibles"""
        print("\n🛡️ Test Security Endpoints Exploration...")
        
        security_endpoints = [
            "/security/health",
            "/security/dashboard",
            "/security/recommendations",
            "/security/mfa/status",
            "/security/behavior/analyze",
            "/security/audit",
            "/security/compliance"
        ]
        
        working_endpoints = []
        for endpoint in security_endpoints:
            if endpoint == "/security/behavior/analyze":
                # POST endpoint
                response = await self.make_request("POST", endpoint, 
                                                 {"action": "test", "context": {}}, 
                                                 auth_required=True)
            else:
                response = await self.make_request("GET", endpoint, auth_required=True)
            
            if response["status"] == 200:
                working_endpoints.append(endpoint)
                print(f"   ✅ {endpoint}: Working")
            else:
                print(f"   ❌ {endpoint}: {response['status']}")
        
        self.comprehensive_results["security_endpoints_exploration"] = {
            "working_endpoints": working_endpoints,
            "total_tested": len(security_endpoints),
            "working_count": len(working_endpoints)
        }
        
        return len(working_endpoints) > 0

    async def run_all_comprehensive_tests(self):
        """Exécute tous les tests complets"""
        print("🎯 DÉBUT DES TESTS COMPLETS QUANTUMSHIELD")
        print("=" * 60)
        
        # Configuration
        if not await self.setup_auth():
            print("❌ Impossible de configurer l'authentification")
            return
        
        # Tests avec données correctes
        print("\n🔧 TESTS AVEC DONNÉES CORRECTES")
        print("-" * 40)
        await self.test_advanced_crypto_generate_zk_proof_corrected()
        await self.test_smart_contracts_templates_authenticated()
        await self.test_consensus_stake_corrected()
        await self.test_ota_firmware_register_corrected()
        
        # Tests avec méthodes HTTP correctes
        print("\n🌐 TESTS AVEC MÉTHODES HTTP CORRECTES")
        print("-" * 40)
        await self.test_smart_contracts_deploy_get_method()
        await self.test_security_gdpr_report_get_method()
        
        # Exploration d'endpoints
        print("\n🔍 EXPLORATION D'ENDPOINTS")
        print("-" * 40)
        await self.test_ota_endpoints_exploration()
        await self.test_security_endpoints_exploration()
        
        # Résumé des résultats
        self.print_comprehensive_summary()

    def print_comprehensive_summary(self):
        """Affiche un résumé des tests complets"""
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES TESTS COMPLETS")
        print("=" * 60)
        
        working_count = 0
        total_count = 0
        
        # Tests avec données correctes
        print("\n🔧 TESTS AVEC DONNÉES CORRECTES:")
        corrected_tests = ["generate_zk_proof_corrected", "smart_contracts_templates", 
                          "consensus_stake_corrected", "ota_firmware_register_corrected"]
        for test in corrected_tests:
            if test in self.comprehensive_results:
                result = self.comprehensive_results[test]
                status = "✅ FONCTIONNEL" if result["working"] else f"❌ ÉCHEC ({result['status']})"
                print(f"   - {test}: {status}")
                if result["working"]:
                    working_count += 1
                total_count += 1
        
        # Tests avec méthodes correctes
        print("\n🌐 TESTS AVEC MÉTHODES HTTP CORRECTES:")
        method_tests = ["smart_contracts_deploy_get", "security_gdpr_report_get"]
        for test in method_tests:
            if test in self.comprehensive_results:
                result = self.comprehensive_results[test]
                status = "✅ FONCTIONNEL" if result["working"] else f"❌ ÉCHEC ({result['status']})"
                print(f"   - {test}: {status}")
                if result["working"]:
                    working_count += 1
                total_count += 1
        
        # Exploration d'endpoints
        print("\n🔍 EXPLORATION D'ENDPOINTS:")
        exploration_tests = ["ota_endpoints_exploration", "security_endpoints_exploration"]
        for test in exploration_tests:
            if test in self.comprehensive_results:
                result = self.comprehensive_results[test]
                working_endpoints = result["working_count"]
                total_endpoints = result["total_tested"]
                print(f"   - {test}: {working_endpoints}/{total_endpoints} endpoints working")
                if working_endpoints > 0:
                    working_count += 1
                total_count += 1
        
        # Statistiques finales
        success_rate = (working_count / total_count * 100) if total_count > 0 else 0
        print(f"\n📈 TAUX DE RÉUSSITE: {working_count}/{total_count} ({success_rate:.1f}%)")
        
        # Recommandations
        print("\n💡 RECOMMANDATIONS:")
        failed_tests = [test for test, result in self.comprehensive_results.items() 
                       if isinstance(result, dict) and not result.get("working", True)]
        if failed_tests:
            print("   Tests nécessitant des corrections:")
            for test in failed_tests:
                result = self.comprehensive_results[test]
                print(f"   - {test}: Vérifier la structure des données et les endpoints")
        else:
            print("   Tous les tests fonctionnent correctement!")
        
        print("\n" + "=" * 60)

async def main():
    """Fonction principale"""
    tester = ComprehensiveQuantumShieldTester()
    
    try:
        await tester.setup()
        await tester.run_all_comprehensive_tests()
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
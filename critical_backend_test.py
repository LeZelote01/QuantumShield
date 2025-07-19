#!/usr/bin/env python3
"""
Test critique pour QuantumShield - Focus sur les erreurs identifiées
Teste spécifiquement les endpoints avec erreurs HTTP 500, 404, et 400
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

class CriticalQuantumShieldTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user = {
            "username": f"critical_tester_{uuid.uuid4().hex[:8]}",
            "email": f"critical_tester_{uuid.uuid4().hex[:8]}@quantumshield.com",
            "password": "SecurePassword123!"
        }
        self.test_data = {}
        self.critical_results = {}

    async def setup(self):
        """Initialise la session HTTP"""
        self.session = aiohttp.ClientSession()
        print("🔧 Session HTTP initialisée pour tests critiques")

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

    # ===== TESTS DES ERREURS HTTP 500 =====
    
    async def test_advanced_crypto_hybrid_decrypt(self):
        """Test du déchiffrement hybride (erreur HTTP 500 connue)"""
        print("\n🔓 Test Advanced Crypto Hybrid Decrypt (HTTP 500)...")
        
        # Créer des données de test valides
        test_encrypted_data = {
            "algorithm": "Kyber-768+AES",
            "kem_ciphertext": "test_kem_ciphertext_data",
            "aes_iv": "test_aes_iv_12345",
            "encrypted_message": "test_encrypted_message_data"
        }
        
        decrypt_request = {
            "encrypted_data": test_encrypted_data,
            "keypair_id": "test_keypair_id"
        }
        
        response = await self.make_request("POST", "/advanced-crypto/hybrid-decrypt", 
                                         decrypt_request, auth_required=True)
        
        print(f"   Status: {response['status']}")
        print(f"   Response: {response['data']}")
        
        self.critical_results["hybrid_decrypt"] = {
            "status": response["status"],
            "working": response["status"] == 200,
            "error": response.get("error") or response["data"] if response["status"] != 200 else None
        }
        
        if response["status"] == 200:
            print("✅ Hybrid decrypt working")
            return True
        else:
            print(f"❌ Hybrid decrypt failed with status {response['status']}")
            return False

    async def test_security_dashboard(self):
        """Test du dashboard sécurité (erreur HTTP 500 connue)"""
        print("\n📊 Test Security Dashboard (HTTP 500)...")
        
        response = await self.make_request("GET", "/security/dashboard", auth_required=True)
        
        print(f"   Status: {response['status']}")
        print(f"   Response: {response['data']}")
        
        self.critical_results["security_dashboard"] = {
            "status": response["status"],
            "working": response["status"] == 200,
            "error": response.get("error") or response["data"] if response["status"] != 200 else None
        }
        
        if response["status"] == 200:
            print("✅ Security dashboard working")
            return True
        else:
            print(f"❌ Security dashboard failed with status {response['status']}")
            return False

    async def test_advanced_crypto_generate_zk_proof(self):
        """Test de génération ZK-proofs (erreur HTTP 500 connue)"""
        print("\n🔬 Test Advanced Crypto Generate ZK-Proof (HTTP 500)...")
        
        zk_request = {
            "proof_type": "membership",
            "statement": "test_statement",
            "witness": "test_witness",
            "public_parameters": {"test": "params"}
        }
        
        response = await self.make_request("POST", "/advanced-crypto/generate-zk-proof", 
                                         zk_request, auth_required=True)
        
        print(f"   Status: {response['status']}")
        print(f"   Response: {response['data']}")
        
        self.critical_results["generate_zk_proof"] = {
            "status": response["status"],
            "working": response["status"] == 200,
            "error": response.get("error") or response["data"] if response["status"] != 200 else None
        }
        
        if response["status"] == 200:
            print("✅ ZK-proof generation working")
            return True
        else:
            print(f"❌ ZK-proof generation failed with status {response['status']}")
            return False

    # ===== TESTS DES ERREURS HTTP 404 =====
    
    async def test_advanced_blockchain_health(self):
        """Test du health check blockchain avancé (erreur HTTP 404 connue)"""
        print("\n🏥 Test Advanced Blockchain Health (HTTP 404)...")
        
        response = await self.make_request("GET", "/advanced-blockchain/health")
        
        print(f"   Status: {response['status']}")
        print(f"   Response: {response['data']}")
        
        self.critical_results["advanced_blockchain_health"] = {
            "status": response["status"],
            "working": response["status"] == 200,
            "error": response.get("error") or response["data"] if response["status"] != 200 else None
        }
        
        if response["status"] == 200:
            print("✅ Advanced blockchain health working")
            return True
        else:
            print(f"❌ Advanced blockchain health failed with status {response['status']}")
            return False

    async def test_smart_contracts_templates(self):
        """Test des templates smart contracts (erreur HTTP 404 connue)"""
        print("\n📋 Test Smart Contracts Templates (HTTP 404)...")
        
        response = await self.make_request("GET", "/advanced-blockchain/smart-contracts/templates")
        
        print(f"   Status: {response['status']}")
        print(f"   Response: {response['data']}")
        
        self.critical_results["smart_contracts_templates"] = {
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

    # ===== TESTS DES ERREURS HTTP 400 =====
    
    async def test_smart_contracts_deploy(self):
        """Test de déploiement smart contracts (erreur HTTP 400 connue)"""
        print("\n🚀 Test Smart Contracts Deploy (HTTP 400)...")
        
        deploy_request = {
            "template_name": "basic_token",
            "parameters": {
                "name": "TestToken",
                "symbol": "TEST",
                "initial_supply": 1000000
            },
            "gas_limit": 500000
        }
        
        response = await self.make_request("POST", "/advanced-blockchain/smart-contracts/deploy", 
                                         deploy_request, auth_required=True)
        
        print(f"   Status: {response['status']}")
        print(f"   Response: {response['data']}")
        
        self.critical_results["smart_contracts_deploy"] = {
            "status": response["status"],
            "working": response["status"] == 200,
            "error": response.get("error") or response["data"] if response["status"] != 200 else None
        }
        
        if response["status"] == 200:
            print("✅ Smart contracts deploy working")
            return True
        else:
            print(f"❌ Smart contracts deploy failed with status {response['status']}")
            return False

    async def test_governance_proposal_create(self):
        """Test de création de proposition gouvernance (erreur HTTP 400 connue)"""
        print("\n🗳️ Test Governance Proposal Create (HTTP 400)...")
        
        proposal_request = {
            "title": "Test Governance Proposal",
            "description": "This is a test proposal for governance testing",
            "proposal_type": "parameter_change",
            "parameters": {
                "parameter_name": "block_reward",
                "new_value": 15
            },
            "voting_period_days": 7
        }
        
        response = await self.make_request("POST", "/advanced-blockchain/governance/proposals", 
                                         proposal_request, auth_required=True)
        
        print(f"   Status: {response['status']}")
        print(f"   Response: {response['data']}")
        
        self.critical_results["governance_proposal_create"] = {
            "status": response["status"],
            "working": response["status"] == 200,
            "error": response.get("error") or response["data"] if response["status"] != 200 else None
        }
        
        if response["status"] == 200:
            print("✅ Governance proposal create working")
            return True
        else:
            print(f"❌ Governance proposal create failed with status {response['status']}")
            return False

    async def test_consensus_stake(self):
        """Test de staking tokens (erreur HTTP 400 connue)"""
        print("\n💰 Test Consensus Stake (HTTP 400)...")
        
        stake_request = {
            "amount": 100.0,
            "validator_id": "validator_1",
            "lock_period_days": 30
        }
        
        response = await self.make_request("POST", "/advanced-blockchain/consensus/stake", 
                                         stake_request, auth_required=True)
        
        print(f"   Status: {response['status']}")
        print(f"   Response: {response['data']}")
        
        self.critical_results["consensus_stake"] = {
            "status": response["status"],
            "working": response["status"] == 200,
            "error": response.get("error") or response["data"] if response["status"] != 200 else None
        }
        
        if response["status"] == 200:
            print("✅ Consensus stake working")
            return True
        else:
            print(f"❌ Consensus stake failed with status {response['status']}")
            return False

    # ===== TESTS DES PROTOCOLES IOT =====
    
    async def test_iot_protocol_mqtt_start(self):
        """Test de démarrage MQTT (erreur de configuration connue)"""
        print("\n📡 Test IoT Protocol MQTT Start...")
        
        mqtt_config = {
            "broker_host": "localhost",
            "broker_port": 1883,
            "client_id": "quantumshield_test",
            "topics": ["test/sensors", "test/commands"]
        }
        
        response = await self.make_request("POST", "/iot-protocol/mqtt/start", 
                                         mqtt_config, auth_required=True)
        
        print(f"   Status: {response['status']}")
        print(f"   Response: {response['data']}")
        
        self.critical_results["iot_mqtt_start"] = {
            "status": response["status"],
            "working": response["status"] == 200,
            "error": response.get("error") or response["data"] if response["status"] != 200 else None
        }
        
        if response["status"] == 200:
            print("✅ IoT MQTT start working")
            return True
        else:
            print(f"❌ IoT MQTT start failed with status {response['status']}")
            return False

    async def test_iot_protocol_coap_start(self):
        """Test de démarrage CoAP (erreur de configuration connue)"""
        print("\n🌐 Test IoT Protocol CoAP Start...")
        
        coap_config = {
            "server_host": "localhost",
            "server_port": 5683,
            "resources": ["/sensors", "/actuators"]
        }
        
        response = await self.make_request("POST", "/iot-protocol/coap/start", 
                                         coap_config, auth_required=True)
        
        print(f"   Status: {response['status']}")
        print(f"   Response: {response['data']}")
        
        self.critical_results["iot_coap_start"] = {
            "status": response["status"],
            "working": response["status"] == 200,
            "error": response.get("error") or response["data"] if response["status"] != 200 else None
        }
        
        if response["status"] == 200:
            print("✅ IoT CoAP start working")
            return True
        else:
            print(f"❌ IoT CoAP start failed with status {response['status']}")
            return False

    # ===== TESTS DES MISES À JOUR OTA =====
    
    async def test_ota_firmware_register(self):
        """Test d'enregistrement firmware OTA (service non opérationnel)"""
        print("\n📦 Test OTA Firmware Register...")
        
        firmware_data = {
            "firmware_id": "test_firmware_v1.0.0",
            "version": "1.0.0",
            "device_type": "smart_sensor",
            "file_size": 1024000,
            "checksum": "sha256:abcd1234567890",
            "description": "Test firmware for smart sensors"
        }
        
        response = await self.make_request("POST", "/ota/firmware/register", 
                                         firmware_data, auth_required=True)
        
        print(f"   Status: {response['status']}")
        print(f"   Response: {response['data']}")
        
        self.critical_results["ota_firmware_register"] = {
            "status": response["status"],
            "working": response["status"] == 200,
            "error": response.get("error") or response["data"] if response["status"] != 200 else None
        }
        
        if response["status"] == 200:
            print("✅ OTA firmware register working")
            return True
        else:
            print(f"❌ OTA firmware register failed with status {response['status']}")
            return False

    async def test_ota_update_schedule(self):
        """Test de planification mise à jour OTA (non implémenté)"""
        print("\n⏰ Test OTA Update Schedule...")
        
        schedule_data = {
            "firmware_id": "test_firmware_v1.0.0",
            "target_devices": ["device_001", "device_002"],
            "scheduled_time": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            "rollback_enabled": True
        }
        
        response = await self.make_request("POST", "/ota/updates/schedule", 
                                         schedule_data, auth_required=True)
        
        print(f"   Status: {response['status']}")
        print(f"   Response: {response['data']}")
        
        self.critical_results["ota_update_schedule"] = {
            "status": response["status"],
            "working": response["status"] == 200,
            "error": response.get("error") or response["data"] if response["status"] != 200 else None
        }
        
        if response["status"] == 200:
            print("✅ OTA update schedule working")
            return True
        else:
            print(f"❌ OTA update schedule failed with status {response['status']}")
            return False

    # ===== TESTS ADDITIONNELS DE SÉCURITÉ =====
    
    async def test_security_honeypot_create(self):
        """Test de création honeypot (non implémenté)"""
        print("\n🍯 Test Security Honeypot Create...")
        
        honeypot_data = {
            "name": "test_honeypot",
            "type": "ssh",
            "port": 2222,
            "enabled": True
        }
        
        response = await self.make_request("POST", "/security/honeypots", 
                                         honeypot_data, auth_required=True)
        
        print(f"   Status: {response['status']}")
        print(f"   Response: {response['data']}")
        
        self.critical_results["security_honeypot_create"] = {
            "status": response["status"],
            "working": response["status"] == 200,
            "error": response.get("error") or response["data"] if response["status"] != 200 else None
        }
        
        if response["status"] == 200:
            print("✅ Security honeypot create working")
            return True
        else:
            print(f"❌ Security honeypot create failed with status {response['status']}")
            return False

    async def test_security_gdpr_report(self):
        """Test de rapport GDPR (non implémenté)"""
        print("\n📋 Test Security GDPR Report...")
        
        response = await self.make_request("GET", "/security/gdpr/report", auth_required=True)
        
        print(f"   Status: {response['status']}")
        print(f"   Response: {response['data']}")
        
        self.critical_results["security_gdpr_report"] = {
            "status": response["status"],
            "working": response["status"] == 200,
            "error": response.get("error") or response["data"] if response["status"] != 200 else None
        }
        
        if response["status"] == 200:
            print("✅ Security GDPR report working")
            return True
        else:
            print(f"❌ Security GDPR report failed with status {response['status']}")
            return False

    async def run_all_critical_tests(self):
        """Exécute tous les tests critiques"""
        print("🎯 DÉBUT DES TESTS CRITIQUES QUANTUMSHIELD")
        print("=" * 60)
        
        # Configuration
        if not await self.setup_auth():
            print("❌ Impossible de configurer l'authentification")
            return
        
        # Tests des erreurs HTTP 500
        print("\n🔥 TESTS DES ERREURS HTTP 500")
        print("-" * 40)
        await self.test_advanced_crypto_hybrid_decrypt()
        await self.test_security_dashboard()
        await self.test_advanced_crypto_generate_zk_proof()
        
        # Tests des erreurs HTTP 404
        print("\n🔍 TESTS DES ERREURS HTTP 404")
        print("-" * 40)
        await self.test_advanced_blockchain_health()
        await self.test_smart_contracts_templates()
        
        # Tests des erreurs HTTP 400
        print("\n⚠️ TESTS DES ERREURS HTTP 400")
        print("-" * 40)
        await self.test_smart_contracts_deploy()
        await self.test_governance_proposal_create()
        await self.test_consensus_stake()
        
        # Tests des protocoles IoT
        print("\n📡 TESTS DES PROTOCOLES IOT")
        print("-" * 40)
        await self.test_iot_protocol_mqtt_start()
        await self.test_iot_protocol_coap_start()
        
        # Tests des mises à jour OTA
        print("\n📦 TESTS DES MISES À JOUR OTA")
        print("-" * 40)
        await self.test_ota_firmware_register()
        await self.test_ota_update_schedule()
        
        # Tests de sécurité avancée
        print("\n🛡️ TESTS DE SÉCURITÉ AVANCÉE")
        print("-" * 40)
        await self.test_security_honeypot_create()
        await self.test_security_gdpr_report()
        
        # Résumé des résultats
        self.print_critical_summary()

    def print_critical_summary(self):
        """Affiche un résumé des tests critiques"""
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES TESTS CRITIQUES")
        print("=" * 60)
        
        working_count = 0
        total_count = len(self.critical_results)
        
        # Erreurs HTTP 500
        print("\n🔥 ERREURS HTTP 500:")
        http_500_tests = ["hybrid_decrypt", "security_dashboard", "generate_zk_proof"]
        for test in http_500_tests:
            if test in self.critical_results:
                result = self.critical_results[test]
                status = "✅ CORRIGÉ" if result["working"] else f"❌ ÉCHEC ({result['status']})"
                print(f"   - {test}: {status}")
                if result["working"]:
                    working_count += 1
        
        # Erreurs HTTP 404
        print("\n🔍 ERREURS HTTP 404:")
        http_404_tests = ["advanced_blockchain_health", "smart_contracts_templates"]
        for test in http_404_tests:
            if test in self.critical_results:
                result = self.critical_results[test]
                status = "✅ CORRIGÉ" if result["working"] else f"❌ ÉCHEC ({result['status']})"
                print(f"   - {test}: {status}")
                if result["working"]:
                    working_count += 1
        
        # Erreurs HTTP 400
        print("\n⚠️ ERREURS HTTP 400:")
        http_400_tests = ["smart_contracts_deploy", "governance_proposal_create", "consensus_stake"]
        for test in http_400_tests:
            if test in self.critical_results:
                result = self.critical_results[test]
                status = "✅ CORRIGÉ" if result["working"] else f"❌ ÉCHEC ({result['status']})"
                print(f"   - {test}: {status}")
                if result["working"]:
                    working_count += 1
        
        # Protocoles IoT
        print("\n📡 PROTOCOLES IOT:")
        iot_tests = ["iot_mqtt_start", "iot_coap_start"]
        for test in iot_tests:
            if test in self.critical_results:
                result = self.critical_results[test]
                status = "✅ FONCTIONNEL" if result["working"] else f"❌ ÉCHEC ({result['status']})"
                print(f"   - {test}: {status}")
                if result["working"]:
                    working_count += 1
        
        # Mises à jour OTA
        print("\n📦 MISES À JOUR OTA:")
        ota_tests = ["ota_firmware_register", "ota_update_schedule"]
        for test in ota_tests:
            if test in self.critical_results:
                result = self.critical_results[test]
                status = "✅ FONCTIONNEL" if result["working"] else f"❌ ÉCHEC ({result['status']})"
                print(f"   - {test}: {status}")
                if result["working"]:
                    working_count += 1
        
        # Sécurité avancée
        print("\n🛡️ SÉCURITÉ AVANCÉE:")
        security_tests = ["security_honeypot_create", "security_gdpr_report"]
        for test in security_tests:
            if test in self.critical_results:
                result = self.critical_results[test]
                status = "✅ FONCTIONNEL" if result["working"] else f"❌ ÉCHEC ({result['status']})"
                print(f"   - {test}: {status}")
                if result["working"]:
                    working_count += 1
        
        # Statistiques finales
        success_rate = (working_count / total_count * 100) if total_count > 0 else 0
        print(f"\n📈 TAUX DE RÉUSSITE: {working_count}/{total_count} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 OBJECTIF ATTEINT: >80% de réussite!")
        else:
            print(f"⚠️ OBJECTIF NON ATTEINT: {80 - success_rate:.1f}% manquants pour atteindre 80%")
        
        print("\n" + "=" * 60)

async def main():
    """Fonction principale"""
    tester = CriticalQuantumShieldTester()
    
    try:
        await tester.setup()
        await tester.run_all_critical_tests()
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
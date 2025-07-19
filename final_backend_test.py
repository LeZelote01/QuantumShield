#!/usr/bin/env python3
"""
Test final pour QuantumShield - Résumé des corrections et problèmes restants
Focus sur les endpoints critiques mentionnés dans la demande de révision
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

class FinalQuantumShieldTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user = {
            "username": f"final_tester_{uuid.uuid4().hex[:8]}",
            "email": f"final_tester_{uuid.uuid4().hex[:8]}@quantumshield.com",
            "password": "SecurePassword123!"
        }
        self.final_results = {}

    async def setup(self):
        """Initialise la session HTTP"""
        self.session = aiohttp.ClientSession()

    async def cleanup(self):
        """Nettoie les ressources"""
        if self.session:
            await self.session.close()

    async def make_request(self, method: str, endpoint: str, data: Dict = None, 
                          headers: Dict = None, auth_required: bool = False) -> Dict:
        """Effectue une requête HTTP avec gestion d'erreurs"""
        url = f"{API_BASE}{endpoint}"
        
        request_headers = {"Content-Type": "application/json"}
        if headers:
            request_headers.update(headers)
        
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
        except Exception as e:
            return {"status": 500, "error": str(e)}

    async def setup_auth(self):
        """Configure l'authentification pour les tests"""
        # Enregistrement
        response = await self.make_request("POST", "/auth/register", self.test_user)
        if response["status"] != 200:
            return False
        
        # Connexion
        login_data = {
            "username": self.test_user["username"],
            "password": self.test_user["password"]
        }
        response = await self.make_request("POST", "/auth/login", login_data)
        if response["status"] == 200 and response["data"].get("token"):
            self.auth_token = response["data"]["token"]
            return True
        
        return False

    async def test_critical_endpoints(self):
        """Test des endpoints critiques mentionnés dans la demande de révision"""
        
        print("🎯 TEST DES ENDPOINTS CRITIQUES QUANTUMSHIELD")
        print("=" * 60)
        
        # Configuration auth
        if not await self.setup_auth():
            print("❌ Impossible de configurer l'authentification")
            return
        
        # 1. Tests des erreurs HTTP 500 (mentionnées dans la demande)
        print("\n🔥 ERREURS HTTP 500 MENTIONNÉES:")
        
        # Hybrid decrypt
        response = await self.make_request("POST", "/advanced-crypto/hybrid-decrypt", {
            "encrypted_data": {"algorithm": "test", "kem_ciphertext": "test", "aes_iv": "test", "encrypted_message": "test"},
            "keypair_id": "test"
        }, auth_required=True)
        self.final_results["hybrid_decrypt"] = response["status"] == 200
        status_msg = "✅ CORRIGÉ" if response["status"] == 200 else f"❌ ÉCHEC ({response['status']})"
        print(f"   - /api/advanced-crypto/hybrid-decrypt: {status_msg}")
        
        # Security dashboard
        response = await self.make_request("GET", "/security/dashboard", auth_required=True)
        self.final_results["security_dashboard"] = response["status"] == 200
        status_msg = "✅ CORRIGÉ" if response["status"] == 200 else f"❌ ÉCHEC ({response['status']})"
        print(f"   - /api/security/dashboard: {status_msg}")
        
        # ZK-proof generation
        response = await self.make_request("POST", "/advanced-crypto/generate-zk-proof", {
            "proof_type": "membership",
            "secret_value": "test_secret",
            "public_parameters": {"test": "params"}
        }, auth_required=True)
        self.final_results["generate_zk_proof"] = response["status"] == 200
        status_msg = "✅ CORRIGÉ" if response["status"] == 200 else f"❌ ÉCHEC ({response['status']})"
        print(f"   - /api/advanced-crypto/generate-zk-proof: {status_msg}")
        
        # 2. Tests des erreurs HTTP 404 (mentionnées dans la demande)
        print("\n🔍 ERREURS HTTP 404 MENTIONNÉES:")
        
        # Advanced blockchain health
        response = await self.make_request("GET", "/advanced-blockchain/health")
        self.final_results["advanced_blockchain_health"] = response["status"] == 200
        status_msg = "✅ CORRIGÉ" if response["status"] == 200 else f"❌ ÉCHEC ({response['status']})"
        print(f"   - /api/advanced-blockchain/health: {status_msg}")
        
        # Smart contracts templates
        response = await self.make_request("GET", "/advanced-blockchain/smart-contracts/templates", auth_required=True)
        self.final_results["smart_contracts_templates"] = response["status"] == 200
        status_msg = "✅ CORRIGÉ" if response["status"] == 200 else f"❌ ÉCHEC ({response['status']})"
        print(f"   - /api/smart-contracts/templates: {status_msg}")
        
        # 3. Tests des erreurs HTTP 400 (mentionnées dans la demande)
        print("\n⚠️ ERREURS HTTP 400 MENTIONNÉES:")
        
        # Smart contracts deploy
        response = await self.make_request("POST", "/advanced-blockchain/smart-contracts/deploy", {
            "template_name": "basic_token",
            "parameters": {"name": "Test", "symbol": "TEST", "initial_supply": 1000},
            "gas_limit": 500000
        }, auth_required=True)
        self.final_results["smart_contracts_deploy"] = response["status"] == 200
        status_msg = "✅ CORRIGÉ" if response["status"] == 200 else f"❌ ÉCHEC ({response['status']})"
        print(f"   - Déploiement smart contracts: {status_msg}")
        
        # Governance proposals
        response = await self.make_request("POST", "/advanced-blockchain/governance/proposals", {
            "title": "Test Proposal",
            "description": "Test description",
            "proposal_type": "parameter_change",
            "parameters": {"parameter_name": "block_reward", "new_value": 15},
            "voting_period_days": 7
        }, auth_required=True)
        self.final_results["governance_proposals"] = response["status"] == 200
        status_msg = "✅ CORRIGÉ" if response["status"] == 200 else f"❌ ÉCHEC ({response['status']})"
        print(f"   - Propositions gouvernance: {status_msg}")
        
        # Staking tokens
        response = await self.make_request("POST", "/advanced-blockchain/consensus/stake", {
            "amount": 100.0,
            "validator_address": "0x1234567890abcdef1234567890abcdef12345678",
            "lock_period_days": 30
        }, auth_required=True)
        self.final_results["staking_tokens"] = response["status"] == 200
        status_msg = "✅ CORRIGÉ" if response["status"] == 200 else f"❌ ÉCHEC ({response['status']})"
        print(f"   - Staking tokens: {status_msg}")
        
        # IoT Protocol
        response = await self.make_request("POST", "/iot-protocol/mqtt/start", {
            "broker_host": "localhost",
            "broker_port": 1883,
            "client_id": "test_client"
        }, auth_required=True)
        self.final_results["iot_protocol"] = response["status"] == 200
        status_msg = "✅ CORRIGÉ" if response["status"] == 200 else f"❌ ÉCHEC ({response['status']})"
        print(f"   - IoT Protocol: {status_msg}")
        
        # 4. Services prioritaires mentionnés
        print("\n🎯 SERVICES PRIORITAIRES:")
        
        # Cryptographie avancée
        response = await self.make_request("GET", "/advanced-crypto/supported-algorithms")
        crypto_working = response["status"] == 200
        print(f"   - Cryptographie avancée: {'✅ FONCTIONNEL' if crypto_working else '❌ PROBLÈME'}")
        
        # Sécurité renforcée
        response = await self.make_request("GET", "/security/health")
        security_working = response["status"] == 200
        print(f"   - Sécurité renforcée: {'✅ FONCTIONNEL' if security_working else '❌ PROBLÈME'}")
        
        # Blockchain avancée
        response = await self.make_request("GET", "/advanced-blockchain/overview", auth_required=True)
        blockchain_working = response["status"] == 200
        print(f"   - Blockchain avancée: {'✅ FONCTIONNEL' if blockchain_working else '❌ PROBLÈME'}")
        
        # Protocoles IoT
        response = await self.make_request("GET", "/iot-protocol/health")
        iot_working = response["status"] == 200
        print(f"   - Protocoles IoT: {'✅ FONCTIONNEL' if iot_working else '❌ PROBLÈME'}")
        
        # Mises à jour OTA
        response = await self.make_request("GET", "/ota/health")
        ota_working = response["status"] == 200
        print(f"   - Mises à jour OTA: {'✅ FONCTIONNEL' if ota_working else '❌ PROBLÈME'}")
        
        # Calcul du taux de réussite
        critical_tests = ["hybrid_decrypt", "security_dashboard", "generate_zk_proof", 
                         "advanced_blockchain_health", "smart_contracts_templates",
                         "smart_contracts_deploy", "governance_proposals", "staking_tokens", "iot_protocol"]
        
        working_count = sum(1 for test in critical_tests if self.final_results.get(test, False))
        total_count = len(critical_tests)
        success_rate = (working_count / total_count * 100) if total_count > 0 else 0
        
        print(f"\n📈 TAUX DE RÉUSSITE CRITIQUE: {working_count}/{total_count} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 OBJECTIF ATTEINT: >80% de réussite sur les endpoints critiques!")
        else:
            missing_percent = 80 - success_rate
            print(f"⚠️ OBJECTIF NON ATTEINT: {missing_percent:.1f}% manquants pour atteindre 80%")
        
        # Résumé des corrections appliquées
        print("\n✅ CORRECTIONS CONFIRMÉES:")
        corrections = []
        if self.final_results.get("hybrid_decrypt"):
            corrections.append("- Déchiffrement hybride (HTTP 500 → 200)")
        if self.final_results.get("security_dashboard"):
            corrections.append("- Dashboard sécurité (HTTP 500 → 200)")
        if self.final_results.get("advanced_blockchain_health"):
            corrections.append("- Health check blockchain avancé (HTTP 404 → 200)")
        
        for correction in corrections:
            print(f"   {correction}")
        
        # Problèmes restants
        print("\n❌ PROBLÈMES RESTANTS:")
        remaining_issues = []
        if not self.final_results.get("generate_zk_proof"):
            remaining_issues.append("- Génération ZK-proofs (validation des données)")
        if not self.final_results.get("smart_contracts_templates"):
            remaining_issues.append("- Templates smart contracts (authentification)")
        if not self.final_results.get("smart_contracts_deploy"):
            remaining_issues.append("- Déploiement smart contracts (méthode HTTP)")
        if not self.final_results.get("governance_proposals"):
            remaining_issues.append("- Propositions gouvernance (validation des données)")
        if not self.final_results.get("staking_tokens"):
            remaining_issues.append("- Staking tokens (validation des données)")
        
        for issue in remaining_issues:
            print(f"   {issue}")
        
        print("\n" + "=" * 60)
        
        return success_rate

async def main():
    """Fonction principale"""
    tester = FinalQuantumShieldTester()
    
    try:
        await tester.setup()
        success_rate = await tester.test_critical_endpoints()
        return success_rate
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
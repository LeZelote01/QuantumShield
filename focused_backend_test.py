#!/usr/bin/env python3
"""
Test ciblé pour les corrections QuantumShield
Focus sur les endpoints corrigés selon la demande de révision
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

class FocusedQuantumShieldTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user = {
            "username": "quantum_focused_tester",
            "email": "focused_tester@quantumshield.com",
            "password": "SecurePassword123!"
        }
        self.test_data = {}
        self.corrected_endpoints_results = {}

    async def setup(self):
        """Initialise la session HTTP"""
        self.session = aiohttp.ClientSession()
        print("🔧 Session HTTP initialisée pour tests ciblés")

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

    async def setup_crypto_keypair(self):
        """Configure une paire de clés pour les tests crypto"""
        print("\n🔑 Configuration des clés cryptographiques...")
        
        # Génération de paire de clés multi-algorithmes
        keypair_request = {
            "encryption_algorithm": "Kyber-768",
            "signature_algorithm": "Dilithium-3"
        }
        response = await self.make_request("POST", "/advanced-crypto/generate-multi-algorithm-keypair", 
                                         keypair_request, auth_required=True)
        
        if response["status"] == 200 and response["data"].get("keypair"):
            keypair = response["data"]["keypair"]
            self.test_data["advanced_keypair_id"] = keypair.get("keypair_id")
            print(f"✅ Paire de clés générée: {keypair.get('keypair_id')}")
            return True
        
        print(f"❌ Échec de génération de clés: {response}")
        return False

    async def test_hybrid_decrypt_correction(self):
        """Test de la correction du déchiffrement hybride (était HTTP 500)"""
        print("\n🔓 Test Correction: Déchiffrement Hybride...")
        
        if not self.test_data.get("advanced_keypair_id"):
            print("❌ Pas de paire de clés disponible")
            self.corrected_endpoints_results["hybrid_decrypt"] = {"status": "failed", "reason": "no_keypair"}
            return False
        
        try:
            # D'abord chiffrer un message
            encrypt_request = {
                "message": "Test message pour déchiffrement hybride corrigé",
                "keypair_id": self.test_data["advanced_keypair_id"]
            }
            encrypt_response = await self.make_request("POST", "/advanced-crypto/hybrid-encrypt", 
                                                     encrypt_request, auth_required=True)
            
            if encrypt_response["status"] != 200:
                print(f"❌ Échec du chiffrement préalable: {encrypt_response['status']}")
                self.corrected_endpoints_results["hybrid_decrypt"] = {"status": "failed", "reason": "encrypt_failed"}
                return False
            
            encrypted_data = encrypt_response["data"]["encrypted_data"]
            
            # Maintenant tester le déchiffrement (endpoint corrigé)
            decrypt_request = {
                "encrypted_data": encrypted_data,
                "keypair_id": self.test_data["advanced_keypair_id"]
            }
            response = await self.make_request("POST", "/advanced-crypto/hybrid-decrypt", 
                                             decrypt_request, auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("decrypted_message") and data.get("status") == "success":
                    print("✅ CORRECTION VALIDÉE: Déchiffrement hybride fonctionne")
                    print(f"   Message déchiffré: {data.get('decrypted_message')}")
                    self.corrected_endpoints_results["hybrid_decrypt"] = {"status": "success", "message": data.get('decrypted_message')}
                    return True
                else:
                    print(f"❌ Déchiffrement échoué: {data}")
                    self.corrected_endpoints_results["hybrid_decrypt"] = {"status": "failed", "reason": "decrypt_logic_failed", "data": data}
            else:
                print(f"❌ Erreur HTTP {response['status']} (était 500 avant correction)")
                self.corrected_endpoints_results["hybrid_decrypt"] = {"status": "failed", "reason": f"http_{response['status']}", "data": response.get('data')}
        
        except Exception as e:
            print(f"❌ Exception: {e}")
            self.corrected_endpoints_results["hybrid_decrypt"] = {"status": "failed", "reason": "exception", "error": str(e)}
        
        return False

    async def test_security_dashboard_correction(self):
        """Test de la correction du dashboard sécurité (était HTTP 500)"""
        print("\n📊 Test Correction: Dashboard Sécurité...")
        
        try:
            response = await self.make_request("GET", "/security/dashboard", auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("dashboard") and data.get("status") == "success":
                    dashboard = data["dashboard"]
                    print("✅ CORRECTION VALIDÉE: Dashboard sécurité fonctionne")
                    overview = dashboard.get("overview", {})
                    print(f"   Événements (24h): {overview.get('events_last_24h', 0)}")
                    print(f"   Alertes actives: {overview.get('active_alerts', 0)}")
                    print(f"   Score sécurité: {dashboard.get('security_score', 0)}")
                    self.corrected_endpoints_results["security_dashboard"] = {"status": "success", "score": dashboard.get('security_score')}
                    return True
                else:
                    print(f"❌ Dashboard incomplet: {data}")
                    self.corrected_endpoints_results["security_dashboard"] = {"status": "failed", "reason": "incomplete_data", "data": data}
            else:
                print(f"❌ Erreur HTTP {response['status']} (était 500 avant correction)")
                self.corrected_endpoints_results["security_dashboard"] = {"status": "failed", "reason": f"http_{response['status']}", "data": response.get('data')}
        
        except Exception as e:
            print(f"❌ Exception: {e}")
            self.corrected_endpoints_results["security_dashboard"] = {"status": "failed", "reason": "exception", "error": str(e)}
        
        return False

    async def test_zk_proof_generation_correction(self):
        """Test de la correction de génération ZK-proofs (était HTTP 500)"""
        print("\n🔬 Test Correction: Génération ZK-Proofs...")
        
        try:
            # Test des 4 types de preuves ZK implémentées
            proof_types = ["membership", "range", "knowledge", "non_interactive"]
            
            for proof_type in proof_types:
                print(f"   Test preuve {proof_type}...")
                
                zk_request = {
                    "proof_type": proof_type,
                    "statement": f"Test statement for {proof_type} proof",
                    "witness": f"Test witness for {proof_type}",
                    "public_parameters": {"test_param": "value"}
                }
                
                response = await self.make_request("POST", "/advanced-crypto/generate-zk-proof", 
                                                 zk_request, auth_required=True)
                
                if response["status"] == 200:
                    data = response["data"]
                    if data.get("proof_data") and data.get("status") == "success":
                        proof_data = data["proof_data"]
                        print(f"   ✅ Preuve {proof_type} générée: {proof_data.get('proof_id')}")
                    else:
                        print(f"   ❌ Échec génération preuve {proof_type}: {data}")
                        self.corrected_endpoints_results["zk_proof_generation"] = {"status": "failed", "reason": f"{proof_type}_failed", "data": data}
                        return False
                else:
                    print(f"   ❌ Erreur HTTP {response['status']} pour preuve {proof_type}")
                    self.corrected_endpoints_results["zk_proof_generation"] = {"status": "failed", "reason": f"http_{response['status']}_for_{proof_type}"}
                    return False
            
            print("✅ CORRECTION VALIDÉE: Génération ZK-proofs fonctionne pour tous les types")
            self.corrected_endpoints_results["zk_proof_generation"] = {"status": "success", "types_tested": proof_types}
            return True
        
        except Exception as e:
            print(f"❌ Exception: {e}")
            self.corrected_endpoints_results["zk_proof_generation"] = {"status": "failed", "reason": "exception", "error": str(e)}
        
        return False

    async def test_advanced_blockchain_health_correction(self):
        """Test de la correction du health check blockchain avancé (était HTTP 404)"""
        print("\n⛓️ Test Correction: Health Check Blockchain Avancé...")
        
        try:
            response = await self.make_request("GET", "/advanced-blockchain/health", auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if "service_ready" in data or "status" in data:
                    print("✅ CORRECTION VALIDÉE: Health check blockchain avancé fonctionne")
                    print(f"   Status: {data.get('status', 'N/A')}")
                    print(f"   Service Ready: {data.get('service_ready', 'N/A')}")
                    self.corrected_endpoints_results["advanced_blockchain_health"] = {"status": "success", "service_status": data.get('status')}
                    return True
                else:
                    print(f"❌ Réponse incomplète: {data}")
                    self.corrected_endpoints_results["advanced_blockchain_health"] = {"status": "failed", "reason": "incomplete_response", "data": data}
            else:
                print(f"❌ Erreur HTTP {response['status']} (était 404 avant correction)")
                self.corrected_endpoints_results["advanced_blockchain_health"] = {"status": "failed", "reason": f"http_{response['status']}", "data": response.get('data')}
        
        except Exception as e:
            print(f"❌ Exception: {e}")
            self.corrected_endpoints_results["advanced_blockchain_health"] = {"status": "failed", "reason": "exception", "error": str(e)}
        
        return False

    async def test_ota_service_correction(self):
        """Test de la correction du service OTA (était non fonctionnel)"""
        print("\n📡 Test Correction: Service OTA...")
        
        try:
            # Test health check OTA
            response = await self.make_request("GET", "/ota/health")
            
            if response["status"] == 200:
                print("✅ CORRECTION VALIDÉE: Health check OTA fonctionne")
                print(f"   Status: {response['data'].get('status', 'N/A')}")
                
                # Test statistiques OTA
                stats_response = await self.make_request("GET", "/ota/statistics", auth_required=True)
                if stats_response["status"] == 200:
                    print("✅ Statistiques OTA fonctionnelles")
                    stats = stats_response["data"]
                    print(f"   Firmware total: {stats.get('total_firmware', 0)}")
                    print(f"   Mises à jour en attente: {stats.get('pending_updates', 0)}")
                    
                    # Test configuration OTA
                    config_response = await self.make_request("GET", "/ota/config", auth_required=True)
                    if config_response["status"] == 200:
                        print("✅ Configuration OTA accessible")
                        self.corrected_endpoints_results["ota_service"] = {"status": "success", "endpoints_working": ["health", "statistics", "config"]}
                        return True
                    else:
                        print(f"❌ Configuration OTA échouée: {config_response['status']}")
                        self.corrected_endpoints_results["ota_service"] = {"status": "partial", "working": ["health", "statistics"], "failed": ["config"]}
                else:
                    print(f"❌ Statistiques OTA échouées: {stats_response['status']}")
                    self.corrected_endpoints_results["ota_service"] = {"status": "partial", "working": ["health"], "failed": ["statistics"]}
            else:
                print(f"❌ Health check OTA échoué: {response['status']}")
                self.corrected_endpoints_results["ota_service"] = {"status": "failed", "reason": f"health_check_http_{response['status']}"}
        
        except Exception as e:
            print(f"❌ Exception: {e}")
            self.corrected_endpoints_results["ota_service"] = {"status": "failed", "reason": "exception", "error": str(e)}
        
        return False

    async def test_governance_improvements(self):
        """Test des améliorations de gouvernance blockchain"""
        print("\n🏛️ Test Améliorations: Gouvernance Blockchain...")
        
        try:
            # Test création de proposition
            proposal_request = {
                "title": "Test Proposal for Governance Improvement",
                "description": "This is a test proposal to validate governance corrections",
                "proposal_type": "parameter_change",
                "parameters": {
                    "parameter_name": "block_time",
                    "new_value": 15,
                    "current_value": 10
                },
                "voting_period_hours": 168
            }
            
            response = await self.make_request("POST", "/advanced-blockchain/governance/proposals", 
                                             proposal_request, auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("proposal") and data.get("status") == "success":
                    proposal = data["proposal"]
                    proposal_id = proposal.get("proposal_id")
                    print("✅ AMÉLIORATION VALIDÉE: Création de proposition fonctionne")
                    print(f"   Proposition ID: {proposal_id}")
                    print(f"   Titre: {proposal.get('title')}")
                    print(f"   Status: {proposal.get('status')}")
                    
                    # Test vote sur la proposition
                    vote_request = {
                        "vote": "yes",
                        "reason": "Test vote for governance validation"
                    }
                    
                    vote_response = await self.make_request("POST", f"/advanced-blockchain/governance/proposals/{proposal_id}/vote", 
                                                          vote_request, auth_required=True)
                    
                    if vote_response["status"] == 200:
                        print("✅ Vote sur proposition fonctionnel")
                        self.corrected_endpoints_results["governance"] = {"status": "success", "proposal_id": proposal_id}
                        return True
                    else:
                        print(f"❌ Vote échoué: {vote_response['status']}")
                        self.corrected_endpoints_results["governance"] = {"status": "partial", "proposal_created": True, "vote_failed": True}
                else:
                    print(f"❌ Création proposition échouée: {data}")
                    self.corrected_endpoints_results["governance"] = {"status": "failed", "reason": "proposal_creation_failed", "data": data}
            else:
                print(f"❌ Erreur HTTP {response['status']} pour création proposition")
                self.corrected_endpoints_results["governance"] = {"status": "failed", "reason": f"http_{response['status']}", "data": response.get('data')}
        
        except Exception as e:
            print(f"❌ Exception: {e}")
            self.corrected_endpoints_results["governance"] = {"status": "failed", "reason": "exception", "error": str(e)}
        
        return False

    async def test_staking_improvements(self):
        """Test des améliorations de staking"""
        print("\n💰 Test Améliorations: Staking de Tokens...")
        
        try:
            # Test staking de tokens
            stake_request = {
                "amount": 100.0,
                "validator_id": "auto_create",  # Création automatique de validateur
                "lock_period_days": 30
            }
            
            response = await self.make_request("POST", "/advanced-blockchain/consensus/stake", 
                                             stake_request, auth_required=True)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("stake_result") and data.get("status") == "success":
                    stake_result = data["stake_result"]
                    print("✅ AMÉLIORATION VALIDÉE: Staking de tokens fonctionne")
                    print(f"   Montant staké: {stake_result.get('amount')}")
                    print(f"   Validateur: {stake_result.get('validator_id')}")
                    print(f"   Période de verrouillage: {stake_result.get('lock_period_days')} jours")
                    print(f"   Récompenses estimées: {stake_result.get('estimated_rewards', 'N/A')}")
                    self.corrected_endpoints_results["staking"] = {"status": "success", "amount": stake_result.get('amount')}
                    return True
                else:
                    print(f"❌ Staking échoué: {data}")
                    self.corrected_endpoints_results["staking"] = {"status": "failed", "reason": "staking_logic_failed", "data": data}
            else:
                print(f"❌ Erreur HTTP {response['status']} pour staking")
                self.corrected_endpoints_results["staking"] = {"status": "failed", "reason": f"http_{response['status']}", "data": response.get('data')}
        
        except Exception as e:
            print(f"❌ Exception: {e}")
            self.corrected_endpoints_results["staking"] = {"status": "failed", "reason": "exception", "error": str(e)}
        
        return False

    async def run_focused_tests(self):
        """Exécute tous les tests ciblés sur les corrections"""
        print("🎯 DÉBUT DES TESTS CIBLÉS SUR LES CORRECTIONS QUANTUMSHIELD")
        print("=" * 70)
        
        await self.setup()
        
        # Configuration préalable
        if not await self.setup_auth():
            print("❌ Impossible de configurer l'authentification")
            return
        
        if not await self.setup_crypto_keypair():
            print("❌ Impossible de configurer les clés crypto")
            return
        
        # Tests des corrections spécifiques
        print("\n🔧 TESTS DES CORRECTIONS APPLIQUÉES:")
        print("-" * 50)
        
        await self.test_hybrid_decrypt_correction()
        await self.test_security_dashboard_correction()
        await self.test_zk_proof_generation_correction()
        await self.test_advanced_blockchain_health_correction()
        await self.test_ota_service_correction()
        await self.test_governance_improvements()
        await self.test_staking_improvements()
        
        await self.cleanup()
        
        # Rapport final
        self.print_correction_report()

    def print_correction_report(self):
        """Affiche le rapport des corrections testées"""
        print("\n" + "=" * 70)
        print("📊 RAPPORT DES CORRECTIONS TESTÉES")
        print("=" * 70)
        
        total_tests = len(self.corrected_endpoints_results)
        successful_tests = sum(1 for result in self.corrected_endpoints_results.values() if result["status"] == "success")
        partial_tests = sum(1 for result in self.corrected_endpoints_results.values() if result["status"] == "partial")
        failed_tests = sum(1 for result in self.corrected_endpoints_results.values() if result["status"] == "failed")
        
        print(f"📈 TAUX DE RÉUSSITE DES CORRECTIONS: {successful_tests}/{total_tests} ({(successful_tests/total_tests)*100:.1f}%)")
        print(f"✅ Corrections validées: {successful_tests}")
        print(f"⚠️ Corrections partielles: {partial_tests}")
        print(f"❌ Corrections échouées: {failed_tests}")
        
        print("\n🔍 DÉTAIL PAR CORRECTION:")
        for endpoint, result in self.corrected_endpoints_results.items():
            status_icon = "✅" if result["status"] == "success" else "⚠️" if result["status"] == "partial" else "❌"
            print(f"{status_icon} {endpoint}: {result['status']}")
            if result["status"] == "failed" and "reason" in result:
                print(f"   Raison: {result['reason']}")
        
        print("\n🎯 RECOMMANDATIONS:")
        if successful_tests == total_tests:
            print("✅ Toutes les corrections sont validées et fonctionnelles!")
            print("✅ Le taux de réussite du backend devrait être significativement amélioré")
        elif successful_tests > failed_tests:
            print("⚠️ La majorité des corrections fonctionnent, mais quelques problèmes persistent")
            print("🔧 Concentrer les efforts sur les corrections échouées")
        else:
            print("❌ Plusieurs corrections nécessitent encore du travail")
            print("🔧 Réviser l'implémentation des endpoints échoués")

async def main():
    """Point d'entrée principal"""
    tester = FocusedQuantumShieldTester()
    await tester.run_focused_tests()

if __name__ == "__main__":
    asyncio.run(main())
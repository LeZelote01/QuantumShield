#!/usr/bin/env python3
"""
Test simple pour QuantumShield - Focus sur les endpoints publics et health checks
Évite les problèmes de rate limiting en testant d'abord les endpoints publics
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

class SimpleQuantumShieldTester:
    def __init__(self):
        self.session = None
        self.test_results = {}

    async def setup(self):
        """Initialise la session HTTP"""
        self.session = aiohttp.ClientSession()
        print("🔧 Session HTTP initialisée pour tests simples")

    async def cleanup(self):
        """Nettoie les ressources"""
        if self.session:
            await self.session.close()
        print("🧹 Nettoyage terminé")

    async def make_request(self, method: str, endpoint: str, data: Dict = None, 
                          headers: Dict = None) -> Dict:
        """Effectue une requête HTTP avec gestion d'erreurs"""
        url = f"{API_BASE}{endpoint}"
        
        # Headers par défaut
        request_headers = {"Content-Type": "application/json"}
        if headers:
            request_headers.update(headers)
        
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

    # ===== TESTS DES ENDPOINTS PUBLICS =====
    
    async def test_health_check(self):
        """Test du health check général"""
        print("\n🏥 Test Health Check...")
        
        response = await self.make_request("GET", "/health")
        
        print(f"   Status: {response['status']}")
        if response["status"] == 200:
            data = response["data"]
            print(f"   Services Status: {data.get('status')}")
            services = data.get('services', {})
            print(f"   Total Services: {len(services)}")
            
            # Compter les services fonctionnels
            working_services = sum(1 for status in services.values() if status)
            print(f"   Working Services: {working_services}/{len(services)}")
            
            self.test_results["health_check"] = {
                "status": response["status"],
                "working": response["status"] == 200,
                "services_count": len(services),
                "working_services": working_services
            }
            print("✅ Health check working")
            return True
        else:
            print(f"❌ Health check failed with status {response['status']}")
            self.test_results["health_check"] = {
                "status": response["status"],
                "working": False,
                "error": response.get("error") or response["data"]
            }
            return False

    async def test_advanced_blockchain_health(self):
        """Test du health check blockchain avancé (erreur HTTP 404 connue)"""
        print("\n🏥 Test Advanced Blockchain Health (HTTP 404)...")
        
        response = await self.make_request("GET", "/advanced-blockchain/health")
        
        print(f"   Status: {response['status']}")
        print(f"   Response: {response['data']}")
        
        self.test_results["advanced_blockchain_health"] = {
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

    async def test_security_health(self):
        """Test du health check sécurité"""
        print("\n🛡️ Test Security Health...")
        
        response = await self.make_request("GET", "/security/health")
        
        print(f"   Status: {response['status']}")
        print(f"   Response: {response['data']}")
        
        self.test_results["security_health"] = {
            "status": response["status"],
            "working": response["status"] == 200,
            "error": response.get("error") or response["data"] if response["status"] != 200 else None
        }
        
        if response["status"] == 200:
            print("✅ Security health working")
            return True
        else:
            print(f"❌ Security health failed with status {response['status']}")
            return False

    async def test_iot_protocol_health(self):
        """Test du health check IoT Protocol"""
        print("\n📡 Test IoT Protocol Health...")
        
        response = await self.make_request("GET", "/iot-protocol/health")
        
        print(f"   Status: {response['status']}")
        print(f"   Response: {response['data']}")
        
        self.test_results["iot_protocol_health"] = {
            "status": response["status"],
            "working": response["status"] == 200,
            "error": response.get("error") or response["data"] if response["status"] != 200 else None
        }
        
        if response["status"] == 200:
            print("✅ IoT Protocol health working")
            return True
        else:
            print(f"❌ IoT Protocol health failed with status {response['status']}")
            return False

    async def test_ota_health(self):
        """Test du health check OTA"""
        print("\n📦 Test OTA Health...")
        
        response = await self.make_request("GET", "/ota/health")
        
        print(f"   Status: {response['status']}")
        print(f"   Response: {response['data']}")
        
        self.test_results["ota_health"] = {
            "status": response["status"],
            "working": response["status"] == 200,
            "error": response.get("error") or response["data"] if response["status"] != 200 else None
        }
        
        if response["status"] == 200:
            print("✅ OTA health working")
            return True
        else:
            print(f"❌ OTA health failed with status {response['status']}")
            return False

    async def test_advanced_crypto_supported_algorithms(self):
        """Test des algorithmes supportés (endpoint public)"""
        print("\n🔬 Test Advanced Crypto Supported Algorithms...")
        
        response = await self.make_request("GET", "/advanced-crypto/supported-algorithms")
        
        print(f"   Status: {response['status']}")
        if response["status"] == 200:
            data = response["data"]
            algorithms = data.get("algorithms", {})
            print(f"   Available algorithms: {len(algorithms)}")
            for alg_name in list(algorithms.keys())[:3]:  # Show first 3
                print(f"   - {alg_name}")
            
            self.test_results["advanced_crypto_algorithms"] = {
                "status": response["status"],
                "working": True,
                "algorithms_count": len(algorithms)
            }
            print("✅ Advanced crypto algorithms working")
            return True
        else:
            print(f"   Response: {response['data']}")
            self.test_results["advanced_crypto_algorithms"] = {
                "status": response["status"],
                "working": False,
                "error": response.get("error") or response["data"]
            }
            print(f"❌ Advanced crypto algorithms failed with status {response['status']}")
            return False

    async def test_advanced_crypto_performance_comparison(self):
        """Test de comparaison des performances (endpoint public)"""
        print("\n📈 Test Advanced Crypto Performance Comparison...")
        
        response = await self.make_request("GET", "/advanced-crypto/performance-comparison")
        
        print(f"   Status: {response['status']}")
        if response["status"] == 200:
            data = response["data"]
            comparison = data.get("performance_comparison", {})
            algorithms = comparison.get("algorithms", {})
            print(f"   Performance data for {len(algorithms)} algorithms")
            
            self.test_results["advanced_crypto_performance"] = {
                "status": response["status"],
                "working": True,
                "algorithms_count": len(algorithms)
            }
            print("✅ Advanced crypto performance working")
            return True
        else:
            print(f"   Response: {response['data']}")
            self.test_results["advanced_crypto_performance"] = {
                "status": response["status"],
                "working": False,
                "error": response.get("error") or response["data"]
            }
            print(f"❌ Advanced crypto performance failed with status {response['status']}")
            return False

    async def test_iot_protocol_status(self):
        """Test du statut des protocoles IoT (endpoint public)"""
        print("\n📡 Test IoT Protocol Status...")
        
        response = await self.make_request("GET", "/iot-protocol/protocols/status")
        
        print(f"   Status: {response['status']}")
        if response["status"] == 200:
            data = response["data"]
            protocols = data.get("protocols", {})
            print(f"   Available protocols: {len(protocols)}")
            for protocol, status in protocols.items():
                enabled = status.get('enabled', False)
                print(f"   - {protocol}: {'enabled' if enabled else 'disabled'}")
            
            self.test_results["iot_protocol_status"] = {
                "status": response["status"],
                "working": True,
                "protocols_count": len(protocols)
            }
            print("✅ IoT Protocol status working")
            return True
        else:
            print(f"   Response: {response['data']}")
            self.test_results["iot_protocol_status"] = {
                "status": response["status"],
                "working": False,
                "error": response.get("error") or response["data"]
            }
            print(f"❌ IoT Protocol status failed with status {response['status']}")
            return False

    async def run_all_simple_tests(self):
        """Exécute tous les tests simples"""
        print("🎯 DÉBUT DES TESTS SIMPLES QUANTUMSHIELD")
        print("=" * 60)
        
        # Tests des health checks
        print("\n🏥 TESTS DES HEALTH CHECKS")
        print("-" * 40)
        await self.test_health_check()
        await self.test_advanced_blockchain_health()
        await self.test_security_health()
        await self.test_iot_protocol_health()
        await self.test_ota_health()
        
        # Tests des endpoints publics
        print("\n🔓 TESTS DES ENDPOINTS PUBLICS")
        print("-" * 40)
        await self.test_advanced_crypto_supported_algorithms()
        await self.test_advanced_crypto_performance_comparison()
        await self.test_iot_protocol_status()
        
        # Résumé des résultats
        self.print_simple_summary()

    def print_simple_summary(self):
        """Affiche un résumé des tests simples"""
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES TESTS SIMPLES")
        print("=" * 60)
        
        working_count = 0
        total_count = len(self.test_results)
        
        # Health checks
        print("\n🏥 HEALTH CHECKS:")
        health_tests = ["health_check", "advanced_blockchain_health", "security_health", "iot_protocol_health", "ota_health"]
        for test in health_tests:
            if test in self.test_results:
                result = self.test_results[test]
                status = "✅ FONCTIONNEL" if result["working"] else f"❌ ÉCHEC ({result['status']})"
                print(f"   - {test}: {status}")
                if result["working"]:
                    working_count += 1
        
        # Endpoints publics
        print("\n🔓 ENDPOINTS PUBLICS:")
        public_tests = ["advanced_crypto_algorithms", "advanced_crypto_performance", "iot_protocol_status"]
        for test in public_tests:
            if test in self.test_results:
                result = self.test_results[test]
                status = "✅ FONCTIONNEL" if result["working"] else f"❌ ÉCHEC ({result['status']})"
                print(f"   - {test}: {status}")
                if result["working"]:
                    working_count += 1
        
        # Statistiques finales
        success_rate = (working_count / total_count * 100) if total_count > 0 else 0
        print(f"\n📈 TAUX DE RÉUSSITE: {working_count}/{total_count} ({success_rate:.1f}%)")
        
        # Analyse des problèmes
        print("\n🔍 ANALYSE DES PROBLÈMES:")
        failed_tests = [test for test, result in self.test_results.items() if not result["working"]]
        if failed_tests:
            print(f"   Tests échoués: {len(failed_tests)}")
            for test in failed_tests:
                result = self.test_results[test]
                print(f"   - {test}: HTTP {result['status']}")
                if result.get("error"):
                    error_msg = str(result["error"])
                    if len(error_msg) > 100:
                        error_msg = error_msg[:100] + "..."
                    print(f"     Erreur: {error_msg}")
        else:
            print("   Aucun problème détecté dans les tests simples!")
        
        print("\n" + "=" * 60)

async def main():
    """Fonction principale"""
    tester = SimpleQuantumShieldTester()
    
    try:
        await tester.setup()
        await tester.run_all_simple_tests()
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
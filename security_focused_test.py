#!/usr/bin/env python3
"""
Test focalisé sur le service de sécurité QuantumShield
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Configuration des tests
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

class SecurityTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user = {
            "username": f"security_tester_{datetime.now().strftime('%H%M%S')}",
            "email": f"security_{datetime.now().strftime('%H%M%S')}@quantumshield.com",
            "password": "SecurePassword123!"
        }

    async def setup(self):
        """Initialise la session HTTP"""
        self.session = aiohttp.ClientSession()
        print("🔧 Session HTTP initialisée")

    async def cleanup(self):
        """Nettoie les ressources"""
        if self.session:
            await self.session.close()
        print("🧹 Nettoyage terminé")

    async def make_request(self, method: str, endpoint: str, data: dict = None, 
                          headers: dict = None, auth_required: bool = False) -> dict:
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
        except Exception as e:
            return {"status": 500, "error": str(e)}

    async def authenticate(self):
        """Authentifie l'utilisateur de test"""
        print("\n🔐 Authentification...")
        
        # Register user
        response = await self.make_request("POST", "/auth/register", self.test_user)
        if response["status"] != 200:
            print(f"❌ Registration failed: {response}")
            return False
        
        # Login
        login_data = {
            "username": self.test_user["username"],
            "password": self.test_user["password"]
        }
        response = await self.make_request("POST", "/auth/login", login_data)
        if response["status"] == 200:
            self.auth_token = response["data"].get("token")
            print("✅ Authentication successful")
            return True
        else:
            print(f"❌ Login failed: {response}")
            return False

    async def test_security_health(self):
        """Test de santé du service de sécurité"""
        print("\n🏥 Test Security Health Check...")
        
        try:
            response = await self.make_request("GET", "/security/health")
            
            if response["status"] == 200:
                data = response["data"]
                print("✅ Security health check successful")
                print(f"   Service Ready: {data.get('service_ready')}")
                print(f"   Status: {data.get('status')}")
                return True
            else:
                print(f"❌ Security health check HTTP error: {response['status']}")
                print(f"   Response: {response.get('data', {})}")
        except Exception as e:
            print(f"❌ Security health check exception: {e}")
        
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
                    return True
                else:
                    print(f"❌ Security dashboard failed: {data}")
            else:
                print(f"❌ Security dashboard HTTP error: {response['status']}")
                print(f"   Response: {response.get('data', {})}")
        except Exception as e:
            print(f"❌ Security dashboard exception: {e}")
        
        return False

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
                    return True
                else:
                    print(f"❌ MFA setup failed: {data}")
            else:
                print(f"❌ MFA setup HTTP error: {response['status']}")
                print(f"   Response: {response.get('data', {})}")
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
                    return True
                else:
                    print(f"❌ MFA status failed: {data}")
            else:
                print(f"❌ MFA status HTTP error: {response['status']}")
                print(f"   Response: {response.get('data', {})}")
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
                    return True
                else:
                    print(f"❌ Behavior analysis failed: {data}")
            else:
                print(f"❌ Behavior analysis HTTP error: {response['status']}")
                print(f"   Response: {response.get('data', {})}")
        except Exception as e:
            print(f"❌ Behavior analysis exception: {e}")
        
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
                    return True
                else:
                    print(f"❌ Security recommendations failed: {data}")
            else:
                print(f"❌ Security recommendations HTTP error: {response['status']}")
                print(f"   Response: {response.get('data', {})}")
        except Exception as e:
            print(f"❌ Security recommendations exception: {e}")
        
        return False

    async def test_advanced_security_features(self):
        """Test des fonctionnalités avancées de sécurité"""
        print("\n🔒 Test Advanced Security Features...")
        
        # Test honeypots
        print("\n🍯 Testing Honeypots...")
        try:
            response = await self.make_request("GET", "/security/honeypots/status", auth_required=True)
            if response["status"] == 200:
                print("✅ Honeypots endpoint accessible")
            else:
                print(f"❌ Honeypots endpoint not available: {response['status']}")
        except Exception as e:
            print(f"❌ Honeypots test exception: {e}")

        # Test backup avancé
        print("\n💾 Testing Advanced Backup...")
        try:
            response = await self.make_request("GET", "/security/backup/status", auth_required=True)
            if response["status"] == 200:
                print("✅ Advanced backup endpoint accessible")
            else:
                print(f"❌ Advanced backup endpoint not available: {response['status']}")
        except Exception as e:
            print(f"❌ Advanced backup test exception: {e}")

        # Test conformité GDPR/CCPA
        print("\n📋 Testing GDPR/CCPA Compliance...")
        try:
            response = await self.make_request("GET", "/security/compliance/gdpr/report", auth_required=True)
            if response["status"] == 200:
                print("✅ GDPR compliance endpoint accessible")
            else:
                print(f"❌ GDPR compliance endpoint not available: {response['status']}")
        except Exception as e:
            print(f"❌ GDPR compliance test exception: {e}")

        try:
            response = await self.make_request("GET", "/security/compliance/ccpa/report", auth_required=True)
            if response["status"] == 200:
                print("✅ CCPA compliance endpoint accessible")
            else:
                print(f"❌ CCPA compliance endpoint not available: {response['status']}")
        except Exception as e:
            print(f"❌ CCPA compliance test exception: {e}")

    async def run_security_tests(self):
        """Exécute tous les tests de sécurité"""
        print("🔒 Démarrage des tests de sécurité QuantumShield")
        print("=" * 60)
        
        await self.setup()
        
        # Authentification
        if not await self.authenticate():
            print("❌ Authentication failed, stopping tests")
            return
        
        # Tests de sécurité
        test_functions = [
            self.test_security_health,
            self.test_security_dashboard,
            self.test_security_mfa_setup,
            self.test_security_mfa_status,
            self.test_security_behavior_analysis,
            self.test_security_recommendations,
            self.test_advanced_security_features
        ]
        
        results = {}
        for test_func in test_functions:
            try:
                result = await test_func()
                results[test_func.__name__] = result
                await asyncio.sleep(0.5)  # Pause entre les tests
            except Exception as e:
                print(f"❌ Test {test_func.__name__} failed with exception: {e}")
                results[test_func.__name__] = False
        
        await self.cleanup()
        
        # Résumé
        print("\n" + "=" * 60)
        print("📋 RÉSUMÉ DES TESTS DE SÉCURITÉ")
        print("=" * 60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:35} {status}")
        
        print("-" * 60)
        print(f"TOTAL: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")

async def main():
    tester = SecurityTester()
    await tester.run_security_tests()

if __name__ == "__main__":
    asyncio.run(main())
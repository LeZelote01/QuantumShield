#!/usr/bin/env python3
"""
Test des nouvelles fonctionnalités QuantumShield
- Routes ERP/CRM complètes
- Intégrations cloud  
- Conformité réglementaire
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

class NewFeaturesTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user = {
            "username": "quantum_new_tester",
            "email": "newtester@quantumshield.com", 
            "password": "SecurePassword123!"
        }
        self.test_results = {
            # Health check with new services
            "health_check_new_services": False,
            
            # ERP/CRM Tests
            "erp_crm_supported_systems": False,
            "erp_crm_sap_connect": False,
            "erp_crm_salesforce_connect": False,
            "erp_crm_oracle_connect": False,
            "erp_crm_dynamics_connect": False,
            "erp_crm_sync_data": False,
            
            # Cloud Integrations Tests
            "cloud_providers": False,
            "cloud_aws_services": False,
            "cloud_azure_services": False,
            "cloud_gcp_services": False,
            "cloud_configure_aws": False,
            "cloud_configure_azure": False,
            "cloud_configure_gcp": False,
            
            # Compliance Tests
            "compliance_user_rights": False,
            "compliance_gdpr_status": False,
            "compliance_ccpa_status": False,
            "compliance_pipeda_status": False,
            "compliance_lgpd_status": False,
            "compliance_data_export": False,
            "compliance_data_deletion": False,
            "compliance_audit_log": False,
        }

    async def setup_session(self):
        """Initialise la session HTTP"""
        self.session = aiohttp.ClientSession()
        print("✅ Session HTTP initialisée")

    async def cleanup_session(self):
        """Nettoie la session HTTP"""
        if self.session:
            await self.session.close()
        print("✅ Session HTTP fermée")

    async def register_and_login(self):
        """Enregistre et connecte un utilisateur de test"""
        try:
            # Enregistrement
            register_data = {
                "username": self.test_user["username"],
                "email": self.test_user["email"],
                "password": self.test_user["password"]
            }
            
            async with self.session.post(f"{API_BASE}/auth/register", json=register_data) as response:
                if response.status == 200:
                    print("✅ Utilisateur enregistré avec succès")
                else:
                    print(f"⚠️ Enregistrement échoué (peut-être déjà existant): {response.status}")

            # Connexion
            login_data = {
                "username": self.test_user["username"],
                "password": self.test_user["password"]
            }
            
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                if response.status == 200:
                    result = await response.json()
                    self.auth_token = result.get("access_token")
                    print("✅ Connexion réussie, token obtenu")
                    return True
                else:
                    print(f"❌ Connexion échouée: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ Erreur lors de l'authentification: {e}")
            return False

    def get_auth_headers(self):
        """Retourne les headers d'authentification"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}

    async def test_health_check_new_services(self):
        """Test du health check avec les nouveaux services"""
        try:
            async with self.session.get(f"{API_BASE}/health") as response:
                if response.status == 200:
                    result = await response.json()
                    services = result.get("services", {})
                    
                    # Vérifier les nouveaux services
                    new_services = ["cloud_integrations", "erp_crm", "compliance"]
                    all_present = all(service in services for service in new_services)
                    
                    if all_present:
                        print("✅ Health check - Tous les nouveaux services sont présents")
                        print(f"   - Cloud Integrations: {services.get('cloud_integrations')}")
                        print(f"   - ERP/CRM: {services.get('erp_crm')}")
                        print(f"   - Compliance: {services.get('compliance')}")
                        self.test_results["health_check_new_services"] = True
                    else:
                        print("❌ Health check - Services manquants")
                        print(f"   Services disponibles: {list(services.keys())}")
                else:
                    print(f"❌ Health check échoué: {response.status}")
        except Exception as e:
            print(f"❌ Erreur health check: {e}")

    # ERP/CRM Tests
    async def test_erp_crm_supported_systems(self):
        """Test des systèmes ERP/CRM supportés"""
        try:
            async with self.session.get(f"{API_BASE}/erp-crm/supported-systems", 
                                      headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    result = await response.json()
                    systems = result.get("systems", [])
                    expected_systems = ["SAP", "Salesforce", "Oracle", "Microsoft Dynamics"]
                    
                    if any(sys in str(systems) for sys in expected_systems):
                        print(f"✅ ERP/CRM - Systèmes supportés: {systems}")
                        self.test_results["erp_crm_supported_systems"] = True
                    else:
                        print(f"❌ ERP/CRM - Systèmes attendus non trouvés: {systems}")
                else:
                    print(f"❌ ERP/CRM supported systems échoué: {response.status}")
                    if response.status == 404:
                        print("   Endpoint non trouvé - service non implémenté")
        except Exception as e:
            print(f"❌ Erreur ERP/CRM supported systems: {e}")

    async def test_erp_crm_connections(self):
        """Test des connexions ERP/CRM"""
        systems = ["sap", "salesforce", "oracle", "dynamics"]
        
        for system in systems:
            try:
                test_config = {
                    "system_type": system,
                    "connection_string": f"test_{system}_connection",
                    "credentials": {
                        "username": f"test_{system}_user",
                        "password": "test_password"
                    }
                }
                
                async with self.session.post(f"{API_BASE}/erp-crm/connect", 
                                           json=test_config,
                                           headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ ERP/CRM - Connexion {system.upper()} réussie")
                        self.test_results[f"erp_crm_{system}_connect"] = True
                    else:
                        print(f"❌ ERP/CRM - Connexion {system.upper()} échouée: {response.status}")
                        
            except Exception as e:
                print(f"❌ Erreur connexion {system.upper()}: {e}")

    async def test_erp_crm_sync_data(self):
        """Test de synchronisation des données ERP/CRM"""
        try:
            sync_config = {
                "system": "sap",
                "data_types": ["customers", "products", "orders"],
                "sync_mode": "incremental"
            }
            
            async with self.session.post(f"{API_BASE}/erp-crm/sync", 
                                       json=sync_config,
                                       headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ ERP/CRM - Synchronisation des données réussie")
                    self.test_results["erp_crm_sync_data"] = True
                else:
                    print(f"❌ ERP/CRM - Synchronisation échouée: {response.status}")
        except Exception as e:
            print(f"❌ Erreur synchronisation ERP/CRM: {e}")

    # Cloud Integrations Tests
    async def test_cloud_providers(self):
        """Test des fournisseurs cloud supportés"""
        try:
            async with self.session.get(f"{API_BASE}/cloud-integrations/providers",
                                      headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    result = await response.json()
                    providers = result.get("providers", [])
                    expected_providers = ["AWS", "Azure", "GCP"]
                    
                    if any(provider in str(providers) for provider in expected_providers):
                        print(f"✅ Cloud - Fournisseurs supportés: {providers}")
                        self.test_results["cloud_providers"] = True
                    else:
                        print(f"❌ Cloud - Fournisseurs attendus non trouvés: {providers}")
                else:
                    print(f"❌ Cloud providers échoué: {response.status}")
        except Exception as e:
            print(f"❌ Erreur cloud providers: {e}")

    async def test_cloud_services(self):
        """Test des services cloud par fournisseur"""
        providers = ["aws", "azure", "gcp"]
        
        for provider in providers:
            try:
                async with self.session.get(f"{API_BASE}/cloud-integrations/{provider}/services",
                                          headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        result = await response.json()
                        services = result.get("services", [])
                        print(f"✅ Cloud - Services {provider.upper()}: {len(services)} services disponibles")
                        self.test_results[f"cloud_{provider}_services"] = True
                    else:
                        print(f"❌ Cloud services {provider.upper()} échoué: {response.status}")
            except Exception as e:
                print(f"❌ Erreur services {provider.upper()}: {e}")

    async def test_cloud_configuration(self):
        """Test de configuration des fournisseurs cloud"""
        providers = ["aws", "azure", "gcp"]
        
        for provider in providers:
            try:
                config = {
                    "provider": provider,
                    "credentials": {
                        "access_key": f"test_{provider}_key",
                        "secret_key": f"test_{provider}_secret"
                    },
                    "region": "us-east-1" if provider == "aws" else "eastus" if provider == "azure" else "us-central1"
                }
                
                async with self.session.post(f"{API_BASE}/cloud-integrations/configure",
                                           json=config,
                                           headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print(f"✅ Cloud - Configuration {provider.upper()} réussie")
                        self.test_results[f"cloud_configure_{provider}"] = True
                    else:
                        print(f"❌ Cloud configuration {provider.upper()} échouée: {response.status}")
            except Exception as e:
                print(f"❌ Erreur configuration {provider.upper()}: {e}")

    # Compliance Tests
    async def test_compliance_user_rights(self):
        """Test des droits utilisateur en conformité"""
        try:
            async with self.session.get(f"{API_BASE}/compliance/user-rights",
                                      headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    result = await response.json()
                    rights = result.get("rights", [])
                    print(f"✅ Compliance - Droits utilisateur: {rights}")
                    self.test_results["compliance_user_rights"] = True
                else:
                    print(f"❌ Compliance user rights échoué: {response.status}")
        except Exception as e:
            print(f"❌ Erreur compliance user rights: {e}")

    async def test_compliance_regulations(self):
        """Test du statut des réglementations"""
        regulations = ["gdpr", "ccpa", "pipeda", "lgpd"]
        
        for regulation in regulations:
            try:
                async with self.session.get(f"{API_BASE}/compliance/{regulation}/status",
                                          headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        result = await response.json()
                        status = result.get("status", "unknown")
                        print(f"✅ Compliance - {regulation.upper()} status: {status}")
                        self.test_results[f"compliance_{regulation}_status"] = True
                    else:
                        print(f"❌ Compliance {regulation.upper()} status échoué: {response.status}")
            except Exception as e:
                print(f"❌ Erreur compliance {regulation.upper()}: {e}")

    async def test_compliance_data_operations(self):
        """Test des opérations de données pour la conformité"""
        try:
            # Test export de données
            export_request = {
                "user_id": self.test_user["username"],
                "data_types": ["personal", "usage", "preferences"]
            }
            
            async with self.session.post(f"{API_BASE}/compliance/data-export",
                                       json=export_request,
                                       headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    print("✅ Compliance - Export de données réussi")
                    self.test_results["compliance_data_export"] = True
                else:
                    print(f"❌ Compliance data export échoué: {response.status}")

            # Test suppression de données
            deletion_request = {
                "user_id": self.test_user["username"],
                "data_types": ["cache", "temporary"]
            }
            
            async with self.session.post(f"{API_BASE}/compliance/data-deletion",
                                       json=deletion_request,
                                       headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    print("✅ Compliance - Suppression de données réussie")
                    self.test_results["compliance_data_deletion"] = True
                else:
                    print(f"❌ Compliance data deletion échoué: {response.status}")

        except Exception as e:
            print(f"❌ Erreur compliance data operations: {e}")

    async def test_compliance_audit_log(self):
        """Test du journal d'audit de conformité"""
        try:
            async with self.session.get(f"{API_BASE}/compliance/audit-log",
                                      headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    result = await response.json()
                    logs = result.get("logs", [])
                    print(f"✅ Compliance - Journal d'audit: {len(logs)} entrées")
                    self.test_results["compliance_audit_log"] = True
                else:
                    print(f"❌ Compliance audit log échoué: {response.status}")
        except Exception as e:
            print(f"❌ Erreur compliance audit log: {e}")

    async def run_all_tests(self):
        """Exécute tous les tests des nouvelles fonctionnalités"""
        print("🚀 Démarrage des tests des nouvelles fonctionnalités QuantumShield")
        print("=" * 70)
        
        await self.setup_session()
        
        # Authentification
        if not await self.register_and_login():
            print("❌ Impossible de s'authentifier, arrêt des tests")
            await self.cleanup_session()
            return self.test_results
        
        print("\n📊 Test du Health Check avec nouveaux services")
        print("-" * 50)
        await self.test_health_check_new_services()
        
        print("\n🏢 Tests ERP/CRM")
        print("-" * 50)
        await self.test_erp_crm_supported_systems()
        await self.test_erp_crm_connections()
        await self.test_erp_crm_sync_data()
        
        print("\n☁️ Tests Cloud Integrations")
        print("-" * 50)
        await self.test_cloud_providers()
        await self.test_cloud_services()
        await self.test_cloud_configuration()
        
        print("\n📋 Tests Compliance")
        print("-" * 50)
        await self.test_compliance_user_rights()
        await self.test_compliance_regulations()
        await self.test_compliance_data_operations()
        await self.test_compliance_audit_log()
        
        await self.cleanup_session()
        
        # Résumé des résultats
        print("\n" + "=" * 70)
        print("📊 RÉSUMÉ DES TESTS DES NOUVELLES FONCTIONNALITÉS")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"Tests réussis: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print()
        
        # Détail par catégorie
        categories = {
            "Health Check": ["health_check_new_services"],
            "ERP/CRM": [k for k in self.test_results.keys() if k.startswith("erp_crm")],
            "Cloud Integrations": [k for k in self.test_results.keys() if k.startswith("cloud")],
            "Compliance": [k for k in self.test_results.keys() if k.startswith("compliance")]
        }
        
        for category, tests in categories.items():
            passed = sum(1 for test in tests if self.test_results[test])
            total = len(tests)
            rate = (passed / total) * 100 if total > 0 else 0
            status = "✅" if rate == 100 else "⚠️" if rate >= 50 else "❌"
            print(f"{status} {category}: {passed}/{total} ({rate:.1f}%)")
        
        print("\n🔍 Tests échoués:")
        failed_tests = [test for test, result in self.test_results.items() if not result]
        if failed_tests:
            for test in failed_tests:
                print(f"  ❌ {test}")
        else:
            print("  Aucun test échoué! 🎉")
        
        return self.test_results

async def main():
    """Point d'entrée principal"""
    tester = NewFeaturesTester()
    results = await tester.run_all_tests()
    
    # Code de sortie basé sur les résultats
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    success_rate = (passed_tests / total_tests) * 100
    
    if success_rate >= 80:
        print(f"\n🎉 Tests réussis avec un taux de succès de {success_rate:.1f}%")
        return 0
    elif success_rate >= 50:
        print(f"\n⚠️ Tests partiellement réussis avec un taux de succès de {success_rate:.1f}%")
        return 1
    else:
        print(f"\n❌ Tests majoritairement échoués avec un taux de succès de {success_rate:.1f}%")
        return 2

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
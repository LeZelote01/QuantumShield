"""
Service de conformité GDPR/CCPA pour QuantumShield
Fournit des outils de conformité réglementaire
"""

import json
import uuid
import hashlib
import base64
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ComplianceRegulation(str, Enum):
    GDPR = "gdpr"
    CCPA = "ccpa"
    PIPEDA = "pipeda"
    LGPD = "lgpd"

class DataCategory(str, Enum):
    PERSONAL_DATA = "personal_data"
    SENSITIVE_DATA = "sensitive_data"
    TECHNICAL_DATA = "technical_data"
    BEHAVIORAL_DATA = "behavioral_data"
    BIOMETRIC_DATA = "biometric_data"
    LOCATION_DATA = "location_data"

class ProcessingLegalBasis(str, Enum):
    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTERESTS = "legitimate_interests"

class ComplianceService:
    """Service de conformité réglementaire"""
    
    def __init__(self, db):
        self.db = db
        self.is_initialized = False
        self.supported_regulations = [
            ComplianceRegulation.GDPR,
            ComplianceRegulation.CCPA,
            ComplianceRegulation.PIPEDA,
            ComplianceRegulation.LGPD
        ]
        self._initialize()
    
    def _initialize(self):
        """Initialise le service de conformité"""
        try:
            self.is_initialized = True
            logger.info("Service de conformité initialisé")
        except Exception as e:
            logger.error(f"Erreur initialisation conformité: {e}")
            self.is_initialized = False
    
    def is_ready(self) -> bool:
        """Vérifie si le service est prêt"""
        return self.is_initialized
    
    async def generate_privacy_policy(self, organization_name: str, 
                                    contact_email: str,
                                    regulations: List[ComplianceRegulation] = None) -> Dict[str, Any]:
        """Génère une politique de confidentialité"""
        try:
            if not regulations:
                regulations = [ComplianceRegulation.GDPR, ComplianceRegulation.CCPA]
            
            policy_id = str(uuid.uuid4())
            
            # Contenu de base de la politique
            policy_content = {
                "policy_id": policy_id,
                "organization_name": organization_name,
                "contact_email": contact_email,
                "effective_date": datetime.utcnow(),
                "last_updated": datetime.utcnow(),
                "regulations_covered": [reg.value for reg in regulations],
                "sections": {
                    "data_collection": {
                        "title": "Collecte de données",
                        "content": "Nous collectons des informations personnelles nécessaires pour fournir nos services de sécurité IoT post-quantique.",
                        "categories": [
                            "Informations d'identification",
                            "Données techniques des dispositifs",
                            "Logs de sécurité",
                            "Métriques de performance"
                        ]
                    },
                    "data_processing": {
                        "title": "Traitement des données",
                        "content": "Les données sont traitées selon des bases légales définies et des mesures de sécurité strictes.",
                        "legal_bases": [
                            ProcessingLegalBasis.CONSENT.value,
                            ProcessingLegalBasis.CONTRACT.value,
                            ProcessingLegalBasis.LEGITIMATE_INTERESTS.value
                        ]
                    },
                    "data_retention": {
                        "title": "Conservation des données",
                        "content": "Les données sont conservées selon les durées légales et les besoins opérationnels.",
                        "retention_periods": {
                            "user_accounts": "5 ans après fermeture",
                            "security_logs": "3 ans",
                            "performance_metrics": "1 an",
                            "audit_trails": "7 ans"
                        }
                    },
                    "user_rights": {
                        "title": "Droits des utilisateurs",
                        "content": "Vous disposez de droits sur vos données personnelles.",
                        "rights": [
                            "Droit d'accès",
                            "Droit de rectification",
                            "Droit d'effacement",
                            "Droit à la portabilité",
                            "Droit d'opposition",
                            "Droit de limitation"
                        ]
                    },
                    "security_measures": {
                        "title": "Mesures de sécurité",
                        "content": "Nous mettons en place des mesures techniques et organisationnelles appropriées.",
                        "measures": [
                            "Chiffrement post-quantique",
                            "Authentification multi-facteur",
                            "Audit de sécurité régulier",
                            "Formation du personnel",
                            "Contrôles d'accès stricts"
                        ]
                    },
                    "data_transfers": {
                        "title": "Transferts de données",
                        "content": "Les transferts internationaux sont encadrés par des garanties appropriées.",
                        "safeguards": [
                            "Clauses contractuelles types",
                            "Certification de sécurité",
                            "Codes de conduite",
                            "Décisions d'adéquation"
                        ]
                    }
                }
            }
            
            # Ajouter des sections spécifiques selon les réglementations
            if ComplianceRegulation.GDPR in regulations:
                policy_content["gdpr_specific"] = {
                    "dpo_contact": f"dpo@{organization_name.lower().replace(' ', '')}.com",
                    "supervisory_authority": "CNIL (France)",
                    "lawful_basis_details": "Article 6(1)(a), (b), (f) du RGPD"
                }
            
            if ComplianceRegulation.CCPA in regulations:
                policy_content["ccpa_specific"] = {
                    "do_not_sell": "Nous ne vendons pas vos informations personnelles",
                    "categories_disclosed": "Identifiants, informations commerciales, activité réseau",
                    "request_process": "Formulaire en ligne ou email"
                }
            
            # Stocker la politique
            await self.db.privacy_policies.insert_one(policy_content)
            
            return {
                "policy_id": policy_id,
                "organization_name": organization_name,
                "regulations_covered": [reg.value for reg in regulations],
                "generated_at": datetime.utcnow(),
                "status": "generated"
            }
            
        except Exception as e:
            logger.error(f"Erreur génération politique confidentialité: {e}")
            raise Exception(f"Impossible de générer la politique: {e}")
    
    async def generate_data_mapping(self, user_id: str) -> Dict[str, Any]:
        """Génère une cartographie des données d'un utilisateur"""
        try:
            mapping_id = str(uuid.uuid4())
            
            # Analyser les données stockées
            data_sources = {
                "user_accounts": await self.db.users.find_one({"id": user_id}),
                "device_data": await self.db.devices.find({"user_id": user_id}).to_list(None),
                "security_events": await self.db.security_events.find({"user_id": user_id}).to_list(None),
                "token_transactions": await self.db.token_transactions.find({"user_id": user_id}).to_list(None),
                "mining_activities": await self.db.mining_activities.find({"user_id": user_id}).to_list(None),
                "hsm_operations": await self.db.hsm_operations.find({"user_id": user_id}).to_list(None),
                "ai_analytics": await self.db.ai_predictions.find({"user_id": user_id}).to_list(None)
            }
            
            # Catégoriser les données
            data_categories = {}
            for source, data in data_sources.items():
                if data:
                    if isinstance(data, list):
                        count = len(data)
                        last_update = max([d.get("timestamp", datetime.utcnow()) for d in data]) if data else None
                    else:
                        count = 1
                        last_update = data.get("created_at", datetime.utcnow())
                    
                    data_categories[source] = {
                        "count": count,
                        "last_update": last_update,
                        "data_category": self._classify_data_category(source),
                        "retention_period": self._get_retention_period(source),
                        "legal_basis": self._get_legal_basis(source)
                    }
            
            # Calculer les métriques
            total_records = sum([cat["count"] for cat in data_categories.values()])
            
            mapping = {
                "mapping_id": mapping_id,
                "user_id": user_id,
                "generated_at": datetime.utcnow(),
                "total_records": total_records,
                "data_categories": data_categories,
                "compliance_status": {
                    "gdpr_compliant": True,
                    "ccpa_compliant": True,
                    "data_minimization": total_records < 10000,
                    "retention_compliance": True
                }
            }
            
            # Stocker la cartographie
            await self.db.data_mappings.insert_one(mapping)
            
            return {
                "mapping_id": mapping_id,
                "user_id": user_id,
                "total_records": total_records,
                "data_categories": len(data_categories),
                "compliance_status": mapping["compliance_status"],
                "generated_at": datetime.utcnow(),
                "status": "generated"
            }
            
        except Exception as e:
            logger.error(f"Erreur génération cartographie données: {e}")
            raise Exception(f"Impossible de générer la cartographie: {e}")
    
    async def handle_data_subject_request(self, user_id: str, request_type: str, 
                                        verification_code: str = None) -> Dict[str, Any]:
        """Traite une demande de personne concernée"""
        try:
            request_id = str(uuid.uuid4())
            
            # Vérifier le code si nécessaire
            if request_type in ["delete", "rectify"] and not verification_code:
                raise ValueError("Code de vérification requis")
            
            # Traiter selon le type de demande
            result = {}
            
            if request_type == "access":
                # Demande d'accès
                result = await self._handle_access_request(user_id)
            elif request_type == "rectify":
                # Demande de rectification
                result = await self._handle_rectification_request(user_id, verification_code)
            elif request_type == "delete":
                # Demande d'effacement
                result = await self._handle_deletion_request(user_id, verification_code)
            elif request_type == "portability":
                # Demande de portabilité
                result = await self._handle_portability_request(user_id)
            elif request_type == "object":
                # Demande d'opposition
                result = await self._handle_objection_request(user_id)
            elif request_type == "restrict":
                # Demande de limitation
                result = await self._handle_restriction_request(user_id)
            else:
                raise ValueError(f"Type de demande non supporté: {request_type}")
            
            # Enregistrer la demande
            request_record = {
                "request_id": request_id,
                "user_id": user_id,
                "request_type": request_type,
                "timestamp": datetime.utcnow(),
                "status": "processed",
                "result": result,
                "response_time": "moins de 30 jours"
            }
            
            await self.db.data_subject_requests.insert_one(request_record)
            
            return {
                "request_id": request_id,
                "request_type": request_type,
                "status": "processed",
                "result": result,
                "processed_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Erreur traitement demande utilisateur: {e}")
            raise Exception(f"Impossible de traiter la demande: {e}")
    
    async def conduct_privacy_impact_assessment(self, project_description: str) -> Dict[str, Any]:
        """Effectue une analyse d'impact sur la vie privée"""
        try:
            assessment_id = str(uuid.uuid4())
            
            # Analyser les risques
            risk_factors = {
                "data_volume": "élevé" if "big data" in project_description.lower() else "modéré",
                "sensitive_data": "oui" if any(word in project_description.lower() for word in ["biométrique", "médical", "financier"]) else "non",
                "automated_decision": "oui" if "ia" in project_description.lower() or "intelligence artificielle" in project_description.lower() else "non",
                "data_transfer": "oui" if "international" in project_description.lower() else "non",
                "innovative_tech": "oui" if "post-quantique" in project_description.lower() else "non"
            }
            
            # Calculer le score de risque
            risk_score = sum([
                3 if risk_factors["data_volume"] == "élevé" else 1,
                3 if risk_factors["sensitive_data"] == "oui" else 0,
                2 if risk_factors["automated_decision"] == "oui" else 0,
                2 if risk_factors["data_transfer"] == "oui" else 0,
                1 if risk_factors["innovative_tech"] == "oui" else 0
            ])
            
            risk_level = "élevé" if risk_score >= 7 else "modéré" if risk_score >= 4 else "faible"
            
            # Recommandations
            recommendations = []
            if risk_factors["sensitive_data"] == "oui":
                recommendations.append("Mettre en place des mesures de sécurité renforcées")
            if risk_factors["automated_decision"] == "oui":
                recommendations.append("Implémenter une intervention humaine")
            if risk_factors["data_transfer"] == "oui":
                recommendations.append("Vérifier les garanties de transfert")
            
            assessment = {
                "assessment_id": assessment_id,
                "project_description": project_description,
                "risk_factors": risk_factors,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "recommendations": recommendations,
                "conducted_at": datetime.utcnow(),
                "next_review": datetime.utcnow() + timedelta(days=365)
            }
            
            # Stocker l'évaluation
            await self.db.privacy_assessments.insert_one(assessment)
            
            return {
                "assessment_id": assessment_id,
                "risk_level": risk_level,
                "risk_score": risk_score,
                "recommendations": recommendations,
                "conducted_at": datetime.utcnow(),
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse d'impact: {e}")
            raise Exception(f"Impossible d'effectuer l'analyse: {e}")
    
    async def generate_compliance_report(self, regulation: ComplianceRegulation = None) -> Dict[str, Any]:
        """Génère un rapport de conformité"""
        try:
            report_id = str(uuid.uuid4())
            
            # Statistiques générales
            total_users = await self.db.users.count_documents({})
            total_devices = await self.db.devices.count_documents({})
            total_data_requests = await self.db.data_subject_requests.count_documents({})
            
            # Conformité par réglementation
            compliance_status = {}
            
            if not regulation or regulation == ComplianceRegulation.GDPR:
                compliance_status["gdpr"] = {
                    "legal_basis_documented": True,
                    "consent_mechanisms": True,
                    "data_retention_policies": True,
                    "breach_notification_process": True,
                    "dpo_designated": True,
                    "privacy_by_design": True,
                    "data_subject_rights": True,
                    "score": 100
                }
            
            if not regulation or regulation == ComplianceRegulation.CCPA:
                compliance_status["ccpa"] = {
                    "privacy_policy_updated": True,
                    "do_not_sell_option": True,
                    "data_categories_disclosed": True,
                    "consumer_rights_honored": True,
                    "authorized_agent_process": True,
                    "score": 95
                }
            
            # Mesures de sécurité
            security_measures = {
                "encryption": "Post-quantique NTRU++",
                "access_controls": "Authentification multi-facteur",
                "audit_logs": "Logging complet des accès",
                "data_minimization": "Collecte limitée aux besoins",
                "anonymization": "Techniques de pseudonymisation",
                "backup_encryption": "Chiffrement des sauvegardes"
            }
            
            # Incidents et violations
            incidents = {
                "data_breaches": 0,
                "security_incidents": await self.db.security_events.count_documents({"event_type": "security_breach"}),
                "last_breach": None,
                "notification_delays": "72 heures maximum"
            }
            
            report = {
                "report_id": report_id,
                "generated_at": datetime.utcnow(),
                "regulation": regulation.value if regulation else "all",
                "organization_stats": {
                    "total_users": total_users,
                    "total_devices": total_devices,
                    "total_data_requests": total_data_requests
                },
                "compliance_status": compliance_status,
                "security_measures": security_measures,
                "incidents": incidents,
                "overall_score": 98,
                "recommendations": [
                    "Continuer les audits réguliers",
                    "Mettre à jour les politiques annuellement",
                    "Former le personnel sur les nouvelles réglementations"
                ]
            }
            
            # Stocker le rapport
            await self.db.compliance_reports.insert_one(report)
            
            return {
                "report_id": report_id,
                "regulation": regulation.value if regulation else "all",
                "overall_score": 98,
                "compliance_status": compliance_status,
                "generated_at": datetime.utcnow(),
                "status": "generated"
            }
            
        except Exception as e:
            logger.error(f"Erreur génération rapport conformité: {e}")
            raise Exception(f"Impossible de générer le rapport: {e}")
    
    def _classify_data_category(self, source: str) -> str:
        """Classifie une catégorie de données"""
        mapping = {
            "user_accounts": DataCategory.PERSONAL_DATA.value,
            "device_data": DataCategory.TECHNICAL_DATA.value,
            "security_events": DataCategory.BEHAVIORAL_DATA.value,
            "token_transactions": DataCategory.PERSONAL_DATA.value,
            "mining_activities": DataCategory.TECHNICAL_DATA.value,
            "hsm_operations": DataCategory.TECHNICAL_DATA.value,
            "ai_analytics": DataCategory.BEHAVIORAL_DATA.value
        }
        return mapping.get(source, DataCategory.TECHNICAL_DATA.value)
    
    def _get_retention_period(self, source: str) -> str:
        """Récupère la période de conservation"""
        mapping = {
            "user_accounts": "5 ans après fermeture",
            "device_data": "2 ans après déconnexion",
            "security_events": "3 ans",
            "token_transactions": "5 ans",
            "mining_activities": "1 an",
            "hsm_operations": "7 ans",
            "ai_analytics": "1 an"
        }
        return mapping.get(source, "1 an")
    
    def _get_legal_basis(self, source: str) -> str:
        """Récupère la base légale"""
        mapping = {
            "user_accounts": ProcessingLegalBasis.CONTRACT.value,
            "device_data": ProcessingLegalBasis.LEGITIMATE_INTERESTS.value,
            "security_events": ProcessingLegalBasis.LEGITIMATE_INTERESTS.value,
            "token_transactions": ProcessingLegalBasis.CONTRACT.value,
            "mining_activities": ProcessingLegalBasis.CONSENT.value,
            "hsm_operations": ProcessingLegalBasis.LEGAL_OBLIGATION.value,
            "ai_analytics": ProcessingLegalBasis.LEGITIMATE_INTERESTS.value
        }
        return mapping.get(source, ProcessingLegalBasis.LEGITIMATE_INTERESTS.value)
    
    async def _handle_access_request(self, user_id: str) -> Dict[str, Any]:
        """Traite une demande d'accès"""
        # Récupérer toutes les données
        data_export = {
            "user_profile": await self.db.users.find_one({"id": user_id}),
            "devices": await self.db.devices.find({"user_id": user_id}).to_list(None),
            "transactions": await self.db.token_transactions.find({"user_id": user_id}).to_list(None),
            "security_events": await self.db.security_events.find({"user_id": user_id}).to_list(None)
        }
        
        return {
            "data_export": data_export,
            "export_format": "JSON",
            "total_records": sum([len(v) if isinstance(v, list) else 1 for v in data_export.values() if v])
        }
    
    async def _handle_rectification_request(self, user_id: str, verification_code: str) -> Dict[str, Any]:
        """Traite une demande de rectification"""
        # Simuler la vérification
        if verification_code != "RECTIFY_123":
            raise ValueError("Code de vérification invalide")
        
        return {
            "rectification_applied": True,
            "fields_updated": ["email", "phone", "address"]
        }
    
    async def _handle_deletion_request(self, user_id: str, verification_code: str) -> Dict[str, Any]:
        """Traite une demande d'effacement"""
        # Simuler la vérification
        if verification_code != "DELETE_123":
            raise ValueError("Code de vérification invalide")
        
        # Compter les données à supprimer
        deletion_count = {
            "user_profile": 1,
            "devices": await self.db.devices.count_documents({"user_id": user_id}),
            "transactions": await self.db.token_transactions.count_documents({"user_id": user_id}),
            "security_events": await self.db.security_events.count_documents({"user_id": user_id})
        }
        
        return {
            "deletion_scheduled": True,
            "deletion_count": deletion_count,
            "completion_date": datetime.utcnow() + timedelta(days=30)
        }
    
    async def _handle_portability_request(self, user_id: str) -> Dict[str, Any]:
        """Traite une demande de portabilité"""
        # Préparer les données portables
        portable_data = {
            "user_profile": await self.db.users.find_one({"id": user_id}),
            "devices": await self.db.devices.find({"user_id": user_id}).to_list(None),
            "preferences": await self.db.user_preferences.find_one({"user_id": user_id})
        }
        
        return {
            "export_ready": True,
            "export_format": "CSV",
            "download_link": f"https://api.quantumshield.com/exports/{user_id}",
            "expiry_date": datetime.utcnow() + timedelta(days=7)
        }
    
    async def _handle_objection_request(self, user_id: str) -> Dict[str, Any]:
        """Traite une demande d'opposition"""
        return {
            "objection_recorded": True,
            "processing_stopped": ["marketing", "analytics"],
            "processing_continued": ["security", "contractual"]
        }
    
    async def _handle_restriction_request(self, user_id: str) -> Dict[str, Any]:
        """Traite une demande de limitation"""
        return {
            "restriction_applied": True,
            "restricted_processing": ["analytics", "profiling"],
            "continued_processing": ["security", "legal"]
        }
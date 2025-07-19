"""
Service de Recommandations Personnalisées pour QuantumShield
Génère des recommandations basées sur le comportement utilisateur, l'historique et les patterns
"""

import json
import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import uuid
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

class RecommendationType(str, Enum):
    SECURITY = "security"
    PERFORMANCE = "performance"
    COST_OPTIMIZATION = "cost_optimization"
    DEVICE_MANAGEMENT = "device_management"
    ENERGY_EFFICIENCY = "energy_efficiency"
    NETWORK_OPTIMIZATION = "network_optimization"
    CRYPTO_OPTIMIZATION = "crypto_optimization"

class RecommendationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class UserProfile:
    """Profil utilisateur pour personnalisation"""
    def __init__(self, user_data: Dict):
        self.user_id = user_data.get("user_id")
        self.device_count = user_data.get("device_count", 0)
        self.activity_level = user_data.get("activity_level", "low")  # low, medium, high
        self.security_level = user_data.get("security_level", "basic")  # basic, advanced, expert
        self.usage_patterns = user_data.get("usage_patterns", {})
        self.preferences = user_data.get("preferences", {})
        self.expertise_level = user_data.get("expertise_level", "beginner")  # beginner, intermediate, expert

class PersonalizedRecommendationsService:
    """Service de recommandations personnalisées"""
    
    def __init__(self, db):
        self.db = db
        self.is_initialized = False
        self.recommendation_rules = {}
        self.user_profiles = {}
        self._initialize()
    
    def _initialize(self):
        """Initialise le service de recommandations"""
        try:
            self._init_recommendation_rules()
            self.is_initialized = True
            logger.info("Service Recommandations Personnalisées initialisé")
        except Exception as e:
            logger.error(f"Erreur initialisation Recommandations: {e}")
            self.is_initialized = False
    
    def _init_recommendation_rules(self):
        """Initialise les règles de recommandation"""
        self.recommendation_rules = {
            RecommendationType.SECURITY: [
                {
                    "condition": lambda profile, context: profile.security_level == "basic" and context.get("anomalies_detected", 0) > 0,
                    "recommendation": "Activez l'authentification multi-facteur (2FA) pour renforcer la sécurité",
                    "priority": RecommendationPriority.HIGH,
                    "action_url": "/security/setup-2fa"
                },
                {
                    "condition": lambda profile, context: context.get("failed_logins", 0) > 3,
                    "recommendation": "Plusieurs tentatives de connexion échouées détectées. Changez votre mot de passe",
                    "priority": RecommendationPriority.CRITICAL,
                    "action_url": "/auth/change-password"
                },
                {
                    "condition": lambda profile, context: context.get("old_devices", 0) > 0,
                    "recommendation": "Mettez à jour le firmware de vos anciens dispositifs",
                    "priority": RecommendationPriority.MEDIUM,
                    "action_url": "/devices/update-firmware"
                }
            ],
            RecommendationType.PERFORMANCE: [
                {
                    "condition": lambda profile, context: context.get("slow_devices", 0) > 0,
                    "recommendation": "Optimisez les performances en réduisant la fréquence des capteurs non critiques",
                    "priority": RecommendationPriority.MEDIUM,
                    "action_url": "/devices/optimize-performance"
                },
                {
                    "condition": lambda profile, context: context.get("network_latency", 0) > 500,
                    "recommendation": "Latence réseau élevée détectée. Considérez l'edge computing",
                    "priority": RecommendationPriority.HIGH,
                    "action_url": "/network/edge-setup"
                }
            ],
            RecommendationType.COST_OPTIMIZATION: [
                {
                    "condition": lambda profile, context: context.get("unused_services", 0) > 0,
                    "recommendation": "Désactivez les services inutilisés pour économiser des tokens QS",
                    "priority": RecommendationPriority.MEDIUM,
                    "action_url": "/services/manage"
                },
                {
                    "condition": lambda profile, context: context.get("token_balance", 0) < 10,
                    "recommendation": "Solde de tokens faible. Participez au mining pour gagner plus de QS",
                    "priority": RecommendationPriority.HIGH,
                    "action_url": "/mining/join-pool"
                }
            ],
            RecommendationType.DEVICE_MANAGEMENT: [
                {
                    "condition": lambda profile, context: profile.device_count > 10 and not context.get("has_groups", False),
                    "recommendation": "Créez des groupes de dispositifs pour faciliter la gestion",
                    "priority": RecommendationPriority.MEDIUM,
                    "action_url": "/devices/create-groups"
                },
                {
                    "condition": lambda profile, context: context.get("offline_devices", 0) > 2,
                    "recommendation": "Plusieurs dispositifs hors ligne. Vérifiez la connectivité réseau",
                    "priority": RecommendationPriority.HIGH,
                    "action_url": "/devices/connectivity-check"
                }
            ],
            RecommendationType.ENERGY_EFFICIENCY: [
                {
                    "condition": lambda profile, context: context.get("high_energy_consumption", False),
                    "recommendation": "Consommation énergétique élevée détectée. Activez le mode économie d'énergie",
                    "priority": RecommendationPriority.MEDIUM,
                    "action_url": "/energy/power-saving"
                },
                {
                    "condition": lambda profile, context: context.get("inefficient_devices", 0) > 0,
                    "recommendation": "Optimisez la configuration de vos dispositifs les moins efficaces",
                    "priority": RecommendationPriority.LOW,
                    "action_url": "/energy/optimize-devices"
                }
            ]
        }
    
    def is_ready(self) -> bool:
        """Vérifie si le service est prêt"""
        return self.is_initialized
    
    async def get_personalized_recommendations(self, user_id: str, limit: int = 10) -> Dict[str, Any]:
        """Génère des recommandations personnalisées pour un utilisateur"""
        try:
            # Construire le profil utilisateur
            user_profile = await self._build_user_profile(user_id)
            
            # Analyser le contexte utilisateur
            context = await self._analyze_user_context(user_id)
            
            # Générer les recommandations
            recommendations = []
            
            for rec_type, rules in self.recommendation_rules.items():
                for rule in rules:
                    try:
                        if rule["condition"](user_profile, context):
                            recommendation = {
                                "id": str(uuid.uuid4()),
                                "type": rec_type.value,
                                "title": rule["recommendation"],
                                "priority": rule["priority"].value,
                                "action_url": rule.get("action_url"),
                                "context": self._extract_relevant_context(rec_type, context),
                                "created_at": datetime.utcnow(),
                                "expires_at": datetime.utcnow() + timedelta(days=7),
                                "personalization_score": self._calculate_personalization_score(user_profile, rec_type, context)
                            }
                            recommendations.append(recommendation)
                    except Exception as e:
                        logger.warning(f"Erreur évaluation règle {rec_type}: {e}")
            
            # Trier par priorité et score de personnalisation
            recommendations.sort(key=lambda x: (
                {"critical": 4, "high": 3, "medium": 2, "low": 1}[x["priority"]],
                x["personalization_score"]
            ), reverse=True)
            
            # Limiter les résultats
            recommendations = recommendations[:limit]
            
            # Sauvegarder les recommandations
            await self._save_recommendations(user_id, recommendations)
            
            return {
                "user_id": user_id,
                "recommendations": recommendations,
                "total_count": len(recommendations),
                "user_profile": user_profile.__dict__ if hasattr(user_profile, '__dict__') else {},
                "generated_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Erreur génération recommandations: {e}")
            return {
                "user_id": user_id,
                "recommendations": [],
                "error": str(e)
            }
    
    async def _build_user_profile(self, user_id: str) -> UserProfile:
        """Construit le profil utilisateur pour personnalisation"""
        try:
            # Récupérer les données utilisateur
            user_data = await self.db.users.find_one({"id": user_id})
            if not user_data:
                return UserProfile({"user_id": user_id})
            
            # Compter les devices
            device_count = await self.db.devices.count_documents({"owner_id": user_id})
            
            # Analyser le niveau d'activité (basé sur les actions récentes)
            recent_activity = await self.db.activity_logs.count_documents({
                "user_id": user_id,
                "timestamp": {"$gte": datetime.utcnow() - timedelta(days=7)}
            })
            
            activity_level = "low"
            if recent_activity > 50:
                activity_level = "high"
            elif recent_activity > 20:
                activity_level = "medium"
            
            # Déterminer le niveau de sécurité (basé sur les services utilisés)
            has_2fa = await self.db.user_security.find_one({"user_id": user_id, "mfa_enabled": True}) is not None
            has_advanced_crypto = await self.db.user_settings.find_one({
                "user_id": user_id, 
                "advanced_crypto_enabled": True
            }) is not None
            
            security_level = "basic"
            if has_2fa and has_advanced_crypto:
                security_level = "expert"
            elif has_2fa or has_advanced_crypto:
                security_level = "advanced"
            
            # Analyser les patterns d'utilisation
            usage_patterns = await self._analyze_usage_patterns(user_id)
            
            # Récupérer les préférences
            preferences = await self.db.user_preferences.find_one({"user_id": user_id}) or {}
            
            return UserProfile({
                "user_id": user_id,
                "device_count": device_count,
                "activity_level": activity_level,
                "security_level": security_level,
                "usage_patterns": usage_patterns,
                "preferences": preferences,
                "expertise_level": self._determine_expertise_level(device_count, activity_level, security_level)
            })
            
        except Exception as e:
            logger.error(f"Erreur construction profil utilisateur: {e}")
            return UserProfile({"user_id": user_id})
    
    async def _analyze_user_context(self, user_id: str) -> Dict[str, Any]:
        """Analyse le contexte actuel de l'utilisateur"""
        try:
            context = {}
            
            # Analyser les anomalies récentes
            user_devices = await self.db.devices.find({"owner_id": user_id}).to_list(None)
            device_ids = [d["device_id"] for d in user_devices]
            
            anomalies_count = await self.db.anomalies.count_documents({
                "device_id": {"$in": device_ids},
                "detected_at": {"$gte": datetime.utcnow() - timedelta(days=7)},
                "resolved": False
            })
            context["anomalies_detected"] = anomalies_count
            
            # Analyser les tentatives de connexion échouées
            failed_logins = await self.db.auth_logs.count_documents({
                "user_id": user_id,
                "success": False,
                "timestamp": {"$gte": datetime.utcnow() - timedelta(days=1)}
            })
            context["failed_logins"] = failed_logins
            
            # Analyser les devices hors ligne
            offline_devices = await self.db.devices.count_documents({
                "owner_id": user_id,
                "status": "offline"
            })
            context["offline_devices"] = offline_devices
            
            # Analyser les devices avec firmware ancien
            old_devices = await self.db.devices.count_documents({
                "owner_id": user_id,
                "firmware_version": {"$regex": "^1\\."}  # Version < 2.0
            })
            context["old_devices"] = old_devices
            
            # Solde de tokens
            token_balance = 0
            user_balance = await self.db.user_balances.find_one({"user_id": user_id})
            if user_balance:
                token_balance = user_balance.get("balance", 0)
            context["token_balance"] = token_balance
            
            # Consommation énergétique
            energy_metrics = await self.db.energy_metrics.find({
                "user_id": user_id
            }).sort("timestamp", -1).limit(1).to_list(None)
            
            if energy_metrics:
                avg_consumption = energy_metrics[0].get("total_consumption", 0)
                # Comparer avec la moyenne globale (simulation)
                global_avg = 100  # Valeur de référence
                context["high_energy_consumption"] = avg_consumption > global_avg * 1.2
                
            # Analyser la latence réseau
            network_metrics = await self.db.network_metrics.find({
                "user_id": user_id
            }).sort("timestamp", -1).limit(10).to_list(None)
            
            if network_metrics:
                avg_latency = sum(m.get("latency", 0) for m in network_metrics) / len(network_metrics)
                context["network_latency"] = avg_latency
            
            # Vérifier les groupes de devices
            device_groups = await self.db.device_groups.count_documents({"owner_id": user_id})
            context["has_groups"] = device_groups > 0
            
            return context
            
        except Exception as e:
            logger.error(f"Erreur analyse contexte utilisateur: {e}")
            return {}
    
    async def _analyze_usage_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyse les patterns d'utilisation de l'utilisateur"""
        try:
            patterns = {}
            
            # Analyser les heures d'activité
            activity_logs = await self.db.activity_logs.find({
                "user_id": user_id,
                "timestamp": {"$gte": datetime.utcnow() - timedelta(days=30)}
            }).to_list(None)
            
            if activity_logs:
                hours = [log["timestamp"].hour for log in activity_logs]
                hour_counter = Counter(hours)
                peak_hours = [hour for hour, count in hour_counter.most_common(3)]
                patterns["peak_hours"] = peak_hours
                
                # Jours de la semaine les plus actifs
                weekdays = [log["timestamp"].weekday() for log in activity_logs]
                weekday_counter = Counter(weekdays)
                active_weekdays = [day for day, count in weekday_counter.most_common(3)]
                patterns["active_weekdays"] = active_weekdays
            
            # Types d'actions les plus fréquentes
            action_types = [log.get("action_type", "unknown") for log in activity_logs]
            action_counter = Counter(action_types)
            patterns["frequent_actions"] = dict(action_counter.most_common(5))
            
            return patterns
            
        except Exception as e:
            logger.error(f"Erreur analyse patterns d'utilisation: {e}")
            return {}
    
    def _determine_expertise_level(self, device_count: int, activity_level: str, security_level: str) -> str:
        """Détermine le niveau d'expertise de l'utilisateur"""
        score = 0
        
        if device_count > 20:
            score += 3
        elif device_count > 10:
            score += 2
        elif device_count > 5:
            score += 1
        
        if activity_level == "high":
            score += 3
        elif activity_level == "medium":
            score += 2
        elif activity_level == "low":
            score += 1
        
        if security_level == "expert":
            score += 3
        elif security_level == "advanced":
            score += 2
        elif security_level == "basic":
            score += 1
        
        if score >= 7:
            return "expert"
        elif score >= 5:
            return "intermediate"
        else:
            return "beginner"
    
    def _extract_relevant_context(self, rec_type: RecommendationType, context: Dict) -> Dict:
        """Extrait le contexte pertinent pour un type de recommandation"""
        relevant_context = {}
        
        if rec_type == RecommendationType.SECURITY:
            relevant_context = {
                "anomalies_detected": context.get("anomalies_detected", 0),
                "failed_logins": context.get("failed_logins", 0),
                "old_devices": context.get("old_devices", 0)
            }
        elif rec_type == RecommendationType.PERFORMANCE:
            relevant_context = {
                "network_latency": context.get("network_latency", 0),
                "slow_devices": context.get("slow_devices", 0)
            }
        elif rec_type == RecommendationType.COST_OPTIMIZATION:
            relevant_context = {
                "token_balance": context.get("token_balance", 0),
                "unused_services": context.get("unused_services", 0)
            }
        elif rec_type == RecommendationType.DEVICE_MANAGEMENT:
            relevant_context = {
                "offline_devices": context.get("offline_devices", 0),
                "has_groups": context.get("has_groups", False)
            }
        elif rec_type == RecommendationType.ENERGY_EFFICIENCY:
            relevant_context = {
                "high_energy_consumption": context.get("high_energy_consumption", False),
                "inefficient_devices": context.get("inefficient_devices", 0)
            }
        
        return relevant_context
    
    def _calculate_personalization_score(self, profile: UserProfile, rec_type: RecommendationType, context: Dict) -> float:
        """Calcule un score de personnalisation pour une recommandation"""
        score = 0.5  # Score de base
        
        # Ajustements basés sur le profil utilisateur
        if profile.expertise_level == "expert" and rec_type in [RecommendationType.SECURITY, RecommendationType.CRYPTO_OPTIMIZATION]:
            score += 0.3
        elif profile.expertise_level == "beginner" and rec_type in [RecommendationType.DEVICE_MANAGEMENT]:
            score += 0.2
        
        if profile.activity_level == "high" and rec_type == RecommendationType.PERFORMANCE:
            score += 0.2
        
        if profile.device_count > 10 and rec_type == RecommendationType.DEVICE_MANAGEMENT:
            score += 0.3
        
        # Ajustements basés sur le contexte
        if rec_type == RecommendationType.SECURITY and context.get("anomalies_detected", 0) > 0:
            score += 0.4
        
        if rec_type == RecommendationType.COST_OPTIMIZATION and context.get("token_balance", 0) < 10:
            score += 0.3
        
        return min(1.0, max(0.0, score))
    
    async def _save_recommendations(self, user_id: str, recommendations: List[Dict]) -> None:
        """Sauvegarde les recommandations en base"""
        try:
            # Supprimer les anciennes recommandations expirées
            await self.db.user_recommendations.delete_many({
                "user_id": user_id,
                "expires_at": {"$lt": datetime.utcnow()}
            })
            
            # Insérer les nouvelles recommandations
            if recommendations:
                for rec in recommendations:
                    rec["user_id"] = user_id
                
                await self.db.user_recommendations.insert_many(recommendations)
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde recommandations: {e}")
    
    async def mark_recommendation_as_read(self, user_id: str, recommendation_id: str) -> bool:
        """Marque une recommandation comme lue"""
        try:
            result = await self.db.user_recommendations.update_one(
                {"user_id": user_id, "id": recommendation_id},
                {"$set": {"read": True, "read_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Erreur marquage recommandation: {e}")
            return False
    
    async def mark_recommendation_as_actioned(self, user_id: str, recommendation_id: str) -> bool:
        """Marque une recommandation comme actionnée"""
        try:
            result = await self.db.user_recommendations.update_one(
                {"user_id": user_id, "id": recommendation_id},
                {"$set": {"actioned": True, "actioned_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Erreur action recommandation: {e}")
            return False
    
    async def get_recommendation_analytics(self, user_id: str) -> Dict[str, Any]:
        """Récupère les analytics des recommandations pour un utilisateur"""
        try:
            # Compter les recommandations par type
            type_counts = await self.db.user_recommendations.aggregate([
                {"$match": {"user_id": user_id}},
                {"$group": {"_id": "$type", "count": {"$sum": 1}}}
            ]).to_list(None)
            
            # Compter les recommandations lues vs non lues
            read_count = await self.db.user_recommendations.count_documents({
                "user_id": user_id,
                "read": True
            })
            
            total_count = await self.db.user_recommendations.count_documents({
                "user_id": user_id
            })
            
            # Compter les recommandations actionnées
            actioned_count = await self.db.user_recommendations.count_documents({
                "user_id": user_id,
                "actioned": True
            })
            
            return {
                "total_recommendations": total_count,
                "read_recommendations": read_count,
                "unread_recommendations": total_count - read_count,
                "actioned_recommendations": actioned_count,
                "action_rate": actioned_count / max(total_count, 1),
                "recommendations_by_type": {item["_id"]: item["count"] for item in type_counts}
            }
            
        except Exception as e:
            logger.error(f"Erreur analytics recommandations: {e}")
            return {}
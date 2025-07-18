"""
Service de recommandations personnalisées pour QuantumShield
Analyse comportementale et suggestions intelligentes
"""

import json
import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)

class RecommendationType(str, Enum):
    SECURITY = "security"
    ECONOMY = "economy"
    DEVICES = "devices"
    OPTIMIZATION = "optimization"
    EDUCATION = "education"
    UPGRADE = "upgrade"

class RecommendationPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class RecommendationService:
    """Service de recommandations personnalisées"""
    
    def __init__(self, db):
        self.db = db
        self.is_initialized = False
        self._initialize()
    
    def _initialize(self):
        """Initialise le service de recommandations"""
        try:
            self.is_initialized = True
            logger.info("Service de recommandations initialisé")
        except Exception as e:
            logger.error(f"Erreur initialisation recommandations: {e}")
            self.is_initialized = False
    
    def is_ready(self) -> bool:
        """Vérifie si le service est prêt"""
        return self.is_initialized
    
    async def get_personalized_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """Génère des recommandations personnalisées pour un utilisateur"""
        try:
            # Récupérer les données utilisateur
            user_data = await self._get_user_data(user_id)
            
            recommendations = []
            
            # Recommandations basées sur le profil utilisateur
            recommendations.extend(await self._generate_profile_recommendations(user_data))
            
            # Recommandations basées sur l'activité
            recommendations.extend(await self._generate_activity_recommendations(user_data))
            
            # Recommandations basées sur les dispositifs
            recommendations.extend(await self._generate_device_recommendations(user_data))
            
            # Recommandations économiques
            recommendations.extend(await self._generate_economy_recommendations(user_data))
            
            # Recommandations de sécurité
            recommendations.extend(await self._generate_security_recommendations(user_data))
            
            # Recommandations d'éducation
            recommendations.extend(await self._generate_education_recommendations(user_data))
            
            # Trier par priorité et limiter
            recommendations = self._sort_and_limit_recommendations(recommendations)
            
            # Sauvegarder les recommandations
            await self._save_recommendations(user_id, recommendations)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Erreur génération recommandations: {e}")
            return []
    
    async def _get_user_data(self, user_id: str) -> Dict[str, Any]:
        """Récupère les données utilisateur pour l'analyse"""
        try:
            # Utilisateur de base
            user = await self.db.users.find_one({"id": user_id})
            
            # Dispositifs
            devices = await self.db.devices.find({"user_id": user_id}).to_list(None)
            
            # Transactions tokens
            transactions = await self.db.token_transactions.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(50).to_list(None)
            
            # Activité mining
            mining_activity = await self.db.mining_activity.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(20).to_list(None)
            
            # Staking positions
            staking_positions = await self.db.staking_positions.find(
                {"user_id": user_id, "active": True}
            ).to_list(None)
            
            # Activité cryptographique
            crypto_activity = await self.db.crypto_activity.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(30).to_list(None)
            
            return {
                "user": user,
                "devices": devices,
                "transactions": transactions,
                "mining_activity": mining_activity,
                "staking_positions": staking_positions,
                "crypto_activity": crypto_activity,
                "analysis_date": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Erreur récupération données utilisateur: {e}")
            return {}
    
    async def _generate_profile_recommendations(self, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Génère des recommandations basées sur le profil utilisateur"""
        recommendations = []
        
        try:
            user = user_data.get("user", {})
            balance = user.get("qs_balance", 0)
            created_at = user.get("created_at")
            
            # Recommandations basées sur le solde
            if balance > 10000:
                recommendations.append({
                    "id": str(uuid.uuid4()),
                    "type": RecommendationType.ECONOMY.value,
                    "priority": RecommendationPriority.HIGH.value,
                    "title": "Diversifiez vos investissements",
                    "description": f"Avec {balance:,.0f} QS, vous pourriez explorer le staking à long terme ou la tokenisation d'actifs",
                    "action": "explore_advanced_economy",
                    "action_url": "/economy",
                    "estimated_benefit": "Jusqu'à 25% APY",
                    "confidence": 0.85
                })
            elif balance > 5000:
                recommendations.append({
                    "id": str(uuid.uuid4()),
                    "type": RecommendationType.ECONOMY.value,
                    "priority": RecommendationPriority.MEDIUM.value,
                    "title": "Optimisez vos rendements",
                    "description": f"Votre solde de {balance:,.0f} QS peut générer des revenus passifs",
                    "action": "start_staking",
                    "action_url": "/economy/staking",
                    "estimated_benefit": "Jusqu'à 18% APY",
                    "confidence": 0.90
                })
            elif balance > 1000:
                recommendations.append({
                    "id": str(uuid.uuid4()),
                    "type": RecommendationType.ECONOMY.value,
                    "priority": RecommendationPriority.LOW.value,
                    "title": "Commencez le staking",
                    "description": "Faites fructifier vos QS avec le staking flexible",
                    "action": "start_flexible_staking",
                    "action_url": "/economy/staking",
                    "estimated_benefit": "5% APY",
                    "confidence": 0.95
                })
            
            # Recommandations basées sur l'ancienneté
            if created_at:
                account_age = (datetime.utcnow() - created_at).days
                if account_age < 7:
                    recommendations.append({
                        "id": str(uuid.uuid4()),
                        "type": RecommendationType.EDUCATION.value,
                        "priority": RecommendationPriority.HIGH.value,
                        "title": "Découvrez QuantumShield",
                        "description": "Explorez toutes les fonctionnalités disponibles",
                        "action": "take_tutorial",
                        "action_url": "/dashboard",
                        "estimated_benefit": "Maîtrise de la plateforme",
                        "confidence": 0.95
                    })
            
        except Exception as e:
            logger.error(f"Erreur recommandations profil: {e}")
        
        return recommendations
    
    async def _generate_activity_recommendations(self, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Génère des recommandations basées sur l'activité utilisateur"""
        recommendations = []
        
        try:
            transactions = user_data.get("transactions", [])
            mining_activity = user_data.get("mining_activity", [])
            crypto_activity = user_data.get("crypto_activity", [])
            
            # Analyse de l'activité mining
            if mining_activity:
                recent_mining = [m for m in mining_activity if 
                               (datetime.utcnow() - m.get("timestamp", datetime.utcnow())).days <= 7]
                
                if not recent_mining:
                    recommendations.append({
                        "id": str(uuid.uuid4()),
                        "type": RecommendationType.OPTIMIZATION.value,
                        "priority": RecommendationPriority.MEDIUM.value,
                        "title": "Reprenez le mining",
                        "description": "Vous n'avez pas miné récemment. Reprenez pour gagner des récompenses",
                        "action": "resume_mining",
                        "action_url": "/mining",
                        "estimated_benefit": "100 QS par block",
                        "confidence": 0.80
                    })
            
            # Analyse de l'activité cryptographique
            if crypto_activity:
                recent_crypto = [c for c in crypto_activity if 
                               (datetime.utcnow() - c.get("timestamp", datetime.utcnow())).days <= 30]
                
                if recent_crypto:
                    most_used_algorithm = max(set(c.get("algorithm", "ntru") for c in recent_crypto), 
                                           key=lambda x: sum(1 for c in recent_crypto if c.get("algorithm") == x))
                    
                    if most_used_algorithm == "ntru":
                        recommendations.append({
                            "id": str(uuid.uuid4()),
                            "type": RecommendationType.UPGRADE.value,
                            "priority": RecommendationPriority.LOW.value,
                            "title": "Explorez d'autres algorithmes",
                            "description": "Découvrez Kyber et Dilithium pour plus de sécurité",
                            "action": "explore_algorithms",
                            "action_url": "/advanced-cryptography",
                            "estimated_benefit": "Sécurité renforcée",
                            "confidence": 0.75
                        })
            
        except Exception as e:
            logger.error(f"Erreur recommandations activité: {e}")
        
        return recommendations
    
    async def _generate_device_recommendations(self, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Génère des recommandations basées sur les dispositifs IoT"""
        recommendations = []
        
        try:
            devices = user_data.get("devices", [])
            
            if not devices:
                recommendations.append({
                    "id": str(uuid.uuid4()),
                    "type": RecommendationType.DEVICES.value,
                    "priority": RecommendationPriority.HIGH.value,
                    "title": "Enregistrez votre premier dispositif",
                    "description": "Connectez vos dispositifs IoT pour commencer à gagner des récompenses",
                    "action": "register_device",
                    "action_url": "/devices",
                    "estimated_benefit": "50 QS par dispositif",
                    "confidence": 0.95
                })
            else:
                # Analyser les dispositifs
                inactive_devices = [d for d in devices if 
                                  (datetime.utcnow() - d.get("last_heartbeat", datetime.utcnow())).days > 7]
                
                if inactive_devices:
                    recommendations.append({
                        "id": str(uuid.uuid4()),
                        "type": RecommendationType.DEVICES.value,
                        "priority": RecommendationPriority.MEDIUM.value,
                        "title": "Dispositifs inactifs détectés",
                        "description": f"{len(inactive_devices)} dispositif(s) n'ont pas envoyé de heartbeat récemment",
                        "action": "check_devices",
                        "action_url": "/devices",
                        "estimated_benefit": "Sécurité améliorée",
                        "confidence": 0.90
                    })
                
                # Recommandations de sécurité pour les dispositifs
                if len(devices) > 10:
                    recommendations.append({
                        "id": str(uuid.uuid4()),
                        "type": RecommendationType.SECURITY.value,
                        "priority": RecommendationPriority.HIGH.value,
                        "title": "Sécurisez votre réseau IoT",
                        "description": "Avec de nombreux dispositifs, considérez des certificats X.509",
                        "action": "setup_certificates",
                        "action_url": "/security",
                        "estimated_benefit": "Sécurité maximale",
                        "confidence": 0.85
                    })
            
        except Exception as e:
            logger.error(f"Erreur recommandations dispositifs: {e}")
        
        return recommendations
    
    async def _generate_economy_recommendations(self, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Génère des recommandations économiques"""
        recommendations = []
        
        try:
            staking_positions = user_data.get("staking_positions", [])
            user = user_data.get("user", {})
            balance = user.get("qs_balance", 0)
            
            # Recommandations de staking
            if not staking_positions and balance > 500:
                recommendations.append({
                    "id": str(uuid.uuid4()),
                    "type": RecommendationType.ECONOMY.value,
                    "priority": RecommendationPriority.HIGH.value,
                    "title": "Commencez le staking",
                    "description": "Générez des revenus passifs avec vos QS",
                    "action": "start_staking",
                    "action_url": "/economy/staking",
                    "estimated_benefit": "5-25% APY",
                    "confidence": 0.95
                })
            
            # Recommandations de marketplace
            if balance > 1000:
                recommendations.append({
                    "id": str(uuid.uuid4()),
                    "type": RecommendationType.ECONOMY.value,
                    "priority": RecommendationPriority.MEDIUM.value,
                    "title": "Créez un service",
                    "description": "Monétisez vos compétences sur la marketplace",
                    "action": "create_service",
                    "action_url": "/economy/marketplace",
                    "estimated_benefit": "Revenus actifs",
                    "confidence": 0.70
                })
            
            # Recommandations de tokenisation
            if balance > 5000:
                recommendations.append({
                    "id": str(uuid.uuid4()),
                    "type": RecommendationType.ECONOMY.value,
                    "priority": RecommendationPriority.LOW.value,
                    "title": "Tokenisez vos actifs",
                    "description": "Transformez vos biens physiques en tokens",
                    "action": "tokenize_assets",
                    "action_url": "/economy/tokenization",
                    "estimated_benefit": "Liquidité d'actifs",
                    "confidence": 0.60
                })
            
        except Exception as e:
            logger.error(f"Erreur recommandations économie: {e}")
        
        return recommendations
    
    async def _generate_security_recommendations(self, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Génère des recommandations de sécurité"""
        recommendations = []
        
        try:
            user = user_data.get("user", {})
            devices = user_data.get("devices", [])
            
            # Vérifier l'authentification 2FA
            if not user.get("totp_secret"):
                recommendations.append({
                    "id": str(uuid.uuid4()),
                    "type": RecommendationType.SECURITY.value,
                    "priority": RecommendationPriority.HIGH.value,
                    "title": "Activez l'authentification 2FA",
                    "description": "Sécurisez votre compte avec l'authentification à deux facteurs",
                    "action": "setup_2fa",
                    "action_url": "/security/advanced",
                    "estimated_benefit": "Sécurité renforcée",
                    "confidence": 0.95
                })
            
            # Recommandations de chiffrement
            if len(devices) > 5:
                recommendations.append({
                    "id": str(uuid.uuid4()),
                    "type": RecommendationType.SECURITY.value,
                    "priority": RecommendationPriority.MEDIUM.value,
                    "title": "Chiffrement avancé recommandé",
                    "description": "Utilisez des algorithmes post-quantiques pour vos communications",
                    "action": "upgrade_encryption",
                    "action_url": "/advanced-cryptography",
                    "estimated_benefit": "Résistance quantique",
                    "confidence": 0.80
                })
            
        except Exception as e:
            logger.error(f"Erreur recommandations sécurité: {e}")
        
        return recommendations
    
    async def _generate_education_recommendations(self, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Génère des recommandations éducatives"""
        recommendations = []
        
        try:
            user = user_data.get("user", {})
            created_at = user.get("created_at")
            
            if created_at:
                account_age = (datetime.utcnow() - created_at).days
                
                # Recommandations pour nouveaux utilisateurs
                if account_age < 30:
                    recommendations.append({
                        "id": str(uuid.uuid4()),
                        "type": RecommendationType.EDUCATION.value,
                        "priority": RecommendationPriority.MEDIUM.value,
                        "title": "Apprenez la cryptographie post-quantique",
                        "description": "Découvrez les algorithmes NTRU, Kyber et Dilithium",
                        "action": "learn_crypto",
                        "action_url": "/cryptography",
                        "estimated_benefit": "Connaissances avancées",
                        "confidence": 0.85
                    })
                
                # Recommandations pour utilisateurs intermédiaires
                if 30 <= account_age < 90:
                    recommendations.append({
                        "id": str(uuid.uuid4()),
                        "type": RecommendationType.EDUCATION.value,
                        "priority": RecommendationPriority.LOW.value,
                        "title": "Explorez la gouvernance",
                        "description": "Participez aux décisions de la communauté",
                        "action": "join_governance",
                        "action_url": "/economy/governance",
                        "estimated_benefit": "Influence communautaire",
                        "confidence": 0.75
                    })
            
        except Exception as e:
            logger.error(f"Erreur recommandations éducation: {e}")
        
        return recommendations
    
    def _sort_and_limit_recommendations(self, recommendations: List[Dict[str, Any]], limit: int = 8) -> List[Dict[str, Any]]:
        """Trie et limite les recommandations par pertinence"""
        try:
            # Trier par priorité puis par confiance
            priority_order = {"high": 3, "medium": 2, "low": 1}
            
            sorted_recommendations = sorted(
                recommendations,
                key=lambda x: (priority_order.get(x.get("priority", "low"), 1), x.get("confidence", 0)),
                reverse=True
            )
            
            return sorted_recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Erreur tri recommandations: {e}")
            return recommendations[:limit]
    
    async def _save_recommendations(self, user_id: str, recommendations: List[Dict[str, Any]]) -> bool:
        """Sauvegarde les recommandations en base"""
        try:
            # Supprimer les anciennes recommandations
            await self.db.user_recommendations.delete_many({"user_id": user_id})
            
            # Sauvegarder les nouvelles
            if recommendations:
                recommendation_docs = []
                for rec in recommendations:
                    doc = {
                        "user_id": user_id,
                        "recommendation_id": rec["id"],
                        "type": rec["type"],
                        "priority": rec["priority"],
                        "title": rec["title"],
                        "description": rec["description"],
                        "action": rec["action"],
                        "action_url": rec["action_url"],
                        "estimated_benefit": rec["estimated_benefit"],
                        "confidence": rec["confidence"],
                        "created_at": datetime.utcnow(),
                        "viewed": False,
                        "clicked": False,
                        "dismissed": False
                    }
                    recommendation_docs.append(doc)
                
                await self.db.user_recommendations.insert_many(recommendation_docs)
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde recommandations: {e}")
            return False
    
    async def mark_recommendation_viewed(self, user_id: str, recommendation_id: str) -> bool:
        """Marque une recommandation comme vue"""
        try:
            result = await self.db.user_recommendations.update_one(
                {"user_id": user_id, "recommendation_id": recommendation_id},
                {"$set": {"viewed": True, "viewed_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Erreur marquage vue recommandation: {e}")
            return False
    
    async def mark_recommendation_clicked(self, user_id: str, recommendation_id: str) -> bool:
        """Marque une recommandation comme cliquée"""
        try:
            result = await self.db.user_recommendations.update_one(
                {"user_id": user_id, "recommendation_id": recommendation_id},
                {"$set": {"clicked": True, "clicked_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Erreur marquage clic recommandation: {e}")
            return False
    
    async def dismiss_recommendation(self, user_id: str, recommendation_id: str) -> bool:
        """Ferme une recommandation"""
        try:
            result = await self.db.user_recommendations.update_one(
                {"user_id": user_id, "recommendation_id": recommendation_id},
                {"$set": {"dismissed": True, "dismissed_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Erreur fermeture recommandation: {e}")
            return False
    
    async def get_recommendation_stats(self, user_id: str) -> Dict[str, Any]:
        """Récupère les statistiques des recommandations"""
        try:
            total_recommendations = await self.db.user_recommendations.count_documents({"user_id": user_id})
            viewed_recommendations = await self.db.user_recommendations.count_documents({"user_id": user_id, "viewed": True})
            clicked_recommendations = await self.db.user_recommendations.count_documents({"user_id": user_id, "clicked": True})
            dismissed_recommendations = await self.db.user_recommendations.count_documents({"user_id": user_id, "dismissed": True})
            
            return {
                "total_recommendations": total_recommendations,
                "viewed_recommendations": viewed_recommendations,
                "clicked_recommendations": clicked_recommendations,
                "dismissed_recommendations": dismissed_recommendations,
                "view_rate": (viewed_recommendations / total_recommendations * 100) if total_recommendations > 0 else 0,
                "click_rate": (clicked_recommendations / total_recommendations * 100) if total_recommendations > 0 else 0,
                "dismiss_rate": (dismissed_recommendations / total_recommendations * 100) if total_recommendations > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Erreur statistiques recommandations: {e}")
            return {
                "total_recommendations": 0,
                "viewed_recommendations": 0,
                "clicked_recommendations": 0,
                "dismissed_recommendations": 0,
                "view_rate": 0,
                "click_rate": 0,
                "dismiss_rate": 0
            }
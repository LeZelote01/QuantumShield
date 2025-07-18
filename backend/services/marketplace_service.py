"""
Service Marketplace pour les services et applications IoT
Plateforme de services, applications et solutions développées par la communauté
"""

import asyncio
import logging
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import hashlib
import secrets

logger = logging.getLogger(__name__)

class ServiceCategory(str, Enum):
    IOT_MANAGEMENT = "iot_management"
    SECURITY = "security"
    ANALYTICS = "analytics"
    AUTOMATION = "automation"
    MONITORING = "monitoring"
    COMMUNICATION = "communication"
    STORAGE = "storage"
    MACHINE_LEARNING = "machine_learning"
    BLOCKCHAIN = "blockchain"
    ENERGY = "energy"

class ServiceStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    BETA = "beta"
    DEVELOPMENT = "development"

class PricingModel(str, Enum):
    FREE = "free"
    FREEMIUM = "freemium"
    SUBSCRIPTION = "subscription"
    PAY_PER_USE = "pay_per_use"
    ONE_TIME = "one_time"

class ServiceType(str, Enum):
    APPLICATION = "application"
    API = "api"
    WIDGET = "widget"
    PLUGIN = "plugin"
    TEMPLATE = "template"
    LIBRARY = "library"

class MarketplaceService:
    """Service de marketplace pour les services IoT"""
    
    def __init__(self, db):
        self.db = db
        self.active_services = {}
        self.service_instances = {}
        self.user_subscriptions = {}
        self.revenue_tracking = {}
        self.is_initialized = False
        self._initialize()
    
    def _initialize(self):
        """Initialise le service de marketplace"""
        try:
            # Configuration par défaut
            self.config = {
                "commission_rate": 0.15,  # 15% de commission
                "free_tier_limit": 1000,  # Limite requêtes gratuites
                "max_services_per_user": 10,
                "review_required": True,
                "auto_approval_threshold": 0.8,
                "payout_threshold": 100.0,  # Seuil de paiement en QS
                "supported_languages": ["python", "javascript", "java", "go", "rust"],
                "max_service_size": 100 * 1024 * 1024,  # 100MB
            }
            
            # Initialiser les services prédéfinis
            asyncio.create_task(self._initialize_default_services())
            
            self.is_initialized = True
            logger.info("Service Marketplace initialisé")
            
        except Exception as e:
            logger.error(f"Erreur initialisation Marketplace: {str(e)}")
            self.is_initialized = False
    
    def is_ready(self) -> bool:
        """Vérifie si le service est prêt"""
        return self.is_initialized
    
    async def _initialize_default_services(self):
        """Initialise les services par défaut"""
        try:
            # Services système de base
            default_services = [
                {
                    "name": "Device Monitor Pro",
                    "category": ServiceCategory.MONITORING,
                    "description": "Surveillance avancée des dispositifs IoT avec alertes intelligentes",
                    "service_type": ServiceType.APPLICATION,
                    "pricing_model": PricingModel.FREEMIUM,
                    "price": 0.0,
                    "premium_price": 10.0,
                    "features": ["Monitoring temps réel", "Alertes avancées", "Tableaux de bord", "Historique"],
                    "provider": "QuantumShield",
                    "version": "1.0.0"
                },
                {
                    "name": "Crypto Analytics API",
                    "category": ServiceCategory.ANALYTICS,
                    "description": "API d'analyse des performances cryptographiques",
                    "service_type": ServiceType.API,
                    "pricing_model": PricingModel.PAY_PER_USE,
                    "price": 0.01,
                    "features": ["Analyse performance", "Benchmarking", "Comparaison algorithmes"],
                    "provider": "QuantumShield",
                    "version": "1.0.0"
                },
                {
                    "name": "Security Audit Suite",
                    "category": ServiceCategory.SECURITY,
                    "description": "Suite d'audit de sécurité pour dispositifs IoT",
                    "service_type": ServiceType.APPLICATION,
                    "pricing_model": PricingModel.SUBSCRIPTION,
                    "price": 25.0,
                    "features": ["Audit sécurité", "Vulnerability scanning", "Compliance check"],
                    "provider": "QuantumShield",
                    "version": "1.0.0"
                },
                {
                    "name": "ML Anomaly Detector",
                    "category": ServiceCategory.MACHINE_LEARNING,
                    "description": "Détecteur d'anomalies basé sur l'apprentissage automatique",
                    "service_type": ServiceType.API,
                    "pricing_model": PricingModel.FREEMIUM,
                    "price": 0.0,
                    "premium_price": 50.0,
                    "features": ["ML Detection", "Pattern Recognition", "Predictive Analytics"],
                    "provider": "QuantumShield",
                    "version": "1.0.0"
                },
                {
                    "name": "Energy Optimizer",
                    "category": ServiceCategory.ENERGY,
                    "description": "Optimisation de la consommation énergétique des dispositifs",
                    "service_type": ServiceType.APPLICATION,
                    "pricing_model": PricingModel.SUBSCRIPTION,
                    "price": 15.0,
                    "features": ["Optimisation énergie", "Reporting", "Recommandations"],
                    "provider": "QuantumShield",
                    "version": "1.0.0"
                }
            ]
            
            for service_data in default_services:
                existing = await self.db.marketplace_services.find_one({"name": service_data["name"]})
                if not existing:
                    await self._create_service_entry(service_data)
            
            logger.info("Services par défaut initialisés")
            
        except Exception as e:
            logger.error(f"Erreur initialisation services par défaut: {str(e)}")
    
    async def _create_service_entry(self, service_data: Dict[str, Any]) -> str:
        """Crée une entrée de service dans la base"""
        try:
            service_id = str(uuid.uuid4())
            
            service_entry = {
                "service_id": service_id,
                "name": service_data["name"],
                "description": service_data["description"],
                "category": service_data["category"].value if isinstance(service_data["category"], ServiceCategory) else service_data["category"],
                "service_type": service_data["service_type"].value if isinstance(service_data["service_type"], ServiceType) else service_data["service_type"],
                "pricing_model": service_data["pricing_model"].value if isinstance(service_data["pricing_model"], PricingModel) else service_data["pricing_model"],
                "price": service_data["price"],
                "premium_price": service_data.get("premium_price", 0.0),
                "features": service_data["features"],
                "provider": service_data["provider"],
                "provider_id": service_data.get("provider_id", "system"),
                "version": service_data["version"],
                "status": ServiceStatus.ACTIVE.value,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "downloads": 0,
                "active_users": 0,
                "revenue": 0.0,
                "rating": 0.0,
                "review_count": 0,
                "tags": service_data.get("tags", []),
                "requirements": service_data.get("requirements", []),
                "documentation": service_data.get("documentation", ""),
                "source_code": service_data.get("source_code", ""),
                "demo_url": service_data.get("demo_url", ""),
                "support_email": service_data.get("support_email", "support@quantumshield.tech")
            }
            
            await self.db.marketplace_services.insert_one(service_entry)
            
            return service_id
            
        except Exception as e:
            logger.error(f"Erreur création entrée service: {str(e)}")
            raise
    
    # ==============================
    # Gestion des services
    # ==============================
    
    async def publish_service(self,
                            name: str,
                            description: str,
                            category: ServiceCategory,
                            service_type: ServiceType,
                            pricing_model: PricingModel,
                            price: float,
                            features: List[str],
                            provider_id: str,
                            version: str = "1.0.0",
                            premium_price: Optional[float] = None,
                            source_code: Optional[str] = None,
                            documentation: Optional[str] = None,
                            requirements: Optional[List[str]] = None,
                            tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """Publie un nouveau service sur la marketplace"""
        try:
            # Vérifier les limites utilisateur
            user_service_count = await self.db.marketplace_services.count_documents({
                "provider_id": provider_id,
                "status": {"$ne": ServiceStatus.DEPRECATED.value}
            })
            
            if user_service_count >= self.config["max_services_per_user"]:
                return {
                    "success": False,
                    "error": f"Limite de {self.config['max_services_per_user']} services atteinte"
                }
            
            # Vérifier si le nom est unique
            existing = await self.db.marketplace_services.find_one({
                "name": name,
                "provider_id": provider_id
            })
            
            if existing:
                return {
                    "success": False,
                    "error": "Un service avec ce nom existe déjà"
                }
            
            # Créer l'entrée du service
            service_data = {
                "name": name,
                "description": description,
                "category": category,
                "service_type": service_type,
                "pricing_model": pricing_model,
                "price": price,
                "premium_price": premium_price or 0.0,
                "features": features,
                "provider": await self._get_provider_name(provider_id),
                "provider_id": provider_id,
                "version": version,
                "source_code": source_code or "",
                "documentation": documentation or "",
                "requirements": requirements or [],
                "tags": tags or []
            }
            
            service_id = await self._create_service_entry(service_data)
            
            # Déclencher le processus de review si nécessaire
            if self.config["review_required"]:
                await self._submit_for_review(service_id)
            
            logger.info(f"Service publié: {name} par {provider_id}")
            
            return {
                "success": True,
                "service_id": service_id,
                "name": name,
                "status": "pending_review" if self.config["review_required"] else "active"
            }
            
        except Exception as e:
            logger.error(f"Erreur publication service: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_provider_name(self, provider_id: str) -> str:
        """Récupère le nom du fournisseur"""
        try:
            if provider_id == "system":
                return "QuantumShield"
            
            # Récupérer depuis la base users
            user = await self.db.users.find_one({"id": provider_id})
            return user.get("username", "Unknown") if user else "Unknown"
            
        except Exception as e:
            logger.error(f"Erreur récupération nom fournisseur: {str(e)}")
            return "Unknown"
    
    async def _submit_for_review(self, service_id: str):
        """Soumet un service pour review"""
        try:
            review_data = {
                "review_id": str(uuid.uuid4()),
                "service_id": service_id,
                "status": "pending",
                "submitted_at": datetime.utcnow(),
                "reviewer_id": None,
                "review_notes": "",
                "score": 0.0,
                "automated_checks": await self._run_automated_checks(service_id)
            }
            
            await self.db.service_reviews.insert_one(review_data)
            
            # Auto-approuver si le score est suffisant
            if review_data["automated_checks"]["score"] >= self.config["auto_approval_threshold"]:
                await self._approve_service(service_id)
            
        except Exception as e:
            logger.error(f"Erreur soumission review: {str(e)}")
    
    async def _run_automated_checks(self, service_id: str) -> Dict[str, Any]:
        """Exécute les vérifications automatiques"""
        try:
            service = await self.db.marketplace_services.find_one({"service_id": service_id})
            if not service:
                return {"score": 0.0, "checks": []}
            
            checks = []
            score = 0.0
            max_score = 10.0
            
            # Vérification du nom
            if len(service["name"]) >= 5:
                checks.append({"check": "name_length", "passed": True, "points": 1.0})
                score += 1.0
            else:
                checks.append({"check": "name_length", "passed": False, "points": 0.0})
            
            # Vérification de la description
            if len(service["description"]) >= 50:
                checks.append({"check": "description_length", "passed": True, "points": 2.0})
                score += 2.0
            else:
                checks.append({"check": "description_length", "passed": False, "points": 0.0})
            
            # Vérification des features
            if len(service["features"]) >= 3:
                checks.append({"check": "features_count", "passed": True, "points": 1.0})
                score += 1.0
            else:
                checks.append({"check": "features_count", "passed": False, "points": 0.0})
            
            # Vérification de la documentation
            if len(service["documentation"]) >= 100:
                checks.append({"check": "documentation", "passed": True, "points": 2.0})
                score += 2.0
            else:
                checks.append({"check": "documentation", "passed": False, "points": 0.0})
            
            # Vérification du pricing
            if service["pricing_model"] != PricingModel.FREE.value or service["price"] > 0:
                checks.append({"check": "pricing_model", "passed": True, "points": 1.0})
                score += 1.0
            else:
                checks.append({"check": "pricing_model", "passed": False, "points": 0.0})
            
            # Vérification des tags
            if len(service["tags"]) >= 2:
                checks.append({"check": "tags", "passed": True, "points": 1.0})
                score += 1.0
            else:
                checks.append({"check": "tags", "passed": False, "points": 0.0})
            
            # Vérification de la version
            if service["version"] and "." in service["version"]:
                checks.append({"check": "version_format", "passed": True, "points": 1.0})
                score += 1.0
            else:
                checks.append({"check": "version_format", "passed": False, "points": 0.0})
            
            # Vérification du support
            if service["support_email"] and "@" in service["support_email"]:
                checks.append({"check": "support_contact", "passed": True, "points": 1.0})
                score += 1.0
            else:
                checks.append({"check": "support_contact", "passed": False, "points": 0.0})
            
            return {
                "score": score / max_score,
                "total_score": score,
                "max_score": max_score,
                "checks": checks
            }
            
        except Exception as e:
            logger.error(f"Erreur vérifications automatiques: {str(e)}")
            return {"score": 0.0, "checks": []}
    
    async def _approve_service(self, service_id: str):
        """Approuve un service"""
        try:
            await self.db.marketplace_services.update_one(
                {"service_id": service_id},
                {"$set": {"status": ServiceStatus.ACTIVE.value, "approved_at": datetime.utcnow()}}
            )
            
            await self.db.service_reviews.update_one(
                {"service_id": service_id},
                {"$set": {"status": "approved", "reviewed_at": datetime.utcnow()}}
            )
            
            logger.info(f"Service approuvé: {service_id}")
            
        except Exception as e:
            logger.error(f"Erreur approbation service: {str(e)}")
    
    async def search_services(self,
                            query: Optional[str] = None,
                            category: Optional[ServiceCategory] = None,
                            service_type: Optional[ServiceType] = None,
                            pricing_model: Optional[PricingModel] = None,
                            max_price: Optional[float] = None,
                            tags: Optional[List[str]] = None,
                            sort_by: str = "relevance",
                            limit: int = 20) -> List[Dict[str, Any]]:
        """Recherche des services dans la marketplace"""
        try:
            # Construire la requête
            search_query = {"status": ServiceStatus.ACTIVE.value}
            
            if query:
                search_query["$or"] = [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}},
                    {"tags": {"$regex": query, "$options": "i"}}
                ]
            
            if category:
                search_query["category"] = category.value
            
            if service_type:
                search_query["service_type"] = service_type.value
            
            if pricing_model:
                search_query["pricing_model"] = pricing_model.value
            
            if max_price is not None:
                search_query["price"] = {"$lte": max_price}
            
            if tags:
                search_query["tags"] = {"$in": tags}
            
            # Définir l'ordre de tri
            sort_order = []
            if sort_by == "price_asc":
                sort_order = [("price", 1)]
            elif sort_by == "price_desc":
                sort_order = [("price", -1)]
            elif sort_by == "rating":
                sort_order = [("rating", -1)]
            elif sort_by == "newest":
                sort_order = [("created_at", -1)]
            elif sort_by == "popular":
                sort_order = [("downloads", -1)]
            else:  # relevance
                sort_order = [("rating", -1), ("downloads", -1)]
            
            # Exécuter la recherche
            services = await self.db.marketplace_services.find(search_query).sort(sort_order).limit(limit).to_list(None)
            
            # Nettoyer les données
            result = []
            for service in services:
                service.pop("_id", None)
                service.pop("source_code", None)  # Ne pas exposer le code source
                result.append(service)
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur recherche services: {str(e)}")
            return []
    
    async def get_service_details(self, service_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les détails d'un service"""
        try:
            service = await self.db.marketplace_services.find_one({"service_id": service_id})
            if not service:
                return None
            
            # Nettoyer les données
            service.pop("_id", None)
            service.pop("source_code", None)  # Ne pas exposer le code source
            
            # Ajouter des statistiques
            service["reviews"] = await self._get_service_reviews(service_id)
            service["similar_services"] = await self._get_similar_services(service_id)
            
            return service
            
        except Exception as e:
            logger.error(f"Erreur récupération détails service: {str(e)}")
            return None
    
    async def _get_service_reviews(self, service_id: str) -> List[Dict[str, Any]]:
        """Récupère les reviews d'un service"""
        try:
            reviews = await self.db.service_user_reviews.find({"service_id": service_id}).sort("created_at", -1).limit(10).to_list(None)
            
            result = []
            for review in reviews:
                review.pop("_id", None)
                review.pop("user_id", None)  # Anonymiser
                result.append(review)
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur récupération reviews: {str(e)}")
            return []
    
    async def _get_similar_services(self, service_id: str) -> List[Dict[str, Any]]:
        """Récupère les services similaires"""
        try:
            # Récupérer le service de référence
            ref_service = await self.db.marketplace_services.find_one({"service_id": service_id})
            if not ref_service:
                return []
            
            # Chercher des services similaires
            similar = await self.db.marketplace_services.find({
                "service_id": {"$ne": service_id},
                "category": ref_service["category"],
                "status": ServiceStatus.ACTIVE.value
            }).limit(5).to_list(None)
            
            result = []
            for service in similar:
                service.pop("_id", None)
                service.pop("source_code", None)
                result.append({
                    "service_id": service["service_id"],
                    "name": service["name"],
                    "description": service["description"],
                    "price": service["price"],
                    "rating": service["rating"]
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur récupération services similaires: {str(e)}")
            return []
    
    # ==============================
    # Gestion des subscriptions
    # ==============================
    
    async def subscribe_to_service(self, user_id: str, service_id: str) -> Dict[str, Any]:
        """S'abonner à un service"""
        try:
            # Vérifier si le service existe
            service = await self.db.marketplace_services.find_one({"service_id": service_id})
            if not service:
                return {
                    "success": False,
                    "error": "Service non trouvé"
                }
            
            # Vérifier si l'utilisateur est déjà abonné
            existing_sub = await self.db.service_subscriptions.find_one({
                "user_id": user_id,
                "service_id": service_id,
                "status": "active"
            })
            
            if existing_sub:
                return {
                    "success": False,
                    "error": "Déjà abonné à ce service"
                }
            
            # Calculer le coût
            cost = service["price"] if service["pricing_model"] == PricingModel.SUBSCRIPTION.value else 0.0
            
            # Vérifier le solde utilisateur
            if cost > 0:
                user_balance = await self._get_user_balance(user_id)
                if user_balance < cost:
                    return {
                        "success": False,
                        "error": "Solde insuffisant"
                    }
            
            # Créer la subscription
            subscription_data = {
                "subscription_id": str(uuid.uuid4()),
                "user_id": user_id,
                "service_id": service_id,
                "service_name": service["name"],
                "pricing_model": service["pricing_model"],
                "price": service["price"],
                "status": "active",
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(days=30) if service["pricing_model"] == PricingModel.SUBSCRIPTION.value else None,
                "usage_count": 0,
                "usage_limit": self.config["free_tier_limit"] if service["pricing_model"] == PricingModel.FREE.value else None
            }
            
            await self.db.service_subscriptions.insert_one(subscription_data)
            
            # Débiter le compte utilisateur
            if cost > 0:
                await self._debit_user_account(user_id, cost, f"Abonnement à {service['name']}")
            
            # Créditer le fournisseur
            if cost > 0:
                commission = cost * self.config["commission_rate"]
                provider_revenue = cost - commission
                await self._credit_provider_account(service["provider_id"], provider_revenue)
            
            # Mettre à jour les statistiques
            await self.db.marketplace_services.update_one(
                {"service_id": service_id},
                {"$inc": {"active_users": 1}}
            )
            
            logger.info(f"Abonnement créé: {user_id} -> {service_id}")
            
            return {
                "success": True,
                "subscription_id": subscription_data["subscription_id"],
                "service_name": service["name"],
                "cost": cost,
                "expires_at": subscription_data["expires_at"]
            }
            
        except Exception as e:
            logger.error(f"Erreur abonnement service: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_user_balance(self, user_id: str) -> float:
        """Récupère le solde utilisateur"""
        try:
            user = await self.db.users.find_one({"id": user_id})
            return user.get("qs_balance", 0.0) if user else 0.0
            
        except Exception as e:
            logger.error(f"Erreur récupération solde: {str(e)}")
            return 0.0
    
    async def _debit_user_account(self, user_id: str, amount: float, description: str):
        """Débite le compte utilisateur"""
        try:
            # Débiter le solde
            await self.db.users.update_one(
                {"id": user_id},
                {"$inc": {"qs_balance": -amount}}
            )
            
            # Enregistrer la transaction
            transaction_data = {
                "transaction_id": str(uuid.uuid4()),
                "user_id": user_id,
                "amount": -amount,
                "type": "debit",
                "description": description,
                "timestamp": datetime.utcnow()
            }
            
            await self.db.marketplace_transactions.insert_one(transaction_data)
            
        except Exception as e:
            logger.error(f"Erreur débit compte: {str(e)}")
    
    async def _credit_provider_account(self, provider_id: str, amount: float):
        """Crédite le compte fournisseur"""
        try:
            # Créer ou mettre à jour le solde fournisseur
            await self.db.provider_earnings.update_one(
                {"provider_id": provider_id},
                {
                    "$inc": {"balance": amount, "total_earned": amount},
                    "$set": {"updated_at": datetime.utcnow()}
                },
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"Erreur crédit fournisseur: {str(e)}")
    
    # ==============================
    # Statistiques et analytics
    # ==============================
    
    async def get_marketplace_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques générales de la marketplace"""
        try:
            # Compter les services par statut
            total_services = await self.db.marketplace_services.count_documents({})
            active_services = await self.db.marketplace_services.count_documents({"status": ServiceStatus.ACTIVE.value})
            
            # Compter les abonnements actifs
            active_subscriptions = await self.db.service_subscriptions.count_documents({"status": "active"})
            
            # Calculer le chiffre d'affaires total
            total_revenue = await self.db.marketplace_transactions.aggregate([
                {"$match": {"type": "debit"}},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
            ]).to_list(None)
            
            revenue = abs(total_revenue[0]["total"]) if total_revenue else 0.0
            
            # Top catégories
            categories = await self.db.marketplace_services.aggregate([
                {"$match": {"status": ServiceStatus.ACTIVE.value}},
                {"$group": {"_id": "$category", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 5}
            ]).to_list(None)
            
            # Top services
            top_services = await self.db.marketplace_services.find({
                "status": ServiceStatus.ACTIVE.value
            }).sort("downloads", -1).limit(5).to_list(None)
            
            return {
                "total_services": total_services,
                "active_services": active_services,
                "active_subscriptions": active_subscriptions,
                "total_revenue": revenue,
                "commission_earned": revenue * self.config["commission_rate"],
                "top_categories": categories,
                "top_services": [
                    {
                        "service_id": s["service_id"],
                        "name": s["name"],
                        "downloads": s["downloads"],
                        "rating": s["rating"]
                    }
                    for s in top_services
                ]
            }
            
        except Exception as e:
            logger.error(f"Erreur récupération statistiques: {str(e)}")
            return {}
    
    async def get_user_subscriptions(self, user_id: str) -> List[Dict[str, Any]]:
        """Récupère les abonnements d'un utilisateur"""
        try:
            subscriptions = await self.db.service_subscriptions.find({"user_id": user_id}).sort("created_at", -1).to_list(None)
            
            result = []
            for sub in subscriptions:
                sub.pop("_id", None)
                result.append(sub)
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur récupération abonnements: {str(e)}")
            return []
    
    async def get_provider_earnings(self, provider_id: str) -> Dict[str, Any]:
        """Récupère les gains d'un fournisseur"""
        try:
            earnings = await self.db.provider_earnings.find_one({"provider_id": provider_id})
            
            if not earnings:
                return {
                    "provider_id": provider_id,
                    "balance": 0.0,
                    "total_earned": 0.0,
                    "services_published": 0
                }
            
            # Compter les services publiés
            services_count = await self.db.marketplace_services.count_documents({"provider_id": provider_id})
            
            earnings.pop("_id", None)
            earnings["services_published"] = services_count
            
            return earnings
            
        except Exception as e:
            logger.error(f"Erreur récupération gains fournisseur: {str(e)}")
            return {}
    
    async def shutdown(self):
        """Arrête le service marketplace"""
        try:
            self.active_services.clear()
            self.service_instances.clear()
            self.user_subscriptions.clear()
            
            logger.info("Service Marketplace arrêté")
            
        except Exception as e:
            logger.error(f"Erreur arrêt service Marketplace: {str(e)}")
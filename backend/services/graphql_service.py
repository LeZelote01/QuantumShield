"""
Service GraphQL pour QuantumShield
Fournit des queries complexes et des mutations pour tous les services
"""

import graphene
from graphene import ObjectType, String, Int, Float, Boolean, List, Field, Mutation, Schema, DateTime
from typing import Dict, Any, Optional, List as ListType
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

# ==============================
# Types GraphQL
# ==============================

class DeviceType(ObjectType):
    """Type GraphQL pour les devices"""
    device_id = String()
    device_name = String()
    device_type = String()
    owner_id = String()
    status = String()
    last_heartbeat = DateTime()
    firmware_hash = String()
    location = String()
    capabilities = List(String)
    created_at = DateTime()
    uptime_percentage = Float()
    total_heartbeats = Int()
    anomalies_count = Int()

class UserType(ObjectType):
    """Type GraphQL pour les utilisateurs"""
    id = String()
    username = String()
    email = String()
    qs_balance = Float()
    created_at = DateTime()
    reputation_score = Float()
    total_devices = Int()
    active_stakes = Int()
    total_earned = Float()

class TransactionType(ObjectType):
    """Type GraphQL pour les transactions blockchain"""
    hash = String()
    from_address = String()
    to_address = String()
    amount = Float()
    transaction_type = String()
    timestamp = DateTime()
    block_number = Int()
    status = String()

class ServiceType(ObjectType):
    """Type GraphQL pour les services marketplace"""
    service_id = String()
    name = String()
    description = String()
    category = String()
    service_type = String()
    pricing_model = String()
    price = Float()
    rating = Float()
    downloads = Int()
    active_users = Int()
    provider = String()
    created_at = DateTime()

class Query(ObjectType):
    """Queries GraphQL principales"""
    
    # Device queries
    device = Field(DeviceType, device_id=String(required=True))
    devices_by_user = List(DeviceType, user_id=String(required=True))
    devices_by_type = List(DeviceType, device_type=String(required=True))
    offline_devices = List(DeviceType)
    
    # User queries
    user = Field(UserType, user_id=String(required=True))
    users_by_reputation = List(UserType, min_reputation=Float())
    top_token_holders = List(UserType, limit=Int())
    
    # Marketplace queries
    service = Field(ServiceType, service_id=String(required=True))
    services_by_category = List(ServiceType, category=String(required=True))
    popular_services = List(ServiceType, limit=Int())
    
    # Complex aggregation queries
    system_overview = Field(String)
    user_portfolio = Field(String, user_id=String(required=True))
    device_analytics = Field(String, device_id=String(required=True))

class GraphQLService:
    """Service GraphQL pour QuantumShield"""
    
    def __init__(self, db, services_dict):
        self.db = db
        self.services = services_dict
        self.schema = Schema(query=Query)
        
        # Enregistrer les resolvers
        self._register_resolvers()
        
        logger.info("Service GraphQL initialisé")
    
    def _register_resolvers(self):
        """Enregistre les resolvers GraphQL"""
        
        # Device resolvers
        async def resolve_device(root, info, device_id):
            return await self._resolve_device(device_id)
        
        async def resolve_devices_by_user(root, info, user_id):
            return await self._resolve_devices_by_user(user_id)
        
        async def resolve_devices_by_type(root, info, device_type):
            return await self._resolve_devices_by_type(device_type)
        
        async def resolve_offline_devices(root, info):
            return await self._resolve_offline_devices()
        
        # User resolvers
        async def resolve_user(root, info, user_id):
            return await self._resolve_user(user_id)
        
        async def resolve_users_by_reputation(root, info, min_reputation=None):
            return await self._resolve_users_by_reputation(min_reputation)
        
        async def resolve_top_token_holders(root, info, limit=None):
            return await self._resolve_top_token_holders(limit)
        
        # Service resolvers
        async def resolve_service(root, info, service_id):
            return await self._resolve_service(service_id)
        
        async def resolve_services_by_category(root, info, category):
            return await self._resolve_services_by_category(category)
        
        async def resolve_popular_services(root, info, limit=None):
            return await self._resolve_popular_services(limit)
        
        # Complex resolvers
        async def resolve_system_overview(root, info):
            return await self._resolve_system_overview()
        
        async def resolve_user_portfolio(root, info, user_id):
            return await self._resolve_user_portfolio(user_id)
        
        async def resolve_device_analytics(root, info, device_id):
            return await self._resolve_device_analytics(device_id)
        
        # Assigner les resolvers
        Query.device = resolve_device
        Query.devices_by_user = resolve_devices_by_user
        Query.devices_by_type = resolve_devices_by_type
        Query.offline_devices = resolve_offline_devices
        Query.user = resolve_user
        Query.users_by_reputation = resolve_users_by_reputation
        Query.top_token_holders = resolve_top_token_holders
        Query.service = resolve_service
        Query.services_by_category = resolve_services_by_category
        Query.popular_services = resolve_popular_services
        Query.system_overview = resolve_system_overview
        Query.user_portfolio = resolve_user_portfolio
        Query.device_analytics = resolve_device_analytics
    
    # ==============================
    # Resolvers pour les devices
    # ==============================
    
    async def _resolve_device(self, device_id: str) -> Optional[DeviceType]:
        """Résout une query pour un device spécifique"""
        try:
            device_service = self.services.get('device_service')
            if not device_service:
                return None
                
            device = await device_service.get_device(device_id)
            if not device:
                return None
            
            # Enrichir avec des métriques
            metrics = await device_service.get_device_metrics(device_id)
            
            return DeviceType(
                device_id=device.device_id,
                device_name=device.device_name,
                device_type=device.device_type,
                owner_id=device.owner_id,
                status=device.status,
                last_heartbeat=device.last_heartbeat,
                firmware_hash=device.firmware_hash,
                location=device.location,
                capabilities=device.capabilities,
                created_at=device.created_at,
                uptime_percentage=metrics.get("uptime_percentage", 0),
                total_heartbeats=metrics.get("total_heartbeats", 0),
                anomalies_count=metrics.get("anomalies_detected", 0)
            )
            
        except Exception as e:
            logger.error(f"Erreur resolve_device: {e}")
            return None
    
    async def _resolve_devices_by_user(self, user_id: str) -> ListType[DeviceType]:
        """Résout une query pour les devices d'un utilisateur"""
        try:
            device_service = self.services.get('device_service')
            if not device_service:
                return []
                
            devices = await device_service.get_user_devices(user_id)
            
            result = []
            for device in devices:
                metrics = await device_service.get_device_metrics(device.device_id)
                
                result.append(DeviceType(
                    device_id=device.device_id,
                    device_name=device.device_name,
                    device_type=device.device_type,
                    owner_id=device.owner_id,
                    status=device.status,
                    last_heartbeat=device.last_heartbeat,
                    firmware_hash=device.firmware_hash,
                    location=device.location,
                    capabilities=device.capabilities,
                    created_at=device.created_at,
                    uptime_percentage=metrics.get("uptime_percentage", 0),
                    total_heartbeats=metrics.get("total_heartbeats", 0),
                    anomalies_count=metrics.get("anomalies_detected", 0)
                ))
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur resolve_devices_by_user: {e}")
            return []
    
    async def _resolve_devices_by_type(self, device_type: str) -> ListType[DeviceType]:
        """Résout une query pour les devices d'un type spécifique"""
        try:
            device_service = self.services.get('device_service')
            if not device_service:
                return []
                
            devices_data = await self.db.devices.find({"device_type": device_type}).to_list(None)
            
            result = []
            for device_data in devices_data:
                metrics = await device_service.get_device_metrics(device_data["device_id"])
                
                result.append(DeviceType(
                    device_id=device_data["device_id"],
                    device_name=device_data["device_name"],
                    device_type=device_data["device_type"],
                    owner_id=device_data["owner_id"],
                    status=device_data["status"],
                    last_heartbeat=device_data.get("last_heartbeat"),
                    firmware_hash=device_data["firmware_hash"],
                    location=device_data.get("location"),
                    capabilities=device_data.get("capabilities", []),
                    created_at=device_data["created_at"],
                    uptime_percentage=metrics.get("uptime_percentage", 0),
                    total_heartbeats=metrics.get("total_heartbeats", 0),
                    anomalies_count=metrics.get("anomalies_detected", 0)
                ))
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur resolve_devices_by_type: {e}")
            return []
    
    async def _resolve_offline_devices(self) -> ListType[DeviceType]:
        """Résout une query pour les devices hors ligne"""
        try:
            device_service = self.services.get('device_service')
            if not device_service:
                return []
                
            devices = await device_service.get_offline_devices()
            
            result = []
            for device in devices:
                metrics = await device_service.get_device_metrics(device.device_id)
                
                result.append(DeviceType(
                    device_id=device.device_id,
                    device_name=device.device_name,
                    device_type=device.device_type,
                    owner_id=device.owner_id,
                    status=device.status,
                    last_heartbeat=device.last_heartbeat,
                    firmware_hash=device.firmware_hash,
                    location=device.location,
                    capabilities=device.capabilities,
                    created_at=device.created_at,
                    uptime_percentage=metrics.get("uptime_percentage", 0),
                    total_heartbeats=metrics.get("total_heartbeats", 0),
                    anomalies_count=metrics.get("anomalies_detected", 0)
                ))
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur resolve_offline_devices: {e}")
            return []
    
    async def _resolve_user(self, user_id: str) -> Optional[UserType]:
        """Résout une query pour un utilisateur spécifique"""
        try:
            user_data = await self.db.users.find_one({"id": user_id})
            if not user_data:
                return None
            
            # Enrichir avec des statistiques
            device_count = await self.db.devices.count_documents({"owner_id": user_id})
            active_stakes = await self.db.staking_positions.count_documents({"user_id": user_id, "active": True})
            
            return UserType(
                id=user_data["id"],
                username=user_data["username"],
                email=user_data.get("email"),
                qs_balance=user_data.get("qs_balance", 0),
                created_at=user_data["created_at"],
                reputation_score=user_data.get("reputation_score", 0),
                total_devices=device_count,
                active_stakes=active_stakes,
                total_earned=user_data.get("total_earned", 0)
            )
            
        except Exception as e:
            logger.error(f"Erreur resolve_user: {e}")
            return None
    
    async def _resolve_users_by_reputation(self, min_reputation: Optional[float] = None) -> ListType[UserType]:
        """Résout une query pour les utilisateurs par réputation"""
        try:
            query = {}
            if min_reputation is not None:
                query["reputation_score"] = {"$gte": min_reputation}
            
            users_data = await self.db.users.find(query).sort("reputation_score", -1).limit(50).to_list(None)
            
            result = []
            for user_data in users_data:
                device_count = await self.db.devices.count_documents({"owner_id": user_data["id"]})
                active_stakes = await self.db.staking_positions.count_documents({"user_id": user_data["id"], "active": True})
                
                result.append(UserType(
                    id=user_data["id"],
                    username=user_data["username"],
                    email=user_data.get("email"),
                    qs_balance=user_data.get("qs_balance", 0),
                    created_at=user_data["created_at"],
                    reputation_score=user_data.get("reputation_score", 0),
                    total_devices=device_count,
                    active_stakes=active_stakes,
                    total_earned=user_data.get("total_earned", 0)
                ))
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur resolve_users_by_reputation: {e}")
            return []
    
    async def _resolve_top_token_holders(self, limit: Optional[int] = None) -> ListType[UserType]:
        """Résout une query pour les top holders de tokens"""
        try:
            limit = limit or 20
            users_data = await self.db.users.find({}).sort("qs_balance", -1).limit(limit).to_list(None)
            
            result = []
            for user_data in users_data:
                device_count = await self.db.devices.count_documents({"owner_id": user_data["id"]})
                active_stakes = await self.db.staking_positions.count_documents({"user_id": user_data["id"], "active": True})
                
                result.append(UserType(
                    id=user_data["id"],
                    username=user_data["username"],
                    email=user_data.get("email"),
                    qs_balance=user_data.get("qs_balance", 0),
                    created_at=user_data["created_at"],
                    reputation_score=user_data.get("reputation_score", 0),
                    total_devices=device_count,
                    active_stakes=active_stakes,
                    total_earned=user_data.get("total_earned", 0)
                ))
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur resolve_top_token_holders: {e}")
            return []
    
    async def _resolve_service(self, service_id: str) -> Optional[ServiceType]:
        """Résout une query pour un service spécifique"""
        try:
            service_data = await self.db.marketplace_services.find_one({"service_id": service_id})
            if not service_data:
                return None
            
            return ServiceType(
                service_id=service_data["service_id"],
                name=service_data["name"],
                description=service_data["description"],
                category=service_data["category"],
                service_type=service_data["service_type"],
                pricing_model=service_data["pricing_model"],
                price=service_data["price"],
                rating=service_data["rating"],
                downloads=service_data["downloads"],
                active_users=service_data["active_users"],
                provider=service_data["provider"],
                created_at=service_data["created_at"]
            )
            
        except Exception as e:
            logger.error(f"Erreur resolve_service: {e}")
            return None
    
    async def _resolve_services_by_category(self, category: str) -> ListType[ServiceType]:
        """Résout une query pour les services par catégorie"""
        try:
            services_data = await self.db.marketplace_services.find({"category": category}).to_list(None)
            
            result = []
            for service_data in services_data:
                result.append(ServiceType(
                    service_id=service_data["service_id"],
                    name=service_data["name"],
                    description=service_data["description"],
                    category=service_data["category"],
                    service_type=service_data["service_type"],
                    pricing_model=service_data["pricing_model"],
                    price=service_data["price"],
                    rating=service_data["rating"],
                    downloads=service_data["downloads"],
                    active_users=service_data["active_users"],
                    provider=service_data["provider"],
                    created_at=service_data["created_at"]
                ))
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur resolve_services_by_category: {e}")
            return []
    
    async def _resolve_popular_services(self, limit: Optional[int] = None) -> ListType[ServiceType]:
        """Résout une query pour les services populaires"""
        try:
            limit = limit or 10
            services_data = await self.db.marketplace_services.find({}).sort("downloads", -1).limit(limit).to_list(None)
            
            result = []
            for service_data in services_data:
                result.append(ServiceType(
                    service_id=service_data["service_id"],
                    name=service_data["name"],
                    description=service_data["description"],
                    category=service_data["category"],
                    service_type=service_data["service_type"],
                    pricing_model=service_data["pricing_model"],
                    price=service_data["price"],
                    rating=service_data["rating"],
                    downloads=service_data["downloads"],
                    active_users=service_data["active_users"],
                    provider=service_data["provider"],
                    created_at=service_data["created_at"]
                ))
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur resolve_popular_services: {e}")
            return []
    
    # ==============================
    # Resolvers complexes
    # ==============================
    
    async def _resolve_system_overview(self) -> str:
        """Résout une query pour un overview du système"""
        try:
            # Statistiques des devices
            total_devices = await self.db.devices.count_documents({})
            active_devices = await self.db.devices.count_documents({
                "last_heartbeat": {"$gte": datetime.utcnow() - timedelta(minutes=5)}
            })
            
            # Statistiques des utilisateurs
            total_users = await self.db.users.count_documents({})
            
            # Statistiques des anomalies
            recent_anomalies = await self.db.anomalies.count_documents({
                "timestamp": {"$gte": datetime.utcnow() - timedelta(hours=24)}
            })
            
            overview = {
                "devices": {
                    "total_devices": total_devices,
                    "active_devices": active_devices,
                    "offline_devices": total_devices - active_devices,
                    "uptime_percentage": (active_devices / total_devices * 100) if total_devices > 0 else 0
                },
                "users": {
                    "total_users": total_users
                },
                "security": {
                    "anomalies_24h": recent_anomalies
                }
            }
            
            return json.dumps(overview, default=str)
            
        except Exception as e:
            logger.error(f"Erreur resolve_system_overview: {e}")
            return json.dumps({"error": str(e)})
    
    async def _resolve_user_portfolio(self, user_id: str) -> str:
        """Résout une query pour le portfolio d'un utilisateur"""
        try:
            # Récupérer les données utilisateur
            user_data = await self.db.users.find_one({"id": user_id})
            if not user_data:
                return json.dumps({"error": "Utilisateur non trouvé"})
            
            # Devices de l'utilisateur
            device_service = self.services.get('device_service')
            user_devices = []
            if device_service:
                user_devices = await device_service.get_user_devices(user_id)
            
            # Positions de staking
            staking_positions = await self.db.staking_positions.find({"user_id": user_id, "active": True}).to_list(None)
            
            # Calcul du portefeuille
            total_staked = sum(pos.get("amount", 0) for pos in staking_positions)
            total_rewards = sum(pos.get("rewards_earned", 0) for pos in staking_positions)
            
            portfolio = {
                "user_info": {
                    "id": user_data["id"],
                    "username": user_data["username"],
                    "qs_balance": user_data.get("qs_balance", 0),
                    "reputation_score": user_data.get("reputation_score", 0)
                },
                "devices": {
                    "total_devices": len(user_devices),
                    "devices_by_type": {}
                },
                "staking": {
                    "total_staked": total_staked,
                    "total_rewards": total_rewards,
                    "active_positions": len(staking_positions)
                },
                "net_worth": user_data.get("qs_balance", 0) + total_staked + total_rewards
            }
            
            # Grouper devices par type
            for device in user_devices:
                device_type = device.device_type
                if device_type not in portfolio["devices"]["devices_by_type"]:
                    portfolio["devices"]["devices_by_type"][device_type] = 0
                portfolio["devices"]["devices_by_type"][device_type] += 1
            
            return json.dumps(portfolio, default=str)
            
        except Exception as e:
            logger.error(f"Erreur resolve_user_portfolio: {e}")
            return json.dumps({"error": str(e)})
    
    async def _resolve_device_analytics(self, device_id: str) -> str:
        """Résout une query pour l'analytique d'un device"""
        try:
            device_service = self.services.get('device_service')
            if not device_service:
                return json.dumps({"error": "Service device non disponible"})
            
            # Récupérer le device
            device = await device_service.get_device(device_id)
            if not device:
                return json.dumps({"error": "Device non trouvé"})
            
            # Métriques du device
            metrics = await device_service.get_device_metrics(device_id)
            
            # Anomalies récentes
            recent_anomalies = await self.db.anomalies.find({
                "device_id": device_id,
                "timestamp": {"$gte": datetime.utcnow() - timedelta(days=7)}
            }).sort("timestamp", -1).to_list(None)
            
            analytics = {
                "device_info": {
                    "device_id": device.device_id,
                    "device_name": device.device_name,
                    "device_type": device.device_type,
                    "status": device.status,
                    "firmware_hash": device.firmware_hash
                },
                "performance": {
                    "uptime_percentage": metrics.get("uptime_percentage", 0),
                    "total_heartbeats": metrics.get("total_heartbeats", 0),
                    "uptime_hours": metrics.get("uptime_hours", 0)
                },
                "security": {
                    "anomalies_count": len(recent_anomalies),
                    "last_anomaly": recent_anomalies[0]["timestamp"] if recent_anomalies else None,
                    "anomaly_types": list(set([a["anomaly_type"] for a in recent_anomalies]))
                }
            }
            
            return json.dumps(analytics, default=str)
            
        except Exception as e:
            logger.error(f"Erreur resolve_device_analytics: {e}")
            return json.dumps({"error": str(e)})
    
    def get_schema(self) -> Schema:
        """Retourne le schema GraphQL"""
        return self.schema
    
    async def execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Exécute une query GraphQL"""
        try:
            result = await self.schema.execute_async(query, variable_values=variables)
            return {
                "data": result.data,
                "errors": [str(error) for error in result.errors] if result.errors else None
            }
        except Exception as e:
            logger.error(f"Erreur exécution query GraphQL: {e}")
            return {
                "data": None,
                "errors": [str(e)]
            }
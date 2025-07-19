"""
Service API Gateway avec rate limiting pour QuantumShield
Gestion des quotas, authentification, monitoring et protection contre les abus
"""

import asyncio
import time
import hashlib
import uuid
import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import aiohttp
from fastapi import Request, HTTPException, status

logger = logging.getLogger(__name__)

class RateLimitType(str, Enum):
    PER_MINUTE = "per_minute"
    PER_HOUR = "per_hour"
    PER_DAY = "per_day"
    PER_MONTH = "per_month"

class APITier(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class RequestStatus(str, Enum):
    ALLOWED = "allowed"
    BLOCKED = "blocked"
    RATE_LIMITED = "rate_limited"

class APIGatewayService:
    """Service API Gateway avec rate limiting avancé"""
    
    def __init__(self, db):
        self.db = db
        self.is_initialized = False
        self.rate_limits = {}
        self.request_cache = defaultdict(list)
        self.blocked_ips = set()
        self.api_keys = {}
        
        # Configuration par défaut des tiers
        self.tier_limits = {
            APITier.FREE: {
                RateLimitType.PER_MINUTE: 10,
                RateLimitType.PER_HOUR: 100,
                RateLimitType.PER_DAY: 1000,
                RateLimitType.PER_MONTH: 10000
            },
            APITier.BASIC: {
                RateLimitType.PER_MINUTE: 50,
                RateLimitType.PER_HOUR: 1000,
                RateLimitType.PER_DAY: 10000,
                RateLimitType.PER_MONTH: 100000
            },
            APITier.PRO: {
                RateLimitType.PER_MINUTE: 200,
                RateLimitType.PER_HOUR: 5000,
                RateLimitType.PER_DAY: 50000,
                RateLimitType.PER_MONTH: 1000000
            },
            APITier.ENTERPRISE: {
                RateLimitType.PER_MINUTE: 1000,
                RateLimitType.PER_HOUR: 50000,
                RateLimitType.PER_DAY: 500000,
                RateLimitType.PER_MONTH: 10000000
            }
        }
        
        # Endpoints sensibles avec limites spéciales
        self.sensitive_endpoints = {
            "/api/auth/login": {RateLimitType.PER_MINUTE: 5},
            "/api/auth/register": {RateLimitType.PER_MINUTE: 3},
            "/api/crypto/generate-keys": {RateLimitType.PER_MINUTE: 20},
            "/api/mining/submit": {RateLimitType.PER_MINUTE: 100}
        }
        
        self._initialize()
    
    def _initialize(self):
        """Initialise le service API Gateway"""
        try:
            self.is_initialized = True
            logger.info("Service API Gateway initialisé")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation: {e}")
            self.is_initialized = False
    
    def is_ready(self) -> bool:
        """Vérifie si le service est prêt"""
        return self.is_initialized
    
    # ===== GESTION DES API KEYS =====
    
    async def create_api_key(self, user_id: str, tier: APITier, 
                           description: str = None) -> Dict[str, Any]:
        """Crée une nouvelle clé API"""
        try:
            # Générer une clé API sécurisée
            api_key = f"qs_{uuid.uuid4().hex}"
            api_secret = hashlib.sha256(f"{api_key}_{time.time()}".encode()).hexdigest()
            
            # Configuration de la clé
            key_config = {
                "api_key": api_key,
                "api_secret": api_secret,
                "user_id": user_id,
                "tier": tier.value,
                "description": description,
                "created_at": datetime.utcnow(),
                "last_used": None,
                "is_active": True,
                "usage_stats": {
                    "total_requests": 0,
                    "successful_requests": 0,
                    "failed_requests": 0,
                    "rate_limited_requests": 0
                },
                "rate_limits": self.tier_limits[tier].copy()
            }
            
            # Sauvegarder en base
            await self.db.api_keys.insert_one(key_config)
            
            # Mettre à jour le cache
            self.api_keys[api_key] = key_config
            
            return {
                "api_key": api_key,
                "api_secret": api_secret,
                "tier": tier.value,
                "rate_limits": key_config["rate_limits"],
                "created_at": key_config["created_at"]
            }
            
        except Exception as e:
            logger.error(f"Erreur création clé API: {e}")
            raise Exception(f"Impossible de créer la clé API: {e}")
    
    async def validate_api_key(self, api_key: str, api_secret: str = None) -> Optional[Dict[str, Any]]:
        """Valide une clé API"""
        try:
            # Vérifier dans le cache d'abord
            if api_key in self.api_keys:
                key_config = self.api_keys[api_key]
            else:
                # Chercher en base
                key_config = await self.db.api_keys.find_one({"api_key": api_key})
                if key_config:
                    self.api_keys[api_key] = key_config
            
            if not key_config or not key_config.get("is_active", False):
                return None
            
            # Vérifier le secret si fourni
            if api_secret and key_config.get("api_secret") != api_secret:
                return None
            
            # Mettre à jour la dernière utilisation
            await self.db.api_keys.update_one(
                {"api_key": api_key},
                {"$set": {"last_used": datetime.utcnow()}}
            )
            
            return key_config
            
        except Exception as e:
            logger.error(f"Erreur validation clé API: {e}")
            return None
    
    async def revoke_api_key(self, api_key: str, user_id: str) -> bool:
        """Révoque une clé API"""
        try:
            result = await self.db.api_keys.update_one(
                {"api_key": api_key, "user_id": user_id},
                {
                    "$set": {
                        "is_active": False,
                        "revoked_at": datetime.utcnow()
                    }
                }
            )
            
            # Supprimer du cache
            if api_key in self.api_keys:
                del self.api_keys[api_key]
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Erreur révocation clé API: {e}")
            return False
    
    # ===== RATE LIMITING =====
    
    def _get_rate_limit_key(self, identifier: str, endpoint: str, 
                           limit_type: RateLimitType) -> str:
        """Génère une clé pour le rate limiting"""
        return f"{identifier}:{endpoint}:{limit_type.value}"
    
    def _get_time_window(self, limit_type: RateLimitType) -> int:
        """Retourne la fenêtre de temps en secondes"""
        windows = {
            RateLimitType.PER_MINUTE: 60,
            RateLimitType.PER_HOUR: 3600,
            RateLimitType.PER_DAY: 86400,
            RateLimitType.PER_MONTH: 2592000  # 30 jours
        }
        return windows.get(limit_type, 60)
    
    async def check_rate_limit(self, request: Request, api_key: str = None) -> Tuple[bool, Dict[str, Any]]:
        """Vérifie les limites de taux pour une requête"""
        try:
            # Identifier l'utilisateur
            if api_key:
                key_config = await self.validate_api_key(api_key)
                if not key_config:
                    return False, {"error": "Clé API invalide", "status": RequestStatus.BLOCKED}
                
                identifier = api_key
                tier = APITier(key_config["tier"])
                user_limits = key_config.get("rate_limits", self.tier_limits[tier])
            else:
                # Utiliser l'IP comme identifiant pour les requêtes sans clé API
                identifier = request.client.host
                tier = APITier.FREE
                user_limits = self.tier_limits[tier]
            
            # Vérifier si l'IP est bloquée
            if identifier in self.blocked_ips:
                return False, {"error": "IP bloquée", "status": RequestStatus.BLOCKED}
            
            endpoint = request.url.path
            current_time = time.time()
            
            # Vérifier les limites pour l'endpoint spécifique
            endpoint_limits = self.sensitive_endpoints.get(endpoint, {})
            
            rate_limit_info = {
                "identifier": identifier,
                "endpoint": endpoint,
                "tier": tier.value,
                "limits": {},
                "current_usage": {},
                "reset_times": {}
            }
            
            # Vérifier chaque type de limite
            for limit_type in RateLimitType:
                # Déterminer la limite
                if limit_type in endpoint_limits:
                    limit = endpoint_limits[limit_type]
                else:
                    limit = user_limits.get(limit_type, self.tier_limits[tier][limit_type])
                
                # Calculer la fenêtre de temps
                window = self._get_time_window(limit_type)
                window_start = current_time - window
                
                # Clé de cache pour cette limite
                cache_key = self._get_rate_limit_key(identifier, endpoint, limit_type)
                
                # Nettoyer les anciennes requêtes
                if cache_key in self.request_cache:
                    self.request_cache[cache_key] = [
                        req_time for req_time in self.request_cache[cache_key]
                        if req_time > window_start
                    ]
                
                # Compter les requêtes actuelles
                current_count = len(self.request_cache[cache_key])
                
                # Informations pour la réponse
                rate_limit_info["limits"][limit_type.value] = limit
                rate_limit_info["current_usage"][limit_type.value] = current_count
                rate_limit_info["reset_times"][limit_type.value] = int(current_time + window)
                
                # Vérifier si la limite est dépassée
                if current_count >= limit:
                    # Mettre à jour les statistiques d'erreur
                    if api_key:
                        await self._update_api_key_stats(api_key, "rate_limited")
                    
                    return False, {
                        "error": f"Limite de taux dépassée pour {limit_type.value}",
                        "status": RequestStatus.RATE_LIMITED,
                        "rate_limit_info": rate_limit_info,
                        "retry_after": window
                    }
            
            # Toutes les limites sont respectées, enregistrer la requête
            for limit_type in RateLimitType:
                cache_key = self._get_rate_limit_key(identifier, endpoint, limit_type)
                self.request_cache[cache_key].append(current_time)
            
            # Mettre à jour les statistiques de succès
            if api_key:
                await self._update_api_key_stats(api_key, "success")
            
            return True, {
                "status": RequestStatus.ALLOWED,
                "rate_limit_info": rate_limit_info
            }
            
        except Exception as e:
            logger.error(f"Erreur vérification rate limit: {e}")
            return False, {"error": "Erreur interne", "status": RequestStatus.BLOCKED}
    
    async def _update_api_key_stats(self, api_key: str, result_type: str):
        """Met à jour les statistiques d'utilisation d'une clé API"""
        try:
            update_fields = {
                "usage_stats.total_requests": 1
            }
            
            if result_type == "success":
                update_fields["usage_stats.successful_requests"] = 1
            elif result_type == "error":
                update_fields["usage_stats.failed_requests"] = 1
            elif result_type == "rate_limited":
                update_fields["usage_stats.rate_limited_requests"] = 1
            
            await self.db.api_keys.update_one(
                {"api_key": api_key},
                {"$inc": update_fields}
            )
            
        except Exception as e:
            logger.error(f"Erreur mise à jour stats API key: {e}")
    
    # ===== GESTION DES BLOCAGES =====
    
    async def block_ip(self, ip_address: str, reason: str, duration_hours: int = 24) -> bool:
        """Bloque une adresse IP"""
        try:
            self.blocked_ips.add(ip_address)
            
            # Enregistrer en base
            block_record = {
                "ip_address": ip_address,
                "reason": reason,
                "blocked_at": datetime.utcnow(),
                "unblock_at": datetime.utcnow() + timedelta(hours=duration_hours),
                "is_active": True
            }
            
            await self.db.blocked_ips.insert_one(block_record)
            
            logger.warning(f"IP {ip_address} bloquée: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur blocage IP: {e}")
            return False
    
    async def unblock_ip(self, ip_address: str) -> bool:
        """Débloque une adresse IP"""
        try:
            self.blocked_ips.discard(ip_address)
            
            await self.db.blocked_ips.update_many(
                {"ip_address": ip_address, "is_active": True},
                {"$set": {"is_active": False, "unblocked_at": datetime.utcnow()}}
            )
            
            logger.info(f"IP {ip_address} débloquée")
            return True
            
        except Exception as e:
            logger.error(f"Erreur déblocage IP: {e}")
            return False
    
    # ===== ANALYTICS ET MONITORING =====
    
    async def get_api_usage_stats(self, user_id: str = None, 
                                 start_date: datetime = None,
                                 end_date: datetime = None) -> Dict[str, Any]:
        """Récupère les statistiques d'utilisation de l'API"""
        try:
            # Critères de recherche
            criteria = {}
            if user_id:
                criteria["user_id"] = user_id
            
            # Récupérer les clés API
            api_keys = await self.db.api_keys.find(criteria).to_list(None)
            
            # Analyser les statistiques
            total_stats = {
                "total_keys": len(api_keys),
                "active_keys": len([k for k in api_keys if k.get("is_active", False)]),
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "rate_limited_requests": 0
            }
            
            tier_stats = defaultdict(lambda: {
                "count": 0,
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "rate_limited_requests": 0
            })
            
            for key_config in api_keys:
                tier = key_config.get("tier", "free")
                usage = key_config.get("usage_stats", {})
                
                tier_stats[tier]["count"] += 1
                
                for stat_type in ["total_requests", "successful_requests", "failed_requests", "rate_limited_requests"]:
                    value = usage.get(stat_type, 0)
                    total_stats[stat_type] += value
                    tier_stats[tier][stat_type] += value
            
            return {
                "overview": total_stats,
                "by_tier": dict(tier_stats),
                "top_api_keys": sorted(
                    api_keys,
                    key=lambda x: x.get("usage_stats", {}).get("total_requests", 0),
                    reverse=True
                )[:10]
            }
            
        except Exception as e:
            logger.error(f"Erreur stats API: {e}")
            return {"overview": {}, "by_tier": {}, "top_api_keys": []}
    
    async def get_rate_limit_violations(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Récupère les violations de rate limiting récentes"""
        try:
            # Pour la démo, on retourne quelques violations simulées
            violations = []
            
            # En réalité, on pourrait avoir une collection dédiée pour les violations
            # ou analyser les logs
            
            return violations
            
        except Exception as e:
            logger.error(f"Erreur récupération violations: {e}")
            return []
    
    async def get_gateway_health(self) -> Dict[str, Any]:
        """Récupère l'état de santé de l'API Gateway"""
        try:
            current_time = datetime.utcnow()
            
            # Compter les requêtes récentes
            recent_requests = sum(
                len([req for req in requests if req > time.time() - 300])  # 5 minutes
                for requests in self.request_cache.values()
            )
            
            # Compter les IPs bloquées
            blocked_count = len(self.blocked_ips)
            
            # Compter les clés API actives
            active_keys = await self.db.api_keys.count_documents({"is_active": True})
            
            return {
                "status": "healthy" if self.is_ready() else "unhealthy",
                "current_time": current_time,
                "recent_requests_5min": recent_requests,
                "blocked_ips": blocked_count,
                "active_api_keys": active_keys,
                "cache_size": len(self.request_cache),
                "memory_usage": {
                    "request_cache_entries": sum(len(reqs) for reqs in self.request_cache.values()),
                    "api_keys_cached": len(self.api_keys)
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur health check gateway: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    # ===== CONFIGURATION =====
    
    async def update_rate_limits(self, tier: APITier, new_limits: Dict[str, int]) -> bool:
        """Met à jour les limites de taux pour un tier"""
        try:
            # Valider les nouvelles limites
            for limit_type, value in new_limits.items():
                if limit_type not in [lt.value for lt in RateLimitType]:
                    raise ValueError(f"Type de limite invalide: {limit_type}")
                if value < 0:
                    raise ValueError(f"Valeur invalide: {value}")
            
            # Mettre à jour la configuration
            for limit_type, value in new_limits.items():
                self.tier_limits[tier][RateLimitType(limit_type)] = value
            
            # Mettre à jour les clés API existantes de ce tier
            await self.db.api_keys.update_many(
                {"tier": tier.value},
                {"$set": {f"rate_limits.{limit_type}": value for limit_type, value in new_limits.items()}}
            )
            
            logger.info(f"Limites mises à jour pour tier {tier.value}: {new_limits}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur mise à jour limites: {e}")
            return False
    
    async def add_sensitive_endpoint(self, endpoint: str, limits: Dict[str, int]) -> bool:
        """Ajoute un endpoint avec des limites spéciales"""
        try:
            # Valider les limites
            validated_limits = {}
            for limit_type, value in limits.items():
                if limit_type in [lt.value for lt in RateLimitType]:
                    validated_limits[RateLimitType(limit_type)] = value
            
            self.sensitive_endpoints[endpoint] = validated_limits
            
            logger.info(f"Endpoint sensible ajouté: {endpoint} avec limites {validated_limits}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur ajout endpoint sensible: {e}")
            return False
    
    # ===== PROXY ET LOAD BALANCING =====
    
    async def proxy_request(self, request_data: Dict[str, Any], 
                          target_service: str) -> Dict[str, Any]:
        """Proxifie une requête vers un service backend"""
        try:
            # Configuration des services backend
            services = {
                "crypto": "http://localhost:8001/api/crypto",
                "blockchain": "http://localhost:8001/api/blockchain",
                "devices": "http://localhost:8001/api/devices",
                "tokens": "http://localhost:8001/api/tokens"
            }
            
            if target_service not in services:
                raise ValueError(f"Service non supporté: {target_service}")
            
            base_url = services[target_service]
            endpoint = request_data.get("endpoint", "")
            method = request_data.get("method", "GET").upper()
            headers = request_data.get("headers", {})
            data = request_data.get("data")
            
            # Effectuer la requête
            async with aiohttp.ClientSession() as session:
                url = f"{base_url}{endpoint}"
                
                if method == "GET":
                    async with session.get(url, headers=headers) as response:
                        result = await response.json()
                        status_code = response.status
                elif method == "POST":
                    async with session.post(url, headers=headers, json=data) as response:
                        result = await response.json()
                        status_code = response.status
                elif method == "PUT":
                    async with session.put(url, headers=headers, json=data) as response:
                        result = await response.json()
                        status_code = response.status
                elif method == "DELETE":
                    async with session.delete(url, headers=headers) as response:
                        result = await response.json()
                        status_code = response.status
                else:
                    raise ValueError(f"Méthode HTTP non supportée: {method}")
                
                return {
                    "status_code": status_code,
                    "data": result,
                    "target_service": target_service,
                    "proxied_at": datetime.utcnow()
                }
                
        except Exception as e:
            logger.error(f"Erreur proxy requête: {e}")
            return {
                "status_code": 500,
                "error": str(e),
                "target_service": target_service
            }
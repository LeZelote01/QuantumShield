"""
Service de Webhooks pour QuantumShield
Gère les notifications en temps réel et les intégrations externes
"""

import asyncio
import aiohttp
import json
import logging
import hashlib
import hmac
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
import secrets
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class WebhookStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISABLED = "disabled"
    FAILED = "failed"

class WebhookEvent(str, Enum):
    DEVICE_REGISTERED = "device.registered"
    DEVICE_OFFLINE = "device.offline"
    DEVICE_ANOMALY = "device.anomaly"
    DEVICE_HEARTBEAT = "device.heartbeat"
    USER_REGISTERED = "user.registered"
    TOKEN_TRANSFER = "token.transfer"
    BLOCK_MINED = "block.mined"
    TRANSACTION_CONFIRMED = "transaction.confirmed"
    SERVICE_PURCHASED = "service.purchased"
    STAKING_REWARD = "staking.reward"
    SECURITY_ALERT = "security.alert"
    FIRMWARE_UPDATE = "firmware.update"
    CERTIFICATE_EXPIRING = "certificate.expiring"

class WebhookDeliveryStatus(str, Enum):
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"

class WebhookService:
    """Service de gestion des webhooks"""
    
    def __init__(self, db):
        self.db = db
        self.active_webhooks = {}
        self.event_handlers = {}
        self.retry_config = {
            "max_retries": 3,
            "retry_delays": [5, 30, 300],  # 5s, 30s, 5min
            "timeout": 30
        }
        self.is_initialized = False
        self._initialize()
    
    def _initialize(self):
        """Initialise le service de webhooks"""
        try:
            # Enregistrer les handlers d'événements
            self._register_event_handlers()
            
            # Charger les webhooks actifs
            asyncio.create_task(self._load_active_webhooks())
            
            # Démarrer les workers de retry
            asyncio.create_task(self._start_retry_workers())
            
            self.is_initialized = True
            logger.info("Service Webhooks initialisé")
            
        except Exception as e:
            logger.error(f"Erreur initialisation Webhooks: {str(e)}")
            self.is_initialized = False
    
    def is_ready(self) -> bool:
        """Vérifie si le service est prêt"""
        return self.is_initialized
    
    def _register_event_handlers(self):
        """Enregistre les handlers d'événements"""
        try:
            # Handlers pour les événements système
            self.event_handlers = {
                WebhookEvent.DEVICE_REGISTERED: self._handle_device_registered,
                WebhookEvent.DEVICE_OFFLINE: self._handle_device_offline,
                WebhookEvent.DEVICE_ANOMALY: self._handle_device_anomaly,
                WebhookEvent.DEVICE_HEARTBEAT: self._handle_device_heartbeat,
                WebhookEvent.USER_REGISTERED: self._handle_user_registered,
                WebhookEvent.TOKEN_TRANSFER: self._handle_token_transfer,
                WebhookEvent.BLOCK_MINED: self._handle_block_mined,
                WebhookEvent.TRANSACTION_CONFIRMED: self._handle_transaction_confirmed,
                WebhookEvent.SERVICE_PURCHASED: self._handle_service_purchased,
                WebhookEvent.STAKING_REWARD: self._handle_staking_reward,
                WebhookEvent.SECURITY_ALERT: self._handle_security_alert,
                WebhookEvent.FIRMWARE_UPDATE: self._handle_firmware_update,
                WebhookEvent.CERTIFICATE_EXPIRING: self._handle_certificate_expiring
            }
            
            logger.info("Handlers d'événements enregistrés")
            
        except Exception as e:
            logger.error(f"Erreur enregistrement handlers: {str(e)}")
    
    async def _load_active_webhooks(self):
        """Charge les webhooks actifs depuis la base de données"""
        try:
            webhooks = await self.db.webhooks.find({"status": WebhookStatus.ACTIVE.value}).to_list(None)
            
            for webhook in webhooks:
                self.active_webhooks[webhook["webhook_id"]] = webhook
            
            logger.info(f"Chargé {len(webhooks)} webhooks actifs")
            
        except Exception as e:
            logger.error(f"Erreur chargement webhooks: {str(e)}")
    
    async def _start_retry_workers(self):
        """Démarre les workers de retry"""
        try:
            # Worker pour les retries
            asyncio.create_task(self._retry_worker())
            
            # Worker pour nettoyer les anciens logs
            asyncio.create_task(self._cleanup_worker())
            
            logger.info("Workers de retry démarrés")
            
        except Exception as e:
            logger.error(f"Erreur démarrage workers: {str(e)}")
    
    # ==============================
    # Gestion des webhooks
    # ==============================
    
    async def register_webhook(self,
                             url: str,
                             events: List[WebhookEvent],
                             user_id: str,
                             secret: Optional[str] = None,
                             headers: Optional[Dict[str, str]] = None,
                             name: Optional[str] = None) -> Dict[str, Any]:
        """Enregistre un nouveau webhook"""
        try:
            # Valider l'URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return {
                    "success": False,
                    "error": "URL invalide"
                }
            
            # Générer un secret si non fourni
            if not secret:
                secret = secrets.token_urlsafe(32)
            
            # Créer le webhook
            webhook_id = str(uuid.uuid4())
            webhook_data = {
                "webhook_id": webhook_id,
                "url": url,
                "events": [event.value for event in events],
                "user_id": user_id,
                "secret": secret,
                "headers": headers or {},
                "name": name or f"Webhook {webhook_id[:8]}",
                "status": WebhookStatus.ACTIVE.value,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "last_ping": None,
                "success_count": 0,
                "failure_count": 0,
                "total_deliveries": 0
            }
            
            # Sauvegarder en base
            await self.db.webhooks.insert_one(webhook_data)
            
            # Ajouter aux webhooks actifs
            self.active_webhooks[webhook_id] = webhook_data
            
            logger.info(f"Webhook enregistré: {webhook_id} pour {user_id}")
            
            return {
                "success": True,
                "webhook_id": webhook_id,
                "url": url,
                "events": [event.value for event in events],
                "secret": secret
            }
            
        except Exception as e:
            logger.error(f"Erreur enregistrement webhook: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_webhook(self,
                           webhook_id: str,
                           url: Optional[str] = None,
                           events: Optional[List[WebhookEvent]] = None,
                           status: Optional[WebhookStatus] = None,
                           headers: Optional[Dict[str, str]] = None,
                           name: Optional[str] = None) -> Dict[str, Any]:
        """Met à jour un webhook"""
        try:
            # Récupérer le webhook
            webhook = await self.db.webhooks.find_one({"webhook_id": webhook_id})
            if not webhook:
                return {
                    "success": False,
                    "error": "Webhook non trouvé"
                }
            
            # Préparer les mises à jour
            updates = {"updated_at": datetime.utcnow()}
            
            if url:
                parsed_url = urlparse(url)
                if not parsed_url.scheme or not parsed_url.netloc:
                    return {
                        "success": False,
                        "error": "URL invalide"
                    }
                updates["url"] = url
            
            if events:
                updates["events"] = [event.value for event in events]
            
            if status:
                updates["status"] = status.value
            
            if headers is not None:
                updates["headers"] = headers
            
            if name:
                updates["name"] = name
            
            # Mettre à jour en base
            await self.db.webhooks.update_one(
                {"webhook_id": webhook_id},
                {"$set": updates}
            )
            
            # Mettre à jour le cache
            if webhook_id in self.active_webhooks:
                self.active_webhooks[webhook_id].update(updates)
            
            # Si le webhook est désactivé, le retirer du cache
            if status == WebhookStatus.INACTIVE:
                self.active_webhooks.pop(webhook_id, None)
            elif status == WebhookStatus.ACTIVE:
                updated_webhook = await self.db.webhooks.find_one({"webhook_id": webhook_id})
                self.active_webhooks[webhook_id] = updated_webhook
            
            logger.info(f"Webhook mis à jour: {webhook_id}")
            
            return {
                "success": True,
                "webhook_id": webhook_id,
                "updates": updates
            }
            
        except Exception as e:
            logger.error(f"Erreur mise à jour webhook: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_webhook(self, webhook_id: str) -> Dict[str, Any]:
        """Supprime un webhook"""
        try:
            # Supprimer de la base
            result = await self.db.webhooks.delete_one({"webhook_id": webhook_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": "Webhook non trouvé"
                }
            
            # Supprimer du cache
            self.active_webhooks.pop(webhook_id, None)
            
            logger.info(f"Webhook supprimé: {webhook_id}")
            
            return {
                "success": True,
                "webhook_id": webhook_id
            }
            
        except Exception as e:
            logger.error(f"Erreur suppression webhook: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_webhook(self, webhook_id: str) -> Dict[str, Any]:
        """Test un webhook avec un événement de test"""
        try:
            webhook = await self.db.webhooks.find_one({"webhook_id": webhook_id})
            if not webhook:
                return {
                    "success": False,
                    "error": "Webhook non trouvé"
                }
            
            # Créer un événement de test
            test_event = {
                "event": "webhook.test",
                "timestamp": datetime.utcnow(),
                "data": {
                    "webhook_id": webhook_id,
                    "message": "Test webhook from QuantumShield"
                }
            }
            
            # Envoyer l'événement
            delivery_result = await self._deliver_webhook(webhook, test_event)
            
            # Mettre à jour le last_ping
            await self.db.webhooks.update_one(
                {"webhook_id": webhook_id},
                {"$set": {"last_ping": datetime.utcnow()}}
            )
            
            return {
                "success": delivery_result["success"],
                "webhook_id": webhook_id,
                "delivery_result": delivery_result
            }
            
        except Exception as e:
            logger.error(f"Erreur test webhook: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def list_webhooks(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Liste les webhooks"""
        try:
            query = {}
            if user_id:
                query["user_id"] = user_id
            
            webhooks = await self.db.webhooks.find(query).sort("created_at", -1).to_list(None)
            
            # Nettoyer les données sensibles
            result = []
            for webhook in webhooks:
                webhook.pop("_id", None)
                webhook.pop("secret", None)  # Ne pas exposer le secret
                result.append(webhook)
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur liste webhooks: {str(e)}")
            return []
    
    # ==============================
    # Émission d'événements
    # ==============================
    
    async def emit_event(self, event_type: WebhookEvent, data: Dict[str, Any]):
        """Émet un événement vers tous les webhooks concernés"""
        try:
            # Traiter l'événement avec le handler approprié
            if event_type in self.event_handlers:
                processed_data = await self.event_handlers[event_type](data)
            else:
                processed_data = data
            
            # Créer l'événement
            event_payload = {
                "event": event_type.value,
                "timestamp": datetime.utcnow(),
                "data": processed_data
            }
            
            # Trouver les webhooks concernés
            relevant_webhooks = [
                webhook for webhook in self.active_webhooks.values()
                if event_type.value in webhook["events"]
            ]
            
            # Envoyer à chaque webhook
            for webhook in relevant_webhooks:
                asyncio.create_task(
                    self._deliver_webhook_with_retry(webhook, event_payload)
                )
            
            logger.info(f"Événement émis: {event_type.value} vers {len(relevant_webhooks)} webhooks")
            
        except Exception as e:
            logger.error(f"Erreur émission événement: {str(e)}")
    
    async def _deliver_webhook_with_retry(self, webhook: Dict[str, Any], event_payload: Dict[str, Any]):
        """Délivre un webhook avec système de retry"""
        try:
            # Créer l'entrée de livraison
            delivery_id = str(uuid.uuid4())
            delivery_data = {
                "delivery_id": delivery_id,
                "webhook_id": webhook["webhook_id"],
                "event": event_payload["event"],
                "payload": event_payload,
                "status": WebhookDeliveryStatus.PENDING.value,
                "created_at": datetime.utcnow(),
                "retry_count": 0,
                "next_retry": datetime.utcnow(),
                "last_error": None
            }
            
            await self.db.webhook_deliveries.insert_one(delivery_data)
            
            # Tenter la livraison
            delivery_result = await self._deliver_webhook(webhook, event_payload)
            
            # Mettre à jour le statut
            if delivery_result["success"]:
                await self.db.webhook_deliveries.update_one(
                    {"delivery_id": delivery_id},
                    {"$set": {
                        "status": WebhookDeliveryStatus.DELIVERED.value,
                        "delivered_at": datetime.utcnow(),
                        "response_status": delivery_result.get("status_code"),
                        "response_time": delivery_result.get("response_time")
                    }}
                )
                
                # Incrémenter les compteurs de succès
                await self.db.webhooks.update_one(
                    {"webhook_id": webhook["webhook_id"]},
                    {"$inc": {"success_count": 1, "total_deliveries": 1}}
                )
            else:
                # Programmer le retry
                await self.db.webhook_deliveries.update_one(
                    {"delivery_id": delivery_id},
                    {"$set": {
                        "status": WebhookDeliveryStatus.RETRYING.value,
                        "last_error": delivery_result.get("error"),
                        "next_retry": datetime.utcnow() + timedelta(seconds=self.retry_config["retry_delays"][0])
                    }}
                )
            
        except Exception as e:
            logger.error(f"Erreur livraison webhook: {str(e)}")
    
    async def _deliver_webhook(self, webhook: Dict[str, Any], event_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Délivre un webhook à une URL"""
        try:
            # Préparer les headers
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "QuantumShield-Webhook/1.0",
                "X-Webhook-Event": event_payload["event"],
                "X-Webhook-Delivery": str(uuid.uuid4()),
                "X-Webhook-Timestamp": str(int(datetime.utcnow().timestamp()))
            }
            
            # Ajouter les headers personnalisés
            if webhook.get("headers"):
                headers.update(webhook["headers"])
            
            # Préparer le payload
            payload = json.dumps(event_payload, default=str)
            
            # Générer la signature
            if webhook.get("secret"):
                signature = hmac.new(
                    webhook["secret"].encode(),
                    payload.encode(),
                    hashlib.sha256
                ).hexdigest()
                headers["X-Webhook-Signature"] = f"sha256={signature}"
            
            # Envoyer la requête
            start_time = datetime.utcnow()
            
            timeout = aiohttp.ClientTimeout(total=self.retry_config["timeout"])
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    webhook["url"],
                    data=payload,
                    headers=headers
                ) as response:
                    response_time = (datetime.utcnow() - start_time).total_seconds()
                    
                    if response.status >= 200 and response.status < 300:
                        return {
                            "success": True,
                            "status_code": response.status,
                            "response_time": response_time
                        }
                    else:
                        return {
                            "success": False,
                            "status_code": response.status,
                            "response_time": response_time,
                            "error": f"HTTP {response.status}"
                        }
            
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # ==============================
    # Handlers d'événements
    # ==============================
    
    async def _handle_device_registered(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler pour l'événement device registered"""
        return {
            "device_id": data.get("device_id"),
            "device_name": data.get("device_name"),
            "device_type": data.get("device_type"),
            "owner_id": data.get("owner_id"),
            "location": data.get("location"),
            "capabilities": data.get("capabilities"),
            "registered_at": data.get("created_at")
        }
    
    async def _handle_device_offline(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler pour l'événement device offline"""
        return {
            "device_id": data.get("device_id"),
            "device_name": data.get("device_name"),
            "last_heartbeat": data.get("last_heartbeat"),
            "offline_duration": data.get("offline_duration")
        }
    
    async def _handle_device_anomaly(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler pour l'événement device anomaly"""
        return {
            "device_id": data.get("device_id"),
            "anomaly_type": data.get("anomaly_type"),
            "severity": data.get("severity"),
            "description": data.get("description"),
            "detected_at": data.get("timestamp"),
            "sensor_data": data.get("sensor_data")
        }
    
    async def _handle_device_heartbeat(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler pour l'événement device heartbeat"""
        return {
            "device_id": data.get("device_id"),
            "status": data.get("status"),
            "sensor_data": data.get("sensor_data"),
            "firmware_hash": data.get("firmware_hash"),
            "heartbeat_at": data.get("timestamp")
        }
    
    async def _handle_user_registered(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler pour l'événement user registered"""
        return {
            "user_id": data.get("user_id"),
            "username": data.get("username"),
            "email": data.get("email"),
            "registered_at": data.get("created_at")
        }
    
    async def _handle_token_transfer(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler pour l'événement token transfer"""
        return {
            "transaction_hash": data.get("transaction_hash"),
            "from_address": data.get("from_address"),
            "to_address": data.get("to_address"),
            "amount": data.get("amount"),
            "token_type": data.get("token_type", "QS"),
            "transferred_at": data.get("timestamp")
        }
    
    async def _handle_block_mined(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler pour l'événement block mined"""
        return {
            "block_number": data.get("block_number"),
            "block_hash": data.get("block_hash"),
            "miner_address": data.get("miner_address"),
            "transactions_count": data.get("transactions_count"),
            "difficulty": data.get("difficulty"),
            "mined_at": data.get("timestamp")
        }
    
    async def _handle_transaction_confirmed(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler pour l'événement transaction confirmed"""
        return {
            "transaction_hash": data.get("transaction_hash"),
            "from_address": data.get("from_address"),
            "to_address": data.get("to_address"),
            "amount": data.get("amount"),
            "block_number": data.get("block_number"),
            "confirmed_at": data.get("timestamp")
        }
    
    async def _handle_service_purchased(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler pour l'événement service purchased"""
        return {
            "service_id": data.get("service_id"),
            "service_name": data.get("service_name"),
            "buyer_id": data.get("buyer_id"),
            "provider_id": data.get("provider_id"),
            "price": data.get("price"),
            "purchased_at": data.get("timestamp")
        }
    
    async def _handle_staking_reward(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler pour l'événement staking reward"""
        return {
            "user_id": data.get("user_id"),
            "stake_id": data.get("stake_id"),
            "reward_amount": data.get("reward_amount"),
            "pool_id": data.get("pool_id"),
            "reward_type": data.get("reward_type"),
            "rewarded_at": data.get("timestamp")
        }
    
    async def _handle_security_alert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler pour l'événement security alert"""
        return {
            "alert_type": data.get("alert_type"),
            "severity": data.get("severity"),
            "description": data.get("description"),
            "affected_resource": data.get("affected_resource"),
            "triggered_at": data.get("timestamp")
        }
    
    async def _handle_firmware_update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler pour l'événement firmware update"""
        return {
            "device_id": data.get("device_id"),
            "old_version": data.get("old_version"),
            "new_version": data.get("new_version"),
            "update_status": data.get("update_status"),
            "updated_at": data.get("timestamp")
        }
    
    async def _handle_certificate_expiring(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler pour l'événement certificate expiring"""
        return {
            "certificate_id": data.get("certificate_id"),
            "subject": data.get("subject"),
            "expires_at": data.get("expires_at"),
            "days_until_expiry": data.get("days_until_expiry"),
            "certificate_type": data.get("certificate_type")
        }
    
    # ==============================
    # Workers
    # ==============================
    
    async def _retry_worker(self):
        """Worker pour retry les webhooks échoués"""
        try:
            while True:
                # Attendre 30 secondes entre les cycles
                await asyncio.sleep(30)
                
                # Récupérer les livraisons à retry
                now = datetime.utcnow()
                deliveries = await self.db.webhook_deliveries.find({
                    "status": WebhookDeliveryStatus.RETRYING.value,
                    "next_retry": {"$lte": now},
                    "retry_count": {"$lt": self.retry_config["max_retries"]}
                }).to_list(None)
                
                for delivery in deliveries:
                    try:
                        # Récupérer le webhook
                        webhook = await self.db.webhooks.find_one({"webhook_id": delivery["webhook_id"]})
                        if not webhook or webhook["status"] != WebhookStatus.ACTIVE.value:
                            continue
                        
                        # Retry la livraison
                        result = await self._deliver_webhook(webhook, delivery["payload"])
                        
                        if result["success"]:
                            # Succès - marquer comme livré
                            await self.db.webhook_deliveries.update_one(
                                {"delivery_id": delivery["delivery_id"]},
                                {"$set": {
                                    "status": WebhookDeliveryStatus.DELIVERED.value,
                                    "delivered_at": datetime.utcnow(),
                                    "response_status": result.get("status_code"),
                                    "response_time": result.get("response_time")
                                }}
                            )
                            
                            # Incrémenter les compteurs
                            await self.db.webhooks.update_one(
                                {"webhook_id": webhook["webhook_id"]},
                                {"$inc": {"success_count": 1, "total_deliveries": 1}}
                            )
                        else:
                            # Échec - programmer le prochain retry
                            retry_count = delivery["retry_count"] + 1
                            
                            if retry_count >= self.retry_config["max_retries"]:
                                # Abandon après max retries
                                await self.db.webhook_deliveries.update_one(
                                    {"delivery_id": delivery["delivery_id"]},
                                    {"$set": {
                                        "status": WebhookDeliveryStatus.FAILED.value,
                                        "last_error": result.get("error"),
                                        "failed_at": datetime.utcnow()
                                    }}
                                )
                                
                                # Incrémenter les compteurs d'échec
                                await self.db.webhooks.update_one(
                                    {"webhook_id": webhook["webhook_id"]},
                                    {"$inc": {"failure_count": 1, "total_deliveries": 1}}
                                )
                            else:
                                # Programmer le prochain retry
                                delay = self.retry_config["retry_delays"][min(retry_count - 1, len(self.retry_config["retry_delays"]) - 1)]
                                
                                await self.db.webhook_deliveries.update_one(
                                    {"delivery_id": delivery["delivery_id"]},
                                    {"$set": {
                                        "retry_count": retry_count,
                                        "last_error": result.get("error"),
                                        "next_retry": datetime.utcnow() + timedelta(seconds=delay)
                                    }}
                                )
                    
                    except Exception as e:
                        logger.error(f"Erreur retry webhook: {str(e)}")
                        continue
                
        except Exception as e:
            logger.error(f"Erreur retry worker: {str(e)}")
    
    async def _cleanup_worker(self):
        """Worker pour nettoyer les anciens logs"""
        try:
            while True:
                # Attendre 1 heure entre les nettoyages
                await asyncio.sleep(3600)
                
                # Supprimer les livraisons plus anciennes que 30 jours
                cutoff_date = datetime.utcnow() - timedelta(days=30)
                
                await self.db.webhook_deliveries.delete_many({
                    "created_at": {"$lt": cutoff_date}
                })
                
                logger.info("Nettoyage des anciens logs de webhooks effectué")
                
        except Exception as e:
            logger.error(f"Erreur cleanup worker: {str(e)}")
    
    # ==============================
    # Statistiques
    # ==============================
    
    async def get_webhook_stats(self, webhook_id: Optional[str] = None) -> Dict[str, Any]:
        """Récupère les statistiques des webhooks"""
        try:
            if webhook_id:
                # Statistiques pour un webhook spécifique
                webhook = await self.db.webhooks.find_one({"webhook_id": webhook_id})
                if not webhook:
                    return {"error": "Webhook non trouvé"}
                
                # Statistiques de livraison
                delivery_stats = await self.db.webhook_deliveries.aggregate([
                    {"$match": {"webhook_id": webhook_id}},
                    {"$group": {
                        "_id": "$status",
                        "count": {"$sum": 1}
                    }}
                ]).to_list(None)
                
                stats = {
                    "webhook_id": webhook_id,
                    "name": webhook["name"],
                    "url": webhook["url"],
                    "events": webhook["events"],
                    "status": webhook["status"],
                    "created_at": webhook["created_at"],
                    "last_ping": webhook.get("last_ping"),
                    "success_count": webhook["success_count"],
                    "failure_count": webhook["failure_count"],
                    "total_deliveries": webhook["total_deliveries"],
                    "success_rate": (webhook["success_count"] / max(1, webhook["total_deliveries"])) * 100,
                    "delivery_stats": {stat["_id"]: stat["count"] for stat in delivery_stats}
                }
                
                return stats
            else:
                # Statistiques globales
                total_webhooks = await self.db.webhooks.count_documents({})
                active_webhooks = await self.db.webhooks.count_documents({"status": WebhookStatus.ACTIVE.value})
                
                total_deliveries = await self.db.webhook_deliveries.count_documents({})
                successful_deliveries = await self.db.webhook_deliveries.count_documents({"status": WebhookDeliveryStatus.DELIVERED.value})
                
                return {
                    "total_webhooks": total_webhooks,
                    "active_webhooks": active_webhooks,
                    "total_deliveries": total_deliveries,
                    "successful_deliveries": successful_deliveries,
                    "success_rate": (successful_deliveries / max(1, total_deliveries)) * 100,
                    "supported_events": [event.value for event in WebhookEvent]
                }
                
        except Exception as e:
            logger.error(f"Erreur récupération stats webhooks: {str(e)}")
            return {"error": str(e)}
    
    async def shutdown(self):
        """Arrête le service de webhooks"""
        try:
            self.active_webhooks.clear()
            self.event_handlers.clear()
            
            logger.info("Service Webhooks arrêté")
            
        except Exception as e:
            logger.error(f"Erreur arrêt service Webhooks: {str(e)}")
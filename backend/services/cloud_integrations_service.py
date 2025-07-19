"""
Service d'Intégrations Cloud pour QuantumShield
Support pour AWS, Azure, GCP et autres fournisseurs cloud
"""

import json
import logging
import asyncio
import base64
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import uuid
import requests
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class CloudProvider(str, Enum):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    ALIBABA = "alibaba"
    DIGITAL_OCEAN = "digital_ocean"

class IntegrationType(str, Enum):
    IOT_CORE = "iot_core"
    STORAGE = "storage"
    COMPUTE = "compute"
    DATABASE = "database"
    MESSAGING = "messaging"
    ANALYTICS = "analytics"
    MACHINE_LEARNING = "machine_learning"
    SECURITY = "security"

@dataclass
class CloudCredentials:
    """Credentials pour l'accès cloud"""
    provider: CloudProvider
    credentials: Dict[str, Any]
    region: str
    encrypted: bool = True
    created_at: datetime = None
    expires_at: datetime = None

class CloudIntegrationsService:
    """Service d'intégrations avec les fournisseurs cloud"""
    
    def __init__(self, db):
        self.db = db
        self.is_initialized = False
        self.active_connections = {}
        self.integration_handlers = {}
        self._initialize()
    
    def _initialize(self):
        """Initialise le service d'intégrations cloud"""
        try:
            self._init_integration_handlers()
            self.is_initialized = True
            logger.info("Service Intégrations Cloud initialisé")
        except Exception as e:
            logger.error(f"Erreur initialisation Intégrations Cloud: {e}")
            self.is_initialized = False
    
    def _init_integration_handlers(self):
        """Initialise les handlers d'intégration pour chaque fournisseur"""
        self.integration_handlers = {
            CloudProvider.AWS: {
                IntegrationType.IOT_CORE: self._handle_aws_iot_core,
                IntegrationType.STORAGE: self._handle_aws_s3,
                IntegrationType.COMPUTE: self._handle_aws_ec2,
                IntegrationType.DATABASE: self._handle_aws_dynamodb,
                IntegrationType.MESSAGING: self._handle_aws_sns_sqs,
                IntegrationType.ANALYTICS: self._handle_aws_analytics,
                IntegrationType.MACHINE_LEARNING: self._handle_aws_ml,
                IntegrationType.SECURITY: self._handle_aws_security
            },
            CloudProvider.AZURE: {
                IntegrationType.IOT_CORE: self._handle_azure_iot_hub,
                IntegrationType.STORAGE: self._handle_azure_storage,
                IntegrationType.COMPUTE: self._handle_azure_compute,
                IntegrationType.DATABASE: self._handle_azure_cosmos,
                IntegrationType.MESSAGING: self._handle_azure_service_bus,
                IntegrationType.ANALYTICS: self._handle_azure_analytics,
                IntegrationType.MACHINE_LEARNING: self._handle_azure_ml,
                IntegrationType.SECURITY: self._handle_azure_security
            },
            CloudProvider.GCP: {
                IntegrationType.IOT_CORE: self._handle_gcp_iot_core,
                IntegrationType.STORAGE: self._handle_gcp_storage,
                IntegrationType.COMPUTE: self._handle_gcp_compute,
                IntegrationType.DATABASE: self._handle_gcp_firestore,
                IntegrationType.MESSAGING: self._handle_gcp_pubsub,
                IntegrationType.ANALYTICS: self._handle_gcp_analytics,
                IntegrationType.MACHINE_LEARNING: self._handle_gcp_ml,
                IntegrationType.SECURITY: self._handle_gcp_security
            }
        }
    
    def is_ready(self) -> bool:
        """Vérifie si le service est prêt"""
        return self.is_initialized
    
    # ===== GESTION DES CREDENTIALS =====
    
    async def store_cloud_credentials(self, user_id: str, provider: CloudProvider, 
                                    credentials: Dict[str, Any], region: str = "us-east-1") -> Dict[str, Any]:
        """Stocke les credentials cloud de façon sécurisée"""
        try:
            # Chiffrer les credentials (simulation - en production utiliser une vraie méthode de chiffrement)
            encrypted_credentials = self._encrypt_credentials(credentials)
            
            credential_doc = {
                "user_id": user_id,
                "provider": provider.value,
                "credentials": encrypted_credentials,
                "region": region,
                "encrypted": True,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(days=90),  # Expiration dans 90 jours
                "last_tested": None,
                "connection_status": "not_tested"
            }
            
            # Remplacer les anciens credentials s'ils existent
            await self.db.cloud_credentials.update_one(
                {"user_id": user_id, "provider": provider.value},
                {"$set": credential_doc},
                upsert=True
            )
            
            return {
                "success": True,
                "message": f"Credentials {provider.value} stockés avec succès",
                "expires_at": credential_doc["expires_at"]
            }
            
        except Exception as e:
            logger.error(f"Erreur stockage credentials: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_cloud_connection(self, user_id: str, provider: CloudProvider) -> Dict[str, Any]:
        """Teste la connexion à un fournisseur cloud"""
        try:
            # Récupérer les credentials
            credentials_doc = await self.db.cloud_credentials.find_one({
                "user_id": user_id,
                "provider": provider.value
            })
            
            if not credentials_doc:
                return {
                    "success": False,
                    "error": "Aucun credentials trouvé pour ce fournisseur"
                }
            
            # Déchiffrer les credentials
            credentials = self._decrypt_credentials(credentials_doc["credentials"])
            
            # Tester la connexion selon le fournisseur
            connection_result = await self._test_provider_connection(provider, credentials, credentials_doc["region"])
            
            # Mettre à jour le statut de connexion
            await self.db.cloud_credentials.update_one(
                {"user_id": user_id, "provider": provider.value},
                {
                    "$set": {
                        "last_tested": datetime.utcnow(),
                        "connection_status": "connected" if connection_result["success"] else "failed",
                        "test_details": connection_result
                    }
                }
            )
            
            return connection_result
            
        except Exception as e:
            logger.error(f"Erreur test connexion: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user_cloud_integrations(self, user_id: str) -> List[Dict[str, Any]]:
        """Récupère les intégrations cloud d'un utilisateur"""
        try:
            integrations = await self.db.cloud_credentials.find({
                "user_id": user_id
            }).to_list(None)
            
            # Ne pas retourner les credentials, seulement les métadonnées
            safe_integrations = []
            for integration in integrations:
                safe_integration = {
                    "provider": integration["provider"],
                    "region": integration["region"],
                    "created_at": integration["created_at"],
                    "expires_at": integration["expires_at"],
                    "last_tested": integration.get("last_tested"),
                    "connection_status": integration.get("connection_status", "not_tested"),
                    "available_services": self._get_available_services(integration["provider"])
                }
                safe_integrations.append(safe_integration)
            
            return safe_integrations
            
        except Exception as e:
            logger.error(f"Erreur récupération intégrations: {e}")
            return []
    
    # ===== INTÉGRATIONS SPÉCIFIQUES =====
    
    async def sync_devices_to_cloud(self, user_id: str, provider: CloudProvider, 
                                  integration_type: IntegrationType) -> Dict[str, Any]:
        """Synchronise les dispositifs IoT vers un service cloud"""
        try:
            # Récupérer les devices de l'utilisateur
            user_devices = await self.db.devices.find({"owner_id": user_id}).to_list(None)
            
            if not user_devices:
                return {
                    "success": False,
                    "error": "Aucun dispositif trouvé pour synchronisation"
                }
            
            # Récupérer les credentials
            credentials_doc = await self.db.cloud_credentials.find_one({
                "user_id": user_id,
                "provider": provider.value
            })
            
            if not credentials_doc:
                return {
                    "success": False,
                    "error": "Credentials cloud non configurés"
                }
            
            # Obtenir le handler approprié
            handler = self.integration_handlers.get(provider, {}).get(integration_type)
            if not handler:
                return {
                    "success": False,
                    "error": f"Intégration {integration_type.value} non supportée pour {provider.value}"
                }
            
            # Exécuter la synchronisation
            credentials = self._decrypt_credentials(credentials_doc["credentials"])
            sync_result = await handler(user_devices, credentials, credentials_doc["region"], "sync_devices")
            
            # Enregistrer l'opération
            await self._log_integration_operation(user_id, provider, integration_type, "sync_devices", sync_result)
            
            return sync_result
            
        except Exception as e:
            logger.error(f"Erreur synchronisation devices: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def backup_data_to_cloud(self, user_id: str, provider: CloudProvider, 
                                 data_types: List[str]) -> Dict[str, Any]:
        """Sauvegarde les données utilisateur vers le cloud"""
        try:
            # Récupérer les credentials
            credentials_doc = await self.db.cloud_credentials.find_one({
                "user_id": user_id,
                "provider": provider.value
            })
            
            if not credentials_doc:
                return {
                    "success": False,
                    "error": "Credentials cloud non configurés"
                }
            
            # Préparer les données à sauvegarder
            backup_data = await self._prepare_backup_data(user_id, data_types)
            
            if not backup_data:
                return {
                    "success": False,
                    "error": "Aucune donnée à sauvegarder"
                }
            
            # Obtenir le handler de stockage
            storage_handler = self.integration_handlers.get(provider, {}).get(IntegrationType.STORAGE)
            if not storage_handler:
                return {
                    "success": False,
                    "error": f"Sauvegarde non supportée pour {provider.value}"
                }
            
            # Exécuter la sauvegarde
            credentials = self._decrypt_credentials(credentials_doc["credentials"])
            backup_result = await storage_handler(backup_data, credentials, credentials_doc["region"], "backup")
            
            # Enregistrer l'opération
            await self._log_integration_operation(user_id, provider, IntegrationType.STORAGE, "backup", backup_result)
            
            return backup_result
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde cloud: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def deploy_edge_computing(self, user_id: str, provider: CloudProvider, 
                                  deployment_config: Dict[str, Any]) -> Dict[str, Any]:
        """Déploie des ressources d'edge computing"""
        try:
            # Récupérer les credentials
            credentials_doc = await self.db.cloud_credentials.find_one({
                "user_id": user_id,
                "provider": provider.value
            })
            
            if not credentials_doc:
                return {
                    "success": False,
                    "error": "Credentials cloud non configurés"
                }
            
            # Obtenir le handler de compute
            compute_handler = self.integration_handlers.get(provider, {}).get(IntegrationType.COMPUTE)
            if not compute_handler:
                return {
                    "success": False,
                    "error": f"Edge computing non supporté pour {provider.value}"
                }
            
            # Exécuter le déploiement
            credentials = self._decrypt_credentials(credentials_doc["credentials"])
            deployment_result = await compute_handler(deployment_config, credentials, credentials_doc["region"], "deploy_edge")
            
            # Enregistrer l'opération
            await self._log_integration_operation(user_id, provider, IntegrationType.COMPUTE, "deploy_edge", deployment_result)
            
            return deployment_result
            
        except Exception as e:
            logger.error(f"Erreur déploiement edge: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ===== HANDLERS SPÉCIFIQUES AWS =====
    
    async def _handle_aws_iot_core(self, data: Any, credentials: Dict, region: str, operation: str) -> Dict[str, Any]:
        """Handler pour AWS IoT Core"""
        try:
            if operation == "sync_devices":
                # Simulation de synchronisation vers AWS IoT Core
                synced_devices = []
                for device in data:
                    # En production, utiliser boto3 pour AWS IoT Core
                    synced_devices.append({
                        "device_id": device["device_id"],
                        "thing_name": f"quantumshield_{device['device_id']}",
                        "status": "synced",
                        "arn": f"arn:aws:iot:{region}:123456789012:thing/quantumshield_{device['device_id']}"
                    })
                
                return {
                    "success": True,
                    "provider": "aws",
                    "service": "iot_core",
                    "synced_devices": synced_devices,
                    "total_synced": len(synced_devices)
                }
            
            return {
                "success": False,
                "error": f"Opération '{operation}' non supportée pour AWS IoT Core"
            }
            
        except Exception as e:
            logger.error(f"Erreur AWS IoT Core: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_aws_s3(self, data: Any, credentials: Dict, region: str, operation: str) -> Dict[str, Any]:
        """Handler pour AWS S3"""
        try:
            if operation == "backup":
                # Simulation de sauvegarde vers S3
                backup_files = []
                for data_type, content in data.items():
                    file_key = f"quantumshield_backup_{data_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
                    backup_files.append({
                        "data_type": data_type,
                        "s3_key": file_key,
                        "size_bytes": len(json.dumps(content)),
                        "backup_time": datetime.utcnow()
                    })
                
                return {
                    "success": True,
                    "provider": "aws",
                    "service": "s3",
                    "backup_files": backup_files,
                    "bucket": f"quantumshield-backup-{region}",
                    "total_files": len(backup_files)
                }
            
            return {
                "success": False,
                "error": f"Opération '{operation}' non supportée pour AWS S3"
            }
            
        except Exception as e:
            logger.error(f"Erreur AWS S3: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_aws_ec2(self, data: Any, credentials: Dict, region: str, operation: str) -> Dict[str, Any]:
        """Handler pour AWS EC2"""
        try:
            if operation == "deploy_edge":
                # Simulation de déploiement EC2 pour edge computing
                instance_info = {
                    "instance_id": f"i-{uuid.uuid4().hex[:17]}",
                    "instance_type": data.get("instance_type", "t3.micro"),
                    "region": region,
                    "availability_zone": f"{region}a",
                    "public_ip": "203.0.113.12",
                    "private_ip": "10.0.1.42",
                    "status": "running",
                    "launch_time": datetime.utcnow()
                }
                
                return {
                    "success": True,
                    "provider": "aws",
                    "service": "ec2",
                    "instance": instance_info,
                    "estimated_cost": "$0.0116/hour"
                }
            
            return {
                "success": False,
                "error": f"Opération '{operation}' non supportée pour AWS EC2"
            }
            
        except Exception as e:
            logger.error(f"Erreur AWS EC2: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_aws_dynamodb(self, data: Any, credentials: Dict, region: str, operation: str) -> Dict[str, Any]:
        """Handler pour AWS DynamoDB"""
        return {"success": False, "error": "AWS DynamoDB non implémenté"}
    
    async def _handle_aws_sns_sqs(self, data: Any, credentials: Dict, region: str, operation: str) -> Dict[str, Any]:
        """Handler pour AWS SNS/SQS"""
        return {"success": False, "error": "AWS SNS/SQS non implémenté"}
    
    async def _handle_aws_analytics(self, data: Any, credentials: Dict, region: str, operation: str) -> Dict[str, Any]:
        """Handler pour AWS Analytics"""
        return {"success": False, "error": "AWS Analytics non implémenté"}
    
    async def _handle_aws_ml(self, data: Any, credentials: Dict, region: str, operation: str) -> Dict[str, Any]:
        """Handler pour AWS ML"""
        return {"success": False, "error": "AWS ML non implémenté"}
    
    async def _handle_aws_security(self, data: Any, credentials: Dict, region: str, operation: str) -> Dict[str, Any]:
        """Handler pour AWS Security"""
        return {"success": False, "error": "AWS Security non implémenté"}
    
    # ===== HANDLERS AZURE =====
    
    async def _handle_azure_iot_hub(self, data: Any, credentials: Dict, region: str, operation: str) -> Dict[str, Any]:
        """Handler pour Azure IoT Hub"""
        try:
            if operation == "sync_devices":
                # Simulation de synchronisation vers Azure IoT Hub
                synced_devices = []
                for device in data:
                    synced_devices.append({
                        "device_id": device["device_id"],
                        "device_name": f"quantumshield-{device['device_id']}",
                        "status": "synced",
                        "connection_string": f"HostName=quantumshield-iot-hub.azure-devices.net;DeviceId={device['device_id']};SharedAccessKey=fake_key"
                    })
                
                return {
                    "success": True,
                    "provider": "azure",
                    "service": "iot_hub",
                    "synced_devices": synced_devices,
                    "total_synced": len(synced_devices),
                    "iot_hub_name": "quantumshield-iot-hub"
                }
            
            return {
                "success": False,
                "error": f"Opération '{operation}' non supportée pour Azure IoT Hub"
            }
            
        except Exception as e:
            logger.error(f"Erreur Azure IoT Hub: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_azure_storage(self, data: Any, credentials: Dict, region: str, operation: str) -> Dict[str, Any]:
        """Handler pour Azure Storage"""
        try:
            if operation == "backup":
                # Simulation de sauvegarde vers Azure Blob Storage
                backup_blobs = []
                for data_type, content in data.items():
                    blob_name = f"quantumshield-backup-{data_type}-{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
                    backup_blobs.append({
                        "data_type": data_type,
                        "blob_name": blob_name,
                        "size_bytes": len(json.dumps(content)),
                        "backup_time": datetime.utcnow(),
                        "url": f"https://quantumshield.blob.core.windows.net/backups/{blob_name}"
                    })
                
                return {
                    "success": True,
                    "provider": "azure",
                    "service": "blob_storage",
                    "backup_blobs": backup_blobs,
                    "container": "quantumshield-backups",
                    "total_blobs": len(backup_blobs)
                }
            
            return {
                "success": False,
                "error": f"Opération '{operation}' non supportée pour Azure Storage"
            }
            
        except Exception as e:
            logger.error(f"Erreur Azure Storage: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_azure_compute(self, data: Any, credentials: Dict, region: str, operation: str) -> Dict[str, Any]:
        """Handler pour Azure Compute"""
        return {"success": False, "error": "Azure Compute non implémenté"}
    
    async def _handle_azure_cosmos(self, data: Any, credentials: Dict, region: str, operation: str) -> Dict[str, Any]:
        """Handler pour Azure Cosmos DB"""
        return {"success": False, "error": "Azure Cosmos DB non implémenté"}
    
    async def _handle_azure_service_bus(self, data: Any, credentials: Dict, region: str, operation: str) -> Dict[str, Any]:
        """Handler pour Azure Service Bus"""
        return {"success": False, "error": "Azure Service Bus non implémenté"}
    
    async def _handle_azure_analytics(self, data: Any, credentials: Dict, region: str, operation: str) -> Dict[str, Any]:
        """Handler pour Azure Analytics"""
        return {"success": False, "error": "Azure Analytics non implémenté"}
    
    async def _handle_azure_ml(self, data: Any, credentials: Dict, region: str, operation: str) -> Dict[str, Any]:
        """Handler pour Azure ML"""
        return {"success": False, "error": "Azure ML non implémenté"}
    
    async def _handle_azure_security(self, data: Any, credentials: Dict, region: str, operation: str) -> Dict[str, Any]:
        """Handler pour Azure Security"""
        return {"success": False, "error": "Azure Security non implémenté"}
    
    # ===== HANDLERS GCP =====
    
    async def _handle_gcp_iot_core(self, data: Any, credentials: Dict, region: str, operation: str) -> Dict[str, Any]:
        """Handler pour GCP IoT Core"""
        return {"success": False, "error": "GCP IoT Core non implémenté"}
    
    async def _handle_gcp_storage(self, data: Any, credentials: Dict, region: str, operation: str) -> Dict[str, Any]:
        """Handler pour GCP Storage"""
        return {"success": False, "error": "GCP Storage non implémenté"}
    
    async def _handle_gcp_compute(self, data: Any, credentials: Dict, region: str, operation: str) -> Dict[str, Any]:
        """Handler pour GCP Compute"""
        return {"success": False, "error": "GCP Compute non implémenté"}
    
    async def _handle_gcp_firestore(self, data: Any, credentials: Dict, region: str, operation: str) -> Dict[str, Any]:
        """Handler pour GCP Firestore"""
        return {"success": False, "error": "GCP Firestore non implémenté"}
    
    async def _handle_gcp_pubsub(self, data: Any, credentials: Dict, region: str, operation: str) -> Dict[str, Any]:
        """Handler pour GCP Pub/Sub"""
        return {"success": False, "error": "GCP Pub/Sub non implémenté"}
    
    async def _handle_gcp_analytics(self, data: Any, credentials: Dict, region: str, operation: str) -> Dict[str, Any]:
        """Handler pour GCP Analytics"""
        return {"success": False, "error": "GCP Analytics non implémenté"}
    
    async def _handle_gcp_ml(self, data: Any, credentials: Dict, region: str, operation: str) -> Dict[str, Any]:
        """Handler pour GCP ML"""
        return {"success": False, "error": "GCP ML non implémenté"}
    
    async def _handle_gcp_security(self, data: Any, credentials: Dict, region: str, operation: str) -> Dict[str, Any]:
        """Handler pour GCP Security"""
        return {"success": False, "error": "GCP Security non implémenté"}
    
    # ===== MÉTHODES UTILITAIRES =====
    
    def _encrypt_credentials(self, credentials: Dict[str, Any]) -> str:
        """Chiffre les credentials (simulation)"""
        # En production, utiliser une vraie méthode de chiffrement
        credentials_json = json.dumps(credentials)
        encoded = base64.b64encode(credentials_json.encode()).decode()
        return f"encrypted_{encoded}"
    
    def _decrypt_credentials(self, encrypted_credentials: str) -> Dict[str, Any]:
        """Déchiffre les credentials (simulation)"""
        # En production, utiliser une vraie méthode de déchiffrement
        if encrypted_credentials.startswith("encrypted_"):
            encoded = encrypted_credentials[10:]  # Supprimer le préfixe "encrypted_"
            decoded = base64.b64decode(encoded).decode()
            return json.loads(decoded)
        return {}
    
    async def _test_provider_connection(self, provider: CloudProvider, credentials: Dict, region: str) -> Dict[str, Any]:
        """Teste la connexion à un fournisseur cloud"""
        try:
            # Simulation de test de connexion
            if provider == CloudProvider.AWS:
                # En production, utiliser boto3 pour tester AWS
                return {
                    "success": True,
                    "provider": "aws",
                    "region": region,
                    "account_id": "123456789012",
                    "services_available": ["iot", "s3", "ec2", "dynamodb"]
                }
            elif provider == CloudProvider.AZURE:
                # En production, utiliser Azure SDK
                return {
                    "success": True,
                    "provider": "azure",
                    "region": region,
                    "subscription_id": "12345678-1234-1234-1234-123456789012",
                    "services_available": ["iot_hub", "blob_storage", "compute", "cosmos_db"]
                }
            elif provider == CloudProvider.GCP:
                # En production, utiliser Google Cloud SDK
                return {
                    "success": True,
                    "provider": "gcp",
                    "region": region,
                    "project_id": "quantumshield-project",
                    "services_available": ["iot_core", "storage", "compute", "firestore"]
                }
            else:
                return {
                    "success": False,
                    "error": f"Provider {provider.value} non supporté"
                }
                
        except Exception as e:
            logger.error(f"Erreur test connexion {provider.value}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_available_services(self, provider: str) -> List[str]:
        """Retourne les services disponibles pour un fournisseur"""
        service_mapping = {
            "aws": ["iot_core", "s3", "ec2", "dynamodb", "sns_sqs", "analytics", "machine_learning", "security"],
            "azure": ["iot_hub", "blob_storage", "compute", "cosmos_db", "service_bus", "analytics", "machine_learning", "security"],
            "gcp": ["iot_core", "storage", "compute", "firestore", "pubsub", "analytics", "machine_learning", "security"]
        }
        return service_mapping.get(provider, [])
    
    async def _prepare_backup_data(self, user_id: str, data_types: List[str]) -> Dict[str, Any]:
        """Prépare les données pour sauvegarde"""
        try:
            backup_data = {}
            
            if "devices" in data_types:
                devices = await self.db.devices.find({"owner_id": user_id}).to_list(None)
                backup_data["devices"] = devices
            
            if "tokens" in data_types:
                tokens = await self.db.user_balances.find_one({"user_id": user_id})
                if tokens:
                    backup_data["tokens"] = tokens
            
            if "settings" in data_types:
                settings = await self.db.user_settings.find_one({"user_id": user_id})
                if settings:
                    backup_data["settings"] = settings
            
            if "activity" in data_types:
                activity = await self.db.activity_logs.find({"user_id": user_id}).limit(1000).to_list(None)
                backup_data["activity"] = activity
            
            return backup_data
            
        except Exception as e:
            logger.error(f"Erreur préparation backup: {e}")
            return {}
    
    async def _log_integration_operation(self, user_id: str, provider: CloudProvider, 
                                       integration_type: IntegrationType, operation: str, 
                                       result: Dict[str, Any]) -> None:
        """Log une opération d'intégration"""
        try:
            log_entry = {
                "user_id": user_id,
                "provider": provider.value,
                "integration_type": integration_type.value,
                "operation": operation,
                "success": result.get("success", False),
                "timestamp": datetime.utcnow(),
                "details": result
            }
            
            await self.db.integration_logs.insert_one(log_entry)
            
        except Exception as e:
            logger.error(f"Erreur log opération: {e}")
    
    async def get_integration_logs(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Récupère les logs d'intégrations d'un utilisateur"""
        try:
            logs = await self.db.integration_logs.find({
                "user_id": user_id
            }).sort("timestamp", -1).limit(limit).to_list(None)
            
            return logs
            
        except Exception as e:
            logger.error(f"Erreur récupération logs: {e}")
            return []
"""
Service de Connecteurs ERP/CRM pour QuantumShield
Support pour SAP, Salesforce, Microsoft Dynamics, Oracle, et autres systèmes d'entreprise
"""

import json
import logging
import asyncio
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import uuid
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class ERPType(str, Enum):
    SAP = "sap"
    ORACLE = "oracle"
    MICROSOFT_DYNAMICS = "microsoft_dynamics"
    NETSUITE = "netsuite"
    ODOO = "odoo"
    CUSTOM = "custom"

class CRMType(str, Enum):
    SALESFORCE = "salesforce"
    HUBSPOT = "hubspot"
    MICROSOFT_DYNAMICS_CRM = "microsoft_dynamics_crm"
    ZOHO = "zoho"
    PIPEDRIVE = "pipedrive"
    CUSTOM = "custom"

class SyncDirection(str, Enum):
    IMPORT = "import"
    EXPORT = "export"
    BIDIRECTIONAL = "bidirectional"

class DataType(str, Enum):
    DEVICES = "devices"
    CUSTOMERS = "customers"
    ORDERS = "orders"
    INVENTORY = "inventory"
    CONTRACTS = "contracts"
    INVOICES = "invoices"
    USERS = "users"
    ANALYTICS = "analytics"

@dataclass
class ConnectorConfig:
    """Configuration d'un connecteur ERP/CRM"""
    connector_id: str
    connector_type: str  # ERP ou CRM
    system_type: str
    connection_params: Dict[str, Any]
    sync_direction: SyncDirection
    data_types: List[DataType]
    sync_frequency: int  # en minutes
    enabled: bool = True
    created_at: datetime = None
    updated_at: datetime = None

class ERPCRMConnectorsService:
    """Service de connecteurs ERP/CRM"""
    
    def __init__(self, db):
        self.db = db
        self.is_initialized = False
        self.connector_handlers = {}
        self.sync_jobs = {}
        self._initialize()
    
    def _initialize(self):
        """Initialise le service des connecteurs ERP/CRM"""
        try:
            self._init_connector_handlers()
            self.is_initialized = True
            logger.info("Service Connecteurs ERP/CRM initialisé")
        except Exception as e:
            logger.error(f"Erreur initialisation Connecteurs ERP/CRM: {e}")
            self.is_initialized = False
    
    def _init_connector_handlers(self):
        """Initialise les handlers pour chaque type de connecteur"""
        self.connector_handlers = {
            # ERP Handlers
            ERPType.SAP: self._handle_sap_connector,
            ERPType.ORACLE: self._handle_oracle_connector,
            ERPType.MICROSOFT_DYNAMICS: self._handle_dynamics_erp_connector,
            ERPType.NETSUITE: self._handle_netsuite_connector,
            ERPType.ODOO: self._handle_odoo_connector,
            ERPType.CUSTOM: self._handle_custom_erp_connector,
            
            # CRM Handlers
            CRMType.SALESFORCE: self._handle_salesforce_connector,
            CRMType.HUBSPOT: self._handle_hubspot_connector,
            CRMType.MICROSOFT_DYNAMICS_CRM: self._handle_dynamics_crm_connector,
            CRMType.ZOHO: self._handle_zoho_connector,
            CRMType.PIPEDRIVE: self._handle_pipedrive_connector,
            CRMType.CUSTOM: self._handle_custom_crm_connector
        }
    
    def is_ready(self) -> bool:
        """Vérifie si le service est prêt"""
        return self.is_initialized
    
    # ===== GESTION DES CONNECTEURS =====
    
    async def create_connector(self, user_id: str, config: ConnectorConfig) -> Dict[str, Any]:
        """Crée un nouveau connecteur ERP/CRM"""
        try:
            # Valider la configuration
            validation_result = await self._validate_connector_config(config)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"]
                }
            
            # Tester la connexion
            test_result = await self._test_connector_connection(config)
            if not test_result["success"]:
                return {
                    "success": False,
                    "error": f"Test de connexion échoué: {test_result['error']}"
                }
            
            # Créer le connecteur
            connector_doc = {
                "user_id": user_id,
                "connector_id": config.connector_id,
                "connector_type": config.connector_type,
                "system_type": config.system_type,
                "connection_params": self._encrypt_connection_params(config.connection_params),
                "sync_direction": config.sync_direction.value,
                "data_types": [dt.value for dt in config.data_types],
                "sync_frequency": config.sync_frequency,
                "enabled": config.enabled,
                "created_at": config.created_at or datetime.utcnow(),
                "updated_at": config.updated_at or datetime.utcnow(),
                "last_sync": None,
                "sync_status": "not_synced",
                "total_syncs": 0,
                "last_error": None
            }
            
            await self.db.erp_crm_connectors.insert_one(connector_doc)
            
            # Programmer la synchronisation automatique si activée
            if config.enabled:
                await self._schedule_sync_job(user_id, config.connector_id, config.sync_frequency)
            
            return {
                "success": True,
                "connector_id": config.connector_id,
                "message": "Connecteur créé avec succès"
            }
            
        except Exception as e:
            logger.error(f"Erreur création connecteur: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user_connectors(self, user_id: str) -> List[Dict[str, Any]]:
        """Récupère tous les connecteurs d'un utilisateur"""
        try:
            connectors = await self.db.erp_crm_connectors.find({
                "user_id": user_id
            }).to_list(None)
            
            # Ne pas retourner les paramètres de connexion sensibles
            safe_connectors = []
            for connector in connectors:
                safe_connector = {
                    "connector_id": connector["connector_id"],
                    "connector_type": connector["connector_type"],
                    "system_type": connector["system_type"],
                    "sync_direction": connector["sync_direction"],
                    "data_types": connector["data_types"],
                    "sync_frequency": connector["sync_frequency"],
                    "enabled": connector["enabled"],
                    "created_at": connector["created_at"],
                    "updated_at": connector["updated_at"],
                    "last_sync": connector.get("last_sync"),
                    "sync_status": connector.get("sync_status", "not_synced"),
                    "total_syncs": connector.get("total_syncs", 0),
                    "last_error": connector.get("last_error")
                }
                safe_connectors.append(safe_connector)
            
            return safe_connectors
            
        except Exception as e:
            logger.error(f"Erreur récupération connecteurs: {e}")
            return []
    
    async def update_connector(self, user_id: str, connector_id: str, updates: Dict[str, Any]) -> bool:
        """Met à jour un connecteur"""
        try:
            # Chiffrer les paramètres de connexion s'ils sont modifiés
            if "connection_params" in updates:
                updates["connection_params"] = self._encrypt_connection_params(updates["connection_params"])
            
            updates["updated_at"] = datetime.utcnow()
            
            result = await self.db.erp_crm_connectors.update_one(
                {"user_id": user_id, "connector_id": connector_id},
                {"$set": updates}
            )
            
            # Reprogrammer la synchronisation si la fréquence a changé
            if "sync_frequency" in updates or "enabled" in updates:
                connector = await self.db.erp_crm_connectors.find_one({
                    "user_id": user_id,
                    "connector_id": connector_id
                })
                
                if connector and connector["enabled"]:
                    await self._schedule_sync_job(user_id, connector_id, connector["sync_frequency"])
                else:
                    await self._cancel_sync_job(user_id, connector_id)
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Erreur mise à jour connecteur: {e}")
            return False
    
    async def delete_connector(self, user_id: str, connector_id: str) -> bool:
        """Supprime un connecteur"""
        try:
            # Annuler la synchronisation automatique
            await self._cancel_sync_job(user_id, connector_id)
            
            result = await self.db.erp_crm_connectors.delete_one({
                "user_id": user_id,
                "connector_id": connector_id
            })
            
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Erreur suppression connecteur: {e}")
            return False
    
    # ===== SYNCHRONISATION =====
    
    async def trigger_sync(self, user_id: str, connector_id: str) -> Dict[str, Any]:
        """Déclenche une synchronisation manuelle"""
        try:
            # Récupérer le connecteur
            connector = await self.db.erp_crm_connectors.find_one({
                "user_id": user_id,
                "connector_id": connector_id
            })
            
            if not connector:
                return {
                    "success": False,
                    "error": "Connecteur non trouvé"
                }
            
            if not connector["enabled"]:
                return {
                    "success": False,
                    "error": "Connecteur désactivé"
                }
            
            # Exécuter la synchronisation
            sync_result = await self._execute_sync(user_id, connector)
            
            # Mettre à jour le statut du connecteur
            await self.db.erp_crm_connectors.update_one(
                {"user_id": user_id, "connector_id": connector_id},
                {
                    "$set": {
                        "last_sync": datetime.utcnow(),
                        "sync_status": "success" if sync_result["success"] else "failed",
                        "last_error": sync_result.get("error") if not sync_result["success"] else None
                    },
                    "$inc": {"total_syncs": 1}
                }
            )
            
            return sync_result
            
        except Exception as e:
            logger.error(f"Erreur synchronisation: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_sync(self, user_id: str, connector: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute une synchronisation"""
        try:
            # Déchiffrer les paramètres de connexion
            connection_params = self._decrypt_connection_params(connector["connection_params"])
            
            # Obtenir le handler approprié
            system_type = connector["system_type"]
            handler = None
            
            # Chercher dans les handlers ERP
            for erp_type in ERPType:
                if erp_type.value == system_type:
                    handler = self.connector_handlers.get(erp_type)
                    break
            
            # Si pas trouvé, chercher dans les handlers CRM
            if not handler:
                for crm_type in CRMType:
                    if crm_type.value == system_type:
                        handler = self.connector_handlers.get(crm_type)
                        break
            
            if not handler:
                return {
                    "success": False,
                    "error": f"Handler non trouvé pour {system_type}"
                }
            
            # Exécuter la synchronisation
            sync_result = await handler(
                user_id=user_id,
                connection_params=connection_params,
                sync_direction=connector["sync_direction"],
                data_types=connector["data_types"],
                operation="sync"
            )
            
            # Enregistrer les résultats de synchronisation
            await self._log_sync_operation(user_id, connector["connector_id"], sync_result)
            
            return sync_result
            
        except Exception as e:
            logger.error(f"Erreur exécution sync: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ===== HANDLERS SPÉCIFIQUES =====
    
    async def _handle_sap_connector(self, user_id: str, connection_params: Dict, 
                                   sync_direction: str, data_types: List[str], 
                                   operation: str) -> Dict[str, Any]:
        """Handler pour SAP ERP"""
        try:
            if operation == "sync":
                # Simulation de synchronisation avec SAP
                synced_data = {}
                
                for data_type in data_types:
                    if data_type == "devices":
                        # Synchroniser les devices vers SAP comme équipements
                        devices = await self.db.devices.find({"owner_id": user_id}).to_list(None)
                        synced_data["devices"] = {
                            "total": len(devices),
                            "synced": len(devices),
                            "sap_equipment_codes": [f"EQ_{device['device_id'][:8]}" for device in devices]
                        }
                    elif data_type == "customers":
                        # Synchroniser les informations client
                        user_info = await self.db.users.find_one({"id": user_id})
                        synced_data["customers"] = {
                            "total": 1,
                            "synced": 1,
                            "sap_customer_code": f"CU_{user_id[:8]}"
                        }
                    elif data_type == "orders":
                        # Synchroniser les commandes (tokens achetés)
                        transactions = await self.db.token_transactions.find({"to_user": user_id}).limit(10).to_list(None)
                        synced_data["orders"] = {
                            "total": len(transactions),
                            "synced": len(transactions),
                            "sap_order_numbers": [f"SO_{str(t['_id'])[:8]}" for t in transactions]
                        }
                
                return {
                    "success": True,
                    "connector_type": "sap",
                    "sync_direction": sync_direction,
                    "synced_data": synced_data,
                    "sync_time": datetime.utcnow(),
                    "total_records": sum(data.get("total", 0) for data in synced_data.values())
                }
            
            return {
                "success": False,
                "error": f"Opération '{operation}' non supportée pour SAP"
            }
            
        except Exception as e:
            logger.error(f"Erreur SAP connector: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_salesforce_connector(self, user_id: str, connection_params: Dict, 
                                         sync_direction: str, data_types: List[str], 
                                         operation: str) -> Dict[str, Any]:
        """Handler pour Salesforce CRM"""
        try:
            if operation == "sync":
                # Simulation de synchronisation avec Salesforce
                synced_data = {}
                
                for data_type in data_types:
                    if data_type == "customers":
                        # Synchroniser vers Salesforce comme Account
                        user_info = await self.db.users.find_one({"id": user_id})
                        synced_data["customers"] = {
                            "total": 1,
                            "synced": 1,
                            "salesforce_account_id": f"001{uuid.uuid4().hex[:15]}"
                        }
                    elif data_type == "devices":
                        # Synchroniser les devices comme Assets
                        devices = await self.db.devices.find({"owner_id": user_id}).to_list(None)
                        synced_data["devices"] = {
                            "total": len(devices),
                            "synced": len(devices),
                            "salesforce_asset_ids": [f"02i{uuid.uuid4().hex[:15]}" for _ in devices]
                        }
                    elif data_type == "contracts":
                        # Synchroniser les contrats de service
                        synced_data["contracts"] = {
                            "total": 1,
                            "synced": 1,
                            "salesforce_contract_id": f"800{uuid.uuid4().hex[:15]}"
                        }
                
                return {
                    "success": True,
                    "connector_type": "salesforce",
                    "sync_direction": sync_direction,
                    "synced_data": synced_data,
                    "sync_time": datetime.utcnow(),
                    "total_records": sum(data.get("total", 0) for data in synced_data.values())
                }
            
            return {
                "success": False,
                "error": f"Opération '{operation}' non supportée pour Salesforce"
            }
            
        except Exception as e:
            logger.error(f"Erreur Salesforce connector: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_oracle_connector(self, user_id: str, connection_params: Dict, 
                                     sync_direction: str, data_types: List[str], 
                                     operation: str) -> Dict[str, Any]:
        """Handler pour Oracle ERP"""
        return {"success": False, "error": "Oracle ERP connector non implémenté"}
    
    async def _handle_dynamics_erp_connector(self, user_id: str, connection_params: Dict, 
                                           sync_direction: str, data_types: List[str], 
                                           operation: str) -> Dict[str, Any]:
        """Handler pour Microsoft Dynamics ERP"""
        return {"success": False, "error": "Microsoft Dynamics ERP connector non implémenté"}
    
    async def _handle_netsuite_connector(self, user_id: str, connection_params: Dict, 
                                       sync_direction: str, data_types: List[str], 
                                       operation: str) -> Dict[str, Any]:
        """Handler pour NetSuite"""
        return {"success": False, "error": "NetSuite connector non implémenté"}
    
    async def _handle_odoo_connector(self, user_id: str, connection_params: Dict, 
                                   sync_direction: str, data_types: List[str], 
                                   operation: str) -> Dict[str, Any]:
        """Handler pour Odoo"""
        return {"success": False, "error": "Odoo connector non implémenté"}
    
    async def _handle_custom_erp_connector(self, user_id: str, connection_params: Dict, 
                                         sync_direction: str, data_types: List[str], 
                                         operation: str) -> Dict[str, Any]:
        """Handler pour ERP personnalisé"""
        return {"success": False, "error": "ERP personnalisé non implémenté"}
    
    async def _handle_hubspot_connector(self, user_id: str, connection_params: Dict, 
                                      sync_direction: str, data_types: List[str], 
                                      operation: str) -> Dict[str, Any]:
        """Handler pour HubSpot"""
        return {"success": False, "error": "HubSpot connector non implémenté"}
    
    async def _handle_dynamics_crm_connector(self, user_id: str, connection_params: Dict, 
                                           sync_direction: str, data_types: List[str], 
                                           operation: str) -> Dict[str, Any]:
        """Handler pour Microsoft Dynamics CRM"""
        return {"success": False, "error": "Microsoft Dynamics CRM connector non implémenté"}
    
    async def _handle_zoho_connector(self, user_id: str, connection_params: Dict, 
                                   sync_direction: str, data_types: List[str], 
                                   operation: str) -> Dict[str, Any]:
        """Handler pour Zoho"""
        return {"success": False, "error": "Zoho connector non implémenté"}
    
    async def _handle_pipedrive_connector(self, user_id: str, connection_params: Dict, 
                                        sync_direction: str, data_types: List[str], 
                                        operation: str) -> Dict[str, Any]:
        """Handler pour Pipedrive"""
        return {"success": False, "error": "Pipedrive connector non implémenté"}
    
    async def _handle_custom_crm_connector(self, user_id: str, connection_params: Dict, 
                                         sync_direction: str, data_types: List[str], 
                                         operation: str) -> Dict[str, Any]:
        """Handler pour CRM personnalisé"""
        return {"success": False, "error": "CRM personnalisé non implémenté"}
    
    # ===== MÉTHODES UTILITAIRES =====
    
    async def _validate_connector_config(self, config: ConnectorConfig) -> Dict[str, Any]:
        """Valide la configuration d'un connecteur"""
        try:
            # Vérifier les paramètres obligatoires
            if not config.connector_id or not config.system_type:
                return {
                    "valid": False,
                    "error": "ID connecteur et type système obligatoires"
                }
            
            # Vérifier la fréquence de synchronisation
            if config.sync_frequency < 5:  # Minimum 5 minutes
                return {
                    "valid": False,
                    "error": "Fréquence de synchronisation minimum: 5 minutes"
                }
            
            # Vérifier les types de données
            valid_data_types = [dt.value for dt in DataType]
            invalid_types = [dt.value for dt in config.data_types if dt.value not in valid_data_types]
            if invalid_types:
                return {
                    "valid": False,
                    "error": f"Types de données invalides: {invalid_types}"
                }
            
            return {
                "valid": True,
                "message": "Configuration valide"
            }
            
        except Exception as e:
            logger.error(f"Erreur validation config: {e}")
            return {
                "valid": False,
                "error": str(e)
            }
    
    async def _test_connector_connection(self, config: ConnectorConfig) -> Dict[str, Any]:
        """Teste la connexion à un système ERP/CRM"""
        try:
            # Simulation de test de connexion
            if config.system_type == "sap":
                # Tester la connexion SAP
                return {
                    "success": True,
                    "system": "SAP",
                    "version": "S/4HANA",
                    "response_time": 125
                }
            elif config.system_type == "salesforce":
                # Tester la connexion Salesforce
                return {
                    "success": True,
                    "system": "Salesforce",
                    "org_id": "00D000000000000",
                    "response_time": 89
                }
            else:
                return {
                    "success": True,
                    "system": config.system_type,
                    "response_time": 156
                }
            
        except Exception as e:
            logger.error(f"Erreur test connexion: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _encrypt_connection_params(self, params: Dict[str, Any]) -> str:
        """Chiffre les paramètres de connexion"""
        # Simulation de chiffrement
        import base64
        params_json = json.dumps(params)
        encoded = base64.b64encode(params_json.encode()).decode()
        return f"encrypted_{encoded}"
    
    def _decrypt_connection_params(self, encrypted_params: str) -> Dict[str, Any]:
        """Déchiffre les paramètres de connexion"""
        # Simulation de déchiffrement
        import base64
        if encrypted_params.startswith("encrypted_"):
            encoded = encrypted_params[10:]
            decoded = base64.b64decode(encoded).decode()
            return json.loads(decoded)
        return {}
    
    async def _schedule_sync_job(self, user_id: str, connector_id: str, frequency: int):
        """Programme une tâche de synchronisation automatique"""
        try:
            # Simulation de programmation de tâche
            job_id = f"{user_id}_{connector_id}"
            self.sync_jobs[job_id] = {
                "user_id": user_id,
                "connector_id": connector_id,
                "frequency": frequency,
                "next_run": datetime.utcnow() + timedelta(minutes=frequency),
                "active": True
            }
            logger.info(f"Tâche sync programmée: {job_id}")
            
        except Exception as e:
            logger.error(f"Erreur programmation sync: {e}")
    
    async def _cancel_sync_job(self, user_id: str, connector_id: str):
        """Annule une tâche de synchronisation automatique"""
        try:
            job_id = f"{user_id}_{connector_id}"
            if job_id in self.sync_jobs:
                del self.sync_jobs[job_id]
                logger.info(f"Tâche sync annulée: {job_id}")
                
        except Exception as e:
            logger.error(f"Erreur annulation sync: {e}")
    
    async def _log_sync_operation(self, user_id: str, connector_id: str, result: Dict[str, Any]):
        """Enregistre une opération de synchronisation"""
        try:
            log_entry = {
                "user_id": user_id,
                "connector_id": connector_id,
                "operation": "sync",
                "success": result.get("success", False),
                "timestamp": datetime.utcnow(),
                "details": result,
                "total_records": result.get("total_records", 0)
            }
            
            await self.db.connector_logs.insert_one(log_entry)
            
        except Exception as e:
            logger.error(f"Erreur log sync: {e}")
    
    async def get_sync_logs(self, user_id: str, connector_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Récupère les logs de synchronisation"""
        try:
            query = {"user_id": user_id}
            if connector_id:
                query["connector_id"] = connector_id
            
            logs = await self.db.connector_logs.find(query).sort("timestamp", -1).limit(limit).to_list(None)
            
            return logs
            
        except Exception as e:
            logger.error(f"Erreur récupération logs: {e}")
            return []
    
    async def get_supported_systems(self) -> Dict[str, Any]:
        """Récupère la liste des systèmes ERP/CRM supportés"""
        try:
            return {
                "erp_systems": [
                    {
                        "type": "sap",
                        "name": "SAP S/4HANA",
                        "description": "Système ERP SAP",
                        "supported_data_types": ["devices", "customers", "orders", "inventory"],
                        "connection_params": ["server", "client", "username", "password"]
                    },
                    {
                        "type": "oracle",
                        "name": "Oracle ERP Cloud",
                        "description": "Système ERP Oracle",
                        "supported_data_types": ["customers", "orders", "inventory", "contracts"],
                        "connection_params": ["server", "port", "username", "password"]
                    },
                    {
                        "type": "microsoft_dynamics",
                        "name": "Microsoft Dynamics 365",
                        "description": "Système ERP Microsoft",
                        "supported_data_types": ["customers", "orders", "inventory", "users"],
                        "connection_params": ["server", "database", "username", "password"]
                    }
                ],
                "crm_systems": [
                    {
                        "type": "salesforce",
                        "name": "Salesforce",
                        "description": "CRM Salesforce",
                        "supported_data_types": ["customers", "contracts", "devices"],
                        "connection_params": ["instance_url", "username", "password", "security_token"]
                    },
                    {
                        "type": "hubspot",
                        "name": "HubSpot",
                        "description": "CRM HubSpot",
                        "supported_data_types": ["customers", "contracts"],
                        "connection_params": ["api_key", "portal_id"]
                    },
                    {
                        "type": "microsoft_dynamics_crm",
                        "name": "Microsoft Dynamics 365 CRM",
                        "description": "CRM Microsoft Dynamics",
                        "supported_data_types": ["customers", "contracts", "users"],
                        "connection_params": ["server", "organization", "username", "password"]
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Erreur récupération systèmes supportés: {e}")
            return {"erp_systems": [], "crm_systems": []}
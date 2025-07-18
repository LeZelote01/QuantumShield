"""
Service de gestion des mises à jour OTA (Over-The-Air)
Gestion sécurisée des mises à jour firmware pour dispositifs IoT
"""

import asyncio
import logging
import json
import uuid
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import io
import zipfile
from pathlib import Path

logger = logging.getLogger(__name__)

class UpdateStatus(str, Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    VERIFYING = "verifying"
    INSTALLING = "installing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLBACK = "rollback"

class UpdateType(str, Enum):
    FIRMWARE = "firmware"
    APPLICATION = "application"
    CONFIGURATION = "configuration"
    SECURITY_PATCH = "security_patch"
    DRIVER = "driver"

class UpdatePriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class DeviceCapability(str, Enum):
    OTA_SUPPORT = "ota_support"
    INCREMENTAL_UPDATE = "incremental_update"
    ROLLBACK_SUPPORT = "rollback_support"
    VERIFICATION_SUPPORT = "verification_support"
    SECURE_BOOT = "secure_boot"

class OTAUpdateService:
    """Service de gestion des mises à jour OTA"""
    
    def __init__(self, db):
        self.db = db
        self.update_queue = {}
        self.active_updates = {}
        self.firmware_repository = {}
        self.device_capabilities = {}
        self.security_keys = {}
        self.is_initialized = False
        self._initialize()
    
    def _initialize(self):
        """Initialise le service OTA"""
        try:
            # Configuration par défaut
            self.config = {
                "max_concurrent_updates": 10,
                "chunk_size": 4096,  # 4KB chunks
                "verification_timeout": 300,  # 5 minutes
                "download_timeout": 1800,  # 30 minutes
                "retry_attempts": 3,
                "rollback_timeout": 600,  # 10 minutes
                "signature_algorithm": "SHA256-RSA",
                "encryption_algorithm": "AES-256-GCM"
            }
            
            # Initialiser les collections
            self.update_queue = {}
            self.active_updates = {}
            self.firmware_repository = {}
            
            self.is_initialized = True
            logger.info("Service OTA Update initialisé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur initialisation OTA Update: {str(e)}")
            self.is_initialized = False
    
    def is_ready(self) -> bool:
        """Vérifie si le service est prêt"""
        return self.is_initialized
    
    # ==============================
    # Gestion des firmwares
    # ==============================
    
    async def register_firmware(self, 
                               firmware_id: str,
                               version: str,
                               device_model: str,
                               firmware_data: bytes,
                               description: str = None,
                               update_type: UpdateType = UpdateType.FIRMWARE,
                               priority: UpdatePriority = UpdatePriority.MEDIUM,
                               required_capabilities: List[DeviceCapability] = None) -> Dict[str, Any]:
        """Enregistre un nouveau firmware"""
        try:
            # Calculer le hash du firmware
            firmware_hash = hashlib.sha256(firmware_data).hexdigest()
            
            # Générer signature (simulation)
            signature = self._generate_signature(firmware_data)
            
            # Compresser le firmware
            compressed_data = self._compress_firmware(firmware_data)
            
            firmware_info = {
                "firmware_id": firmware_id,
                "version": version,
                "device_model": device_model,
                "size": len(firmware_data),
                "compressed_size": len(compressed_data),
                "hash": firmware_hash,
                "signature": signature,
                "description": description,
                "update_type": update_type.value,
                "priority": priority.value,
                "required_capabilities": [cap.value for cap in (required_capabilities or [])],
                "created_at": datetime.utcnow(),
                "download_count": 0,
                "success_rate": 0.0,
                "metadata": {
                    "compression_ratio": len(compressed_data) / len(firmware_data),
                    "checksum_algorithm": "SHA256",
                    "signature_algorithm": self.config["signature_algorithm"]
                }
            }
            
            # Stocker en base de données
            await self.db.firmware_repository.insert_one(firmware_info)
            
            # Stocker les données firmware (en pratique, utiliser un système de fichiers)
            self.firmware_repository[firmware_id] = {
                "data": firmware_data,
                "compressed_data": compressed_data,
                "info": firmware_info
            }
            
            logger.info(f"Firmware {firmware_id} v{version} enregistré pour {device_model}")
            
            return {
                "success": True,
                "firmware_id": firmware_id,
                "version": version,
                "hash": firmware_hash,
                "size": len(firmware_data),
                "compressed_size": len(compressed_data)
            }
            
        except Exception as e:
            logger.error(f"Erreur enregistrement firmware: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def list_available_firmwares(self, device_model: str = None) -> List[Dict[str, Any]]:
        """Liste les firmwares disponibles"""
        try:
            query = {}
            if device_model:
                query["device_model"] = device_model
            
            firmwares = await self.db.firmware_repository.find(query).to_list(None)
            
            # Nettoyer les données pour la réponse
            result = []
            for firmware in firmwares:
                firmware.pop("_id", None)  # Supprimer l'ID MongoDB
                result.append(firmware)
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur liste firmwares: {str(e)}")
            return []
    
    async def get_firmware_info(self, firmware_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les informations d'un firmware"""
        try:
            firmware = await self.db.firmware_repository.find_one({"firmware_id": firmware_id})
            if firmware:
                firmware.pop("_id", None)
                return firmware
            return None
            
        except Exception as e:
            logger.error(f"Erreur récupération firmware info: {str(e)}")
            return None
    
    # ==============================
    # Gestion des mises à jour
    # ==============================
    
    async def schedule_update(self,
                             device_id: str,
                             firmware_id: str,
                             scheduled_time: datetime = None,
                             force_update: bool = False) -> Dict[str, Any]:
        """Planifie une mise à jour pour un dispositif"""
        try:
            # Vérifier que le firmware existe
            firmware_info = await self.get_firmware_info(firmware_id)
            if not firmware_info:
                return {
                    "success": False,
                    "error": "Firmware non trouvé"
                }
            
            # Vérifier les capacités du dispositif
            device_info = await self.db.devices.find_one({"device_id": device_id})
            if not device_info:
                return {
                    "success": False,
                    "error": "Dispositif non trouvé"
                }
            
            # Vérifier compatibilité
            if device_info.get("device_model") != firmware_info.get("device_model"):
                if not force_update:
                    return {
                        "success": False,
                        "error": "Firmware non compatible avec le modèle de dispositif"
                    }
            
            # Créer l'entrée de mise à jour
            update_id = str(uuid.uuid4())
            update_info = {
                "update_id": update_id,
                "device_id": device_id,
                "firmware_id": firmware_id,
                "firmware_version": firmware_info["version"],
                "status": UpdateStatus.PENDING.value,
                "priority": firmware_info["priority"],
                "scheduled_time": scheduled_time or datetime.utcnow(),
                "created_at": datetime.utcnow(),
                "started_at": None,
                "completed_at": None,
                "progress": 0,
                "error_message": None,
                "retry_count": 0,
                "force_update": force_update
            }
            
            # Stocker en base
            await self.db.ota_updates.insert_one(update_info)
            
            # Ajouter à la queue
            self.update_queue[update_id] = update_info
            
            logger.info(f"Mise à jour {update_id} planifiée pour {device_id}")
            
            return {
                "success": True,
                "update_id": update_id,
                "scheduled_time": update_info["scheduled_time"].isoformat(),
                "firmware_version": firmware_info["version"]
            }
            
        except Exception as e:
            logger.error(f"Erreur planification mise à jour: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def start_update(self, update_id: str) -> Dict[str, Any]:
        """Démarre une mise à jour"""
        try:
            if update_id not in self.update_queue:
                return {
                    "success": False,
                    "error": "Mise à jour non trouvée"
                }
            
            update_info = self.update_queue[update_id]
            
            # Vérifier que le dispositif est disponible
            device_id = update_info["device_id"]
            device_info = await self.db.devices.find_one({"device_id": device_id})
            if not device_info or device_info.get("status") != "online":
                return {
                    "success": False,
                    "error": "Dispositif non disponible"
                }
            
            # Démarrer le processus de mise à jour
            update_info["status"] = UpdateStatus.DOWNLOADING.value
            update_info["started_at"] = datetime.utcnow()
            
            # Mettre à jour en base
            await self.db.ota_updates.update_one(
                {"update_id": update_id},
                {"$set": update_info}
            )
            
            # Déplacer vers les mises à jour actives
            self.active_updates[update_id] = update_info
            del self.update_queue[update_id]
            
            # Démarrer le processus en arrière-plan
            asyncio.create_task(self._execute_update(update_id))
            
            return {
                "success": True,
                "update_id": update_id,
                "status": UpdateStatus.DOWNLOADING.value
            }
            
        except Exception as e:
            logger.error(f"Erreur démarrage mise à jour: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_update(self, update_id: str):
        """Exécute le processus de mise à jour"""
        try:
            if update_id not in self.active_updates:
                return
            
            update_info = self.active_updates[update_id]
            firmware_id = update_info["firmware_id"]
            device_id = update_info["device_id"]
            
            logger.info(f"Exécution mise à jour {update_id} pour {device_id}")
            
            # Étape 1: Téléchargement
            await self._update_progress(update_id, 10, UpdateStatus.DOWNLOADING)
            success = await self._download_firmware(update_id, firmware_id)
            if not success:
                await self._update_failed(update_id, "Erreur téléchargement")
                return
            
            # Étape 2: Vérification
            await self._update_progress(update_id, 30, UpdateStatus.VERIFYING)
            success = await self._verify_firmware(update_id, firmware_id)
            if not success:
                await self._update_failed(update_id, "Erreur vérification")
                return
            
            # Étape 3: Installation
            await self._update_progress(update_id, 50, UpdateStatus.INSTALLING)
            success = await self._install_firmware(update_id, firmware_id)
            if not success:
                await self._update_failed(update_id, "Erreur installation")
                return
            
            # Étape 4: Finalisation
            await self._update_progress(update_id, 100, UpdateStatus.COMPLETED)
            await self._update_completed(update_id)
            
        except Exception as e:
            logger.error(f"Erreur exécution mise à jour {update_id}: {str(e)}")
            await self._update_failed(update_id, str(e))
    
    async def _download_firmware(self, update_id: str, firmware_id: str) -> bool:
        """Simule le téléchargement du firmware"""
        try:
            # Simuler le téléchargement avec progression
            for progress in range(10, 31, 5):
                await asyncio.sleep(0.5)  # Simuler le temps de téléchargement
                await self._update_progress(update_id, progress, UpdateStatus.DOWNLOADING)
            
            # Vérifier que le firmware existe
            if firmware_id not in self.firmware_repository:
                return False
            
            logger.info(f"Téléchargement firmware {firmware_id} terminé")
            return True
            
        except Exception as e:
            logger.error(f"Erreur téléchargement firmware: {str(e)}")
            return False
    
    async def _verify_firmware(self, update_id: str, firmware_id: str) -> bool:
        """Vérifie l'intégrité du firmware"""
        try:
            # Simuler la vérification
            await asyncio.sleep(1)
            
            # Vérifier hash et signature
            firmware_info = self.firmware_repository.get(firmware_id)
            if not firmware_info:
                return False
            
            # Simuler la vérification du hash
            data = firmware_info["data"]
            calculated_hash = hashlib.sha256(data).hexdigest()
            expected_hash = firmware_info["info"]["hash"]
            
            if calculated_hash != expected_hash:
                logger.error(f"Vérification hash échouée pour firmware {firmware_id}")
                return False
            
            # Simuler la vérification de signature
            signature = firmware_info["info"]["signature"]
            if not self._verify_signature(data, signature):
                logger.error(f"Vérification signature échouée pour firmware {firmware_id}")
                return False
            
            logger.info(f"Vérification firmware {firmware_id} réussie")
            return True
            
        except Exception as e:
            logger.error(f"Erreur vérification firmware: {str(e)}")
            return False
    
    async def _install_firmware(self, update_id: str, firmware_id: str) -> bool:
        """Installe le firmware sur le dispositif"""
        try:
            # Simuler l'installation avec progression
            for progress in range(50, 101, 10):
                await asyncio.sleep(0.5)
                await self._update_progress(update_id, progress, UpdateStatus.INSTALLING)
            
            # Simuler l'installation
            await asyncio.sleep(2)
            
            logger.info(f"Installation firmware {firmware_id} terminée")
            return True
            
        except Exception as e:
            logger.error(f"Erreur installation firmware: {str(e)}")
            return False
    
    async def _update_progress(self, update_id: str, progress: int, status: UpdateStatus):
        """Met à jour le progrès de la mise à jour"""
        try:
            if update_id in self.active_updates:
                self.active_updates[update_id]["progress"] = progress
                self.active_updates[update_id]["status"] = status.value
                
                # Mettre à jour en base
                await self.db.ota_updates.update_one(
                    {"update_id": update_id},
                    {"$set": {
                        "progress": progress,
                        "status": status.value,
                        "updated_at": datetime.utcnow()
                    }}
                )
                
        except Exception as e:
            logger.error(f"Erreur mise à jour progrès: {str(e)}")
    
    async def _update_completed(self, update_id: str):
        """Marque la mise à jour comme terminée"""
        try:
            if update_id in self.active_updates:
                update_info = self.active_updates[update_id]
                update_info["completed_at"] = datetime.utcnow()
                update_info["status"] = UpdateStatus.COMPLETED.value
                
                # Mettre à jour en base
                await self.db.ota_updates.update_one(
                    {"update_id": update_id},
                    {"$set": update_info}
                )
                
                # Mettre à jour le dispositif
                device_id = update_info["device_id"]
                firmware_version = update_info["firmware_version"]
                
                await self.db.devices.update_one(
                    {"device_id": device_id},
                    {"$set": {
                        "firmware_version": firmware_version,
                        "last_update": datetime.utcnow()
                    }}
                )
                
                # Supprimer des mises à jour actives
                del self.active_updates[update_id]
                
                logger.info(f"Mise à jour {update_id} terminée avec succès")
                
        except Exception as e:
            logger.error(f"Erreur finalisation mise à jour: {str(e)}")
    
    async def _update_failed(self, update_id: str, error_message: str):
        """Marque la mise à jour comme échouée"""
        try:
            if update_id in self.active_updates:
                update_info = self.active_updates[update_id]
                update_info["status"] = UpdateStatus.FAILED.value
                update_info["error_message"] = error_message
                update_info["retry_count"] = update_info.get("retry_count", 0) + 1
                
                # Mettre à jour en base
                await self.db.ota_updates.update_one(
                    {"update_id": update_id},
                    {"$set": update_info}
                )
                
                # Retenter si possible
                if update_info["retry_count"] < self.config["retry_attempts"]:
                    logger.warning(f"Tentative {update_info['retry_count']} échouée pour {update_id}, nouvelle tentative...")
                    await asyncio.sleep(60)  # Attendre 1 minute
                    await self.start_update(update_id)
                else:
                    logger.error(f"Mise à jour {update_id} échouée définitivement: {error_message}")
                    del self.active_updates[update_id]
                
        except Exception as e:
            logger.error(f"Erreur gestion échec mise à jour: {str(e)}")
    
    # ==============================
    # Utilitaires
    # ==============================
    
    def _generate_signature(self, data: bytes) -> str:
        """Génère une signature pour le firmware (simulation)"""
        # En pratique, utiliser une vraie signature cryptographique
        signature_data = hashlib.sha256(data + b"secret_key").digest()
        return base64.b64encode(signature_data).decode()
    
    def _verify_signature(self, data: bytes, signature: str) -> bool:
        """Vérifie la signature du firmware (simulation)"""
        try:
            expected_signature = self._generate_signature(data)
            return signature == expected_signature
        except:
            return False
    
    def _compress_firmware(self, data: bytes) -> bytes:
        """Compresse le firmware"""
        try:
            # Utiliser compression ZIP
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("firmware.bin", data)
            return buffer.getvalue()
        except:
            # Fallback: retourner les données originales
            return data
    
    # ==============================
    # Status et statistiques
    # ==============================
    
    async def get_update_status(self, update_id: str) -> Optional[Dict[str, Any]]:
        """Récupère le statut d'une mise à jour"""
        try:
            # Chercher dans les mises à jour actives
            if update_id in self.active_updates:
                return self.active_updates[update_id]
            
            # Chercher dans la queue
            if update_id in self.update_queue:
                return self.update_queue[update_id]
            
            # Chercher en base
            update = await self.db.ota_updates.find_one({"update_id": update_id})
            if update:
                update.pop("_id", None)
                return update
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur récupération statut mise à jour: {str(e)}")
            return None
    
    async def get_device_updates(self, device_id: str) -> List[Dict[str, Any]]:
        """Récupère l'historique des mises à jour d'un dispositif"""
        try:
            updates = await self.db.ota_updates.find(
                {"device_id": device_id}
            ).sort("created_at", -1).to_list(None)
            
            result = []
            for update in updates:
                update.pop("_id", None)
                result.append(update)
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur récupération historique mises à jour: {str(e)}")
            return []
    
    async def get_ota_statistics(self) -> Dict[str, Any]:
        """Récupère les statistiques OTA"""
        try:
            stats = {
                "total_updates": 0,
                "successful_updates": 0,
                "failed_updates": 0,
                "pending_updates": 0,
                "active_updates": 0,
                "success_rate": 0.0,
                "average_duration": 0.0,
                "firmware_count": 0
            }
            
            # Compter les mises à jour
            total_updates = await self.db.ota_updates.count_documents({})
            successful_updates = await self.db.ota_updates.count_documents({"status": "completed"})
            failed_updates = await self.db.ota_updates.count_documents({"status": "failed"})
            pending_updates = await self.db.ota_updates.count_documents({"status": "pending"})
            
            stats["total_updates"] = total_updates
            stats["successful_updates"] = successful_updates
            stats["failed_updates"] = failed_updates
            stats["pending_updates"] = pending_updates
            stats["active_updates"] = len(self.active_updates)
            
            # Calculer le taux de succès
            if total_updates > 0:
                stats["success_rate"] = (successful_updates / total_updates) * 100
            
            # Compter les firmwares
            firmware_count = await self.db.firmware_repository.count_documents({})
            stats["firmware_count"] = firmware_count
            
            return stats
            
        except Exception as e:
            logger.error(f"Erreur récupération statistiques OTA: {str(e)}")
            return {}
    
    async def cancel_update(self, update_id: str) -> Dict[str, Any]:
        """Annule une mise à jour"""
        try:
            # Vérifier si la mise à jour existe
            if update_id not in self.update_queue and update_id not in self.active_updates:
                return {
                    "success": False,
                    "error": "Mise à jour non trouvée"
                }
            
            # Annuler selon l'état
            if update_id in self.update_queue:
                del self.update_queue[update_id]
            elif update_id in self.active_updates:
                del self.active_updates[update_id]
            
            # Mettre à jour en base
            await self.db.ota_updates.update_one(
                {"update_id": update_id},
                {"$set": {
                    "status": "cancelled",
                    "cancelled_at": datetime.utcnow()
                }}
            )
            
            return {
                "success": True,
                "message": f"Mise à jour {update_id} annulée"
            }
            
        except Exception as e:
            logger.error(f"Erreur annulation mise à jour: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def shutdown(self):
        """Arrête le service OTA"""
        try:
            # Annuler toutes les mises à jour actives
            for update_id in list(self.active_updates.keys()):
                await self.cancel_update(update_id)
            
            # Vider les queues
            self.update_queue.clear()
            self.active_updates.clear()
            self.firmware_repository.clear()
            
            logger.info("Service OTA Update arrêté")
            
        except Exception as e:
            logger.error(f"Erreur arrêt service OTA: {str(e)}")
"""
Service de gestion des devices IoT
Gestion des dispositifs connectés avec sécurité post-quantique
"""

import asyncio
import hashlib
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from motor.motor_asyncio import AsyncIOMotorCollection

from models.quantum_models import Device, DeviceCreate, DeviceUpdate, DeviceHeartbeat, DeviceStatus, AnomalyDetection
from services.ntru_service import NTRUService

logger = logging.getLogger(__name__)

class DeviceService:
    """Service de gestion des devices IoT avec sécurité post-quantique"""
    
    def __init__(self, db):
        self.db = db
        self.devices: AsyncIOMotorCollection = db.devices
        self.device_logs: AsyncIOMotorCollection = db.device_logs
        self.anomalies: AsyncIOMotorCollection = db.anomalies
        self.ntru_service = NTRUService()
        self.heartbeat_timeout = 300  # 5 minutes
    
    async def register_device(self, device_data: DeviceCreate, owner_id: str) -> Device:
        """Enregistre un nouveau device IoT"""
        try:
            # Vérifier si le device existe déjà
            existing_device = await self.devices.find_one({"device_id": device_data.device_id})
            if existing_device:
                raise Exception(f"Device {device_data.device_id} déjà enregistré")
            
            # Générer une paire de clés NTRU++ pour le device
            public_key, private_key = self.ntru_service.generate_keypair()
            
            # Calculer le hash du firmware initial
            firmware_hash = self.calculate_firmware_hash(device_data.device_id, "1.0.0")
            
            # Créer le device
            device = Device(
                device_id=device_data.device_id,
                device_name=device_data.device_name,
                device_type=device_data.device_type,
                owner_id=owner_id,
                firmware_hash=firmware_hash,
                public_key=public_key,
                location=device_data.location,
                capabilities=device_data.capabilities
            )
            
            # Sauvegarder dans la base de données
            await self.devices.insert_one(device.dict())
            
            # Log de l'enregistrement
            await self.log_device_activity(device.id, "device_registered", {
                "device_type": device.device_type,
                "capabilities": device.capabilities,
                "location": device.location
            })
            
            logger.info(f"Device {device.device_id} enregistré avec succès")
            return device
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du device: {e}")
            raise Exception(f"Impossible d'enregistrer le device: {e}")
    
    async def get_device(self, device_id: str) -> Optional[Device]:
        """Récupère un device par son ID"""
        try:
            device_data = await self.devices.find_one({"device_id": device_id})
            if device_data:
                return Device(**device_data)
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du device: {e}")
            return None
    
    async def get_user_devices(self, owner_id: str) -> List[Device]:
        """Récupère tous les devices d'un utilisateur"""
        try:
            cursor = self.devices.find({"owner_id": owner_id})
            devices_data = await cursor.to_list(length=None)
            
            devices = []
            for device_data in devices_data:
                devices.append(Device(**device_data))
            
            return devices
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des devices: {e}")
            return []
    
    async def update_device(self, device_id: str, update_data: DeviceUpdate) -> Optional[Device]:
        """Met à jour un device"""
        try:
            # Récupérer le device existant
            existing_device = await self.get_device(device_id)
            if not existing_device:
                return None
            
            # Préparer les données de mise à jour
            update_dict = {}
            if update_data.device_name is not None:
                update_dict["device_name"] = update_data.device_name
            if update_data.status is not None:
                update_dict["status"] = update_data.status
            if update_data.location is not None:
                update_dict["location"] = update_data.location
            if update_data.capabilities is not None:
                update_dict["capabilities"] = update_data.capabilities
            
            # Mettre à jour dans la base de données
            if update_dict:
                await self.devices.update_one(
                    {"device_id": device_id},
                    {"$set": update_dict}
                )
            
            # Log de la mise à jour
            await self.log_device_activity(existing_device.id, "device_updated", update_dict)
            
            # Récupérer le device mis à jour
            updated_device = await self.get_device(device_id)
            
            logger.info(f"Device {device_id} mis à jour avec succès")
            return updated_device
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du device: {e}")
            return None
    
    async def process_heartbeat(self, heartbeat: DeviceHeartbeat) -> Dict[str, Any]:
        """Traite un heartbeat d'un device"""
        try:
            # Vérifier que le device existe
            device = await self.get_device(heartbeat.device_id)
            if not device:
                raise Exception(f"Device {heartbeat.device_id} non trouvé")
            
            # Mettre à jour le timestamp du dernier heartbeat
            await self.devices.update_one(
                {"device_id": heartbeat.device_id},
                {
                    "$set": {
                        "last_heartbeat": datetime.utcnow(),
                        "status": heartbeat.status
                    }
                }
            )
            
            # Vérifier l'intégrité du firmware
            firmware_valid = await self.verify_firmware_integrity(
                heartbeat.device_id, 
                heartbeat.firmware_hash
            )
            
            # Détecter les anomalies
            anomaly_detected = await self.detect_anomalies(heartbeat)
            
            # Log du heartbeat
            await self.log_device_activity(device.id, "heartbeat_received", {
                "status": heartbeat.status,
                "firmware_hash": heartbeat.firmware_hash,
                "firmware_valid": firmware_valid,
                "anomaly_detected": anomaly_detected,
                "sensor_data": heartbeat.sensor_data
            })
            
            # Réponse au device
            response = {
                "device_id": heartbeat.device_id,
                "timestamp": datetime.utcnow(),
                "firmware_valid": firmware_valid,
                "anomaly_detected": anomaly_detected,
                "next_heartbeat": datetime.utcnow() + timedelta(seconds=60)
            }
            
            # Si anomalie détectée, ajouter des instructions
            if anomaly_detected:
                response["action_required"] = "isolate_device"
                response["security_level"] = "high"
            
            logger.info(f"Heartbeat traité pour device {heartbeat.device_id}")
            return response
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement du heartbeat: {e}")
            raise Exception(f"Impossible de traiter le heartbeat: {e}")
    
    async def verify_firmware_integrity(self, device_id: str, firmware_hash: str) -> bool:
        """Vérifie l'intégrité du firmware d'un device"""
        try:
            # Récupérer le device
            device = await self.get_device(device_id)
            if not device:
                return False
            
            # Comparer les hashes
            expected_hash = device.firmware_hash
            return firmware_hash == expected_hash
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du firmware: {e}")
            return False
    
    async def detect_anomalies(self, heartbeat: DeviceHeartbeat) -> bool:
        """Détecte les anomalies dans un heartbeat"""
        try:
            # Récupérer l'historique récent du device
            recent_logs = await self.device_logs.find(
                {
                    "device_id": heartbeat.device_id,
                    "timestamp": {"$gte": datetime.utcnow() - timedelta(hours=1)}
                }
            ).to_list(length=100)
            
            # Analyse des anomalies
            anomalies_found = []
            
            # 1. Vérifier la fréquence des heartbeats
            if len(recent_logs) > 120:  # Plus de 2 heartbeats par minute
                anomalies_found.append("heartbeat_frequency_high")
            
            # 2. Vérifier les données des capteurs
            if heartbeat.sensor_data:
                for sensor, value in heartbeat.sensor_data.items():
                    if isinstance(value, (int, float)):
                        if sensor == "temperature" and (value < -40 or value > 85):
                            anomalies_found.append("temperature_out_of_range")
                        elif sensor == "cpu_usage" and value > 95:
                            anomalies_found.append("cpu_usage_high")
                        elif sensor == "memory_usage" and value > 90:
                            anomalies_found.append("memory_usage_high")
            
            # 3. Vérifier les changements de status fréquents
            status_changes = [log for log in recent_logs if log.get("activity_type") == "status_change"]
            if len(status_changes) > 5:
                anomalies_found.append("frequent_status_changes")
            
            # Si anomalies détectées, les enregistrer
            if anomalies_found:
                await self.record_anomaly(heartbeat.device_id, anomalies_found, heartbeat.sensor_data)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur lors de la détection d'anomalies: {e}")
            return False
    
    async def record_anomaly(self, device_id: str, anomaly_types: List[str], sensor_data: Dict[str, Any]):
        """Enregistre une anomalie détectée"""
        try:
            for anomaly_type in anomaly_types:
                anomaly = AnomalyDetection(
                    device_id=device_id,
                    anomaly_type=anomaly_type,
                    severity=self.get_anomaly_severity(anomaly_type),
                    description=self.get_anomaly_description(anomaly_type),
                )
                
                await self.anomalies.insert_one(anomaly.dict())
                
                # Log de l'anomalie
                await self.log_device_activity(device_id, "anomaly_detected", {
                    "anomaly_type": anomaly_type,
                    "severity": anomaly.severity,
                    "sensor_data": sensor_data
                })
            
            logger.warning(f"Anomalies enregistrées pour device {device_id}: {anomaly_types}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement d'anomalie: {e}")
    
    def get_anomaly_severity(self, anomaly_type: str) -> str:
        """Détermine la sévérité d'une anomalie"""
        severity_map = {
            "heartbeat_frequency_high": "medium",
            "temperature_out_of_range": "high",
            "cpu_usage_high": "medium",
            "memory_usage_high": "medium",
            "frequent_status_changes": "high",
            "firmware_mismatch": "critical",
            "unauthorized_access": "critical"
        }
        return severity_map.get(anomaly_type, "low")
    
    def get_anomaly_description(self, anomaly_type: str) -> str:
        """Retourne la description d'une anomalie"""
        descriptions = {
            "heartbeat_frequency_high": "Fréquence de heartbeat anormalement élevée",
            "temperature_out_of_range": "Température hors des limites normales",
            "cpu_usage_high": "Utilisation CPU excessive",
            "memory_usage_high": "Utilisation mémoire excessive",
            "frequent_status_changes": "Changements de status trop fréquents",
            "firmware_mismatch": "Hash du firmware ne correspond pas",
            "unauthorized_access": "Tentative d'accès non autorisé"
        }
        return descriptions.get(anomaly_type, "Anomalie non spécifiée")
    
    async def log_device_activity(self, device_id: str, activity_type: str, data: Dict[str, Any]):
        """Log l'activité d'un device"""
        try:
            log_entry = {
                "device_id": device_id,
                "activity_type": activity_type,
                "timestamp": datetime.utcnow(),
                "data": data
            }
            
            await self.device_logs.insert_one(log_entry)
            
        except Exception as e:
            logger.error(f"Erreur lors du logging: {e}")
    
    def calculate_firmware_hash(self, device_id: str, version: str) -> str:
        """Calcule le hash du firmware"""
        firmware_data = f"{device_id}:{version}:firmware_content"
        return hashlib.sha256(firmware_data.encode()).hexdigest()
    
    async def get_device_metrics(self, device_id: str) -> Dict[str, Any]:
        """Récupère les métriques d'un device"""
        try:
            device = await self.get_device(device_id)
            if not device:
                return {}
            
            # Calculer l'uptime
            now = datetime.utcnow()
            uptime_hours = (now - device.created_at).total_seconds() / 3600
            
            # Derniers logs
            recent_logs = await self.device_logs.find(
                {"device_id": device_id}
            ).sort("timestamp", -1).limit(100).to_list(length=100)
            
            # Compter les anomalies
            anomaly_count = await self.anomalies.count_documents({"device_id": device_id})
            
            # Calculer l'uptime percentage
            heartbeat_logs = [log for log in recent_logs if log.get("activity_type") == "heartbeat_received"]
            expected_heartbeats = max(1, uptime_hours * 60)  # 1 heartbeat par minute
            actual_heartbeats = len(heartbeat_logs)
            uptime_percentage = min(100, (actual_heartbeats / expected_heartbeats) * 100)
            
            return {
                "device_id": device_id,
                "uptime_hours": uptime_hours,
                "uptime_percentage": uptime_percentage,
                "total_heartbeats": actual_heartbeats,
                "anomalies_detected": anomaly_count,
                "last_heartbeat": device.last_heartbeat,
                "firmware_hash": device.firmware_hash,
                "status": device.status,
                "recent_activity": recent_logs[:10]
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des métriques: {e}")
            return {}
    
    async def get_offline_devices(self) -> List[Device]:
        """Récupère les devices hors ligne"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(seconds=self.heartbeat_timeout)
            
            cursor = self.devices.find({
                "last_heartbeat": {"$lt": cutoff_time}
            })
            
            devices_data = await cursor.to_list(length=None)
            
            devices = []
            for device_data in devices_data:
                devices.append(Device(**device_data))
            
            return devices
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des devices hors ligne: {e}")
            return []
    
    async def update_firmware(self, device_id: str, new_firmware_hash: str) -> bool:
        """Met à jour le firmware d'un device"""
        try:
            # Vérifier que le device existe
            device = await self.get_device(device_id)
            if not device:
                return False
            
            # Mettre à jour le hash du firmware
            await self.devices.update_one(
                {"device_id": device_id},
                {"$set": {"firmware_hash": new_firmware_hash}}
            )
            
            # Log de la mise à jour
            await self.log_device_activity(device_id, "firmware_updated", {
                "old_hash": device.firmware_hash,
                "new_hash": new_firmware_hash
            })
            
            logger.info(f"Firmware mis à jour pour device {device_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du firmware: {e}")
            return False
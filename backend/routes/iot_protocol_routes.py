"""
Routes pour le service de protocoles IoT
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

# Import du service
from services.iot_protocol_service import IoTProtocolService, IoTProtocol, MessageType, QoSLevel

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

# Instance du service IoT Protocol (sera injectée par le serveur principal)
iot_protocol_service = None

# Modèles Pydantic
class MQTTConfigModel(BaseModel):
    host: str = "localhost"
    port: int = 1883
    keep_alive: int = 60
    qos_level: int = 1

class CoAPConfigModel(BaseModel):
    host: str = "localhost"
    port: int = 5683
    max_payload_size: int = 1024
    timeout: int = 30

class LoRaWANConfigModel(BaseModel):
    gateway_id: str
    frequency: float = 868.1
    spreading_factor: int = 7
    bandwidth: int = 125

class MQTTPublishModel(BaseModel):
    topic: str
    payload: dict
    qos: int = 1

class LoRaWANDownlinkModel(BaseModel):
    device_id: str
    payload: dict

class DeviceCommandModel(BaseModel):
    device_id: str
    command: str
    parameters: Optional[dict] = None

class SensorDataModel(BaseModel):
    device_id: str
    sensor_type: str
    data: dict
    timestamp: Optional[str] = None

# Dépendance pour obtenir le service
def get_iot_protocol_service():
    # Cette fonction sera injectée par le serveur principal
    return None

@router.get("/health")
async def health_check():
    """Vérifie l'état de santé du service IoT Protocol"""
    try:
        service = get_iot_protocol_service()
        if not service:
            return {"status": "error", "message": "Service non disponible"}
        
        return {
            "status": "healthy" if service.is_ready() else "unhealthy",
            "service": "IoT Protocol Service",
            "timestamp": datetime.utcnow().isoformat(),
            "protocols_available": len(service.protocol_configs)
        }
    except Exception as e:
        logger.error(f"Erreur health check IoT Protocol: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/protocols/status")
async def get_protocol_status():
    """Retourne le statut de tous les protocoles IoT"""
    try:
        service = get_iot_protocol_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        status = await service.get_protocol_status()
        return {
            "success": True,
            "protocols": status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Erreur récupération statut protocoles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/protocols/statistics")
async def get_message_statistics():
    """Retourne les statistiques des messages IoT"""
    try:
        service = get_iot_protocol_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        stats = await service.get_message_statistics()
        return {
            "success": True,
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Erreur récupération statistiques: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/devices/connected")
async def get_connected_devices():
    """Retourne la liste des devices connectés"""
    try:
        service = get_iot_protocol_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        devices = await service.get_connected_devices()
        return {
            "success": True,
            "devices": devices,
            "count": len(devices),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Erreur récupération devices connectés: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===================
# MQTT Endpoints
# ===================

@router.post("/mqtt/start")
async def start_mqtt_broker(config: MQTTConfigModel):
    """Démarre le broker MQTT"""
    try:
        service = get_iot_protocol_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        result = await service.start_mqtt_broker(config.host, config.port)
        return result
    except Exception as e:
        logger.error(f"Erreur démarrage MQTT: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mqtt/publish")
async def publish_mqtt_message(message: MQTTPublishModel):
    """Publie un message MQTT"""
    try:
        service = get_iot_protocol_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        result = await service.publish_mqtt_message(
            message.topic, 
            message.payload, 
            message.qos
        )
        return result
    except Exception as e:
        logger.error(f"Erreur publication MQTT: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mqtt/topics")
async def get_mqtt_topics():
    """Retourne les topics MQTT configurés"""
    try:
        service = get_iot_protocol_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        topics = service.protocol_configs.get("mqtt", {}).get("topics", {})
        return {
            "success": True,
            "topics": topics
        }
    except Exception as e:
        logger.error(f"Erreur récupération topics MQTT: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===================
# CoAP Endpoints
# ===================

@router.post("/coap/start")
async def start_coap_server(config: CoAPConfigModel):
    """Démarre le serveur CoAP"""
    try:
        service = get_iot_protocol_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        result = await service.start_coap_server(config.host, config.port)
        return result
    except Exception as e:
        logger.error(f"Erreur démarrage CoAP: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/coap/resources")
async def get_coap_resources():
    """Retourne les ressources CoAP disponibles"""
    try:
        service = get_iot_protocol_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        if not service.coap_server:
            raise HTTPException(status_code=404, detail="Serveur CoAP non démarré")
        
        resources = service.coap_server.get("resources", {})
        return {
            "success": True,
            "resources": resources
        }
    except Exception as e:
        logger.error(f"Erreur récupération ressources CoAP: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===================
# LoRaWAN Endpoints
# ===================

@router.post("/lorawan/start")
async def start_lorawan_gateway(config: LoRaWANConfigModel):
    """Démarre la passerelle LoRaWAN"""
    try:
        service = get_iot_protocol_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        result = await service.start_lorawan_gateway(config.gateway_id)
        return result
    except Exception as e:
        logger.error(f"Erreur démarrage LoRaWAN: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/lorawan/downlink")
async def send_lorawan_downlink(message: LoRaWANDownlinkModel):
    """Envoie un message downlink LoRaWAN"""
    try:
        service = get_iot_protocol_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        result = await service.send_lorawan_downlink(
            message.device_id, 
            message.payload
        )
        return result
    except Exception as e:
        logger.error(f"Erreur envoi downlink LoRaWAN: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/lorawan/gateway/status")
async def get_lorawan_gateway_status():
    """Retourne le statut de la passerelle LoRaWAN"""
    try:
        service = get_iot_protocol_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        if not service.lorawan_gateway:
            raise HTTPException(status_code=404, detail="Passerelle LoRaWAN non démarrée")
        
        gateway_info = {
            "gateway_id": service.lorawan_gateway.get("gateway_id"),
            "frequency": service.lorawan_gateway.get("frequency"),
            "spreading_factor": service.lorawan_gateway.get("spreading_factor"),
            "running": service.lorawan_gateway.get("running"),
            "devices_count": len(service.lorawan_gateway.get("devices", {})),
            "uplink_messages": len(service.lorawan_gateway.get("uplink_messages", [])),
            "downlink_messages": len(service.lorawan_gateway.get("downlink_messages", []))
        }
        
        return {
            "success": True,
            "gateway": gateway_info
        }
    except Exception as e:
        logger.error(f"Erreur récupération statut passerelle LoRaWAN: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===================
# Device Communication
# ===================

@router.post("/devices/command")
async def send_device_command(command: DeviceCommandModel):
    """Envoie une commande à un device"""
    try:
        service = get_iot_protocol_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        # Simuler l'envoi de commande via le protocole approprié
        # En pratique, on déterminerait le protocole du device
        
        command_data = {
            "device_id": command.device_id,
            "command": command.command,
            "parameters": command.parameters,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Traiter la commande via le handler
        await service._handle_command(command_data, IoTProtocol.MQTT)
        
        return {
            "success": True,
            "message": f"Commande {command.command} envoyée au device {command.device_id}",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Erreur envoi commande device: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/devices/sensor-data")
async def receive_sensor_data(sensor_data: SensorDataModel):
    """Reçoit des données de capteur"""
    try:
        service = get_iot_protocol_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        data = {
            "device_id": sensor_data.device_id,
            "sensor_type": sensor_data.sensor_type,
            "data": sensor_data.data,
            "timestamp": sensor_data.timestamp or datetime.utcnow().isoformat()
        }
        
        # Traiter les données via le handler
        await service._handle_sensor_data(data, IoTProtocol.MQTT)
        
        return {
            "success": True,
            "message": f"Données capteur reçues du device {sensor_data.device_id}",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Erreur réception données capteur: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===================
# Configuration
# ===================

@router.get("/config")
async def get_protocol_configurations():
    """Retourne les configurations des protocoles"""
    try:
        service = get_iot_protocol_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        return {
            "success": True,
            "configurations": service.protocol_configs
        }
    except Exception as e:
        logger.error(f"Erreur récupération configurations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/config/{protocol}")
async def update_protocol_config(protocol: str, config: dict):
    """Met à jour la configuration d'un protocole"""
    try:
        service = get_iot_protocol_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        # Valider le protocole
        if protocol not in [p.value for p in IoTProtocol]:
            raise HTTPException(status_code=400, detail="Protocole non supporté")
        
        # Mettre à jour la configuration
        if protocol not in service.protocol_configs:
            service.protocol_configs[protocol] = {}
        
        service.protocol_configs[protocol].update(config)
        
        return {
            "success": True,
            "message": f"Configuration du protocole {protocol} mise à jour",
            "config": service.protocol_configs[protocol]
        }
    except Exception as e:
        logger.error(f"Erreur mise à jour configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/shutdown")
async def shutdown_all_protocols():
    """Arrête tous les protocoles IoT"""
    try:
        service = get_iot_protocol_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        await service.shutdown()
        
        return {
            "success": True,
            "message": "Tous les protocoles IoT arrêtés"
        }
    except Exception as e:
        logger.error(f"Erreur arrêt protocoles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
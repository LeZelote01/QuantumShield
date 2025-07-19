"""
Service de gestion des protocoles IoT
Support pour MQTT, CoAP, LoRaWAN et autres protocoles IoT
"""

import asyncio
import logging
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import hashlib
import struct

try:
    import asyncio_mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    logging.warning("asyncio_mqtt not available, MQTT support limited")

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    logging.warning("websockets not available, WebSocket support limited")

logger = logging.getLogger(__name__)

class IoTProtocol(str, Enum):
    MQTT = "mqtt"
    COAP = "coap"
    LORAWAN = "lorawan"
    ZIGBEE = "zigbee"
    ZWAVE = "zwave"
    THREAD = "thread"
    MATTER = "matter"
    WEBSOCKET = "websocket"

class MessageType(str, Enum):
    HEARTBEAT = "heartbeat"
    SENSOR_DATA = "sensor_data"
    COMMAND = "command"
    ALERT = "alert"
    FIRMWARE_UPDATE = "firmware_update"
    SECURITY_EVENT = "security_event"

class QoSLevel(int, Enum):
    AT_MOST_ONCE = 0
    AT_LEAST_ONCE = 1
    EXACTLY_ONCE = 2

class IoTProtocolService:
    """Service de gestion des protocoles IoT avancés"""
    
    def __init__(self, db):
        self.db = db
        self.mqtt_client = None
        self.coap_server = None
        self.lorawan_gateway = None
        self.connected_devices = {}
        self.message_handlers = {}
        self.protocol_configs = {}
        self.is_initialized = False
        self._initialize()
    
    def _initialize(self):
        """Initialise le service de protocoles IoT"""
        try:
            # Configuration par défaut des protocoles
            self.protocol_configs = {
                IoTProtocol.MQTT: {
                    "enabled": MQTT_AVAILABLE,
                    "broker_host": "localhost",
                    "broker_port": 1883,
                    "keep_alive": 60,
                    "qos_level": QoSLevel.AT_LEAST_ONCE,
                    "topics": {
                        "heartbeat": "quantumshield/heartbeat",
                        "sensor_data": "quantumshield/sensor",
                        "commands": "quantumshield/commands",
                        "alerts": "quantumshield/alerts"
                    }
                },
                IoTProtocol.COAP: {
                    "enabled": True,
                    "host": "localhost",
                    "port": 5683,
                    "max_payload_size": 1024,
                    "timeout": 30,
                    "retries": 3
                },
                IoTProtocol.LORAWAN: {
                    "enabled": True,
                    "gateway_id": "quantumshield-gw-001",
                    "frequency": 868.1,  # MHz pour l'Europe
                    "spreading_factor": 7,
                    "bandwidth": 125,  # kHz
                    "coding_rate": "4/5",
                    "max_payload": 51  # bytes
                },
                IoTProtocol.WEBSOCKET: {
                    "enabled": WEBSOCKETS_AVAILABLE,
                    "host": "localhost",
                    "port": 8765,
                    "max_connections": 1000,
                    "ping_interval": 20,
                    "ping_timeout": 10
                }
            }
            
            # Initialiser les handlers de messages
            self.message_handlers = {
                MessageType.HEARTBEAT: self._handle_heartbeat,
                MessageType.SENSOR_DATA: self._handle_sensor_data,
                MessageType.COMMAND: self._handle_command,
                MessageType.ALERT: self._handle_alert,
                MessageType.FIRMWARE_UPDATE: self._handle_firmware_update,
                MessageType.SECURITY_EVENT: self._handle_security_event
            }
            
            self.is_initialized = True
            logger.info("Service IoT Protocol initialisé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur initialisation IoT Protocol: {str(e)}")
            self.is_initialized = False
    
    def is_ready(self) -> bool:
        """Vérifie si le service est prêt"""
        return self.is_initialized
    
    # ===================
    # MQTT Implementation
    # ===================
    
    async def start_mqtt_broker(self, host: str = "localhost", port: int = 1883):
        """Démarre le broker MQTT"""
        if not MQTT_AVAILABLE:
            logger.warning("MQTT non disponible, utilisation du simulateur")
            return await self._simulate_mqtt_broker()
        
        try:
            self.mqtt_client = asyncio_mqtt.Client(
                hostname=host,
                port=port,
                keepalive=self.protocol_configs[IoTProtocol.MQTT]["keep_alive"]
            )
            
            # Connexion au broker
            await self.mqtt_client.connect()
            logger.info(f"Broker MQTT connecté sur {host}:{port}")
            
            # Démarrer l'écoute des messages
            asyncio.create_task(self._mqtt_message_loop())
            
            return {"success": True, "broker": f"{host}:{port}"}
            
        except Exception as e:
            logger.error(f"Erreur démarrage broker MQTT: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _simulate_mqtt_broker(self):
        """Simulation du broker MQTT pour les tests"""
        logger.info("Démarrage du simulateur MQTT")
        self.mqtt_client = {
            "connected": True,
            "subscriptions": [],
            "messages": []
        }
        return {"success": True, "broker": "mqtt-simulator"}
    
    async def _mqtt_message_loop(self):
        """Boucle de traitement des messages MQTT"""
        try:
            topics = self.protocol_configs[IoTProtocol.MQTT]["topics"]
            
            # S'abonner aux topics
            for topic_name, topic_pattern in topics.items():
                await self.mqtt_client.subscribe(topic_pattern)
                logger.info(f"Abonnement MQTT: {topic_pattern}")
            
            # Écouter les messages
            async with self.mqtt_client.messages() as messages:
                async for message in messages:
                    await self._process_mqtt_message(message)
                    
        except Exception as e:
            logger.error(f"Erreur boucle MQTT: {str(e)}")
    
    async def _process_mqtt_message(self, message):
        """Traite un message MQTT reçu"""
        try:
            topic = message.topic
            payload = json.loads(message.payload.decode())
            
            # Identifier le type de message
            message_type = self._identify_message_type(topic, payload)
            
            # Traiter selon le type
            handler = self.message_handlers.get(message_type)
            if handler:
                await handler(payload, IoTProtocol.MQTT)
            else:
                logger.warning(f"Handler non trouvé pour type: {message_type}")
                
        except Exception as e:
            logger.error(f"Erreur traitement message MQTT: {str(e)}")
    
    async def publish_mqtt_message(self, topic: str, payload: dict, qos: int = 1):
        """Publie un message MQTT"""
        try:
            if not self.mqtt_client:
                return {"success": False, "error": "Client MQTT non connecté"}
            
            message_json = json.dumps(payload)
            await self.mqtt_client.publish(topic, message_json, qos=qos)
            
            return {"success": True, "topic": topic, "message_id": str(uuid.uuid4())}
            
        except Exception as e:
            logger.error(f"Erreur publication MQTT: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # ==================
    # CoAP Implementation
    # ==================
    
    async def start_coap_server(self, host: str = "localhost", port: int = 5683):
        """Démarre le serveur CoAP"""
        try:
            # Simulation du serveur CoAP
            self.coap_server = {
                "host": host,
                "port": port,
                "running": True,
                "resources": {},
                "clients": {}
            }
            
            logger.info(f"Serveur CoAP simulé démarré sur {host}:{port}")
            
            # Créer les ressources par défaut
            await self._create_default_coap_resources()
            
            return {"success": True, "server": f"coap://{host}:{port}"}
            
        except Exception as e:
            logger.error(f"Erreur démarrage serveur CoAP: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _create_default_coap_resources(self):
        """Crée les ressources CoAP par défaut"""
        default_resources = {
            "/devices": "GET,POST",
            "/sensors": "GET,POST",
            "/commands": "POST",
            "/heartbeat": "POST",
            "/firmware": "GET,PUT"
        }
        
        for resource, methods in default_resources.items():
            self.coap_server["resources"][resource] = {
                "methods": methods.split(","),
                "handler": self._handle_coap_request
            }
    
    async def _handle_coap_request(self, resource: str, method: str, payload: dict):
        """Traite une requête CoAP"""
        try:
            # Router selon la ressource
            if resource == "/heartbeat":
                return await self._handle_heartbeat(payload, IoTProtocol.COAP)
            elif resource == "/sensors":
                return await self._handle_sensor_data(payload, IoTProtocol.COAP)
            elif resource == "/commands":
                return await self._handle_command(payload, IoTProtocol.COAP)
            elif resource == "/firmware":
                return await self._handle_firmware_update(payload, IoTProtocol.COAP)
            else:
                return {"success": False, "error": "Ressource non trouvée"}
                
        except Exception as e:
            logger.error(f"Erreur traitement requête CoAP: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # =====================
    # LoRaWAN Implementation
    # =====================
    
    async def start_lorawan_gateway(self, gateway_id: str = None):
        """Démarre la passerelle LoRaWAN"""
        try:
            if not gateway_id:
                gateway_id = self.protocol_configs[IoTProtocol.LORAWAN]["gateway_id"]
            
            self.lorawan_gateway = {
                "gateway_id": gateway_id,
                "frequency": self.protocol_configs[IoTProtocol.LORAWAN]["frequency"],
                "spreading_factor": self.protocol_configs[IoTProtocol.LORAWAN]["spreading_factor"],
                "running": True,
                "devices": {},
                "uplink_messages": [],
                "downlink_messages": []
            }
            
            logger.info(f"Passerelle LoRaWAN démarrée: {gateway_id}")
            
            # Démarrer l'écoute des messages
            asyncio.create_task(self._lorawan_message_loop())
            
            return {"success": True, "gateway_id": gateway_id}
            
        except Exception as e:
            logger.error(f"Erreur démarrage passerelle LoRaWAN: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _lorawan_message_loop(self):
        """Boucle de traitement des messages LoRaWAN"""
        try:
            while self.lorawan_gateway and self.lorawan_gateway["running"]:
                # Simuler la réception de messages
                await asyncio.sleep(5)
                
                # Traiter les messages en attente
                for message in self.lorawan_gateway.get("uplink_messages", []):
                    await self._process_lorawan_message(message)
                
                # Nettoyer les messages traités
                self.lorawan_gateway["uplink_messages"] = []
                
        except Exception as e:
            logger.error(f"Erreur boucle LoRaWAN: {str(e)}")
    
    async def _process_lorawan_message(self, message):
        """Traite un message LoRaWAN reçu"""
        try:
            device_id = message.get("device_id")
            payload = message.get("payload", {})
            
            # Identifier le type de message
            message_type = self._identify_message_type("lorawan", payload)
            
            # Traiter selon le type
            handler = self.message_handlers.get(message_type)
            if handler:
                await handler(payload, IoTProtocol.LORAWAN)
            
        except Exception as e:
            logger.error(f"Erreur traitement message LoRaWAN: {str(e)}")
    
    async def send_lorawan_downlink(self, device_id: str, payload: dict):
        """Envoie un message downlink LoRaWAN"""
        try:
            if not self.lorawan_gateway:
                return {"success": False, "error": "Passerelle LoRaWAN non démarrée"}
            
            downlink_message = {
                "message_id": str(uuid.uuid4()),
                "device_id": device_id,
                "payload": payload,
                "timestamp": datetime.utcnow().isoformat(),
                "frequency": self.lorawan_gateway["frequency"],
                "spreading_factor": self.lorawan_gateway["spreading_factor"]
            }
            
            self.lorawan_gateway["downlink_messages"].append(downlink_message)
            
            return {"success": True, "message_id": downlink_message["message_id"]}
            
        except Exception as e:
            logger.error(f"Erreur envoi downlink LoRaWAN: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # ========================
    # Message Handlers
    # ========================
    
    def _identify_message_type(self, topic_or_resource: str, payload: dict) -> MessageType:
        """Identifie le type de message selon le topic/ressource et payload"""
        if "heartbeat" in topic_or_resource.lower():
            return MessageType.HEARTBEAT
        elif "sensor" in topic_or_resource.lower() or "data" in topic_or_resource.lower():
            return MessageType.SENSOR_DATA
        elif "command" in topic_or_resource.lower():
            return MessageType.COMMAND
        elif "alert" in topic_or_resource.lower():
            return MessageType.ALERT
        elif "firmware" in topic_or_resource.lower():
            return MessageType.FIRMWARE_UPDATE
        elif "security" in topic_or_resource.lower():
            return MessageType.SECURITY_EVENT
        else:
            return MessageType.SENSOR_DATA  # Par défaut
    
    async def _handle_heartbeat(self, payload: dict, protocol: IoTProtocol):
        """Traite un message de heartbeat"""
        try:
            device_id = payload.get("device_id")
            timestamp = payload.get("timestamp", datetime.utcnow().isoformat())
            
            # Enregistrer le heartbeat
            heartbeat_data = {
                "device_id": device_id,
                "protocol": protocol.value,
                "timestamp": timestamp,
                "payload": payload,
                "created_at": datetime.utcnow()
            }
            
            await self.db.device_heartbeats.insert_one(heartbeat_data)
            
            # Mettre à jour le statut du device
            await self.db.devices.update_one(
                {"device_id": device_id},
                {"$set": {"last_heartbeat": timestamp, "status": "online"}}
            )
            
            logger.info(f"Heartbeat reçu de {device_id} via {protocol.value}")
            
        except Exception as e:
            logger.error(f"Erreur traitement heartbeat: {str(e)}")
    
    async def _handle_sensor_data(self, payload: dict, protocol: IoTProtocol):
        """Traite des données de capteur"""
        try:
            device_id = payload.get("device_id")
            sensor_data = payload.get("data", {})
            
            # Enregistrer les données
            sensor_record = {
                "device_id": device_id,
                "protocol": protocol.value,
                "sensor_data": sensor_data,
                "timestamp": payload.get("timestamp", datetime.utcnow().isoformat()),
                "created_at": datetime.utcnow()
            }
            
            await self.db.sensor_data.insert_one(sensor_record)
            
            logger.info(f"Données capteur reçues de {device_id} via {protocol.value}")
            
        except Exception as e:
            logger.error(f"Erreur traitement données capteur: {str(e)}")
    
    async def _handle_command(self, payload: dict, protocol: IoTProtocol):
        """Traite une commande"""
        try:
            device_id = payload.get("device_id")
            command = payload.get("command")
            
            # Enregistrer la commande
            command_record = {
                "device_id": device_id,
                "protocol": protocol.value,
                "command": command,
                "payload": payload,
                "status": "received",
                "timestamp": datetime.utcnow()
            }
            
            await self.db.device_commands.insert_one(command_record)
            
            logger.info(f"Commande reçue pour {device_id} via {protocol.value}: {command}")
            
        except Exception as e:
            logger.error(f"Erreur traitement commande: {str(e)}")
    
    async def _handle_alert(self, payload: dict, protocol: IoTProtocol):
        """Traite une alerte"""
        try:
            device_id = payload.get("device_id")
            alert_type = payload.get("alert_type")
            severity = payload.get("severity", "medium")
            
            # Enregistrer l'alerte
            alert_record = {
                "device_id": device_id,
                "protocol": protocol.value,
                "alert_type": alert_type,
                "severity": severity,
                "payload": payload,
                "status": "active",
                "timestamp": datetime.utcnow()
            }
            
            await self.db.device_alerts.insert_one(alert_record)
            
            logger.warning(f"Alerte {alert_type} reçue de {device_id} via {protocol.value}")
            
        except Exception as e:
            logger.error(f"Erreur traitement alerte: {str(e)}")
    
    async def _handle_firmware_update(self, payload: dict, protocol: IoTProtocol):
        """Traite une mise à jour firmware"""
        try:
            device_id = payload.get("device_id")
            firmware_version = payload.get("firmware_version")
            
            # Enregistrer la mise à jour
            update_record = {
                "device_id": device_id,
                "protocol": protocol.value,
                "firmware_version": firmware_version,
                "payload": payload,
                "status": "initiated",
                "timestamp": datetime.utcnow()
            }
            
            await self.db.firmware_updates.insert_one(update_record)
            
            logger.info(f"Mise à jour firmware {firmware_version} pour {device_id} via {protocol.value}")
            
        except Exception as e:
            logger.error(f"Erreur traitement mise à jour firmware: {str(e)}")
    
    async def _handle_security_event(self, payload: dict, protocol: IoTProtocol):
        """Traite un événement de sécurité"""
        try:
            device_id = payload.get("device_id")
            event_type = payload.get("event_type")
            
            # Enregistrer l'événement
            security_record = {
                "device_id": device_id,
                "protocol": protocol.value,
                "event_type": event_type,
                "payload": payload,
                "status": "detected",
                "timestamp": datetime.utcnow()
            }
            
            await self.db.security_events.insert_one(security_record)
            
            logger.warning(f"Événement sécurité {event_type} détecté pour {device_id} via {protocol.value}")
            
        except Exception as e:
            logger.error(f"Erreur traitement événement sécurité: {str(e)}")
    
    # =====================
    # Status and Statistics
    # =====================
    
    async def get_protocol_status(self) -> Dict[str, Any]:
        """Retourne le statut des protocoles"""
        try:
            status = {}
            
            for protocol in IoTProtocol:
                config = self.protocol_configs.get(protocol, {})
                
                if protocol == IoTProtocol.MQTT:
                    status[protocol.value] = {
                        "enabled": config.get("enabled", False),
                        "connected": self.mqtt_client is not None,
                        "broker": f"{config.get('broker_host')}:{config.get('broker_port')}"
                    }
                elif protocol == IoTProtocol.COAP:
                    status[protocol.value] = {
                        "enabled": config.get("enabled", False),
                        "running": self.coap_server is not None,
                        "server": f"coap://{config.get('host')}:{config.get('port')}"
                    }
                elif protocol == IoTProtocol.LORAWAN:
                    status[protocol.value] = {
                        "enabled": config.get("enabled", False),
                        "running": self.lorawan_gateway is not None,
                        "gateway_id": config.get("gateway_id")
                    }
                else:
                    status[protocol.value] = {
                        "enabled": config.get("enabled", False),
                        "status": "configured"
                    }
            
            return status
            
        except Exception as e:
            logger.error(f"Erreur récupération statut protocoles: {str(e)}")
            return {}
    
    async def get_message_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de messages"""
        try:
            # Compter les messages par type et protocole
            stats = {
                "total_messages": 0,
                "by_protocol": {},
                "by_type": {},
                "recent_activity": []
            }
            
            # Statistiques heartbeats
            heartbeat_count = await self.db.device_heartbeats.count_documents({})
            stats["by_type"]["heartbeat"] = heartbeat_count
            
            # Statistiques données capteur
            sensor_count = await self.db.sensor_data.count_documents({})
            stats["by_type"]["sensor_data"] = sensor_count
            
            # Statistiques commandes
            command_count = await self.db.device_commands.count_documents({})
            stats["by_type"]["commands"] = command_count
            
            # Statistiques alertes
            alert_count = await self.db.device_alerts.count_documents({})
            stats["by_type"]["alerts"] = alert_count
            
            stats["total_messages"] = heartbeat_count + sensor_count + command_count + alert_count
            
            return stats
            
        except Exception as e:
            logger.error(f"Erreur récupération statistiques: {str(e)}")
            return {}
    
    async def get_connected_devices(self) -> List[Dict[str, Any]]:
        """Retourne la liste des devices connectés"""
        try:
            # Récupérer les devices avec heartbeat récent (dernières 5 minutes)
            recent_time = datetime.utcnow() - timedelta(minutes=5)
            
            devices = await self.db.devices.find({
                "last_heartbeat": {"$gte": recent_time.isoformat()},
                "status": "online"
            }).to_list(None)
            
            return devices
            
        except Exception as e:
            logger.error(f"Erreur récupération devices connectés: {str(e)}")
            return []
    
    async def shutdown(self):
        """Arrête tous les protocoles"""
        try:
            # Arrêter MQTT
            if self.mqtt_client:
                await self.mqtt_client.disconnect()
                self.mqtt_client = None
            
            # Arrêter CoAP
            if self.coap_server:
                self.coap_server["running"] = False
                self.coap_server = None
            
            # Arrêter LoRaWAN
            if self.lorawan_gateway:
                self.lorawan_gateway["running"] = False
                self.lorawan_gateway = None
            
            logger.info("Tous les protocoles IoT arrêtés")
            
        except Exception as e:
            logger.error(f"Erreur arrêt protocoles: {str(e)}")
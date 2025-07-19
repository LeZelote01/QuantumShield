"""
Service de géolocalisation des dispositifs IoT
Gestion des coordonnées GPS, zones géographiques et tracking
"""

import asyncio
import logging
import json
import uuid
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

logger = logging.getLogger(__name__)

class LocationStatus(str, Enum):
    ACTIVE = "active"
    OFFLINE = "offline"
    MOVING = "moving"
    STATIONARY = "stationary"
    OUT_OF_BOUNDS = "out_of_bounds"

class GeofenceType(str, Enum):
    CIRCULAR = "circular"
    POLYGON = "polygon"
    RECTANGULAR = "rectangular"

class AlertType(str, Enum):
    GEOFENCE_ENTRY = "geofence_entry"
    GEOFENCE_EXIT = "geofence_exit"
    DEVICE_MOVED = "device_moved"
    LOCATION_LOST = "location_lost"
    SUSPICIOUS_MOVEMENT = "suspicious_movement"

class GeolocationService:
    """Service de géolocalisation pour dispositifs IoT"""
    
    def __init__(self, db):
        self.db = db
        self.active_trackers = {}
        self.geofences = {}
        self.location_history = {}
        self.movement_patterns = {}
        self.is_initialized = False
        self._initialize()
    
    def _initialize(self):
        """Initialise le service de géolocalisation"""
        try:
            # Configuration par défaut
            self.config = {
                "update_interval": 30,  # secondes
                "max_history_days": 30,
                "movement_threshold": 0.001,  # degrés (environ 100m)
                "geofence_precision": 0.0001,  # précision des géofences
                "offline_timeout": 300,  # secondes
                "max_speed_kmh": 200,  # vitesse maximale autorisée
                "anomaly_detection": True
            }
            
            self.is_initialized = True
            logger.info("Service de géolocalisation initialisé")
            
        except Exception as e:
            logger.error(f"Erreur initialisation géolocalisation: {str(e)}")
            self.is_initialized = False
    
    def is_ready(self) -> bool:
        """Vérifie si le service est prêt"""
        return self.is_initialized
    
    # ==============================
    # Gestion des positions
    # ==============================
    
    async def update_device_location(self, 
                                   device_id: str,
                                   latitude: float,
                                   longitude: float,
                                   altitude: Optional[float] = None,
                                   accuracy: Optional[float] = None,
                                   timestamp: Optional[datetime] = None) -> Dict[str, Any]:
        """Met à jour la position d'un dispositif"""
        try:
            if not self._validate_coordinates(latitude, longitude):
                return {
                    "success": False,
                    "error": "Coordonnées invalides"
                }
            
            current_time = timestamp or datetime.utcnow()
            
            # Récupérer la position précédente
            previous_location = await self.db.device_locations.find_one(
                {"device_id": device_id},
                sort=[("timestamp", -1)]
            )
            
            # Calculer la distance et vitesse si position précédente disponible
            distance_km = 0
            speed_kmh = 0
            if previous_location:
                distance_km = self._calculate_distance(
                    previous_location["latitude"], previous_location["longitude"],
                    latitude, longitude
                )
                
                time_diff = (current_time - previous_location["timestamp"]).total_seconds()
                if time_diff > 0:
                    speed_kmh = (distance_km / time_diff) * 3600
            
            # Vérifier les anomalies
            anomaly_detected = self._detect_movement_anomaly(
                device_id, latitude, longitude, speed_kmh, distance_km
            )
            
            # Créer l'entrée de localisation
            location_data = {
                "device_id": device_id,
                "latitude": latitude,
                "longitude": longitude,
                "altitude": altitude,
                "accuracy": accuracy,
                "timestamp": current_time,
                "distance_from_previous": distance_km,
                "speed_kmh": speed_kmh,
                "anomaly_detected": anomaly_detected,
                "address": await self._reverse_geocode(latitude, longitude),
                "geofence_status": await self._check_geofences(device_id, latitude, longitude)
            }
            
            # Enregistrer en base
            await self.db.device_locations.insert_one(location_data)
            
            # Mettre à jour la position actuelle du dispositif
            await self.db.devices.update_one(
                {"device_id": device_id},
                {"$set": {
                    "current_location": {
                        "latitude": latitude,
                        "longitude": longitude,
                        "altitude": altitude,
                        "last_update": current_time,
                        "accuracy": accuracy
                    },
                    "location_status": LocationStatus.ACTIVE.value
                }}
            )
            
            # Déclencher les alertes si nécessaire
            if anomaly_detected or location_data["geofence_status"].get("alerts"):
                await self._trigger_location_alerts(device_id, location_data)
            
            logger.info(f"Position mise à jour pour {device_id}: {latitude}, {longitude}")
            
            return {
                "success": True,
                "device_id": device_id,
                "latitude": latitude,
                "longitude": longitude,
                "distance_moved": distance_km,
                "speed": speed_kmh,
                "anomaly_detected": anomaly_detected,
                "timestamp": current_time
            }
            
        except Exception as e:
            logger.error(f"Erreur mise à jour position: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_device_location(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Récupère la position actuelle d'un dispositif"""
        try:
            device = await self.db.devices.find_one({"device_id": device_id})
            if not device or "current_location" not in device:
                return None
            
            location = device["current_location"]
            
            # Vérifier si la position est récente
            last_update = location.get("last_update")
            if last_update and (datetime.utcnow() - last_update).total_seconds() > self.config["offline_timeout"]:
                location["status"] = LocationStatus.OFFLINE.value
            else:
                location["status"] = LocationStatus.ACTIVE.value
            
            return {
                "device_id": device_id,
                "latitude": location.get("latitude"),
                "longitude": location.get("longitude"),
                "altitude": location.get("altitude"),
                "accuracy": location.get("accuracy"),
                "last_update": last_update,
                "status": location["status"]
            }
            
        except Exception as e:
            logger.error(f"Erreur récupération position: {str(e)}")
            return None
    
    async def get_location_history(self, 
                                 device_id: str,
                                 start_time: Optional[datetime] = None,
                                 end_time: Optional[datetime] = None,
                                 limit: int = 100) -> List[Dict[str, Any]]:
        """Récupère l'historique des positions d'un dispositif"""
        try:
            query = {"device_id": device_id}
            
            if start_time or end_time:
                time_query = {}
                if start_time:
                    time_query["$gte"] = start_time
                if end_time:
                    time_query["$lte"] = end_time
                query["timestamp"] = time_query
            
            locations = await self.db.device_locations.find(query).sort("timestamp", -1).limit(limit).to_list(None)
            
            # Nettoyer les données pour la réponse
            result = []
            for location in locations:
                location.pop("_id", None)
                result.append(location)
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur récupération historique: {str(e)}")
            return []
    
    # ==============================
    # Géofencing
    # ==============================
    
    async def create_geofence(self,
                            name: str,
                            geofence_type: GeofenceType,
                            coordinates: List[Dict[str, float]],
                            radius: Optional[float] = None,
                            device_ids: Optional[List[str]] = None,
                            description: str = None) -> Dict[str, Any]:
        """Crée une géofence"""
        try:
            geofence_id = str(uuid.uuid4())
            
            # Valider les coordonnées
            if not self._validate_geofence_coordinates(geofence_type, coordinates, radius):
                return {
                    "success": False,
                    "error": "Coordonnées de géofence invalides"
                }
            
            geofence_data = {
                "geofence_id": geofence_id,
                "name": name,
                "type": geofence_type.value,
                "coordinates": coordinates,
                "radius": radius,
                "device_ids": device_ids or [],
                "description": description,
                "created_at": datetime.utcnow(),
                "active": True,
                "entry_count": 0,
                "exit_count": 0
            }
            
            # Enregistrer en base
            await self.db.geofences.insert_one(geofence_data)
            
            # Ajouter au cache
            self.geofences[geofence_id] = geofence_data
            
            logger.info(f"Géofence créée: {name} ({geofence_id})")
            
            return {
                "success": True,
                "geofence_id": geofence_id,
                "name": name,
                "type": geofence_type.value,
                "coordinates": coordinates
            }
            
        except Exception as e:
            logger.error(f"Erreur création géofence: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _check_geofences(self, device_id: str, latitude: float, longitude: float) -> Dict[str, Any]:
        """Vérifie si un dispositif est dans une géofence"""
        try:
            # Récupérer les géofences actives pour ce dispositif
            geofences = await self.db.geofences.find({
                "active": True,
                "$or": [
                    {"device_ids": device_id},
                    {"device_ids": {"$size": 0}}  # Géofences globales
                ]
            }).to_list(None)
            
            status = {
                "inside_geofences": [],
                "outside_geofences": [],
                "alerts": []
            }
            
            for geofence in geofences:
                is_inside = self._point_in_geofence(
                    latitude, longitude,
                    geofence["type"],
                    geofence["coordinates"],
                    geofence.get("radius")
                )
                
                if is_inside:
                    status["inside_geofences"].append({
                        "geofence_id": geofence["geofence_id"],
                        "name": geofence["name"]
                    })
                else:
                    status["outside_geofences"].append({
                        "geofence_id": geofence["geofence_id"],
                        "name": geofence["name"]
                    })
            
            return status
            
        except Exception as e:
            logger.error(f"Erreur vérification géofences: {str(e)}")
            return {"inside_geofences": [], "outside_geofences": [], "alerts": []}
    
    def _point_in_geofence(self,
                          latitude: float,
                          longitude: float,
                          geofence_type: str,
                          coordinates: List[Dict[str, float]],
                          radius: Optional[float]) -> bool:
        """Vérifie si un point est dans une géofence"""
        try:
            if geofence_type == GeofenceType.CIRCULAR.value:
                if not coordinates or not radius:
                    return False
                
                center = coordinates[0]
                distance = self._calculate_distance(
                    latitude, longitude,
                    center["latitude"], center["longitude"]
                )
                return distance <= (radius / 1000)  # radius en mètres, distance en km
            
            elif geofence_type == GeofenceType.RECTANGULAR.value:
                if len(coordinates) < 2:
                    return False
                
                min_lat = min(coord["latitude"] for coord in coordinates)
                max_lat = max(coord["latitude"] for coord in coordinates)
                min_lon = min(coord["longitude"] for coord in coordinates)
                max_lon = max(coord["longitude"] for coord in coordinates)
                
                return (min_lat <= latitude <= max_lat and 
                       min_lon <= longitude <= max_lon)
            
            elif geofence_type == GeofenceType.POLYGON.value:
                if len(coordinates) < 3:
                    return False
                
                # Algorithme ray casting
                x, y = longitude, latitude
                n = len(coordinates)
                inside = False
                
                p1x, p1y = coordinates[0]["longitude"], coordinates[0]["latitude"]
                for i in range(1, n + 1):
                    p2x, p2y = coordinates[i % n]["longitude"], coordinates[i % n]["latitude"]
                    if y > min(p1y, p2y):
                        if y <= max(p1y, p2y):
                            if x <= max(p1x, p2x):
                                if p1y != p2y:
                                    xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                                if p1x == p2x or x <= xinters:
                                    inside = not inside
                    p1x, p1y = p2x, p2y
                
                return inside
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur vérification point dans géofence: {str(e)}")
            return False
    
    # ==============================
    # Utilitaires de calcul
    # ==============================
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcule la distance entre deux points GPS (en km)"""
        # Formule de Haversine
        R = 6371  # Rayon de la Terre en km
        
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def _validate_coordinates(self, latitude: float, longitude: float) -> bool:
        """Valide les coordonnées GPS"""
        return (-90 <= latitude <= 90) and (-180 <= longitude <= 180)
    
    def _validate_geofence_coordinates(self,
                                    geofence_type: GeofenceType,
                                    coordinates: List[Dict[str, float]],
                                    radius: Optional[float]) -> bool:
        """Valide les coordonnées d'une géofence"""
        if not coordinates:
            return False
        
        # Vérifier que toutes les coordonnées sont valides
        for coord in coordinates:
            if not self._validate_coordinates(coord.get("latitude", 0), coord.get("longitude", 0)):
                return False
        
        # Vérifications spécifiques au type
        if geofence_type == GeofenceType.CIRCULAR:
            return len(coordinates) == 1 and radius is not None and radius > 0
        elif geofence_type == GeofenceType.RECTANGULAR:
            return len(coordinates) >= 2
        elif geofence_type == GeofenceType.POLYGON:
            return len(coordinates) >= 3
        
        return True
    
    def _detect_movement_anomaly(self,
                               device_id: str,
                               latitude: float,
                               longitude: float,
                               speed_kmh: float,
                               distance_km: float) -> bool:
        """Détecte les anomalies de mouvement"""
        try:
            # Vitesse trop élevée
            if speed_kmh > self.config["max_speed_kmh"]:
                return True
            
            # Déplacement trop grand en une fois
            if distance_km > 10:  # Plus de 10km d'un coup
                return True
            
            # Autres vérifications d'anomalies peuvent être ajoutées ici
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur détection anomalie: {str(e)}")
            return False
    
    async def _reverse_geocode(self, latitude: float, longitude: float) -> str:
        """Conversion inverse des coordonnées en adresse (simulation)"""
        try:
            # Dans un vrai système, utiliser une API comme Google Maps ou OpenStreetMap
            # Pour la démo, on retourne une adresse simulée
            return f"Lat: {latitude:.4f}, Lon: {longitude:.4f}"
            
        except Exception as e:
            logger.error(f"Erreur géocodage inverse: {str(e)}")
            return f"{latitude:.4f}, {longitude:.4f}"
    
    async def _trigger_location_alerts(self, device_id: str, location_data: Dict[str, Any]):
        """Déclenche les alertes de localisation"""
        try:
            alerts = []
            
            if location_data["anomaly_detected"]:
                alerts.append({
                    "type": AlertType.SUSPICIOUS_MOVEMENT.value,
                    "message": f"Mouvement suspect détecté pour {device_id}",
                    "speed": location_data["speed_kmh"],
                    "distance": location_data["distance_from_previous"]
                })
            
            if location_data["geofence_status"].get("alerts"):
                alerts.extend(location_data["geofence_status"]["alerts"])
            
            # Enregistrer les alertes
            for alert in alerts:
                alert_data = {
                    "alert_id": str(uuid.uuid4()),
                    "device_id": device_id,
                    "alert_type": alert["type"],
                    "message": alert["message"],
                    "location": {
                        "latitude": location_data["latitude"],
                        "longitude": location_data["longitude"]
                    },
                    "timestamp": datetime.utcnow(),
                    "resolved": False
                }
                
                await self.db.location_alerts.insert_one(alert_data)
                
        except Exception as e:
            logger.error(f"Erreur déclenchement alertes: {str(e)}")
    
    # ==============================
    # Analytics et statistiques
    # ==============================
    
    async def get_movement_analytics(self, device_id: str, days: int = 7) -> Dict[str, Any]:
        """Analyse les patterns de mouvement d'un dispositif"""
        try:
            start_time = datetime.utcnow() - timedelta(days=days)
            
            # Récupérer l'historique
            locations = await self.db.device_locations.find({
                "device_id": device_id,
                "timestamp": {"$gte": start_time}
            }).sort("timestamp", 1).to_list(None)
            
            if not locations:
                return {"device_id": device_id, "message": "Aucune donnée de localisation"}
            
            # Calculer les statistiques
            total_distance = sum(loc.get("distance_from_previous", 0) for loc in locations)
            max_speed = max(loc.get("speed_kmh", 0) for loc in locations)
            avg_speed = sum(loc.get("speed_kmh", 0) for loc in locations) / len(locations)
            
            # Zones les plus visitées
            location_clusters = self._analyze_location_clusters(locations)
            
            # Patterns temporels
            temporal_patterns = self._analyze_temporal_patterns(locations)
            
            return {
                "device_id": device_id,
                "period_days": days,
                "total_locations": len(locations),
                "total_distance_km": round(total_distance, 2),
                "max_speed_kmh": round(max_speed, 2),
                "avg_speed_kmh": round(avg_speed, 2),
                "location_clusters": location_clusters,
                "temporal_patterns": temporal_patterns,
                "anomalies_detected": sum(1 for loc in locations if loc.get("anomaly_detected", False))
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse mouvement: {str(e)}")
            return {"device_id": device_id, "error": str(e)}
    
    def _analyze_location_clusters(self, locations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyse les clusters de localisation"""
        try:
            # Algorithme de clustering simple basé sur la distance
            clusters = []
            cluster_threshold = 0.5  # 500m
            
            for location in locations:
                lat, lon = location["latitude"], location["longitude"]
                
                # Chercher un cluster existant
                found_cluster = False
                for cluster in clusters:
                    center_lat = cluster["center_latitude"]
                    center_lon = cluster["center_longitude"]
                    
                    if self._calculate_distance(lat, lon, center_lat, center_lon) <= cluster_threshold:
                        cluster["count"] += 1
                        # Recalculer le centre
                        cluster["center_latitude"] = (cluster["center_latitude"] * (cluster["count"] - 1) + lat) / cluster["count"]
                        cluster["center_longitude"] = (cluster["center_longitude"] * (cluster["count"] - 1) + lon) / cluster["count"]
                        found_cluster = True
                        break
                
                if not found_cluster:
                    clusters.append({
                        "center_latitude": lat,
                        "center_longitude": lon,
                        "count": 1
                    })
            
            # Trier par fréquence
            clusters.sort(key=lambda x: x["count"], reverse=True)
            
            return clusters[:10]  # Top 10 clusters
            
        except Exception as e:
            logger.error(f"Erreur analyse clusters: {str(e)}")
            return []
    
    def _analyze_temporal_patterns(self, locations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse les patterns temporels"""
        try:
            hourly_activity = [0] * 24
            daily_activity = [0] * 7
            
            for location in locations:
                timestamp = location["timestamp"]
                hour = timestamp.hour
                day = timestamp.weekday()
                
                hourly_activity[hour] += 1
                daily_activity[day] += 1
            
            return {
                "hourly_activity": hourly_activity,
                "daily_activity": daily_activity,
                "most_active_hour": hourly_activity.index(max(hourly_activity)),
                "most_active_day": daily_activity.index(max(daily_activity))
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse patterns temporels: {str(e)}")
            return {}
    
    async def get_all_devices_locations(self) -> List[Dict[str, Any]]:
        """Récupère les positions de tous les dispositifs"""
        try:
            devices = await self.db.devices.find({
                "current_location": {"$exists": True}
            }).to_list(None)
            
            locations = []
            for device in devices:
                location = device.get("current_location", {})
                if location:
                    locations.append({
                        "device_id": device["device_id"],
                        "device_name": device.get("device_name", "Unknown"),
                        "latitude": location.get("latitude"),
                        "longitude": location.get("longitude"),
                        "altitude": location.get("altitude"),
                        "last_update": location.get("last_update"),
                        "accuracy": location.get("accuracy")
                    })
            
            return locations
            
        except Exception as e:
            logger.error(f"Erreur récupération toutes les positions: {str(e)}")
            return []
    
    async def shutdown(self):
        """Arrête le service de géolocalisation"""
        try:
            # Arrêter les trackers actifs
            self.active_trackers.clear()
            self.geofences.clear()
            
            logger.info("Service de géolocalisation arrêté")
            
        except Exception as e:
            logger.error(f"Erreur arrêt service géolocalisation: {str(e)}")
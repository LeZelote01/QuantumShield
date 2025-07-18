"""
Routes pour la géolocalisation des dispositifs IoT
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

# Import du service (sera injecté par le serveur principal)
geolocation_service = None

router = APIRouter()
logger = logging.getLogger(__name__)

# ==============================
# Modèles Pydantic
# ==============================

class LocationUpdate(BaseModel):
    device_id: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    altitude: Optional[float] = None
    accuracy: Optional[float] = None
    timestamp: Optional[datetime] = None

class GeofenceCreate(BaseModel):
    name: str
    type: str = Field(..., pattern="^(circular|polygon|rectangular)$")
    coordinates: List[Dict[str, float]]
    radius: Optional[float] = None
    device_ids: Optional[List[str]] = []
    description: Optional[str] = None

class LocationHistoryQuery(BaseModel):
    device_id: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: Optional[int] = Field(default=100, le=1000)

# ==============================
# Endpoints de géolocalisation
# ==============================

@router.post("/update-location")
async def update_device_location(location_data: LocationUpdate):
    """Met à jour la position d'un dispositif"""
    try:
        if not geolocation_service:
            raise HTTPException(status_code=503, detail="Service de géolocalisation non disponible")
        
        result = await geolocation_service.update_device_location(
            device_id=location_data.device_id,
            latitude=location_data.latitude,
            longitude=location_data.longitude,
            altitude=location_data.altitude,
            accuracy=location_data.accuracy,
            timestamp=location_data.timestamp
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Erreur mise à jour position: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/device/{device_id}/location")
async def get_device_location(device_id: str):
    """Récupère la position actuelle d'un dispositif"""
    try:
        if not geolocation_service:
            raise HTTPException(status_code=503, detail="Service de géolocalisation non disponible")
        
        location = await geolocation_service.get_device_location(device_id)
        
        if not location:
            raise HTTPException(status_code=404, detail="Position non trouvée")
        
        return location
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération position: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/device/{device_id}/history")
async def get_location_history(
    device_id: str,
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    limit: int = Query(100, le=1000)
):
    """Récupère l'historique des positions d'un dispositif"""
    try:
        if not geolocation_service:
            raise HTTPException(status_code=503, detail="Service de géolocalisation non disponible")
        
        history = await geolocation_service.get_location_history(
            device_id=device_id,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
        
        return {
            "device_id": device_id,
            "locations": history,
            "count": len(history)
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération historique: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/devices/locations")
async def get_all_devices_locations():
    """Récupère les positions de tous les dispositifs"""
    try:
        if not geolocation_service:
            raise HTTPException(status_code=503, detail="Service de géolocalisation non disponible")
        
        locations = await geolocation_service.get_all_devices_locations()
        
        return {
            "locations": locations,
            "count": len(locations)
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération toutes les positions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================
# Endpoints de géofencing
# ==============================

@router.post("/geofences")
async def create_geofence(geofence_data: GeofenceCreate):
    """Crée une nouvelle géofence"""
    try:
        if not geolocation_service:
            raise HTTPException(status_code=503, detail="Service de géolocalisation non disponible")
        
        from services.geolocation_service import GeofenceType
        
        result = await geolocation_service.create_geofence(
            name=geofence_data.name,
            geofence_type=GeofenceType(geofence_data.type),
            coordinates=geofence_data.coordinates,
            radius=geofence_data.radius,
            device_ids=geofence_data.device_ids,
            description=geofence_data.description
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur création géofence: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/geofences")
async def list_geofences():
    """Liste toutes les géofences"""
    try:
        if not geolocation_service:
            raise HTTPException(status_code=503, detail="Service de géolocalisation non disponible")
        
        geofences = await geolocation_service.db.geofences.find({"active": True}).to_list(None)
        
        # Nettoyer les données
        result = []
        for geofence in geofences:
            geofence.pop("_id", None)
            result.append(geofence)
        
        return {
            "geofences": result,
            "count": len(result)
        }
        
    except Exception as e:
        logger.error(f"Erreur liste géofences: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/geofences/{geofence_id}")
async def get_geofence(geofence_id: str):
    """Récupère une géofence spécifique"""
    try:
        if not geolocation_service:
            raise HTTPException(status_code=503, detail="Service de géolocalisation non disponible")
        
        geofence = await geolocation_service.db.geofences.find_one({"geofence_id": geofence_id})
        
        if not geofence:
            raise HTTPException(status_code=404, detail="Géofence non trouvée")
        
        geofence.pop("_id", None)
        return geofence
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération géofence: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/geofences/{geofence_id}")
async def delete_geofence(geofence_id: str):
    """Supprime une géofence"""
    try:
        if not geolocation_service:
            raise HTTPException(status_code=503, detail="Service de géolocalisation non disponible")
        
        result = await geolocation_service.db.geofences.update_one(
            {"geofence_id": geofence_id},
            {"$set": {"active": False, "deleted_at": datetime.utcnow()}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Géofence non trouvée")
        
        return {"message": "Géofence supprimée avec succès"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur suppression géofence: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================
# Endpoints d'analytics
# ==============================

@router.get("/device/{device_id}/analytics")
async def get_movement_analytics(
    device_id: str,
    days: int = Query(7, ge=1, le=30)
):
    """Récupère l'analyse des mouvements d'un dispositif"""
    try:
        if not geolocation_service:
            raise HTTPException(status_code=503, detail="Service de géolocalisation non disponible")
        
        analytics = await geolocation_service.get_movement_analytics(device_id, days)
        
        return analytics
        
    except Exception as e:
        logger.error(f"Erreur analyse mouvement: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts")
async def get_location_alerts(
    device_id: Optional[str] = Query(None),
    limit: int = Query(50, le=200)
):
    """Récupère les alertes de localisation"""
    try:
        if not geolocation_service:
            raise HTTPException(status_code=503, detail="Service de géolocalisation non disponible")
        
        query = {}
        if device_id:
            query["device_id"] = device_id
        
        alerts = await geolocation_service.db.location_alerts.find(query).sort("timestamp", -1).limit(limit).to_list(None)
        
        # Nettoyer les données
        result = []
        for alert in alerts:
            alert.pop("_id", None)
            result.append(alert)
        
        return {
            "alerts": result,
            "count": len(result)
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération alertes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Marque une alerte comme résolue"""
    try:
        if not geolocation_service:
            raise HTTPException(status_code=503, detail="Service de géolocalisation non disponible")
        
        result = await geolocation_service.db.location_alerts.update_one(
            {"alert_id": alert_id},
            {"$set": {"resolved": True, "resolved_at": datetime.utcnow()}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Alerte non trouvée")
        
        return {"message": "Alerte marquée comme résolue"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur résolution alerte: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================
# Endpoints de configuration
# ==============================

@router.get("/config")
async def get_geolocation_config():
    """Récupère la configuration du service de géolocalisation"""
    try:
        if not geolocation_service:
            raise HTTPException(status_code=503, detail="Service de géolocalisation non disponible")
        
        return {
            "config": geolocation_service.config,
            "status": "active" if geolocation_service.is_ready() else "inactive"
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_geolocation_stats():
    """Récupère les statistiques du service de géolocalisation"""
    try:
        if not geolocation_service:
            raise HTTPException(status_code=503, detail="Service de géolocalisation non disponible")
        
        # Compter les dispositifs avec localisation
        devices_with_location = await geolocation_service.db.devices.count_documents({
            "current_location": {"$exists": True}
        })
        
        # Compter les géofences actives
        active_geofences = await geolocation_service.db.geofences.count_documents({
            "active": True
        })
        
        # Compter les alertes non résolues
        unresolved_alerts = await geolocation_service.db.location_alerts.count_documents({
            "resolved": False
        })
        
        # Compter les positions dans la dernière heure
        recent_time = datetime.utcnow() - timedelta(hours=1)
        recent_locations = await geolocation_service.db.device_locations.count_documents({
            "timestamp": {"$gte": recent_time}
        })
        
        return {
            "devices_with_location": devices_with_location,
            "active_geofences": active_geofences,
            "unresolved_alerts": unresolved_alerts,
            "recent_locations": recent_locations,
            "service_status": "active" if geolocation_service.is_ready() else "inactive"
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération statistiques: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
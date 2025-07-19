"""
Routes de gestion des devices IoT
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from models.quantum_models import Device, DeviceCreate, DeviceUpdate, DeviceHeartbeat, DeviceStatus, AnomalyDetection
from routes.auth_routes import get_current_user
from services.device_service import DeviceService

router = APIRouter()

# Modèles de requête
class DeviceMetricsRequest(BaseModel):
    device_id: str
    period_hours: int = 24

class FirmwareUpdateRequest(BaseModel):
    device_id: str
    firmware_hash: str

# Routes
@router.post("/register", response_model=Device)
async def register_device(device_data: DeviceCreate, current_user = Depends(get_current_user)):
    """Enregistre un nouveau device IoT"""
    from server import device_service
    
    try:
        device = await device_service.register_device(device_data, current_user.id)
        
        # Récompenser l'utilisateur pour l'enregistrement
        from server import token_service
        await token_service.reward_user(
            user_id=current_user.id,
            reward_type="device_registration",
            device_id=device.id
        )
        
        return device
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de l'enregistrement: {str(e)}"
        )

@router.get("/", response_model=List[Device])
async def get_user_devices(current_user = Depends(get_current_user)):
    """Récupère tous les devices de l'utilisateur"""
    from server import device_service
    
    try:
        devices = await device_service.get_user_devices(current_user.id)
        return devices
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération: {str(e)}"
        )

@router.get("/{device_id}", response_model=Device)
async def get_device(device_id: str, current_user = Depends(get_current_user)):
    """Récupère un device par son ID"""
    from server import device_service
    
    try:
        device = await device_service.get_device(device_id)
        
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device {device_id} non trouvé"
            )
        
        # Vérifier que l'utilisateur est propriétaire du device
        if device.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé à ce device"
            )
        
        return device
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération: {str(e)}"
        )

@router.put("/{device_id}", response_model=Device)
async def update_device(device_id: str, update_data: DeviceUpdate, current_user = Depends(get_current_user)):
    """Met à jour un device"""
    from server import device_service
    
    try:
        # Vérifier que l'utilisateur est propriétaire
        device = await device_service.get_device(device_id)
        if not device or device.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé à ce device"
            )
        
        updated_device = await device_service.update_device(device_id, update_data)
        
        if not updated_device:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Impossible de mettre à jour le device"
            )
        
        return updated_device
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la mise à jour: {str(e)}"
        )

@router.post("/heartbeat")
async def process_heartbeat(heartbeat: DeviceHeartbeat, current_user = Depends(get_current_user)):
    """Traite un heartbeat d'un device"""
    from server import device_service
    
    try:
        # Vérifier que l'utilisateur est propriétaire
        device = await device_service.get_device(heartbeat.device_id)
        if not device or device.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé à ce device"
            )
        
        response = await device_service.process_heartbeat(heartbeat)
        
        # Récompenser pour la participation au réseau
        if heartbeat.anomaly_detected:
            from server import token_service
            await token_service.reward_user(
                user_id=current_user.id,
                reward_type="anomaly_detection",
                device_id=heartbeat.device_id
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors du traitement: {str(e)}"
        )

@router.get("/{device_id}/metrics")
async def get_device_metrics(device_id: str, current_user = Depends(get_current_user)):
    """Récupère les métriques d'un device"""
    from server import device_service
    
    try:
        # Vérifier que l'utilisateur est propriétaire
        device = await device_service.get_device(device_id)
        if not device or device.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé à ce device"
            )
        
        metrics = await device_service.get_device_metrics(device_id)
        return metrics
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des métriques: {str(e)}"
        )

@router.get("/{device_id}/anomalies")
async def get_device_anomalies(device_id: str, limit: int = 50, current_user = Depends(get_current_user)):
    """Récupère les anomalies d'un device"""
    from server import device_service
    
    try:
        # Vérifier que l'utilisateur est propriétaire
        device = await device_service.get_device(device_id)
        if not device or device.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé à ce device"
            )
        
        cursor = device_service.anomalies.find(
            {"device_id": device_id}
        ).sort("detected_at", -1).limit(limit)
        
        anomalies_data = await cursor.to_list(length=limit)
        
        anomalies = []
        for anomaly_data in anomalies_data:
            anomalies.append(AnomalyDetection(**anomaly_data))
        
        return anomalies
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des anomalies: {str(e)}"
        )

@router.post("/{device_id}/firmware-update")
async def update_firmware(device_id: str, firmware_data: FirmwareUpdateRequest, current_user = Depends(get_current_user)):
    """Met à jour le firmware d'un device"""
    from server import device_service
    
    try:
        # Vérifier que l'utilisateur est propriétaire
        device = await device_service.get_device(device_id)
        if not device or device.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé à ce device"
            )
        
        success = await device_service.update_firmware(device_id, firmware_data.firmware_hash)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Impossible de mettre à jour le firmware"
            )
        
        # Enregistrer sur la blockchain
        from server import blockchain_service
        tx_hash = await blockchain_service.register_firmware_update(
            device_id, 
            firmware_data.firmware_hash, 
            "latest"
        )
        
        # Récompenser l'utilisateur
        from server import token_service
        await token_service.reward_user(
            user_id=current_user.id,
            reward_type="firmware_validation",
            device_id=device_id
        )
        
        return {
            "message": "Firmware mis à jour avec succès",
            "device_id": device_id,
            "firmware_hash": firmware_data.firmware_hash,
            "blockchain_tx": tx_hash
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la mise à jour: {str(e)}"
        )

@router.get("/offline/list")
async def get_offline_devices(current_user = Depends(get_current_user)):
    """Récupère les devices hors ligne de l'utilisateur"""
    from server import device_service
    
    try:
        # Récupérer tous les devices hors ligne
        offline_devices = await device_service.get_offline_devices()
        
        # Filtrer par propriétaire
        user_offline_devices = [
            device for device in offline_devices 
            if device.owner_id == current_user.id
        ]
        
        return user_offline_devices
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération: {str(e)}"
        )

@router.get("/stats/overview")
async def get_devices_overview(current_user = Depends(get_current_user)):
    """Récupère un aperçu des devices de l'utilisateur"""
    from server import device_service
    
    try:
        # Récupérer tous les devices de l'utilisateur
        user_devices = await device_service.get_user_devices(current_user.id)
        
        # Calculer les statistiques
        total_devices = len(user_devices)
        active_devices = len([d for d in user_devices if d.status == DeviceStatus.ACTIVE])
        inactive_devices = len([d for d in user_devices if d.status == DeviceStatus.INACTIVE])
        compromised_devices = len([d for d in user_devices if d.status == DeviceStatus.COMPROMISED])
        
        # Grouper par type
        device_types = {}
        for device in user_devices:
            device_type = device.device_type
            if device_type not in device_types:
                device_types[device_type] = 0
            device_types[device_type] += 1
        
        # Compter les anomalies récentes
        from datetime import datetime, timedelta
        recent_anomalies = await device_service.anomalies.count_documents({
            "device_id": {"$in": [d.device_id for d in user_devices]},
            "detected_at": {"$gte": datetime.utcnow() - timedelta(hours=24)}
        })
        
        return {
            "total_devices": total_devices,
            "active_devices": active_devices,
            "inactive_devices": inactive_devices,
            "compromised_devices": compromised_devices,
            "device_types": device_types,
            "recent_anomalies": recent_anomalies,
            "devices": user_devices
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération de l'aperçu: {str(e)}"
        )

@router.get("/types/available")
async def get_available_device_types():
    """Récupère les types de devices disponibles"""
    return {
        "device_types": [
            {
                "name": "Smart Sensor",
                "description": "Capteur intelligent avec connectivité IoT",
                "capabilities": ["temperature", "humidity", "motion"]
            },
            {
                "name": "Smart Lock",
                "description": "Serrure intelligente avec authentification",
                "capabilities": ["biometric", "keypad", "remote_control"]
            },
            {
                "name": "Smart Camera",
                "description": "Caméra de surveillance intelligente",
                "capabilities": ["video_streaming", "motion_detection", "night_vision"]
            },
            {
                "name": "Smart Thermostat",
                "description": "Thermostat connecté",
                "capabilities": ["temperature_control", "scheduling", "remote_access"]
            },
            {
                "name": "Smart Gateway",
                "description": "Passerelle IoT pour réseau local",
                "capabilities": ["device_management", "data_aggregation", "edge_computing"]
            },
            {
                "name": "Medical Device",
                "description": "Dispositif médical connecté",
                "capabilities": ["vital_signs", "monitoring", "emergency_alerts"]
            },
            {
                "name": "Industrial Controller",
                "description": "Contrôleur industriel IoT",
                "capabilities": ["process_control", "monitoring", "automation"]
            },
            {
                "name": "Vehicle Tracker",
                "description": "Dispositif de suivi véhiculaire",
                "capabilities": ["gps_tracking", "diagnostics", "remote_monitoring"]
            }
        ]
    }
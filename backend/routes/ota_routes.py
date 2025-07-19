"""
Routes pour le service de mises à jour OTA
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, File, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

# Import du service
from services.ota_update_service import OTAUpdateService, UpdateStatus, UpdateType, UpdatePriority, DeviceCapability

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

# Instance du service OTA (sera injectée par le serveur principal)
ota_service = None

# Modèles Pydantic
class FirmwareRegistrationModel(BaseModel):
    firmware_id: str
    version: str
    device_model: str
    description: Optional[str] = None
    update_type: UpdateType = UpdateType.FIRMWARE
    priority: UpdatePriority = UpdatePriority.MEDIUM
    required_capabilities: Optional[List[DeviceCapability]] = None

class UpdateScheduleModel(BaseModel):
    device_id: str
    firmware_id: str
    scheduled_time: Optional[datetime] = None
    force_update: bool = False

class BulkUpdateModel(BaseModel):
    device_ids: List[str]
    firmware_id: str
    scheduled_time: Optional[datetime] = None
    force_update: bool = False

# Dépendance pour obtenir le service
def get_ota_service():
    global ota_service
    if ota_service is None:
        from server import ota_update_service
        return ota_update_service
    return ota_service

@router.get("/health")
async def health_check():
    """Vérifie l'état de santé du service OTA"""
    try:
        service = get_ota_service()
        if not service:
            return {"status": "error", "message": "Service non disponible"}
        
        return {
            "status": "healthy" if service.is_ready() else "unhealthy",
            "service": "OTA Update Service",
            "timestamp": datetime.utcnow().isoformat(),
            "active_updates": len(service.active_updates),
            "queued_updates": len(service.update_queue)
        }
    except Exception as e:
        logger.error(f"Erreur health check OTA: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_ota_statistics():
    """Retourne les statistiques OTA"""
    try:
        service = get_ota_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        stats = await service.get_ota_statistics()
        return {
            "success": True,
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Erreur récupération statistiques OTA: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================
# Gestion des firmwares
# ==============================

@router.post("/firmware/register")
async def register_firmware(
    firmware_info: FirmwareRegistrationModel,
    firmware_file: UploadFile = File(...)
):
    """Enregistre un nouveau firmware"""
    try:
        service = get_ota_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        # Lire le fichier firmware
        firmware_data = await firmware_file.read()
        
        if len(firmware_data) == 0:
            raise HTTPException(status_code=400, detail="Fichier firmware vide")
        
        # Enregistrer le firmware
        result = await service.register_firmware(
            firmware_id=firmware_info.firmware_id,
            version=firmware_info.version,
            device_model=firmware_info.device_model,
            firmware_data=firmware_data,
            description=firmware_info.description,
            update_type=firmware_info.update_type,
            priority=firmware_info.priority,
            required_capabilities=firmware_info.required_capabilities
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Erreur enregistrement firmware: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/firmware/list")
async def list_firmwares(device_model: Optional[str] = None):
    """Liste les firmwares disponibles"""
    try:
        service = get_ota_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        firmwares = await service.list_available_firmwares(device_model)
        return {
            "success": True,
            "firmwares": firmwares,
            "count": len(firmwares)
        }
        
    except Exception as e:
        logger.error(f"Erreur liste firmwares: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/firmware/{firmware_id}")
async def get_firmware_info(firmware_id: str):
    """Récupère les informations d'un firmware"""
    try:
        service = get_ota_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        firmware = await service.get_firmware_info(firmware_id)
        if not firmware:
            raise HTTPException(status_code=404, detail="Firmware non trouvé")
        
        return {
            "success": True,
            "firmware": firmware
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération firmware: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/firmware/{firmware_id}")
async def delete_firmware(firmware_id: str):
    """Supprime un firmware"""
    try:
        service = get_ota_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        # Vérifier qu'aucune mise à jour en cours n'utilise ce firmware
        active_updates = [
            update for update in service.active_updates.values()
            if update.get("firmware_id") == firmware_id
        ]
        
        if active_updates:
            raise HTTPException(
                status_code=409, 
                detail="Firmware utilisé par des mises à jour en cours"
            )
        
        # Supprimer de la base
        await service.db.firmware_repository.delete_one({"firmware_id": firmware_id})
        
        # Supprimer du cache
        if firmware_id in service.firmware_repository:
            del service.firmware_repository[firmware_id]
        
        return {
            "success": True,
            "message": f"Firmware {firmware_id} supprimé"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur suppression firmware: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================
# Gestion des mises à jour
# ==============================

@router.post("/update/schedule")
async def schedule_update(update_info: UpdateScheduleModel):
    """Planifie une mise à jour"""
    try:
        service = get_ota_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        result = await service.schedule_update(
            device_id=update_info.device_id,
            firmware_id=update_info.firmware_id,
            scheduled_time=update_info.scheduled_time,
            force_update=update_info.force_update
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Erreur planification mise à jour: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update/bulk-schedule")
async def schedule_bulk_update(bulk_update: BulkUpdateModel):
    """Planifie des mises à jour en masse"""
    try:
        service = get_ota_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        results = []
        for device_id in bulk_update.device_ids:
            result = await service.schedule_update(
                device_id=device_id,
                firmware_id=bulk_update.firmware_id,
                scheduled_time=bulk_update.scheduled_time,
                force_update=bulk_update.force_update
            )
            results.append({
                "device_id": device_id,
                "result": result
            })
        
        successful = sum(1 for r in results if r["result"].get("success", False))
        
        return {
            "success": True,
            "total_devices": len(bulk_update.device_ids),
            "successful_schedules": successful,
            "failed_schedules": len(bulk_update.device_ids) - successful,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Erreur planification mises à jour en masse: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update/{update_id}/start")
async def start_update(update_id: str):
    """Démarre une mise à jour"""
    try:
        service = get_ota_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        result = await service.start_update(update_id)
        return result
        
    except Exception as e:
        logger.error(f"Erreur démarrage mise à jour: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update/{update_id}/cancel")
async def cancel_update(update_id: str):
    """Annule une mise à jour"""
    try:
        service = get_ota_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        result = await service.cancel_update(update_id)
        return result
        
    except Exception as e:
        logger.error(f"Erreur annulation mise à jour: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/update/{update_id}/status")
async def get_update_status(update_id: str):
    """Récupère le statut d'une mise à jour"""
    try:
        service = get_ota_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        status = await service.get_update_status(update_id)
        if not status:
            raise HTTPException(status_code=404, detail="Mise à jour non trouvée")
        
        return {
            "success": True,
            "update": status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération statut mise à jour: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/device/{device_id}/updates")
async def get_device_updates(device_id: str):
    """Récupère l'historique des mises à jour d'un dispositif"""
    try:
        service = get_ota_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        updates = await service.get_device_updates(device_id)
        return {
            "success": True,
            "device_id": device_id,
            "updates": updates,
            "count": len(updates)
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération historique mises à jour: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/updates/queue")
async def get_update_queue():
    """Récupère la queue des mises à jour"""
    try:
        service = get_ota_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        queue = list(service.update_queue.values())
        active = list(service.active_updates.values())
        
        return {
            "success": True,
            "queued_updates": queue,
            "active_updates": active,
            "queue_count": len(queue),
            "active_count": len(active)
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération queue mises à jour: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/updates/start-all")
async def start_all_queued_updates():
    """Démarre toutes les mises à jour en queue"""
    try:
        service = get_ota_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        results = []
        update_ids = list(service.update_queue.keys())
        
        for update_id in update_ids:
            result = await service.start_update(update_id)
            results.append({
                "update_id": update_id,
                "result": result
            })
        
        successful = sum(1 for r in results if r["result"].get("success", False))
        
        return {
            "success": True,
            "total_updates": len(update_ids),
            "successful_starts": successful,
            "failed_starts": len(update_ids) - successful,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Erreur démarrage mises à jour en masse: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================
# Rollback et récupération
# ==============================

@router.post("/device/{device_id}/rollback")
async def rollback_device(device_id: str):
    """Effectue un rollback du firmware d'un dispositif"""
    try:
        service = get_ota_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        # Récupérer l'historique des mises à jour
        updates = await service.get_device_updates(device_id)
        
        # Trouver la dernière mise à jour réussie
        successful_updates = [
            update for update in updates 
            if update.get("status") == "completed"
        ]
        
        if len(successful_updates) < 2:
            raise HTTPException(
                status_code=400, 
                detail="Pas assez de mises à jour pour effectuer un rollback"
            )
        
        # Prendre la version précédente
        previous_update = successful_updates[1]
        previous_firmware_id = previous_update["firmware_id"]
        
        # Planifier un rollback
        result = await service.schedule_update(
            device_id=device_id,
            firmware_id=previous_firmware_id,
            scheduled_time=datetime.utcnow(),
            force_update=True
        )
        
        if result.get("success"):
            # Démarrer immédiatement le rollback
            await service.start_update(result["update_id"])
            
            return {
                "success": True,
                "message": f"Rollback initié pour {device_id}",
                "update_id": result["update_id"],
                "previous_firmware": previous_firmware_id
            }
        else:
            return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur rollback dispositif: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================
# Monitoring et reporting
# ==============================

@router.get("/reports/summary")
async def get_update_summary():
    """Récupère un résumé des mises à jour"""
    try:
        service = get_ota_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        # Récupérer les statistiques
        stats = await service.get_ota_statistics()
        
        # Récupérer les mises à jour récentes
        recent_updates = await service.db.ota_updates.find(
            {},
            {"_id": 0}
        ).sort("created_at", -1).limit(10).to_list(None)
        
        return {
            "success": True,
            "summary": {
                "statistics": stats,
                "recent_updates": recent_updates,
                "service_status": {
                    "active_updates": len(service.active_updates),
                    "queued_updates": len(service.update_queue),
                    "available_firmwares": len(service.firmware_repository)
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération résumé: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/device-status")
async def get_device_status_report():
    """Récupère un rapport du statut des dispositifs"""
    try:
        service = get_ota_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        # Récupérer tous les dispositifs
        devices = await service.db.devices.find({}, {"_id": 0}).to_list(None)
        
        # Enrichir avec les informations de mise à jour
        for device in devices:
            device_id = device.get("device_id")
            if device_id:
                # Récupérer la dernière mise à jour
                last_update = await service.db.ota_updates.find_one(
                    {"device_id": device_id},
                    {"_id": 0},
                    sort=[("created_at", -1)]
                )
                device["last_update_info"] = last_update
        
        return {
            "success": True,
            "devices": devices,
            "count": len(devices)
        }
        
    except Exception as e:
        logger.error(f"Erreur rapport statut dispositifs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================
# Configuration
# ==============================

@router.get("/config")
async def get_ota_config():
    """Récupère la configuration OTA"""
    try:
        service = get_ota_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        return {
            "success": True,
            "config": service.config
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération configuration OTA: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/config")
async def update_ota_config(config: dict):
    """Met à jour la configuration OTA"""
    try:
        service = get_ota_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        # Mettre à jour la configuration
        service.config.update(config)
        
        return {
            "success": True,
            "message": "Configuration OTA mise à jour",
            "config": service.config
        }
        
    except Exception as e:
        logger.error(f"Erreur mise à jour configuration OTA: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/shutdown")
async def shutdown_ota_service():
    """Arrête le service OTA"""
    try:
        service = get_ota_service()
        if not service:
            raise HTTPException(status_code=503, detail="Service non disponible")
        
        await service.shutdown()
        
        return {
            "success": True,
            "message": "Service OTA arrêté"
        }
        
    except Exception as e:
        logger.error(f"Erreur arrêt service OTA: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
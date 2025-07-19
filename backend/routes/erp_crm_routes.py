"""
Routes pour les connecteurs ERP/CRM
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

from routes.auth_routes import get_current_user
from services.erp_crm_connectors_service import ERPType, CRMType, SyncDirection, DataType, ConnectorConfig

router = APIRouter()

# Modèles de requête
class ConnectorCreateRequest(BaseModel):
    connector_type: str  # "erp" ou "crm"
    system_type: str
    connection_params: Dict[str, Any]
    sync_direction: SyncDirection = SyncDirection.BIDIRECTIONAL
    data_types: List[DataType]
    sync_frequency: int = 60  # minutes
    enabled: bool = True

class ConnectorUpdateRequest(BaseModel):
    connection_params: Optional[Dict[str, Any]] = None
    sync_direction: Optional[SyncDirection] = None
    data_types: Optional[List[DataType]] = None
    sync_frequency: Optional[int] = None
    enabled: Optional[bool] = None

class SyncTriggerRequest(BaseModel):
    connector_id: str

# Variables globales pour les services (injectées depuis server.py)
erp_crm_service = None

def init_erp_crm_service(service):
    global erp_crm_service
    erp_crm_service = service

@router.get("/supported-systems")
async def get_supported_systems():
    """Récupère la liste des systèmes ERP/CRM supportés"""
    if not erp_crm_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service ERP/CRM non disponible"
        )
    
    try:
        systems = await erp_crm_service.get_supported_systems()
        
        return {
            "success": True,
            "data": systems,
            "message": "Systèmes supportés récupérés avec succès"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des systèmes: {str(e)}"
        )

@router.post("/connectors")
async def create_connector(
    request: ConnectorCreateRequest,
    current_user = Depends(get_current_user)
):
    """Crée un nouveau connecteur ERP/CRM"""
    if not erp_crm_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service ERP/CRM non disponible"
        )
    
    try:
        # Créer la configuration du connecteur
        import uuid
        config = ConnectorConfig(
            connector_id=f"{request.system_type}_{str(uuid.uuid4())[:8]}",
            connector_type=request.connector_type,
            system_type=request.system_type,
            connection_params=request.connection_params,
            sync_direction=request.sync_direction,
            data_types=request.data_types,
            sync_frequency=request.sync_frequency,
            enabled=request.enabled,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        result = await erp_crm_service.create_connector(
            user_id=current_user.id,
            config=config
        )
        
        if result["success"]:
            return {
                "success": True,
                "data": {
                    "connector_id": result["connector_id"],
                    "system_type": request.system_type,
                    "connector_type": request.connector_type
                },
                "message": result["message"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création du connecteur: {str(e)}"
        )

@router.get("/connectors")
async def get_user_connectors(current_user = Depends(get_current_user)):
    """Récupère les connecteurs de l'utilisateur"""
    if not erp_crm_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service ERP/CRM non disponible"
        )
    
    try:
        connectors = await erp_crm_service.get_user_connectors(current_user.id)
        
        return {
            "success": True,
            "data": connectors,
            "message": f"Connecteurs récupérés pour {current_user.username}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des connecteurs: {str(e)}"
        )

@router.put("/connectors/{connector_id}")
async def update_connector(
    connector_id: str,
    request: ConnectorUpdateRequest,
    current_user = Depends(get_current_user)
):
    """Met à jour un connecteur"""
    if not erp_crm_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service ERP/CRM non disponible"
        )
    
    try:
        # Préparer les mises à jour
        updates = {}
        if request.connection_params is not None:
            updates["connection_params"] = request.connection_params
        if request.sync_direction is not None:
            updates["sync_direction"] = request.sync_direction.value
        if request.data_types is not None:
            updates["data_types"] = [dt.value for dt in request.data_types]
        if request.sync_frequency is not None:
            updates["sync_frequency"] = request.sync_frequency
        if request.enabled is not None:
            updates["enabled"] = request.enabled
        
        success = await erp_crm_service.update_connector(
            user_id=current_user.id,
            connector_id=connector_id,
            updates=updates
        )
        
        if success:
            return {
                "success": True,
                "message": "Connecteur mis à jour avec succès"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Connecteur non trouvé"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la mise à jour: {str(e)}"
        )

@router.delete("/connectors/{connector_id}")
async def delete_connector(
    connector_id: str,
    current_user = Depends(get_current_user)
):
    """Supprime un connecteur"""
    if not erp_crm_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service ERP/CRM non disponible"
        )
    
    try:
        success = await erp_crm_service.delete_connector(
            user_id=current_user.id,
            connector_id=connector_id
        )
        
        if success:
            return {
                "success": True,
                "message": "Connecteur supprimé avec succès"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Connecteur non trouvé"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la suppression: {str(e)}"
        )

@router.post("/connectors/{connector_id}/sync")
async def trigger_sync(
    connector_id: str,
    current_user = Depends(get_current_user)
):
    """Déclenche une synchronisation manuelle"""
    if not erp_crm_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service ERP/CRM non disponible"
        )
    
    try:
        result = await erp_crm_service.trigger_sync(
            user_id=current_user.id,
            connector_id=connector_id
        )
        
        if result["success"]:
            return {
                "success": True,
                "data": result,
                "message": "Synchronisation déclenchée avec succès"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la synchronisation: {str(e)}"
        )

@router.get("/connectors/{connector_id}/logs")
async def get_connector_logs(
    connector_id: str,
    limit: int = 50,
    current_user = Depends(get_current_user)
):
    """Récupère les logs d'un connecteur"""
    if not erp_crm_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service ERP/CRM non disponible"
        )
    
    try:
        logs = await erp_crm_service.get_sync_logs(
            user_id=current_user.id,
            connector_id=connector_id,
            limit=limit
        )
        
        return {
            "success": True,
            "data": logs,
            "message": f"Logs récupérés pour le connecteur {connector_id}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des logs: {str(e)}"
        )

@router.get("/logs")
async def get_all_sync_logs(
    limit: int = 50,
    current_user = Depends(get_current_user)
):
    """Récupère tous les logs de synchronisation de l'utilisateur"""
    if not erp_crm_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service ERP/CRM non disponible"
        )
    
    try:
        logs = await erp_crm_service.get_sync_logs(
            user_id=current_user.id,
            limit=limit
        )
        
        return {
            "success": True,
            "data": logs,
            "message": f"Logs de synchronisation récupérés pour {current_user.username}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des logs: {str(e)}"
        )

@router.get("/statistics")
async def get_erp_crm_statistics(current_user = Depends(get_current_user)):
    """Récupère les statistiques ERP/CRM de l'utilisateur"""
    try:
        # Simulation de statistiques
        stats = {
            "total_connectors": 0,
            "active_connectors": 0,
            "erp_connectors": 0,
            "crm_connectors": 0,
            "total_syncs": 0,
            "successful_syncs": 0,
            "failed_syncs": 0,
            "last_sync": None,
            "connector_types": {
                "sap": 0,
                "salesforce": 0,
                "oracle": 0,
                "microsoft_dynamics": 0,
                "hubspot": 0,
                "custom": 0
            },
            "sync_frequencies": {
                "5min": 0,
                "15min": 0,
                "30min": 0,
                "1hour": 0,
                "daily": 0
            }
        }
        
        if erp_crm_service:
            # Récupérer les connecteurs réels
            connectors = await erp_crm_service.get_user_connectors(current_user.id)
            stats["total_connectors"] = len(connectors)
            stats["active_connectors"] = len([c for c in connectors if c.get("enabled", False)])
            stats["erp_connectors"] = len([c for c in connectors if c.get("connector_type") == "erp"])
            stats["crm_connectors"] = len([c for c in connectors if c.get("connector_type") == "crm"])
            
            # Compter par type de système
            for connector in connectors:
                system_type = connector.get("system_type", "custom")
                if system_type in stats["connector_types"]:
                    stats["connector_types"][system_type] += 1
                
                # Compter les fréquences de sync
                freq = connector.get("sync_frequency", 60)
                if freq <= 5:
                    stats["sync_frequencies"]["5min"] += 1
                elif freq <= 15:
                    stats["sync_frequencies"]["15min"] += 1
                elif freq <= 30:
                    stats["sync_frequencies"]["30min"] += 1
                elif freq <= 60:
                    stats["sync_frequencies"]["1hour"] += 1
                else:
                    stats["sync_frequencies"]["daily"] += 1
                
                # Stats de synchronisation
                stats["total_syncs"] += connector.get("total_syncs", 0)
                if connector.get("last_sync"):
                    if not stats["last_sync"] or connector["last_sync"] > stats["last_sync"]:
                        stats["last_sync"] = connector["last_sync"]
        
        return {
            "success": True,
            "data": stats,
            "message": "Statistiques ERP/CRM récupérées avec succès"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des statistiques: {str(e)}"
        )

@router.get("/health")
async def erp_crm_health_check():
    """Vérifie la santé du service ERP/CRM"""
    try:
        if not erp_crm_service:
            return {
                "healthy": False,
                "message": "Service ERP/CRM non initialisé",
                "timestamp": datetime.utcnow()
            }
        
        is_ready = erp_crm_service.is_ready()
        return {
            "healthy": is_ready,
            "message": "Service ERP/CRM opérationnel" if is_ready else "Service en cours d'initialisation",
            "supported_erp": len([e for e in ERPType]),
            "supported_crm": len([c for c in CRMType]),
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        return {
            "healthy": False,
            "error": str(e),
            "timestamp": datetime.utcnow()
        }
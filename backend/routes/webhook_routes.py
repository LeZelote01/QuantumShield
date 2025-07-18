"""
Routes Webhooks pour QuantumShield
Gestion des webhooks et notifications temps réel
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, HttpUrl
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from services.webhook_service import WebhookService, WebhookEvent, WebhookStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

# Variables globales pour les services
_webhook_service = None

def init_webhook_service(db):
    """Initialise le service de webhooks"""
    global _webhook_service
    _webhook_service = WebhookService(db)
    logger.info("Service Webhooks initialisé pour les routes")

# ==============================
# Modèles Pydantic
# ==============================

class WebhookCreate(BaseModel):
    url: HttpUrl
    events: List[WebhookEvent]
    name: Optional[str] = None
    headers: Optional[Dict[str, str]] = None

class WebhookUpdate(BaseModel):
    url: Optional[HttpUrl] = None
    events: Optional[List[WebhookEvent]] = None
    status: Optional[WebhookStatus] = None
    name: Optional[str] = None
    headers: Optional[Dict[str, str]] = None

class WebhookResponse(BaseModel):
    webhook_id: str
    url: str
    events: List[str]
    name: str
    status: str
    created_at: datetime
    success_count: int
    failure_count: int
    total_deliveries: int

class WebhookTestResponse(BaseModel):
    success: bool
    webhook_id: str
    delivery_result: Dict[str, Any]

# ==============================
# Endpoints de gestion
# ==============================

@router.post("/", response_model=Dict[str, Any])
async def create_webhook(webhook_data: WebhookCreate, user_id: str = Query(...)):
    """Crée un nouveau webhook"""
    try:
        if _webhook_service is None:
            raise HTTPException(status_code=500, detail="Service webhooks non initialisé")
        
        result = await _webhook_service.register_webhook(
            url=str(webhook_data.url),
            events=webhook_data.events,
            user_id=user_id,
            name=webhook_data.name,
            headers=webhook_data.headers
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Erreur création webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[WebhookResponse])
async def list_webhooks(user_id: Optional[str] = Query(None)):
    """Liste les webhooks"""
    try:
        if _webhook_service is None:
            raise HTTPException(status_code=500, detail="Service webhooks non initialisé")
        
        webhooks = await _webhook_service.list_webhooks(user_id)
        
        return [
            WebhookResponse(
                webhook_id=w["webhook_id"],
                url=w["url"],
                events=w["events"],
                name=w["name"],
                status=w["status"],
                created_at=w["created_at"],
                success_count=w["success_count"],
                failure_count=w["failure_count"],
                total_deliveries=w["total_deliveries"]
            )
            for w in webhooks
        ]
        
    except Exception as e:
        logger.error(f"Erreur liste webhooks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{webhook_id}")
async def get_webhook(webhook_id: str):
    """Récupère un webhook spécifique"""
    try:
        if _webhook_service is None:
            raise HTTPException(status_code=500, detail="Service webhooks non initialisé")
        
        webhooks = await _webhook_service.list_webhooks()
        webhook = next((w for w in webhooks if w["webhook_id"] == webhook_id), None)
        
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook non trouvé")
        
        return webhook
        
    except Exception as e:
        logger.error(f"Erreur récupération webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{webhook_id}")
async def update_webhook(webhook_id: str, webhook_data: WebhookUpdate):
    """Met à jour un webhook"""
    try:
        if _webhook_service is None:
            raise HTTPException(status_code=500, detail="Service webhooks non initialisé")
        
        result = await _webhook_service.update_webhook(
            webhook_id=webhook_id,
            url=str(webhook_data.url) if webhook_data.url else None,
            events=webhook_data.events,
            status=webhook_data.status,
            name=webhook_data.name,
            headers=webhook_data.headers
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Erreur mise à jour webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{webhook_id}")
async def delete_webhook(webhook_id: str):
    """Supprime un webhook"""
    try:
        if _webhook_service is None:
            raise HTTPException(status_code=500, detail="Service webhooks non initialisé")
        
        result = await _webhook_service.delete_webhook(webhook_id)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Erreur suppression webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{webhook_id}/test", response_model=WebhookTestResponse)
async def test_webhook(webhook_id: str):
    """Teste un webhook"""
    try:
        if _webhook_service is None:
            raise HTTPException(status_code=500, detail="Service webhooks non initialisé")
        
        result = await _webhook_service.test_webhook(webhook_id)
        
        return WebhookTestResponse(
            success=result["success"],
            webhook_id=webhook_id,
            delivery_result=result.get("delivery_result", {})
        )
        
    except Exception as e:
        logger.error(f"Erreur test webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================
# Endpoints d'émission d'événements
# ==============================

@router.post("/emit")
async def emit_event(event_type: WebhookEvent, data: Dict[str, Any]):
    """Émet un événement vers les webhooks (admin seulement)"""
    try:
        if _webhook_service is None:
            raise HTTPException(status_code=500, detail="Service webhooks non initialisé")
        
        await _webhook_service.emit_event(event_type, data)
        
        return {
            "success": True,
            "event_type": event_type.value,
            "message": "Événement émis avec succès"
        }
        
    except Exception as e:
        logger.error(f"Erreur émission événement: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================
# Endpoints de statistiques
# ==============================

@router.get("/stats/global")
async def get_global_webhook_stats():
    """Récupère les statistiques globales des webhooks"""
    try:
        if _webhook_service is None:
            raise HTTPException(status_code=500, detail="Service webhooks non initialisé")
        
        stats = await _webhook_service.get_webhook_stats()
        
        return stats
        
    except Exception as e:
        logger.error(f"Erreur récupération stats globales: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/{webhook_id}")
async def get_webhook_stats(webhook_id: str):
    """Récupère les statistiques d'un webhook spécifique"""
    try:
        if _webhook_service is None:
            raise HTTPException(status_code=500, detail="Service webhooks non initialisé")
        
        stats = await _webhook_service.get_webhook_stats(webhook_id)
        
        if "error" in stats:
            raise HTTPException(status_code=404, detail=stats["error"])
        
        return stats
        
    except Exception as e:
        logger.error(f"Erreur récupération stats webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================
# Endpoints d'information
# ==============================

@router.get("/events/supported")
async def get_supported_events():
    """Récupère la liste des événements supportés"""
    try:
        events = [
            {
                "event": event.value,
                "description": get_event_description(event)
            }
            for event in WebhookEvent
        ]
        
        return {
            "supported_events": events,
            "total_events": len(events)
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération événements supportés: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/examples")
async def get_webhook_examples():
    """Récupère des exemples de configuration de webhooks"""
    try:
        examples = {
            "device_monitoring": {
                "description": "Webhook pour monitoring des devices",
                "url": "https://your-server.com/webhooks/device-monitoring",
                "events": [
                    WebhookEvent.DEVICE_REGISTERED.value,
                    WebhookEvent.DEVICE_OFFLINE.value,
                    WebhookEvent.DEVICE_ANOMALY.value
                ],
                "headers": {
                    "Authorization": "Bearer YOUR_API_TOKEN",
                    "X-Custom-Header": "value"
                }
            },
            "security_alerts": {
                "description": "Webhook pour alertes de sécurité",
                "url": "https://your-server.com/webhooks/security-alerts",
                "events": [
                    WebhookEvent.DEVICE_ANOMALY.value,
                    WebhookEvent.SECURITY_ALERT.value,
                    WebhookEvent.CERTIFICATE_EXPIRING.value
                ]
            },
            "business_events": {
                "description": "Webhook pour événements business",
                "url": "https://your-server.com/webhooks/business",
                "events": [
                    WebhookEvent.SERVICE_PURCHASED.value,
                    WebhookEvent.TOKEN_TRANSFER.value,
                    WebhookEvent.STAKING_REWARD.value
                ]
            },
            "blockchain_events": {
                "description": "Webhook pour événements blockchain",
                "url": "https://your-server.com/webhooks/blockchain",
                "events": [
                    WebhookEvent.BLOCK_MINED.value,
                    WebhookEvent.TRANSACTION_CONFIRMED.value
                ]
            }
        }
        
        return {
            "examples": examples,
            "webhook_signature": {
                "description": "Les webhooks incluent une signature HMAC-SHA256",
                "header": "X-Webhook-Signature",
                "format": "sha256=<hash>",
                "verification": "Utilisez votre secret webhook pour vérifier la signature"
            }
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération exemples: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def webhook_health_check():
    """Vérifie la santé du service webhooks"""
    try:
        if _webhook_service is None:
            return {
                "status": "unhealthy",
                "error": "Service webhooks non initialisé"
            }
        
        if not _webhook_service.is_ready():
            return {
                "status": "unhealthy",
                "error": "Service webhooks non prêt"
            }
        
        return {
            "status": "healthy",
            "message": "Service webhooks opérationnel",
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Erreur health check webhooks: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# ==============================
# Fonctions utilitaires
# ==============================

def get_event_description(event: WebhookEvent) -> str:
    """Retourne la description d'un événement"""
    descriptions = {
        WebhookEvent.DEVICE_REGISTERED: "Déclenché quand un nouveau device est enregistré",
        WebhookEvent.DEVICE_OFFLINE: "Déclenché quand un device passe hors ligne",
        WebhookEvent.DEVICE_ANOMALY: "Déclenché quand une anomalie est détectée sur un device",
        WebhookEvent.DEVICE_HEARTBEAT: "Déclenché à chaque heartbeat de device",
        WebhookEvent.USER_REGISTERED: "Déclenché quand un nouvel utilisateur s'inscrit",
        WebhookEvent.TOKEN_TRANSFER: "Déclenché lors d'un transfert de tokens",
        WebhookEvent.BLOCK_MINED: "Déclenché quand un nouveau bloc est miné",
        WebhookEvent.TRANSACTION_CONFIRMED: "Déclenché quand une transaction est confirmée",
        WebhookEvent.SERVICE_PURCHASED: "Déclenché quand un service est acheté",
        WebhookEvent.STAKING_REWARD: "Déclenché quand une récompense de staking est distribuée",
        WebhookEvent.SECURITY_ALERT: "Déclenché lors d'une alerte de sécurité",
        WebhookEvent.FIRMWARE_UPDATE: "Déclenché lors d'une mise à jour firmware",
        WebhookEvent.CERTIFICATE_EXPIRING: "Déclenché quand un certificat approche de l'expiration"
    }
    
    return descriptions.get(event, "Description non disponible")
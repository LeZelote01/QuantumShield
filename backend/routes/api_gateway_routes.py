"""
Routes pour l'API Gateway de QuantumShield
Gestion des clés API, rate limiting, monitoring et proxy
"""

from fastapi import APIRouter, HTTPException, Depends, Request, status
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from routes.auth_routes import get_current_user
from models.api_gateway_models import *
from services.api_gateway_service import APIGatewayService

router = APIRouter()

# Service sera injecté depuis server.py
api_gateway_service = None

def get_api_gateway_service():
    """Récupère le service API Gateway"""
    if api_gateway_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service API Gateway non disponible"
        )
    return api_gateway_service

def init_api_gateway_service(service: APIGatewayService):
    """Initialise le service API Gateway"""
    global api_gateway_service
    api_gateway_service = service

# Helper pour vérifier les droits admin
def is_admin_user(user) -> bool:
    """Vérifie si l'utilisateur a les droits admin"""
    return getattr(user, 'is_admin', False)

# ===== GESTION DES CLÉS API =====

@router.post("/api-keys/create", response_model=StandardResponse)
async def create_api_key(
    request: APIKeyCreateRequest,
    current_user = Depends(get_current_user),
    gateway_service = Depends(get_api_gateway_service)
):
    """Crée une nouvelle clé API"""
    try:
        api_key_data = await gateway_service.create_api_key(
            user_id=current_user.id,
            tier=request.tier,
            description=request.description
        )
        
        return StandardResponse(
            success=True,
            message="Clé API créée avec succès",
            data=api_key_data
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur création clé API: {str(e)}"
        )

@router.post("/api-keys/validate")
async def validate_api_key(
    request: APIKeyValidationRequest,
    gateway_service = Depends(get_api_gateway_service)
):
    """Valide une clé API"""
    try:
        key_config = await gateway_service.validate_api_key(
            api_key=request.api_key,
            api_secret=request.api_secret
        )
        
        if key_config:
            return StandardResponse(
                success=True,
                message="Clé API valide",
                data={
                    "valid": True,
                    "tier": key_config["tier"],
                    "user_id": key_config["user_id"],
                    "rate_limits": key_config["rate_limits"]
                }
            )
        else:
            return StandardResponse(
                success=False,
                message="Clé API invalide",
                data={"valid": False}
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur validation clé API: {str(e)}"
        )

@router.post("/api-keys/revoke")
async def revoke_api_key(
    request: APIKeyRevokeRequest,
    current_user = Depends(get_current_user),
    gateway_service = Depends(get_api_gateway_service)
):
    """Révoque une clé API"""
    try:
        success = await gateway_service.revoke_api_key(
            api_key=request.api_key,
            user_id=current_user.id
        )
        
        if success:
            return StandardResponse(
                success=True,
                message="Clé API révoquée avec succès"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Clé API non trouvée"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur révocation clé API: {str(e)}"
        )

@router.get("/api-keys/my-keys")
async def get_my_api_keys(
    current_user = Depends(get_current_user),
    gateway_service = Depends(get_api_gateway_service)
):
    """Récupère les clés API de l'utilisateur connecté"""
    try:
        # Récupérer depuis la base de données
        from server import db
        
        user_keys = await db.api_keys.find(
            {"user_id": current_user.id}
        ).to_list(None)
        
        # Nettoyer les données sensibles
        cleaned_keys = []
        for key in user_keys:
            cleaned_key = {
                "api_key": key["api_key"],
                "tier": key["tier"],
                "description": key.get("description"),
                "created_at": key["created_at"],
                "last_used": key.get("last_used"),
                "is_active": key["is_active"],
                "usage_stats": key.get("usage_stats", {}),
                "rate_limits": key.get("rate_limits", {})
            }
            cleaned_keys.append(cleaned_key)
        
        return StandardResponse(
            success=True,
            message="Clés API récupérées",
            data={"api_keys": cleaned_keys}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération clés API: {str(e)}"
        )

# ===== RATE LIMITING =====

@router.post("/rate-limit/check")
async def check_rate_limit(
    request: Request,
    api_key: Optional[str] = None,
    gateway_service = Depends(get_api_gateway_service)
):
    """Vérifie les limites de taux pour une requête"""
    try:
        allowed, result = await gateway_service.check_rate_limit(
            request=request,
            api_key=api_key
        )
        
        return {
            "allowed": allowed,
            "result": result,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur vérification rate limit: {str(e)}"
        )

@router.put("/rate-limit/update-tier-limits")
async def update_tier_limits(
    request: TierLimitsUpdateRequest,
    current_user = Depends(get_current_user),
    gateway_service = Depends(get_api_gateway_service)
):
    """Met à jour les limites de taux pour un tier (admin seulement)"""
    try:
        if not is_admin_user(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès administrateur requis"
            )
        
        success = await gateway_service.update_rate_limits(
            tier=request.tier,
            new_limits=request.new_limits
        )
        
        if success:
            return StandardResponse(
                success=True,
                message=f"Limites mises à jour pour tier {request.tier.value}"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erreur mise à jour des limites"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur mise à jour limites: {str(e)}"
        )

@router.post("/rate-limit/add-sensitive-endpoint")
async def add_sensitive_endpoint(
    request: SensitiveEndpointRequest,
    current_user = Depends(get_current_user),
    gateway_service = Depends(get_api_gateway_service)
):
    """Ajoute un endpoint avec des limites spéciales (admin seulement)"""
    try:
        if not is_admin_user(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès administrateur requis"
            )
        
        success = await gateway_service.add_sensitive_endpoint(
            endpoint=request.endpoint,
            limits=request.limits
        )
        
        if success:
            return StandardResponse(
                success=True,
                message=f"Endpoint sensible ajouté: {request.endpoint}"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erreur ajout endpoint sensible"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur ajout endpoint: {str(e)}"
        )

# ===== BLOCAGE D'IPS =====

@router.post("/security/block-ip")
async def block_ip(
    request: IPBlockRequest,
    current_user = Depends(get_current_user),
    gateway_service = Depends(get_api_gateway_service)
):
    """Bloque une adresse IP (admin seulement)"""
    try:
        if not is_admin_user(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès administrateur requis"
            )
        
        success = await gateway_service.block_ip(
            ip_address=request.ip_address,
            reason=request.reason,
            duration_hours=request.duration_hours
        )
        
        if success:
            return StandardResponse(
                success=True,
                message=f"IP {request.ip_address} bloquée pour {request.duration_hours}h"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erreur blocage IP"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur blocage IP: {str(e)}"
        )

@router.post("/security/unblock-ip")
async def unblock_ip(
    request: IPUnblockRequest,
    current_user = Depends(get_current_user),
    gateway_service = Depends(get_api_gateway_service)
):
    """Débloque une adresse IP (admin seulement)"""
    try:
        if not is_admin_user(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès administrateur requis"
            )
        
        success = await gateway_service.unblock_ip(
            ip_address=request.ip_address
        )
        
        if success:
            return StandardResponse(
                success=True,
                message=f"IP {request.ip_address} débloquée"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erreur déblocage IP"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur déblocage IP: {str(e)}"
        )

@router.get("/security/blocked-ips")
async def get_blocked_ips(
    current_user = Depends(get_current_user),
    gateway_service = Depends(get_api_gateway_service)
):
    """Récupère la liste des IPs bloquées (admin seulement)"""
    try:
        if not is_admin_user(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès administrateur requis"
            )
        
        from server import db
        
        blocked_ips = await db.blocked_ips.find(
            {"is_active": True}
        ).to_list(None)
        
        return StandardResponse(
            success=True,
            message="IPs bloquées récupérées",
            data={"blocked_ips": blocked_ips}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération IPs bloquées: {str(e)}"
        )

# ===== ANALYTICS ET MONITORING =====

@router.get("/analytics/usage-stats")
async def get_usage_stats(
    user_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user = Depends(get_current_user),
    gateway_service = Depends(get_api_gateway_service)
):
    """Récupère les statistiques d'utilisation"""
    try:
        # Vérifier les permissions
        if user_id and user_id != current_user.id and not is_admin_user(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé"
            )
        
        # Si pas d'user_id spécifié, utiliser l'utilisateur connecté
        if not user_id:
            user_id = current_user.id
        
        stats = await gateway_service.get_api_usage_stats(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return StandardResponse(
            success=True,
            message="Statistiques récupérées",
            data={"stats": stats}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération statistiques: {str(e)}"
        )

@router.get("/analytics/rate-limit-violations")
async def get_rate_limit_violations(
    limit: int = 100,
    current_user = Depends(get_current_user),
    gateway_service = Depends(get_api_gateway_service)
):
    """Récupère les violations de rate limiting (admin seulement)"""
    try:
        if not is_admin_user(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès administrateur requis"
            )
        
        violations = await gateway_service.get_rate_limit_violations(limit=limit)
        
        return StandardResponse(
            success=True,
            message="Violations récupérées",
            data={"violations": violations}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération violations: {str(e)}"
        )

@router.get("/health")
async def gateway_health_check(
    gateway_service = Depends(get_api_gateway_service)
):
    """Vérifie l'état de santé de l'API Gateway"""
    try:
        health_data = await gateway_service.get_gateway_health()
        
        return {
            "health": health_data,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        return {
            "health": {
                "status": "unhealthy",
                "error": str(e)
            },
            "timestamp": datetime.utcnow()
        }

# ===== PROXY ET LOAD BALANCING =====

@router.post("/proxy/request")
async def proxy_request(
    request: ProxyRequest,
    current_user = Depends(get_current_user),
    gateway_service = Depends(get_api_gateway_service)
):
    """Proxifie une requête vers un service backend"""
    try:
        result = await gateway_service.proxy_request(
            request_data={
                "endpoint": request.endpoint,
                "method": request.method,
                "headers": request.headers,
                "data": request.data
            },
            target_service=request.target_service
        )
        
        return {
            "proxy_result": result,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur proxy: {str(e)}"
        )

# ===== CONFIGURATION =====

@router.get("/config/tiers")
async def get_tier_configurations(
    current_user = Depends(get_current_user),
    gateway_service = Depends(get_api_gateway_service)
):
    """Récupère la configuration des tiers"""
    try:
        return StandardResponse(
            success=True,
            message="Configuration des tiers",
            data={"tier_limits": gateway_service.tier_limits}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération config: {str(e)}"
        )

@router.get("/config/sensitive-endpoints")
async def get_sensitive_endpoints(
    current_user = Depends(get_current_user),
    gateway_service = Depends(get_api_gateway_service)
):
    """Récupère les endpoints sensibles (admin seulement)"""
    try:
        if not is_admin_user(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès administrateur requis"
            )
        
        return StandardResponse(
            success=True,
            message="Endpoints sensibles",
            data={"sensitive_endpoints": gateway_service.sensitive_endpoints}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération endpoints: {str(e)}"
        )

# ===== DASHBOARD =====

@router.get("/dashboard")
async def get_gateway_dashboard(
    current_user = Depends(get_current_user),
    gateway_service = Depends(get_api_gateway_service)
):
    """Récupère les données du dashboard API Gateway"""
    try:
        # Récupérer diverses métriques
        health_data = await gateway_service.get_gateway_health()
        
        # Statistiques générales (admin) ou personnelles (utilisateur)
        if is_admin_user(current_user):
            stats = await gateway_service.get_api_usage_stats()
        else:
            stats = await gateway_service.get_api_usage_stats(user_id=current_user.id)
        
        dashboard_data = {
            "health": health_data,
            "usage_stats": stats,
            "user_tier": "admin" if is_admin_user(current_user) else "user",
            "last_updated": datetime.utcnow()
        }
        
        return StandardResponse(
            success=True,
            message="Dashboard API Gateway",
            data=dashboard_data
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur dashboard: {str(e)}"
        )
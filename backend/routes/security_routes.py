"""
Routes pour la sécurité renforcée
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

from routes.auth_routes import get_current_user
from services.security_service import SecurityService, MFAMethod, SecurityEventType

router = APIRouter()

# Modèles de requête
class MFASetupRequest(BaseModel):
    service_name: str = "QuantumShield"

class MFAVerifyRequest(BaseModel):
    totp_code: str

class MFADisableRequest(BaseModel):
    method: MFAMethod

class BehaviorAnalysisRequest(BaseModel):
    action: str
    context: Dict[str, Any]

class SecurityAuditRequest(BaseModel):
    user_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

# Routes MFA
@router.post("/mfa/setup-totp")
async def setup_totp_mfa(
    request: MFASetupRequest,
    current_user = Depends(get_current_user)
):
    """Configure l'authentification TOTP"""
    from server import security_service
    
    try:
        setup_data = await security_service.setup_totp_mfa(
            user_id=current_user["id"],
            service_name=request.service_name
        )
        
        return {
            "setup_data": setup_data,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur configuration TOTP: {str(e)}"
        )

@router.post("/mfa/verify-totp-setup")
async def verify_totp_setup(
    request: MFAVerifyRequest,
    current_user = Depends(get_current_user)
):
    """Vérifie et active la configuration TOTP"""
    from server import security_service
    
    try:
        verification_data = await security_service.verify_totp_setup(
            user_id=current_user["id"],
            totp_code=request.totp_code
        )
        
        return {
            "verification_data": verification_data,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur vérification TOTP: {str(e)}"
        )

@router.post("/mfa/verify-totp")
async def verify_totp(
    request: MFAVerifyRequest,
    current_user = Depends(get_current_user)
):
    """Vérifie un code TOTP"""
    from server import security_service
    
    try:
        is_valid = await security_service.verify_totp_code(
            user_id=current_user["id"],
            totp_code=request.totp_code
        )
        
        return {
            "valid": is_valid,
            "timestamp": datetime.utcnow(),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur vérification TOTP: {str(e)}"
        )

@router.post("/mfa/disable")
async def disable_mfa(
    request: MFADisableRequest,
    current_user = Depends(get_current_user)
):
    """Désactive la MFA"""
    from server import security_service
    
    try:
        disable_data = await security_service.disable_mfa(
            user_id=current_user["id"],
            method=request.method
        )
        
        return {
            "disable_data": disable_data,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur désactivation MFA: {str(e)}"
        )

@router.get("/mfa/status")
async def get_mfa_status(current_user = Depends(get_current_user)):
    """Récupère le statut MFA"""
    from server import security_service
    
    try:
        status_data = await security_service.get_mfa_status(
            user_id=current_user["id"]
        )
        
        return {
            "mfa_status": status_data,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération statut MFA: {str(e)}"
        )

# Routes analyse comportementale
@router.post("/behavior/analyze")
async def analyze_behavior(
    request: BehaviorAnalysisRequest,
    current_user = Depends(get_current_user)
):
    """Analyse le comportement utilisateur"""
    from server import security_service
    
    try:
        analysis = await security_service.analyze_user_behavior(
            user_id=current_user["id"],
            action=request.action,
            context=request.context
        )
        
        return {
            "analysis": analysis,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur analyse comportementale: {str(e)}"
        )

# Routes audit de sécurité
@router.post("/audit/report")
async def get_security_audit_report(
    request: SecurityAuditRequest,
    current_user = Depends(get_current_user)
):
    """Génère un rapport d'audit de sécurité"""
    from server import security_service
    
    try:
        # Vérifier les permissions (admin uniquement)
        if not current_user.get("is_admin", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès administrateur requis"
            )
        
        report = await security_service.get_security_audit_report(
            user_id=request.user_id,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        return {
            "audit_report": report,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur génération rapport audit: {str(e)}"
        )

@router.get("/dashboard")
async def get_security_dashboard(current_user = Depends(get_current_user)):
    """Récupère le tableau de bord sécurité"""
    from server import security_service
    
    try:
        dashboard_data = await security_service.get_security_dashboard()
        
        return {
            "dashboard": dashboard_data,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur tableau de bord sécurité: {str(e)}"
        )

# Routes pour enregistrer des événements (utilisées par d'autres services)
@router.post("/events/log")
async def log_security_event(
    event_type: SecurityEventType,
    details: Dict[str, Any] = None,
    current_user = Depends(get_current_user)
):
    """Enregistre un événement de sécurité"""
    from server import security_service
    
    try:
        await security_service.log_security_event(
            user_id=current_user["id"],
            event_type=event_type,
            details=details
        )
        
        return {
            "event_logged": True,
            "timestamp": datetime.utcnow(),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur enregistrement événement: {str(e)}"
        )

@router.get("/health")
async def security_health_check():
    """Vérifie la santé du service de sécurité"""
    from server import security_service
    
    try:
        return {
            "service_ready": security_service.is_ready(),
            "timestamp": datetime.utcnow(),
            "status": "healthy"
        }
        
    except Exception as e:
        return {
            "service_ready": False,
            "error": str(e),
            "timestamp": datetime.utcnow(),
            "status": "unhealthy"
        }

@router.get("/recommendations")
async def get_security_recommendations(current_user = Depends(get_current_user)):
    """Récupère les recommandations de sécurité personnalisées"""
    from server import security_service
    
    try:
        # Récupérer le statut MFA
        mfa_status = await security_service.get_mfa_status(current_user["id"])
        
        # Générer des recommandations
        recommendations = []
        
        if not mfa_status["mfa_enabled"]:
            recommendations.append({
                "type": "mfa_setup",
                "priority": "high",
                "title": "Activer l'authentification multi-facteur",
                "description": "Sécurisez votre compte avec l'authentification à deux facteurs",
                "action": "setup_mfa"
            })
        
        recommendations.append({
            "type": "password_strength",
            "priority": "medium",
            "title": "Vérifier la force du mot de passe",
            "description": "Utilisez un mot de passe complexe et unique",
            "action": "check_password"
        })
        
        recommendations.append({
            "type": "activity_review",
            "priority": "low",
            "title": "Examiner l'activité récente",
            "description": "Vérifiez les connexions et actions récentes",
            "action": "review_activity"
        })
        
        return {
            "recommendations": recommendations,
            "user_id": current_user["id"],
            "generated_at": datetime.utcnow(),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur génération recommandations: {str(e)}"
        )
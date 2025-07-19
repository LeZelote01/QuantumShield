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

# Helper function to check admin status
def is_admin_user(user) -> bool:
    """Check if user has admin privileges"""
    return getattr(user, 'is_admin', False)

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
            user_id=current_user.id,
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
            user_id=current_user.id,
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
            user_id=current_user.id,
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
            user_id=current_user.id,
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
            user_id=current_user.id
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
            user_id=current_user.id,
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
        if not is_admin_user(current_user):
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
            user_id=current_user.id,
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
        mfa_status = await security_service.get_mfa_status(current_user.id)
        
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
            "user_id": current_user.id,
            "generated_at": datetime.utcnow(),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur génération recommandations: {str(e)}"
        )

# ===== NOUVELLES ROUTES - SÉCURITÉ RENFORCÉE =====

# Modèles de requête supplémentaires
class HoneypotCreateRequest(BaseModel):
    honeypot_type: str
    config: Dict[str, Any]

class HoneypotTriggerRequest(BaseModel):
    honeypot_id: str
    interaction_data: Dict[str, Any]

class BackupCreateRequest(BaseModel):
    backup_type: str
    data: Dict[str, Any]

class BackupRestoreRequest(BaseModel):
    backup_id: str

class GDPRRequest(BaseModel):
    user_id: str

class DataDeletionRequest(BaseModel):
    user_id: str
    verification_code: str

# Routes Honeypots
@router.post("/honeypots/create")
async def create_honeypot(
    request: HoneypotCreateRequest,
    current_user = Depends(get_current_user)
):
    """Crée un honeypot"""
    from server import security_service
    
    try:
        # Vérifier les permissions admin
        if not is_admin_user(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès administrateur requis"
            )
        
        honeypot = await security_service.create_honeypot(
            honeypot_type=request.honeypot_type,
            config=request.config
        )
        
        return {
            "honeypot": honeypot,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur création honeypot: {str(e)}"
        )

@router.post("/honeypots/trigger")
async def trigger_honeypot(
    request: HoneypotTriggerRequest,
    current_user = Depends(get_current_user)
):
    """Déclenche un honeypot (pour tests)"""
    from server import security_service
    
    try:
        # Vérifier les permissions admin
        if not is_admin_user(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès administrateur requis"
            )
        
        await security_service.trigger_honeypot(
            honeypot_id=request.honeypot_id,
            interaction_data=request.interaction_data
        )
        
        return {
            "triggered": True,
            "timestamp": datetime.utcnow(),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur déclenchement honeypot: {str(e)}"
        )

@router.get("/honeypots/report")
async def get_honeypot_report(current_user = Depends(get_current_user)):
    """Récupère le rapport des honeypots"""
    from server import security_service
    
    try:
        # Vérifier les permissions admin
        if not is_admin_user(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès administrateur requis"
            )
        
        report = await security_service.get_honeypot_report()
        
        return {
            "report": report,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur rapport honeypots: {str(e)}"
        )

# Routes Backup et Récupération
@router.post("/backup/create")
async def create_security_backup(
    request: BackupCreateRequest,
    current_user = Depends(get_current_user)
):
    """Crée une sauvegarde sécurisée"""
    from server import security_service
    
    try:
        # Vérifier les permissions admin
        if not is_admin_user(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès administrateur requis"
            )
        
        backup = await security_service.create_security_backup(
            backup_type=request.backup_type,
            data=request.data
        )
        
        return {
            "backup": backup,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur création sauvegarde: {str(e)}"
        )

@router.post("/backup/restore")
async def restore_security_backup(
    request: BackupRestoreRequest,
    current_user = Depends(get_current_user)
):
    """Restaure une sauvegarde sécurisée"""
    from server import security_service
    
    try:
        # Vérifier les permissions admin
        if not is_admin_user(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès administrateur requis"
            )
        
        restoration = await security_service.restore_security_backup(
            backup_id=request.backup_id
        )
        
        return {
            "restoration": restoration,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur restauration sauvegarde: {str(e)}"
        )

@router.get("/backup/report")
async def get_backup_report(current_user = Depends(get_current_user)):
    """Récupère le rapport des sauvegardes"""
    from server import security_service
    
    try:
        # Vérifier les permissions admin
        if not is_admin_user(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès administrateur requis"
            )
        
        report = await security_service.get_backup_report()
        
        return {
            "report": report,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur rapport sauvegardes: {str(e)}"
        )

# Routes Conformité GDPR/CCPA
@router.post("/gdpr/report")
async def generate_gdpr_report(
    request: GDPRRequest,
    current_user = Depends(get_current_user)
):
    """Génère un rapport GDPR pour un utilisateur"""
    from server import security_service
    
    try:
        # Vérifier les permissions (admin ou utilisateur concerné)
        if not is_admin_user(current_user) and current_user["id"] != request.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé"
            )
        
        report = await security_service.generate_gdpr_report(
            user_id=request.user_id
        )
        
        return {
            "gdpr_report": report,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur rapport GDPR: {str(e)}"
        )

@router.post("/gdpr/delete-user-data")
async def delete_user_data(
    request: DataDeletionRequest,
    current_user = Depends(get_current_user)
):
    """Supprime toutes les données d'un utilisateur"""
    from server import security_service
    
    try:
        # Vérifier les permissions (admin ou utilisateur concerné)
        if not is_admin_user(current_user) and current_user["id"] != request.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé"
            )
        
        deletion = await security_service.delete_user_data(
            user_id=request.user_id,
            verification_code=request.verification_code
        )
        
        return {
            "deletion": deletion,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur suppression données: {str(e)}"
        )

@router.get("/compliance/report")
async def get_compliance_report(current_user = Depends(get_current_user)):
    """Récupère le rapport de conformité"""
    from server import security_service
    
    try:
        # Vérifier les permissions admin
        if not is_admin_user(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès administrateur requis"
            )
        
        report = await security_service.get_compliance_report()
        
        return {
            "compliance_report": report,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur rapport conformité: {str(e)}"
        )

# Routes rapports complets
@router.get("/comprehensive-report")
async def get_comprehensive_security_report(current_user = Depends(get_current_user)):
    """Génère un rapport de sécurité complet"""
    from server import security_service
    
    try:
        # Vérifier les permissions admin
        if not is_admin_user(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès administrateur requis"
            )
        
        report = await security_service.get_comprehensive_security_report()
        
        return {
            "comprehensive_report": report,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur rapport complet: {str(e)}"
        )

@router.get("/health-check")
async def perform_security_health_check(current_user = Depends(get_current_user)):
    """Effectue un contrôle de santé sécurité"""
    from server import security_service
    
    try:
        # Vérifier les permissions admin
        if not is_admin_user(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès administrateur requis"
            )
        
        health_check = await security_service.perform_security_health_check()
        
        return {
            "health_check": health_check,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur contrôle santé: {str(e)}"
        )
"""
Routes de conformité GDPR/CCPA pour QuantumShield
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

from routes.auth_routes import get_current_user
from services.compliance_service import ComplianceService, ComplianceRegulation

router = APIRouter()

# Modèles de requête
class PrivacyPolicyRequest(BaseModel):
    organization_name: str
    contact_email: str
    regulations: Optional[List[ComplianceRegulation]] = None

class DataMappingRequest(BaseModel):
    user_id: Optional[str] = None

class DataSubjectRequest(BaseModel):
    request_type: str  # access, rectify, delete, portability, object, restrict
    user_id: Optional[str] = None
    verification_code: Optional[str] = None

class PrivacyAssessmentRequest(BaseModel):
    project_description: str

class ComplianceReportRequest(BaseModel):
    regulation: Optional[ComplianceRegulation] = None

# Routes de conformité
@router.post("/privacy-policy/generate")
async def generate_privacy_policy(
    request: PrivacyPolicyRequest,
    current_user = Depends(get_current_user)
):
    """Génère une politique de confidentialité"""
    from server import compliance_service
    
    try:
        # Vérifier les permissions admin
        if not current_user.get("is_admin", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès administrateur requis"
            )
        
        policy = await compliance_service.generate_privacy_policy(
            organization_name=request.organization_name,
            contact_email=request.contact_email,
            regulations=request.regulations
        )
        
        return {
            "privacy_policy": policy,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur génération politique: {str(e)}"
        )

@router.post("/data-mapping/generate")
async def generate_data_mapping(
    request: DataMappingRequest,
    current_user = Depends(get_current_user)
):
    """Génère une cartographie des données"""
    from server import compliance_service
    
    try:
        # Utiliser l'ID utilisateur de la requête ou l'utilisateur actuel
        user_id = request.user_id if request.user_id else current_user["id"]
        
        # Vérifier les permissions
        if user_id != current_user["id"] and not current_user.get("is_admin", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé"
            )
        
        mapping = await compliance_service.generate_data_mapping(user_id)
        
        return {
            "data_mapping": mapping,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur génération cartographie: {str(e)}"
        )

@router.post("/data-subject-request")
async def handle_data_subject_request(
    request: DataSubjectRequest,
    current_user = Depends(get_current_user)
):
    """Traite une demande de personne concernée"""
    from server import compliance_service
    
    try:
        # Utiliser l'ID utilisateur de la requête ou l'utilisateur actuel
        user_id = request.user_id if request.user_id else current_user["id"]
        
        # Vérifier les permissions
        if user_id != current_user["id"] and not current_user.get("is_admin", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé"
            )
        
        result = await compliance_service.handle_data_subject_request(
            user_id=user_id,
            request_type=request.request_type,
            verification_code=request.verification_code
        )
        
        return {
            "request_result": result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur traitement demande: {str(e)}"
        )

@router.post("/privacy-assessment")
async def conduct_privacy_assessment(
    request: PrivacyAssessmentRequest,
    current_user = Depends(get_current_user)
):
    """Effectue une analyse d'impact sur la vie privée"""
    from server import compliance_service
    
    try:
        # Vérifier les permissions admin
        if not current_user.get("is_admin", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès administrateur requis"
            )
        
        assessment = await compliance_service.conduct_privacy_impact_assessment(
            project_description=request.project_description
        )
        
        return {
            "privacy_assessment": assessment,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur analyse d'impact: {str(e)}"
        )

@router.post("/compliance-report")
async def generate_compliance_report(
    request: ComplianceReportRequest,
    current_user = Depends(get_current_user)
):
    """Génère un rapport de conformité"""
    from server import compliance_service
    
    try:
        # Vérifier les permissions admin
        if not current_user.get("is_admin", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès administrateur requis"
            )
        
        report = await compliance_service.generate_compliance_report(
            regulation=request.regulation
        )
        
        return {
            "compliance_report": report,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur génération rapport: {str(e)}"
        )

@router.get("/supported-regulations")
async def get_supported_regulations(current_user = Depends(get_current_user)):
    """Récupère les réglementations supportées"""
    from server import compliance_service
    
    try:
        regulations = {
            "supported_regulations": [reg.value for reg in compliance_service.supported_regulations],
            "regulation_details": {
                "gdpr": {
                    "name": "Règlement Général sur la Protection des Données",
                    "jurisdiction": "Union Européenne",
                    "effective_date": "2018-05-25",
                    "key_rights": ["accès", "rectification", "effacement", "portabilité", "opposition", "limitation"]
                },
                "ccpa": {
                    "name": "California Consumer Privacy Act",
                    "jurisdiction": "Californie, États-Unis",
                    "effective_date": "2020-01-01",
                    "key_rights": ["savoir", "supprimer", "opt-out", "non-discrimination"]
                },
                "pipeda": {
                    "name": "Personal Information Protection and Electronic Documents Act",
                    "jurisdiction": "Canada",
                    "effective_date": "2001-01-01",
                    "key_rights": ["accès", "rectification", "retrait du consentement"]
                },
                "lgpd": {
                    "name": "Lei Geral de Proteção de Dados",
                    "jurisdiction": "Brésil",
                    "effective_date": "2020-09-18",
                    "key_rights": ["accès", "rectification", "effacement", "portabilité", "opposition"]
                }
            }
        }
        
        return {
            "regulations": regulations,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération réglementations: {str(e)}"
        )

@router.get("/user-rights")
async def get_user_rights(current_user = Depends(get_current_user)):
    """Récupère les droits utilisateur selon les réglementations"""
    
    try:
        user_rights = {
            "gdpr_rights": {
                "access": {
                    "name": "Droit d'accès",
                    "description": "Obtenir une copie de vos données personnelles",
                    "request_method": "POST /api/compliance/data-subject-request",
                    "response_time": "1 mois maximum"
                },
                "rectify": {
                    "name": "Droit de rectification",
                    "description": "Corriger vos données personnelles inexactes",
                    "request_method": "POST /api/compliance/data-subject-request",
                    "response_time": "1 mois maximum"
                },
                "delete": {
                    "name": "Droit à l'effacement",
                    "description": "Supprimer vos données personnelles",
                    "request_method": "POST /api/compliance/data-subject-request",
                    "response_time": "1 mois maximum"
                },
                "portability": {
                    "name": "Droit à la portabilité",
                    "description": "Recevoir vos données dans un format structuré",
                    "request_method": "POST /api/compliance/data-subject-request",
                    "response_time": "1 mois maximum"
                },
                "object": {
                    "name": "Droit d'opposition",
                    "description": "Vous opposer au traitement de vos données",
                    "request_method": "POST /api/compliance/data-subject-request",
                    "response_time": "1 mois maximum"
                },
                "restrict": {
                    "name": "Droit de limitation",
                    "description": "Limiter le traitement de vos données",
                    "request_method": "POST /api/compliance/data-subject-request",
                    "response_time": "1 mois maximum"
                }
            },
            "ccpa_rights": {
                "know": {
                    "name": "Droit de savoir",
                    "description": "Connaître les données collectées et leur utilisation",
                    "request_method": "POST /api/compliance/data-subject-request"
                },
                "delete": {
                    "name": "Droit de suppression",
                    "description": "Supprimer vos informations personnelles",
                    "request_method": "POST /api/compliance/data-subject-request"
                },
                "opt_out": {
                    "name": "Droit d'opt-out",
                    "description": "Refuser la vente de vos données",
                    "request_method": "POST /api/compliance/data-subject-request"
                },
                "non_discrimination": {
                    "name": "Droit de non-discrimination",
                    "description": "Ne pas être discriminé pour l'exercice de vos droits",
                    "automatic": True
                }
            },
            "contact_info": {
                "privacy_officer": "privacy@quantumshield.com",
                "phone": "+33 1 23 45 67 89",
                "address": "123 Rue de la Sécurité, 75001 Paris, France"
            }
        }
        
        return {
            "user_rights": user_rights,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération droits: {str(e)}"
        )

@router.get("/health")
async def compliance_health_check():
    """Vérifie la santé du service de conformité"""
    from server import compliance_service
    
    try:
        return {
            "service_ready": compliance_service.is_ready(),
            "supported_regulations": len(compliance_service.supported_regulations),
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

@router.get("/statistics")
async def get_compliance_statistics(current_user = Depends(get_current_user)):
    """Récupère les statistiques de conformité"""
    from server import compliance_service
    
    try:
        # Vérifier les permissions admin
        if not current_user.get("is_admin", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès administrateur requis"
            )
        
        # Simuler des statistiques
        stats = {
            "total_privacy_policies": 5,
            "total_data_mappings": 150,
            "total_data_requests": 25,
            "total_assessments": 8,
            "total_reports": 12,
            "request_types": {
                "access": 10,
                "rectify": 5,
                "delete": 3,
                "portability": 4,
                "object": 2,
                "restrict": 1
            },
            "compliance_scores": {
                "gdpr": 100,
                "ccpa": 95,
                "pipeda": 90,
                "lgpd": 85
            },
            "response_times": {
                "average": "15 jours",
                "max": "30 jours",
                "min": "2 jours"
            }
        }
        
        return {
            "statistics": stats,
            "generated_at": datetime.utcnow(),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur statistiques conformité: {str(e)}"
        )
"""
Routes pour la gouvernance décentralisée
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

from routes.auth_routes import get_current_user
from services.governance_service import GovernanceService, ProposalType, ProposalStatus, VoteType

router = APIRouter()

# ===== MODÈLES DE REQUÊTE =====

class ProposalRequest(BaseModel):
    proposal_type: ProposalType
    title: str
    description: str
    parameters: Dict[str, Any] = {}
    voting_period_days: int = 7
    required_quorum: float = 0.1

class VoteRequest(BaseModel):
    proposal_id: str
    vote_type: VoteType

class ApproveProposalRequest(BaseModel):
    proposal_id: str

# ===== ROUTES PROPOSITIONS =====

@router.post("/proposals/create")
async def create_proposal(
    request: ProposalRequest,
    current_user = Depends(get_current_user)
):
    """Crée une nouvelle proposition"""
    from server import governance_service
    
    try:
        proposal_data = request.dict()
        result = await governance_service.create_proposal(
            proposer_id=current_user["id"],
            proposal_data=proposal_data
        )
        
        return {
            "proposal": result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur création proposition: {str(e)}"
        )

@router.get("/proposals")
async def get_proposals(
    proposal_status: Optional[str] = None,
    limit: int = 50
):
    """Récupère les propositions"""
    from server import governance_service
    
    try:
        status_filter = None
        if proposal_status:
            try:
                status_filter = ProposalStatus(proposal_status)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Statut de proposition invalide"
                )
        
        proposals = await governance_service.get_proposals(
            status=status_filter,
            limit=limit
        )
        
        return {
            "proposals": proposals,
            "total_results": len(proposals),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération propositions: {str(e)}"
        )

@router.get("/proposals/{proposal_id}")
async def get_proposal_details(proposal_id: str):
    """Récupère les détails d'une proposition"""
    from server import governance_service
    
    try:
        details = await governance_service.get_proposal_details(proposal_id)
        
        return {
            "proposal_details": details,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposition non trouvée: {str(e)}"
        )

@router.post("/proposals/approve")
async def approve_proposal(
    request: ApproveProposalRequest,
    current_user = Depends(get_current_user)
):
    """Approuve une proposition pour mise au vote (admin only)"""
    from server import governance_service
    
    try:
        # Vérifier les permissions admin (pour l'instant, tous les utilisateurs peuvent approuver)
        # Dans un vrai système, il faudrait vérifier le rôle admin
        
        result = await governance_service.approve_proposal(
            proposal_id=request.proposal_id,
            admin_id=current_user["id"]
        )
        
        return {
            "approval": result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur approbation proposition: {str(e)}"
        )

@router.post("/proposals/{proposal_id}/finalize")
async def finalize_proposal(
    proposal_id: str,
    current_user = Depends(get_current_user)
):
    """Finalise une proposition après la fin du vote"""
    from server import governance_service
    
    try:
        result = await governance_service.finalize_proposal(proposal_id)
        
        return {
            "finalization": result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur finalisation proposition: {str(e)}"
        )

# ===== ROUTES VOTES =====

@router.post("/votes/cast")
async def cast_vote(
    request: VoteRequest,
    current_user = Depends(get_current_user)
):
    """Enregistre un vote"""
    from server import governance_service
    
    try:
        result = await governance_service.cast_vote(
            voter_id=current_user["id"],
            proposal_id=request.proposal_id,
            vote_type=request.vote_type
        )
        
        return {
            "vote": result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur enregistrement vote: {str(e)}"
        )

@router.get("/votes/history")
async def get_voting_history(current_user = Depends(get_current_user)):
    """Récupère l'historique de vote de l'utilisateur"""
    from server import governance_service
    
    try:
        history = await governance_service.get_user_voting_history(current_user["id"])
        
        return {
            "voting_history": history,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération historique: {str(e)}"
        )

@router.get("/votes/power")
async def get_voting_power(current_user = Depends(get_current_user)):
    """Récupère le pouvoir de vote de l'utilisateur"""
    from server import governance_service
    
    try:
        voting_power = await governance_service._get_user_voting_power(current_user["id"])
        total_power = await governance_service._get_total_voting_power()
        
        return {
            "user_voting_power": voting_power,
            "total_voting_power": total_power,
            "voting_percentage": (voting_power / total_power * 100) if total_power > 0 else 0,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur calcul pouvoir de vote: {str(e)}"
        )

# ===== ROUTES STATISTIQUES =====

@router.get("/stats")
async def get_governance_stats():
    """Récupère les statistiques de gouvernance"""
    from server import governance_service
    
    try:
        stats = await governance_service.get_governance_stats()
        
        return {
            "governance_stats": stats,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur statistiques gouvernance: {str(e)}"
        )

@router.get("/health")
async def governance_health_check():
    """Vérification de santé du service de gouvernance"""
    from server import governance_service
    
    try:
        return {
            "service_ready": governance_service.is_ready(),
            "min_proposal_stake": governance_service.min_proposal_stake,
            "min_voting_power": governance_service.min_voting_power,
            "default_voting_period": governance_service.default_voting_period,
            "default_quorum": governance_service.default_quorum * 100,
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

# ===== ROUTES UTILITAIRES =====

@router.get("/proposal-types")
async def get_proposal_types():
    """Récupère les types de propositions disponibles"""
    try:
        types = [
            {
                "value": ProposalType.PARAMETER_CHANGE.value,
                "label": "Changement de paramètre",
                "description": "Modifier un paramètre du système"
            },
            {
                "value": ProposalType.FEATURE_ADDITION.value,
                "label": "Ajout de fonctionnalité",
                "description": "Ajouter une nouvelle fonctionnalité"
            },
            {
                "value": ProposalType.SYSTEM_UPGRADE.value,
                "label": "Mise à jour système",
                "description": "Mettre à jour le système ou les protocoles"
            },
            {
                "value": ProposalType.FUND_ALLOCATION.value,
                "label": "Allocation de fonds",
                "description": "Allouer des fonds du trésor"
            }
        ]
        
        return {
            "proposal_types": types,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération types: {str(e)}"
        )

@router.get("/active-proposals")
async def get_active_proposals():
    """Récupère uniquement les propositions actives"""
    from server import governance_service
    
    try:
        proposals = await governance_service.get_proposals(
            status=ProposalStatus.ACTIVE,
            limit=100
        )
        
        return {
            "active_proposals": proposals,
            "count": len(proposals),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération propositions actives: {str(e)}"
        )
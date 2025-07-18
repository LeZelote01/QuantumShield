"""
Routes pour les recommandations personnalisées
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Dict, Any, List
from datetime import datetime

from routes.auth_routes import get_current_user
from services.recommendations_service import RecommendationService

router = APIRouter()

# ===== MODÈLES DE REQUÊTE =====

class RecommendationActionRequest(BaseModel):
    recommendation_id: str

# ===== ROUTES PRINCIPALES =====

@router.get("/personalized")
async def get_personalized_recommendations(current_user = Depends(get_current_user)):
    """Récupère les recommandations personnalisées pour l'utilisateur"""
    from server import recommendations_service
    
    try:
        recommendations = await recommendations_service.get_personalized_recommendations(current_user["id"])
        
        return {
            "recommendations": recommendations,
            "total_count": len(recommendations),
            "generated_at": datetime.utcnow(),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur génération recommandations: {str(e)}"
        )

@router.post("/viewed")
async def mark_recommendation_viewed(
    request: RecommendationActionRequest,
    current_user = Depends(get_current_user)
):
    """Marque une recommandation comme vue"""
    from server import recommendations_service
    
    try:
        success = await recommendations_service.mark_recommendation_viewed(
            user_id=current_user["id"],
            recommendation_id=request.recommendation_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recommandation non trouvée"
            )
        
        return {
            "recommendation_id": request.recommendation_id,
            "action": "viewed",
            "timestamp": datetime.utcnow(),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur marquage vue: {str(e)}"
        )

@router.post("/clicked")
async def mark_recommendation_clicked(
    request: RecommendationActionRequest,
    current_user = Depends(get_current_user)
):
    """Marque une recommandation comme cliquée"""
    from server import recommendations_service
    
    try:
        success = await recommendations_service.mark_recommendation_clicked(
            user_id=current_user["id"],
            recommendation_id=request.recommendation_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recommandation non trouvée"
            )
        
        return {
            "recommendation_id": request.recommendation_id,
            "action": "clicked",
            "timestamp": datetime.utcnow(),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur marquage clic: {str(e)}"
        )

@router.post("/dismiss")
async def dismiss_recommendation(
    request: RecommendationActionRequest,
    current_user = Depends(get_current_user)
):
    """Ferme une recommandation"""
    from server import recommendations_service
    
    try:
        success = await recommendations_service.dismiss_recommendation(
            user_id=current_user["id"],
            recommendation_id=request.recommendation_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recommandation non trouvée"
            )
        
        return {
            "recommendation_id": request.recommendation_id,
            "action": "dismissed",
            "timestamp": datetime.utcnow(),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur fermeture recommandation: {str(e)}"
        )

@router.get("/stats")
async def get_recommendation_stats(current_user = Depends(get_current_user)):
    """Récupère les statistiques des recommandations de l'utilisateur"""
    from server import recommendations_service
    
    try:
        stats = await recommendations_service.get_recommendation_stats(current_user["id"])
        
        return {
            "recommendation_stats": stats,
            "user_id": current_user["id"],
            "generated_at": datetime.utcnow(),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération statistiques: {str(e)}"
        )

@router.get("/health")
async def recommendations_health_check():
    """Vérification de santé du service de recommandations"""
    from server import recommendations_service
    
    try:
        return {
            "service_ready": recommendations_service.is_ready(),
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

@router.get("/types")
async def get_recommendation_types():
    """Récupère les types de recommandations disponibles"""
    try:
        from services.recommendations_service import RecommendationType, RecommendationPriority
        
        types = [
            {
                "value": RecommendationType.SECURITY.value,
                "label": "Sécurité",
                "description": "Recommandations pour améliorer la sécurité",
                "color": "red"
            },
            {
                "value": RecommendationType.ECONOMY.value,
                "label": "Économie",
                "description": "Opportunités économiques et d'investissement",
                "color": "green"
            },
            {
                "value": RecommendationType.DEVICES.value,
                "label": "Dispositifs",
                "description": "Gestion et optimisation des dispositifs IoT",
                "color": "blue"
            },
            {
                "value": RecommendationType.OPTIMIZATION.value,
                "label": "Optimisation",
                "description": "Améliorations de performance",
                "color": "yellow"
            },
            {
                "value": RecommendationType.EDUCATION.value,
                "label": "Éducation",
                "description": "Apprentissage et formation",
                "color": "purple"
            },
            {
                "value": RecommendationType.UPGRADE.value,
                "label": "Mise à niveau",
                "description": "Nouvelles fonctionnalités et améliorations",
                "color": "indigo"
            }
        ]
        
        priorities = [
            {
                "value": RecommendationPriority.HIGH.value,
                "label": "Haute",
                "description": "Recommandations urgentes",
                "color": "red"
            },
            {
                "value": RecommendationPriority.MEDIUM.value,
                "label": "Moyenne",
                "description": "Recommandations importantes",
                "color": "yellow"
            },
            {
                "value": RecommendationPriority.LOW.value,
                "label": "Basse",
                "description": "Recommandations optionnelles",
                "color": "green"
            }
        ]
        
        return {
            "recommendation_types": types,
            "recommendation_priorities": priorities,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération types: {str(e)}"
        )

@router.get("/refresh")
async def refresh_recommendations(current_user = Depends(get_current_user)):
    """Force la régénération des recommandations"""
    from server import recommendations_service
    
    try:
        recommendations = await recommendations_service.get_personalized_recommendations(current_user["id"])
        
        return {
            "recommendations": recommendations,
            "total_count": len(recommendations),
            "refreshed_at": datetime.utcnow(),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur rafraîchissement recommandations: {str(e)}"
        )
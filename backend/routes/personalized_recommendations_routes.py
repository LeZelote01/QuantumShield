"""
Routes pour les recommandations personnalisées
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

from routes.auth_routes import get_current_user

router = APIRouter()

# Modèles de requête
class RecommendationAction(BaseModel):
    recommendation_id: str
    action_type: str  # "read", "actioned", "dismissed"

class RecommendationFeedback(BaseModel):
    recommendation_id: str
    useful: bool
    comment: Optional[str] = None

# Variables globales pour les services (injectées depuis server.py)
personalized_recommendations_service = None

def init_recommendations_service(service):
    global personalized_recommendations_service
    personalized_recommendations_service = service

@router.get("/")
async def get_personalized_recommendations(
    limit: int = 10,
    include_read: bool = False,
    current_user = Depends(get_current_user)
):
    """Récupère les recommandations personnalisées pour l'utilisateur"""
    if not personalized_recommendations_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service de recommandations non disponible"
        )
    
    try:
        # Récupérer les recommandations
        recommendations_data = await personalized_recommendations_service.get_personalized_recommendations(
            user_id=current_user.id,
            limit=limit
        )
        
        # Filtrer les recommandations lues si nécessaire
        if not include_read:
            # Récupérer les recommandations existantes en base pour vérifier le statut "read"
            existing_recs = await personalized_recommendations_service.db.user_recommendations.find({
                "user_id": current_user.id,
                "read": {"$ne": True}
            }).to_list(None)
            
            existing_ids = {rec["id"] for rec in existing_recs}
            recommendations_data["recommendations"] = [
                rec for rec in recommendations_data["recommendations"] 
                if rec["id"] in existing_ids
            ]
        
        return {
            "success": True,
            "data": recommendations_data,
            "message": f"Recommandations générées pour {current_user.username}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des recommandations: {str(e)}"
        )

@router.get("/analytics")
async def get_recommendations_analytics(current_user = Depends(get_current_user)):
    """Récupère les analytics des recommandations pour l'utilisateur"""
    if not personalized_recommendations_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service de recommandations non disponible"
        )
    
    try:
        analytics = await personalized_recommendations_service.get_recommendation_analytics(
            user_id=current_user.id
        )
        
        return {
            "success": True,
            "data": analytics,
            "message": "Analytics des recommandations récupérées"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des analytics: {str(e)}"
        )

@router.post("/action")
async def handle_recommendation_action(
    action: RecommendationAction,
    current_user = Depends(get_current_user)
):
    """Gère les actions sur les recommandations (lue, actionnée, etc.)"""
    if not personalized_recommendations_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service de recommandations non disponible"
        )
    
    try:
        success = False
        
        if action.action_type == "read":
            success = await personalized_recommendations_service.mark_recommendation_as_read(
                user_id=current_user.id,
                recommendation_id=action.recommendation_id
            )
        elif action.action_type == "actioned":
            success = await personalized_recommendations_service.mark_recommendation_as_actioned(
                user_id=current_user.id,
                recommendation_id=action.recommendation_id
            )
        elif action.action_type == "dismissed":
            # Marquer comme lue et archivée
            success = await personalized_recommendations_service.mark_recommendation_as_read(
                user_id=current_user.id,
                recommendation_id=action.recommendation_id
            )
            # Ajouter un flag "dismissed" 
            await personalized_recommendations_service.db.user_recommendations.update_one(
                {"user_id": current_user.id, "id": action.recommendation_id},
                {"$set": {"dismissed": True, "dismissed_at": datetime.utcnow()}}
            )
        
        if success:
            return {
                "success": True,
                "message": f"Action '{action.action_type}' appliquée avec succès"
            }
        else:
            return {
                "success": False,
                "message": "Recommandation non trouvée ou action échouée"
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'action sur la recommandation: {str(e)}"
        )

@router.post("/feedback")
async def submit_recommendation_feedback(
    feedback: RecommendationFeedback,
    current_user = Depends(get_current_user)
):
    """Soumet un feedback sur une recommandation"""
    if not personalized_recommendations_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service de recommandations non disponible"
        )
    
    try:
        # Enregistrer le feedback
        feedback_doc = {
            "user_id": current_user.id,
            "recommendation_id": feedback.recommendation_id,
            "useful": feedback.useful,
            "comment": feedback.comment,
            "submitted_at": datetime.utcnow()
        }
        
        await personalized_recommendations_service.db.recommendation_feedback.insert_one(feedback_doc)
        
        return {
            "success": True,
            "message": "Feedback enregistré avec succès"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'enregistrement du feedback: {str(e)}"
        )

@router.get("/types")
async def get_recommendation_types():
    """Récupère les types de recommandations disponibles"""
    try:
        types = [
            {
                "type": "security",
                "name": "Sécurité",
                "description": "Recommandations pour renforcer la sécurité"
            },
            {
                "type": "performance",
                "name": "Performance",
                "description": "Optimisations de performance"
            },
            {
                "type": "cost_optimization",
                "name": "Optimisation des coûts",
                "description": "Économies de tokens et réduction des coûts"
            },
            {
                "type": "device_management",
                "name": "Gestion des dispositifs",
                "description": "Amélioration de la gestion des dispositifs IoT"
            },
            {
                "type": "energy_efficiency",
                "name": "Efficacité énergétique",
                "description": "Optimisations de la consommation énergétique"
            },
            {
                "type": "network_optimization",
                "name": "Optimisation réseau",
                "description": "Amélioration des performances réseau"
            },
            {
                "type": "crypto_optimization",
                "name": "Optimisation cryptographique",
                "description": "Optimisations des opérations cryptographiques"
            }
        ]
        
        return {
            "success": True,
            "data": types,
            "message": "Types de recommandations récupérés"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des types: {str(e)}"
        )

@router.get("/by-type/{recommendation_type}")
async def get_recommendations_by_type(
    recommendation_type: str,
    limit: int = 10,
    current_user = Depends(get_current_user)
):
    """Récupère les recommandations d'un type spécifique"""
    if not personalized_recommendations_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service de recommandations non disponible"
        )
    
    try:
        # Récupérer les recommandations filtrées par type
        recommendations = await personalized_recommendations_service.db.user_recommendations.find({
            "user_id": current_user.id,
            "type": recommendation_type,
            "expires_at": {"$gte": datetime.utcnow()}
        }).sort("created_at", -1).limit(limit).to_list(None)
        
        return {
            "success": True,
            "data": {
                "type": recommendation_type,
                "recommendations": recommendations,
                "count": len(recommendations)
            },
            "message": f"Recommandations de type '{recommendation_type}' récupérées"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des recommandations: {str(e)}"
        )

@router.get("/priority/{priority_level}")
async def get_recommendations_by_priority(
    priority_level: str,
    limit: int = 10,
    current_user = Depends(get_current_user)
):
    """Récupère les recommandations par niveau de priorité"""
    if not personalized_recommendations_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service de recommandations non disponible"
        )
    
    try:
        # Valider le niveau de priorité
        valid_priorities = ["low", "medium", "high", "critical"]
        if priority_level not in valid_priorities:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Niveau de priorité invalide. Valeurs acceptées: {valid_priorities}"
            )
        
        # Récupérer les recommandations filtrées par priorité
        recommendations = await personalized_recommendations_service.db.user_recommendations.find({
            "user_id": current_user.id,
            "priority": priority_level,
            "expires_at": {"$gte": datetime.utcnow()}
        }).sort("created_at", -1).limit(limit).to_list(None)
        
        return {
            "success": True,
            "data": {
                "priority": priority_level,
                "recommendations": recommendations,
                "count": len(recommendations)
            },
            "message": f"Recommandations de priorité '{priority_level}' récupérées"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des recommandations: {str(e)}"
        )

@router.delete("/{recommendation_id}")
async def delete_recommendation(
    recommendation_id: str,
    current_user = Depends(get_current_user)
):
    """Supprime une recommandation spécifique"""
    if not personalized_recommendations_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service de recommandations non disponible"
        )
    
    try:
        result = await personalized_recommendations_service.db.user_recommendations.delete_one({
            "user_id": current_user.id,
            "id": recommendation_id
        })
        
        if result.deleted_count > 0:
            return {
                "success": True,
                "message": "Recommandation supprimée avec succès"
            }
        else:
            return {
                "success": False,
                "message": "Recommandation non trouvée"
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la suppression: {str(e)}"
        )

@router.get("/health")
async def get_recommendations_health():
    """Vérifie la santé du service de recommandations"""
    if not personalized_recommendations_service:
        return {
            "healthy": False,
            "message": "Service de recommandations non initialisé"
        }
    
    try:
        is_ready = personalized_recommendations_service.is_ready()
        return {
            "healthy": is_ready,
            "message": "Service de recommandations opérationnel" if is_ready else "Service en cours d'initialisation"
        }
        
    except Exception as e:
        return {
            "healthy": False,
            "message": f"Erreur service: {str(e)}"
        }
"""
Routes pour la marketplace de services
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import uuid

# Import du service (sera injecté par le serveur principal)
marketplace_service = None

router = APIRouter()
logger = logging.getLogger(__name__)

# ==============================
# Modèles Pydantic
# ==============================

class ServicePublish(BaseModel):
    name: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=50, max_length=1000)
    category: str = Field(..., pattern="^(iot_management|security|analytics|automation|monitoring|communication|storage|machine_learning|blockchain|energy)$")
    service_type: str = Field(..., pattern="^(application|api|widget|plugin|template|library)$")
    pricing_model: str = Field(..., pattern="^(free|freemium|subscription|pay_per_use|one_time)$")
    price: float = Field(default=0.0, ge=0.0)
    features: List[str] = Field(..., min_items=1, max_items=10)
    provider_id: str
    version: str = Field(default="1.0.0")
    premium_price: Optional[float] = Field(default=None, ge=0.0)
    source_code: Optional[str] = None
    documentation: Optional[str] = None
    requirements: Optional[List[str]] = []
    tags: Optional[List[str]] = []

class ServiceSubscribe(BaseModel):
    user_id: str
    service_id: str

class ServiceReview(BaseModel):
    service_id: str
    user_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(..., max_length=500)

# ==============================
# Endpoints de gestion des services
# ==============================

@router.post("/services/publish")
async def publish_service(service_data: ServicePublish):
    """Publie un nouveau service sur la marketplace"""
    try:
        if not marketplace_service:
            raise HTTPException(status_code=503, detail="Service marketplace non disponible")
        
        from services.marketplace_service import ServiceCategory, ServiceType, PricingModel
        
        result = await marketplace_service.publish_service(
            name=service_data.name,
            description=service_data.description,
            category=ServiceCategory(service_data.category),
            service_type=ServiceType(service_data.service_type),
            pricing_model=PricingModel(service_data.pricing_model),
            price=service_data.price,
            features=service_data.features,
            provider_id=service_data.provider_id,
            version=service_data.version,
            premium_price=service_data.premium_price,
            source_code=service_data.source_code,
            documentation=service_data.documentation,
            requirements=service_data.requirements,
            tags=service_data.tags
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur publication service: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/services/search")
async def search_services(
    query: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    service_type: Optional[str] = Query(None),
    pricing_model: Optional[str] = Query(None),
    max_price: Optional[float] = Query(None),
    tags: Optional[str] = Query(None),
    sort_by: str = Query("relevance", regex="^(relevance|price_asc|price_desc|rating|newest|popular)$"),
    limit: int = Query(20, ge=1, le=100)
):
    """Recherche des services dans la marketplace"""
    try:
        if not marketplace_service:
            raise HTTPException(status_code=503, detail="Service marketplace non disponible")
        
        from services.marketplace_service import ServiceCategory, ServiceType, PricingModel
        
        # Convertir les paramètres
        cat = ServiceCategory(category) if category else None
        stype = ServiceType(service_type) if service_type else None
        pricing = PricingModel(pricing_model) if pricing_model else None
        tag_list = tags.split(",") if tags else None
        
        services = await marketplace_service.search_services(
            query=query,
            category=cat,
            service_type=stype,
            pricing_model=pricing,
            max_price=max_price,
            tags=tag_list,
            sort_by=sort_by,
            limit=limit
        )
        
        return {
            "services": services,
            "count": len(services),
            "query": query,
            "filters": {
                "category": category,
                "service_type": service_type,
                "pricing_model": pricing_model,
                "max_price": max_price,
                "tags": tag_list
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur recherche services: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/services/{service_id}")
async def get_service_details(service_id: str):
    """Récupère les détails d'un service"""
    try:
        if not marketplace_service:
            raise HTTPException(status_code=503, detail="Service marketplace non disponible")
        
        service = await marketplace_service.get_service_details(service_id)
        
        if not service:
            raise HTTPException(status_code=404, detail="Service non trouvé")
        
        return service
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération détails service: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/services")
async def list_all_services(
    status: Optional[str] = Query("active"),
    category: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100)
):
    """Liste tous les services actifs"""
    try:
        if not marketplace_service:
            raise HTTPException(status_code=503, detail="Service marketplace non disponible")
        
        from services.marketplace_service import ServiceCategory
        
        cat = ServiceCategory(category) if category else None
        
        services = await marketplace_service.search_services(
            category=cat,
            limit=limit
        )
        
        return {
            "services": services,
            "count": len(services)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur liste services: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================
# Endpoints de subscription
# ==============================

@router.post("/services/subscribe")
async def subscribe_to_service(subscription_data: ServiceSubscribe):
    """S'abonne à un service"""
    try:
        if not marketplace_service:
            raise HTTPException(status_code=503, detail="Service marketplace non disponible")
        
        result = await marketplace_service.subscribe_to_service(
            user_id=subscription_data.user_id,
            service_id=subscription_data.service_id
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur abonnement service: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/subscriptions")
async def get_user_subscriptions(user_id: str):
    """Récupère les abonnements d'un utilisateur"""
    try:
        if not marketplace_service:
            raise HTTPException(status_code=503, detail="Service marketplace non disponible")
        
        subscriptions = await marketplace_service.get_user_subscriptions(user_id)
        
        return {
            "subscriptions": subscriptions,
            "count": len(subscriptions)
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération abonnements: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/subscriptions/{subscription_id}")
async def cancel_subscription(subscription_id: str):
    """Annule un abonnement"""
    try:
        if not marketplace_service:
            raise HTTPException(status_code=503, detail="Service marketplace non disponible")
        
        # Marquer l'abonnement comme annulé
        result = await marketplace_service.db.service_subscriptions.update_one(
            {"subscription_id": subscription_id},
            {"$set": {"status": "cancelled", "cancelled_at": datetime.utcnow()}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Abonnement non trouvé")
        
        return {"message": "Abonnement annulé avec succès"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur annulation abonnement: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================
# Endpoints de reviews
# ==============================

@router.post("/services/review")
async def add_service_review(review_data: ServiceReview):
    """Ajoute une review à un service"""
    try:
        if not marketplace_service:
            raise HTTPException(status_code=503, detail="Service marketplace non disponible")
        
        # Vérifier que le service existe
        service = await marketplace_service.get_service_details(review_data.service_id)
        if not service:
            raise HTTPException(status_code=404, detail="Service non trouvé")
        
        # Vérifier que l'utilisateur n'a pas déjà reviewé ce service
        existing_review = await marketplace_service.db.service_user_reviews.find_one({
            "service_id": review_data.service_id,
            "user_id": review_data.user_id
        })
        
        if existing_review:
            raise HTTPException(status_code=400, detail="Vous avez déjà reviewé ce service")
        
        # Créer la review
        review_entry = {
            "review_id": str(uuid.uuid4()),
            "service_id": review_data.service_id,
            "user_id": review_data.user_id,
            "rating": review_data.rating,
            "comment": review_data.comment,
            "created_at": datetime.utcnow()
        }
        
        await marketplace_service.db.service_user_reviews.insert_one(review_entry)
        
        # Mettre à jour la note moyenne du service
        await _update_service_rating(review_data.service_id)
        
        return {
            "message": "Review ajoutée avec succès",
            "review_id": review_entry["review_id"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur ajout review: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/services/{service_id}/reviews")
async def get_service_reviews(service_id: str, limit: int = Query(10, ge=1, le=50)):
    """Récupère les reviews d'un service"""
    try:
        if not marketplace_service:
            raise HTTPException(status_code=503, detail="Service marketplace non disponible")
        
        reviews = await marketplace_service.db.service_user_reviews.find(
            {"service_id": service_id}
        ).sort("created_at", -1).limit(limit).to_list(None)
        
        # Nettoyer les données
        result = []
        for review in reviews:
            review.pop("_id", None)
            review.pop("user_id", None)  # Anonymiser
            result.append(review)
        
        return {
            "reviews": result,
            "count": len(result)
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération reviews: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================
# Endpoints d'administration
# ==============================

@router.get("/stats")
async def get_marketplace_stats():
    """Récupère les statistiques de la marketplace"""
    try:
        if not marketplace_service:
            raise HTTPException(status_code=503, detail="Service marketplace non disponible")
        
        stats = await marketplace_service.get_marketplace_stats()
        
        return stats
        
    except Exception as e:
        logger.error(f"Erreur récupération statistiques: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories")
async def get_service_categories():
    """Récupère les catégories de services disponibles"""
    return {
        "categories": [
            {"id": "iot_management", "name": "IoT Management", "description": "Gestion et orchestration des dispositifs IoT"},
            {"id": "security", "name": "Security", "description": "Solutions de sécurité et cryptographie"},
            {"id": "analytics", "name": "Analytics", "description": "Analyse de données et reporting"},
            {"id": "automation", "name": "Automation", "description": "Automatisation et workflows"},
            {"id": "monitoring", "name": "Monitoring", "description": "Surveillance et alertes"},
            {"id": "communication", "name": "Communication", "description": "Protocoles et messaging"},
            {"id": "storage", "name": "Storage", "description": "Stockage et gestion des données"},
            {"id": "machine_learning", "name": "Machine Learning", "description": "IA et apprentissage automatique"},
            {"id": "blockchain", "name": "Blockchain", "description": "Technologies blockchain et crypto"},
            {"id": "energy", "name": "Energy", "description": "Gestion énergétique et optimisation"}
        ]
    }

@router.get("/config")
async def get_marketplace_config():
    """Récupère la configuration de la marketplace"""
    try:
        if not marketplace_service:
            raise HTTPException(status_code=503, detail="Service marketplace non disponible")
        
        config = marketplace_service.config.copy()
        
        return {
            "config": config,
            "service_status": "active" if marketplace_service.is_ready() else "inactive"
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération config marketplace: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================
# Utilitaires
# ==============================

async def _update_service_rating(service_id: str):
    """Met à jour la note moyenne d'un service"""
    try:
        if not marketplace_service:
            return
        
        # Calculer la moyenne des notes
        reviews = await marketplace_service.db.service_user_reviews.find(
            {"service_id": service_id}
        ).to_list(None)
        
        if reviews:
            avg_rating = sum(r["rating"] for r in reviews) / len(reviews)
            review_count = len(reviews)
            
            # Mettre à jour le service
            await marketplace_service.db.marketplace_services.update_one(
                {"service_id": service_id},
                {"$set": {
                    "rating": round(avg_rating, 1),
                    "review_count": review_count
                }}
            )
        
    except Exception as e:
        logger.error(f"Erreur mise à jour note: {str(e)}")
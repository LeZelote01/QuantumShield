"""
Routes pour les tableaux de bord personnalisables
"""

from fastapi import APIRouter, HTTPException, Depends, status, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

from routes.auth_routes import get_current_user
from services.personalizable_dashboard_service import DashboardConfig, WidgetConfig

router = APIRouter()

# Modèles de requête
class CreateDashboardRequest(BaseModel):
    name: str
    description: Optional[str] = None
    is_default: bool = False
    layout: Dict[str, Any] = Field(default_factory=lambda: {"columns": 3, "rows": 4})
    theme: str = "default"
    auto_refresh: bool = True
    refresh_interval: int = 30

class UpdateDashboardRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_default: Optional[bool] = None
    layout: Optional[Dict[str, Any]] = None
    theme: Optional[str] = None
    auto_refresh: Optional[bool] = None
    refresh_interval: Optional[int] = None

class AddWidgetRequest(BaseModel):
    widget_type: str
    title: str
    size: str = "medium"
    position: Dict[str, int] = Field(default_factory=lambda: {"x": 0, "y": 0})
    settings: Dict[str, Any] = Field(default_factory=dict)
    refresh_interval: int = 60

class UpdateWidgetRequest(BaseModel):
    title: Optional[str] = None
    size: Optional[str] = None
    position: Optional[Dict[str, int]] = None
    settings: Optional[Dict[str, Any]] = None
    refresh_interval: Optional[int] = None
    enabled: Optional[bool] = None

# Variables globales pour les services (injectées depuis server.py)
personalizable_dashboard_service = None

def init_dashboard_service(service):
    global personalizable_dashboard_service
    personalizable_dashboard_service = service

@router.get("/")
async def get_user_dashboards(current_user = Depends(get_current_user)):
    """Récupère tous les dashboards de l'utilisateur"""
    if not personalizable_dashboard_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service de dashboards non disponible"
        )
    
    try:
        dashboards = await personalizable_dashboard_service.get_user_dashboards(current_user.id)
        
        return {
            "success": True,
            "data": dashboards,
            "message": f"Dashboards récupérés pour {current_user.username}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des dashboards: {str(e)}"
        )

@router.post("/")
async def create_dashboard(
    request: CreateDashboardRequest,
    current_user = Depends(get_current_user)
):
    """Crée un nouveau dashboard"""
    if not personalizable_dashboard_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service de dashboards non disponible"
        )
    
    try:
        dashboard_config = DashboardConfig(
            name=request.name,
            description=request.description,
            is_default=request.is_default,
            layout=request.layout,
            theme=request.theme,
            auto_refresh=request.auto_refresh,
            refresh_interval=request.refresh_interval
        )
        
        result = await personalizable_dashboard_service.create_dashboard(
            user_id=current_user.id,
            dashboard_config=dashboard_config
        )
        
        if result["success"]:
            return {
                "success": True,
                "data": {"dashboard_id": result["dashboard_id"]},
                "message": "Dashboard créé avec succès"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Erreur lors de la création")
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création du dashboard: {str(e)}"
        )

@router.get("/{dashboard_id}")
async def get_dashboard(
    dashboard_id: str,
    current_user = Depends(get_current_user)
):
    """Récupère un dashboard spécifique"""
    if not personalizable_dashboard_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service de dashboards non disponible"
        )
    
    try:
        dashboard = await personalizable_dashboard_service.get_dashboard(
            user_id=current_user.id,
            dashboard_id=dashboard_id
        )
        
        if not dashboard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard non trouvé"
            )
        
        return {
            "success": True,
            "data": dashboard,
            "message": "Dashboard récupéré avec succès"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération du dashboard: {str(e)}"
        )

@router.get("/{dashboard_id}/data")
async def get_dashboard_data(
    dashboard_id: str,
    current_user = Depends(get_current_user)
):
    """Récupère les données d'un dashboard avec tous ses widgets"""
    if not personalizable_dashboard_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service de dashboards non disponible"
        )
    
    try:
        dashboard_data = await personalizable_dashboard_service.get_dashboard_data(
            user_id=current_user.id,
            dashboard_id=dashboard_id
        )
        
        if not dashboard_data["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=dashboard_data.get("error", "Dashboard non trouvé")
            )
        
        return {
            "success": True,
            "data": dashboard_data,
            "message": "Données du dashboard récupérées avec succès"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des données: {str(e)}"
        )

@router.put("/{dashboard_id}")
async def update_dashboard(
    dashboard_id: str,
    request: UpdateDashboardRequest,
    current_user = Depends(get_current_user)
):
    """Met à jour un dashboard"""
    if not personalizable_dashboard_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service de dashboards non disponible"
        )
    
    try:
        # Préparer les mises à jour
        updates = {}
        for field, value in request.dict(exclude_unset=True).items():
            if value is not None:
                updates[field] = value
        
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Aucune mise à jour fournie"
            )
        
        success = await personalizable_dashboard_service.update_dashboard(
            user_id=current_user.id,
            dashboard_id=dashboard_id,
            updates=updates
        )
        
        if success:
            return {
                "success": True,
                "message": "Dashboard mis à jour avec succès"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard non trouvé ou mise à jour échouée"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la mise à jour du dashboard: {str(e)}"
        )

@router.delete("/{dashboard_id}")
async def delete_dashboard(
    dashboard_id: str,
    current_user = Depends(get_current_user)
):
    """Supprime un dashboard"""
    if not personalizable_dashboard_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service de dashboards non disponible"
        )
    
    try:
        success = await personalizable_dashboard_service.delete_dashboard(
            user_id=current_user.id,
            dashboard_id=dashboard_id
        )
        
        if success:
            return {
                "success": True,
                "message": "Dashboard supprimé avec succès"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Impossible de supprimer le dashboard (dernier dashboard ou non trouvé)"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la suppression du dashboard: {str(e)}"
        )

@router.post("/{dashboard_id}/widgets")
async def add_widget_to_dashboard(
    dashboard_id: str,
    request: AddWidgetRequest,
    current_user = Depends(get_current_user)
):
    """Ajoute un widget à un dashboard"""
    if not personalizable_dashboard_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service de dashboards non disponible"
        )
    
    try:
        widget_config = WidgetConfig(
            widget_type=request.widget_type,
            title=request.title,
            size=request.size,
            position=request.position,
            settings=request.settings,
            refresh_interval=request.refresh_interval
        )
        
        success = await personalizable_dashboard_service.add_widget_to_dashboard(
            user_id=current_user.id,
            dashboard_id=dashboard_id,
            widget_config=widget_config
        )
        
        if success:
            return {
                "success": True,
                "data": {"widget_id": widget_config.widget_id},
                "message": "Widget ajouté avec succès"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard non trouvé ou ajout échoué"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'ajout du widget: {str(e)}"
        )

@router.put("/{dashboard_id}/widgets/{widget_id}")
async def update_widget_in_dashboard(
    dashboard_id: str,
    widget_id: str,
    request: UpdateWidgetRequest,
    current_user = Depends(get_current_user)
):
    """Met à jour un widget dans un dashboard"""
    if not personalizable_dashboard_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service de dashboards non disponible"
        )
    
    try:
        # Préparer les mises à jour
        updates = {}
        for field, value in request.dict(exclude_unset=True).items():
            if value is not None:
                updates[field] = value
        
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Aucune mise à jour fournie"
            )
        
        success = await personalizable_dashboard_service.update_widget_in_dashboard(
            user_id=current_user.id,
            dashboard_id=dashboard_id,
            widget_id=widget_id,
            updates=updates
        )
        
        if success:
            return {
                "success": True,
                "message": "Widget mis à jour avec succès"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard ou widget non trouvé"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la mise à jour du widget: {str(e)}"
        )

@router.delete("/{dashboard_id}/widgets/{widget_id}")
async def remove_widget_from_dashboard(
    dashboard_id: str,
    widget_id: str,
    current_user = Depends(get_current_user)
):
    """Supprime un widget d'un dashboard"""
    if not personalizable_dashboard_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service de dashboards non disponible"
        )
    
    try:
        success = await personalizable_dashboard_service.remove_widget_from_dashboard(
            user_id=current_user.id,
            dashboard_id=dashboard_id,
            widget_id=widget_id
        )
        
        if success:
            return {
                "success": True,
                "message": "Widget supprimé avec succès"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard ou widget non trouvé"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la suppression du widget: {str(e)}"
        )

@router.get("/widgets/types")
async def get_available_widget_types():
    """Récupère les types de widgets disponibles"""
    try:
        widget_types = [
            {
                "type": "device_status",
                "name": "Statut des Dispositifs",
                "description": "Aperçu du statut de vos dispositifs IoT",
                "sizes": ["small", "medium", "large"]
            },
            {
                "type": "token_balance",
                "name": "Solde QS",
                "description": "Votre solde de tokens QuantumShield",
                "sizes": ["small", "medium"]
            },
            {
                "type": "security_alerts",
                "name": "Alertes de Sécurité",
                "description": "Alertes de sécurité récentes",
                "sizes": ["medium", "large", "wide"]
            },
            {
                "type": "network_stats",
                "name": "Statistiques Réseau",
                "description": "Statistiques de la blockchain et du réseau",
                "sizes": ["medium", "large"]
            },
            {
                "type": "energy_consumption",
                "name": "Consommation Énergétique",
                "description": "Monitoring de la consommation énergétique",
                "sizes": ["medium", "large", "full"]
            },
            {
                "type": "mining_stats",
                "name": "Statistiques Mining",
                "description": "Vos statistiques de mining",
                "sizes": ["small", "medium", "large"]
            },
            {
                "type": "recent_activity",
                "name": "Activité Récente",
                "description": "Votre activité récente sur la plateforme",
                "sizes": ["medium", "large", "wide"]
            },
            {
                "type": "performance_metrics",
                "name": "Métriques de Performance",
                "description": "Métriques de performance du système",
                "sizes": ["medium", "large"]
            },
            {
                "type": "crypto_operations",
                "name": "Opérations Cryptographiques",
                "description": "Historique des opérations cryptographiques",
                "sizes": ["medium", "large", "wide"]
            },
            {
                "type": "anomaly_detection",
                "name": "Détection d'Anomalies",
                "description": "Anomalies détectées sur vos dispositifs",
                "sizes": ["medium", "large", "wide"]
            },
            {
                "type": "recommendations",
                "name": "Recommandations",
                "description": "Recommandations personnalisées",
                "sizes": ["medium", "large", "wide"]
            },
            {
                "type": "custom_chart",
                "name": "Graphique Personnalisé",
                "description": "Créez vos propres graphiques",
                "sizes": ["medium", "large", "full"]
            }
        ]
        
        return {
            "success": True,
            "data": widget_types,
            "message": "Types de widgets récupérés"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des types: {str(e)}"
        )

@router.get("/themes")
async def get_available_themes():
    """Récupère les thèmes disponibles pour les dashboards"""
    try:
        themes = [
            {
                "id": "default",
                "name": "Par défaut",
                "description": "Thème par défaut de QuantumShield",
                "colors": {
                    "primary": "#3B82F6",
                    "secondary": "#10B981",
                    "background": "#F9FAFB",
                    "surface": "#FFFFFF"
                }
            },
            {
                "id": "dark",
                "name": "Sombre",
                "description": "Thème sombre pour une utilisation en faible luminosité",
                "colors": {
                    "primary": "#60A5FA",
                    "secondary": "#34D399",
                    "background": "#111827",
                    "surface": "#1F2937"
                }
            },
            {
                "id": "high_contrast",
                "name": "Contraste Élevé",
                "description": "Thème à contraste élevé pour une meilleure accessibilité",
                "colors": {
                    "primary": "#000000",
                    "secondary": "#FFFFFF",
                    "background": "#FFFFFF",
                    "surface": "#F3F4F6"
                }
            },
            {
                "id": "quantum",
                "name": "Quantum",
                "description": "Thème inspiré de la physique quantique",
                "colors": {
                    "primary": "#8B5CF6",
                    "secondary": "#EC4899",
                    "background": "#0F0F23",
                    "surface": "#1E1E3F"
                }
            }
        ]
        
        return {
            "success": True,
            "data": themes,
            "message": "Thèmes disponibles récupérés"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des thèmes: {str(e)}"
        )

@router.get("/health")
async def get_dashboard_service_health():
    """Vérifie la santé du service de dashboards"""
    if not personalizable_dashboard_service:
        return {
            "healthy": False,
            "message": "Service de dashboards non initialisé"
        }
    
    try:
        is_ready = personalizable_dashboard_service.is_ready()
        return {
            "healthy": is_ready,
            "message": "Service de dashboards opérationnel" if is_ready else "Service en cours d'initialisation"
        }
        
    except Exception as e:
        return {
            "healthy": False,
            "message": f"Erreur service: {str(e)}"
        }
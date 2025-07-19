"""
Routes pour AI Analytics et ML
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from routes.auth_routes import get_current_user
from services.ai_analytics_service import AIAnalyticsService, AnomalyType, PredictionType

router = APIRouter()

# Modèles de requête
class DeviceAnomalyRequest(BaseModel):
    device_id: str
    time_window_hours: int = 24

class NetworkAnomalyRequest(BaseModel):
    time_window_hours: int = 6

class EnergyAnomalyRequest(BaseModel):
    time_window_hours: int = 12

class FailurePredictionRequest(BaseModel):
    device_id: str
    prediction_horizon_days: int = 7

class EnergyPredictionRequest(BaseModel):
    prediction_horizon_days: int = 1

class EnergyOptimizationRequest(BaseModel):
    target_reduction: float = 0.15

# Routes de détection d'anomalies
@router.post("/anomalies/device")
async def detect_device_anomalies(
    request: DeviceAnomalyRequest,
    current_user = Depends(get_current_user)
):
    """Détecte les anomalies comportementales d'un dispositif"""
    from server import ai_analytics_service
    
    try:
        time_window = timedelta(hours=request.time_window_hours)
        
        result = await ai_analytics_service.detect_device_anomalies(
            device_id=request.device_id,
            time_window=time_window
        )
        
        return {
            "anomaly_detection": result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur détection anomalies dispositif: {str(e)}"
        )

@router.post("/anomalies/network")
async def detect_network_anomalies(
    request: NetworkAnomalyRequest,
    current_user = Depends(get_current_user)
):
    """Détecte les anomalies du trafic réseau"""
    from server import ai_analytics_service
    
    try:
        time_window = timedelta(hours=request.time_window_hours)
        
        result = await ai_analytics_service.detect_network_anomalies(
            time_window=time_window
        )
        
        return {
            "anomaly_detection": result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur détection anomalies réseau: {str(e)}"
        )

@router.post("/anomalies/energy")
async def detect_energy_anomalies(
    request: EnergyAnomalyRequest,
    current_user = Depends(get_current_user)
):
    """Détecte les anomalies de consommation énergétique"""
    from server import ai_analytics_service
    
    try:
        time_window = timedelta(hours=request.time_window_hours)
        
        result = await ai_analytics_service.detect_energy_anomalies(
            time_window=time_window
        )
        
        return {
            "anomaly_detection": result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur détection anomalies énergétiques: {str(e)}"
        )

# Routes de prédiction
@router.post("/predictions/device-failure")
async def predict_device_failure(
    request: FailurePredictionRequest,
    current_user = Depends(get_current_user)
):
    """Prédit la probabilité de panne d'un dispositif"""
    from server import ai_analytics_service
    
    try:
        prediction_horizon = timedelta(days=request.prediction_horizon_days)
        
        result = await ai_analytics_service.predict_device_failure(
            device_id=request.device_id,
            prediction_horizon=prediction_horizon
        )
        
        return {
            "failure_prediction": result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur prédiction panne: {str(e)}"
        )

@router.post("/predictions/energy-usage")
async def predict_energy_usage(
    request: EnergyPredictionRequest,
    current_user = Depends(get_current_user)
):
    """Prédit la consommation énergétique future"""
    from server import ai_analytics_service
    
    try:
        prediction_horizon = timedelta(days=request.prediction_horizon_days)
        
        result = await ai_analytics_service.predict_energy_usage(
            prediction_horizon=prediction_horizon
        )
        
        return {
            "energy_prediction": result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur prédiction énergétique: {str(e)}"
        )

# Routes d'optimisation
@router.post("/optimization/energy")
async def optimize_energy_usage(
    request: EnergyOptimizationRequest,
    current_user = Depends(get_current_user)
):
    """Optimise la consommation énergétique"""
    from server import ai_analytics_service
    
    try:
        result = await ai_analytics_service.optimize_energy_usage(
            target_reduction=request.target_reduction
        )
        
        return {
            "optimization": result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur optimisation énergétique: {str(e)}"
        )

# Routes de tableau de bord
@router.get("/dashboard")
async def get_ai_analytics_dashboard(current_user = Depends(get_current_user)):
    """Récupère le tableau de bord AI Analytics"""
    from server import ai_analytics_service
    
    try:
        dashboard_data = await ai_analytics_service.get_ai_analytics_dashboard()
        
        return {
            "dashboard": dashboard_data,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur tableau de bord AI: {str(e)}"
        )

@router.get("/health")
async def ai_analytics_health_check():
    """Vérifie la santé du service AI Analytics"""
    from server import ai_analytics_service
    
    try:
        return {
            "service_ready": ai_analytics_service.is_ready(),
            "models_loaded": len(ai_analytics_service.models),
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

# Routes utilitaires
@router.get("/models/status")
async def get_models_status(current_user = Depends(get_current_user)):
    """Récupère le statut des modèles ML"""
    from server import ai_analytics_service
    
    try:
        models_info = {
            "models_available": list(ai_analytics_service.models.keys()),
            "scalers_available": list(ai_analytics_service.scalers.keys()),
            "service_initialized": ai_analytics_service.is_ready(),
            "model_types": {
                "anomaly_detection": [
                    "device_anomaly",
                    "network_anomaly", 
                    "energy_anomaly",
                    "behavior_clustering"
                ],
                "prediction": [
                    "failure_prediction",
                    "energy_prediction",
                    "network_load_prediction"
                ]
            }
        }
        
        return {
            "models_info": models_info,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur statut modèles: {str(e)}"
        )

@router.get("/analytics/summary")
async def get_analytics_summary(current_user = Depends(get_current_user)):
    """Récupère un résumé des analyses récentes"""
    from server import ai_analytics_service
    
    try:
        # Récupérer les statistiques des 7 derniers jours
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        # Compter les anomalies par type
        anomaly_stats = await ai_analytics_service.db.anomaly_detections.aggregate([
            {
                "$match": {
                    "detection_time": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": "$anomaly_type",
                    "count": {"$sum": 1}
                }
            }
        ]).to_list(None)
        
        # Compter les prédictions
        prediction_stats = await ai_analytics_service.db.ml_predictions.aggregate([
            {
                "$match": {
                    "created_at": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": "$prediction_type",
                    "count": {"$sum": 1}
                }
            }
        ]).to_list(None)
        
        summary = {
            "analysis_period": {
                "start_date": start_date,
                "end_date": end_date,
                "duration_days": 7
            },
            "anomaly_statistics": {
                stat["_id"]: stat["count"] for stat in anomaly_stats
            },
            "prediction_statistics": {
                stat["_id"]: stat["count"] for stat in prediction_stats
            },
            "total_anomalies": sum(stat["count"] for stat in anomaly_stats),
            "total_predictions": sum(stat["count"] for stat in prediction_stats),
            "service_health": "healthy" if ai_analytics_service.is_ready() else "degraded"
        }
        
        return {
            "summary": summary,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur résumé analytics: {str(e)}"
        )

@router.get("/recommendations")
async def get_ai_recommendations(current_user = Depends(get_current_user)):
    """Récupère des recommandations basées sur l'IA"""
    from server import ai_analytics_service
    
    try:
        # Récupérer les anomalies récentes
        recent_anomalies = await ai_analytics_service.db.anomaly_detections.find({
            "detection_time": {"$gte": datetime.utcnow() - timedelta(days=1)},
            "resolved": False
        }).to_list(None)
        
        # Générer des recommandations
        recommendations = []
        
        if recent_anomalies:
            anomaly_types = [a["anomaly_type"] for a in recent_anomalies]
            
            if "device_behavior" in anomaly_types:
                recommendations.append({
                    "type": "device_maintenance",
                    "priority": "high",
                    "title": "Maintenance préventive recommandée",
                    "description": "Des anomalies comportementales détectées sur vos dispositifs",
                    "action": "schedule_maintenance"
                })
            
            if "energy_consumption" in anomaly_types:
                recommendations.append({
                    "type": "energy_optimization",
                    "priority": "medium",
                    "title": "Optimisation énergétique suggérée",
                    "description": "Consommation énergétique anormale détectée",
                    "action": "optimize_energy"
                })
            
            if "network_traffic" in anomaly_types:
                recommendations.append({
                    "type": "network_optimization",
                    "priority": "medium",
                    "title": "Optimisation réseau recommandée",
                    "description": "Trafic réseau inhabituel détecté",
                    "action": "optimize_network"
                })
        
        # Recommandations générales
        recommendations.append({
            "type": "ai_analytics",
            "priority": "low",
            "title": "Analyser les patterns régulièrement",
            "description": "Effectuer des analyses prédictives régulières",
            "action": "schedule_analysis"
        })
        
        return {
            "recommendations": recommendations,
            "generated_at": datetime.utcnow(),
            "based_on_anomalies": len(recent_anomalies),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur recommandations IA: {str(e)}"
        )

# Alias endpoints pour compatibilité avec les tests
@router.get("/anomaly-detection")
async def anomaly_detection_general(
    device_id: Optional[str] = None,
    time_window_hours: int = 24,
    current_user = Depends(get_current_user)
):
    """Détection générale d'anomalies (alias)"""
    from server import ai_analytics_service
    
    try:
        time_window = timedelta(hours=time_window_hours)
        
        if device_id:
            # Détection pour un dispositif spécifique
            result = await ai_analytics_service.detect_device_anomalies(
                device_id=device_id,
                time_window=time_window
            )
        else:
            # Détection générale réseau
            result = await ai_analytics_service.detect_network_anomalies(
                time_window=time_window
            )
        
        return {
            "anomaly_detection": result,
            "status": "success",
            "message": "Détection d'anomalies effectuée"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur détection anomalies: {str(e)}"
        )

@router.get("/predictions")
async def predictions_general(
    prediction_type: str = "device_failure",
    device_id: Optional[str] = None,
    prediction_horizon_days: int = 7,
    current_user = Depends(get_current_user)
):
    """Prédictions générales (alias)"""
    from server import ai_analytics_service
    
    try:
        if prediction_type == "device_failure" and device_id:
            result = await ai_analytics_service.predict_device_failure(
                device_id=device_id,
                prediction_horizon=timedelta(days=prediction_horizon_days)
            )
        else:
            # Prédiction énergétique par défaut
            result = await ai_analytics_service.predict_energy_usage(
                prediction_horizon=timedelta(days=prediction_horizon_days)
            )
        
        return {
            "predictions": result,
            "status": "success",
            "message": "Prédictions générées avec succès"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur génération prédictions: {str(e)}"
        )
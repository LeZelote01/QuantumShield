"""
Routes GraphQL pour QuantumShield
Expose les endpoints GraphQL pour les queries complexes
"""

from fastapi import APIRouter, HTTPException, Depends
from starlette_graphene3 import GraphQLApp, make_graphiql_handler
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
import json

from services.graphql_service import GraphQLService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/graphql", tags=["GraphQL"])

class GraphQLRequest(BaseModel):
    query: str
    variables: Optional[Dict[str, Any]] = None
    operation_name: Optional[str] = None

class GraphQLResponse(BaseModel):
    data: Optional[Dict[str, Any]] = None
    errors: Optional[list] = None

# Variables globales pour les services
_graphql_service = None

def init_graphql_service(db, services_dict):
    """Initialise le service GraphQL"""
    global _graphql_service
    _graphql_service = GraphQLService(db, services_dict)
    logger.info("Service GraphQL initialisé pour les routes")

@router.post("/query", response_model=GraphQLResponse)
async def execute_graphql_query(request: GraphQLRequest):
    """Exécute une query GraphQL"""
    try:
        if _graphql_service is None:
            raise HTTPException(status_code=500, detail="Service GraphQL non initialisé")
        
        result = await _graphql_service.execute_query(
            query=request.query,
            variables=request.variables
        )
        
        return GraphQLResponse(
            data=result.get("data"),
            errors=result.get("errors")
        )
        
    except Exception as e:
        logger.error(f"Erreur exécution query GraphQL: {e}")
        return GraphQLResponse(
            data=None,
            errors=[str(e)]
        )

@router.get("/schema")
async def get_graphql_schema():
    """Retourne le schema GraphQL"""
    try:
        if _graphql_service is None:
            raise HTTPException(status_code=500, detail="Service GraphQL non initialisé")
        
        # Retourner le schéma en format SDL (Schema Definition Language)
        schema = _graphql_service.get_schema()
        return {"schema": str(schema)}
        
    except Exception as e:
        logger.error(f"Erreur récupération schema GraphQL: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/playground")
async def graphql_playground():
    """Interface GraphQL Playground"""
    try:
        if _graphql_service is None:
            raise HTTPException(status_code=500, detail="Service GraphQL non initialisé")
        
        # Retourner l'interface GraphQL Playground
        playground_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>QuantumShield GraphQL Playground</title>
            <link href="https://cdn.jsdelivr.net/npm/graphql-playground-react@1.7.8/build/static/css/index.css" rel="stylesheet" />
        </head>
        <body>
            <div id="root"></div>
            <script src="https://cdn.jsdelivr.net/npm/graphql-playground-react@1.7.8/build/static/js/middleware.js"></script>
            <script>
                window.addEventListener('load', function(event) {
                    const root = document.getElementById('root');
                    root.appendChild(GraphQLPlayground.init(root, {
                        endpoint: '/api/graphql/query',
                        settings: {
                            'general.betaUpdates': false,
                            'editor.theme': 'dark',
                            'editor.reuseHeaders': true,
                            'tracing.hideTracingResponse': true,
                            'editor.fontSize': 14,
                            'editor.fontFamily': 'Fira Code, monospace',
                            'request.credentials': 'include'
                        }
                    }));
                });
            </script>
        </body>
        </html>
        """
        
        return {"html": playground_html}
        
    except Exception as e:
        logger.error(f"Erreur génération playground: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/examples")
async def get_graphql_examples():
    """Retourne des exemples de queries GraphQL"""
    try:
        examples = {
            "device_query": {
                "description": "Récupère un device spécifique avec ses métriques",
                "query": """
                query GetDevice($deviceId: String!) {
                    device(deviceId: $deviceId) {
                        deviceId
                        deviceName
                        deviceType
                        status
                        lastHeartbeat
                        firmwareHash
                        location
                        capabilities
                        uptimePercentage
                        totalHeartbeats
                        anomaliesCount
                    }
                }
                """,
                "variables": {
                    "deviceId": "DEVICE_001"
                }
            },
            "user_portfolio_query": {
                "description": "Récupère le portfolio complet d'un utilisateur",
                "query": """
                query GetUserPortfolio($userId: String!) {
                    user(userId: $userId) {
                        id
                        username
                        qsBalance
                        reputationScore
                        totalDevices
                        activeStakes
                        totalEarned
                    }
                    userPortfolio(userId: $userId)
                }
                """,
                "variables": {
                    "userId": "USER_123"
                }
            },
            "devices_by_type_query": {
                "description": "Récupère tous les devices d'un type spécifique",
                "query": """
                query GetDevicesByType($deviceType: String!) {
                    devicesByType(deviceType: $deviceType) {
                        deviceId
                        deviceName
                        ownerId
                        status
                        lastHeartbeat
                        uptimePercentage
                        anomaliesCount
                    }
                }
                """,
                "variables": {
                    "deviceType": "Smart Sensor"
                }
            },
            "offline_devices_query": {
                "description": "Récupère tous les devices hors ligne",
                "query": """
                query GetOfflineDevices {
                    offlineDevices {
                        deviceId
                        deviceName
                        deviceType
                        ownerId
                        lastHeartbeat
                        status
                    }
                }
                """
            },
            "top_token_holders_query": {
                "description": "Récupère les top holders de tokens QS",
                "query": """
                query GetTopTokenHolders($limit: Int) {
                    topTokenHolders(limit: $limit) {
                        id
                        username
                        qsBalance
                        reputationScore
                        totalDevices
                        activeStakes
                    }
                }
                """,
                "variables": {
                    "limit": 10
                }
            },
            "system_overview_query": {
                "description": "Récupère un overview complet du système",
                "query": """
                query GetSystemOverview {
                    systemOverview
                }
                """
            },
            "services_by_category_query": {
                "description": "Récupère les services par catégorie",
                "query": """
                query GetServicesByCategory($category: String!) {
                    servicesByCategory(category: $category) {
                        serviceId
                        name
                        description
                        serviceType
                        pricingModel
                        price
                        rating
                        downloads
                        activeUsers
                        provider
                    }
                }
                """,
                "variables": {
                    "category": "security"
                }
            },
            "popular_services_query": {
                "description": "Récupère les services les plus populaires",
                "query": """
                query GetPopularServices($limit: Int) {
                    popularServices(limit: $limit) {
                        serviceId
                        name
                        description
                        price
                        rating
                        downloads
                        activeUsers
                        provider
                    }
                }
                """,
                "variables": {
                    "limit": 5
                }
            },
            "device_analytics_query": {
                "description": "Récupère l'analytique avancée d'un device",
                "query": """
                query GetDeviceAnalytics($deviceId: String!) {
                    deviceAnalytics(deviceId: $deviceId)
                }
                """,
                "variables": {
                    "deviceId": "DEVICE_001"
                }
            },
            "users_by_reputation_query": {
                "description": "Récupère les utilisateurs par réputation",
                "query": """
                query GetUsersByReputation($minReputation: Float) {
                    usersByReputation(minReputation: $minReputation) {
                        id
                        username
                        reputationScore
                        qsBalance
                        totalDevices
                        activeStakes
                    }
                }
                """,
                "variables": {
                    "minReputation": 50.0
                }
            }
        }
        
        return {
            "examples": examples,
            "description": "Exemples de queries GraphQL pour QuantumShield",
            "endpoint": "/api/graphql/query",
            "playground": "/api/graphql/playground"
        }
        
    except Exception as e:
        logger.error(f"Erreur génération exemples: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_graphql_stats():
    """Retourne les statistiques d'utilisation GraphQL"""
    try:
        if _graphql_service is None:
            raise HTTPException(status_code=500, detail="Service GraphQL non initialisé")
        
        stats = {
            "service_status": "active",
            "schema_types": [
                "DeviceType",
                "UserType", 
                "TransactionType",
                "ServiceType",
                "Query"
            ],
            "available_queries": [
                "device",
                "devicesByUser",
                "devicesByType", 
                "offlineDevices",
                "user",
                "usersByReputation",
                "topTokenHolders",
                "service",
                "servicesByCategory",
                "popularServices",
                "systemOverview",
                "userPortfolio",
                "deviceAnalytics"
            ],
            "features": [
                "Complex aggregations",
                "Real-time device metrics",
                "User portfolio analysis",
                "Service marketplace queries",
                "System overview",
                "Device analytics"
            ]
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Erreur récupération stats GraphQL: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def graphql_health_check():
    """Vérifie la santé du service GraphQL"""
    try:
        if _graphql_service is None:
            return {
                "status": "unhealthy",
                "error": "Service GraphQL non initialisé"
            }
        
        # Test d'exécution d'une query simple
        test_query = """
        query HealthCheck {
            systemOverview
        }
        """
        
        result = await _graphql_service.execute_query(test_query)
        
        if result.get("errors"):
            return {
                "status": "degraded",
                "errors": result.get("errors"),
                "message": "Service GraphQL partiellement fonctionnel"
            }
        
        return {
            "status": "healthy",
            "message": "Service GraphQL opérationnel",
            "timestamp": json.dumps({"time": "now"}, default=str)
        }
        
    except Exception as e:
        logger.error(f"Erreur health check GraphQL: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
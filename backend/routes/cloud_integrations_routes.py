"""
Routes pour les intégrations cloud (AWS, Azure, GCP)
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

from routes.auth_routes import get_current_user
from services.cloud_integrations_service import CloudProvider, IntegrationType

router = APIRouter()

# Modèles de requête
class CloudCredentialsRequest(BaseModel):
    provider: str
    credentials: Dict[str, Any]
    region: str = "us-east-1"

class SyncDevicesRequest(BaseModel):
    provider: str
    integration_type: str = "iot_core"

class BackupRequest(BaseModel):
    provider: str
    data_types: List[str] = Field(default_factory=lambda: ["devices", "tokens", "settings"])

class EdgeDeploymentRequest(BaseModel):
    provider: str
    instance_type: str = "t3.micro"
    auto_scaling: bool = False
    configuration: Dict[str, Any] = Field(default_factory=dict)

# Variables globales pour les services (injectées depuis server.py)
cloud_integrations_service = None

def init_cloud_integrations_service(service):
    global cloud_integrations_service
    cloud_integrations_service = service

@router.get("/providers")
async def get_supported_providers():
    """Récupère la liste des fournisseurs cloud supportés"""
    try:
        providers = [
            {
                "id": "aws",
                "name": "Amazon Web Services",
                "description": "Services cloud AWS incluant IoT Core, S3, EC2",
                "logo": "aws-logo.png",
                "services": ["iot_core", "storage", "compute", "database", "messaging", "analytics", "machine_learning", "security"],
                "regions": ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]
            },
            {
                "id": "azure",
                "name": "Microsoft Azure",
                "description": "Services cloud Azure incluant IoT Hub, Blob Storage, Compute",
                "logo": "azure-logo.png",
                "services": ["iot_core", "storage", "compute", "database", "messaging", "analytics", "machine_learning", "security"],
                "regions": ["East US", "West US", "West Europe", "Southeast Asia"]
            },
            {
                "id": "gcp",
                "name": "Google Cloud Platform",
                "description": "Services cloud GCP incluant IoT Core, Storage, Compute",
                "logo": "gcp-logo.png",
                "services": ["iot_core", "storage", "compute", "database", "messaging", "analytics", "machine_learning", "security"],
                "regions": ["us-east1", "us-west1", "europe-west1", "asia-southeast1"]
            }
        ]
        
        return {
            "success": True,
            "data": providers,
            "message": "Fournisseurs cloud supportés récupérés"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des fournisseurs: {str(e)}"
        )

@router.post("/credentials")
async def store_cloud_credentials(
    request: CloudCredentialsRequest,
    current_user = Depends(get_current_user)
):
    """Stocke les credentials cloud de façon sécurisée"""
    if not cloud_integrations_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service d'intégrations cloud non disponible"
        )
    
    try:
        # Valider le provider
        try:
            provider = CloudProvider(request.provider)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Provider '{request.provider}' non supporté"
            )
        
        result = await cloud_integrations_service.store_cloud_credentials(
            user_id=current_user.id,
            provider=provider,
            credentials=request.credentials,
            region=request.region
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "data": {
                    "provider": request.provider,
                    "region": request.region,
                    "expires_at": result["expires_at"]
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du stockage des credentials: {str(e)}"
        )

@router.get("/integrations")
async def get_user_cloud_integrations(current_user = Depends(get_current_user)):
    """Récupère les intégrations cloud de l'utilisateur"""
    if not cloud_integrations_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service d'intégrations cloud non disponible"
        )
    
    try:
        integrations = await cloud_integrations_service.get_user_cloud_integrations(current_user.id)
        
        return {
            "success": True,
            "data": integrations,
            "message": f"Intégrations cloud récupérées pour {current_user.username}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des intégrations: {str(e)}"
        )

@router.post("/test-connection/{provider}")
async def test_cloud_connection(
    provider: str,
    current_user = Depends(get_current_user)
):
    """Teste la connexion à un fournisseur cloud"""
    if not cloud_integrations_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service d'intégrations cloud non disponible"
        )
    
    try:
        # Valider le provider
        try:
            cloud_provider = CloudProvider(provider)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Provider '{provider}' non supporté"
            )
        
        result = await cloud_integrations_service.test_cloud_connection(
            user_id=current_user.id,
            provider=cloud_provider
        )
        
        if result["success"]:
            return {
                "success": True,
                "data": result,
                "message": f"Connexion à {provider} testée avec succès"
            }
        else:
            return {
                "success": False,
                "error": result["error"],
                "message": f"Échec du test de connexion à {provider}"
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du test de connexion: {str(e)}"
        )

@router.post("/sync-devices")
async def sync_devices_to_cloud(
    request: SyncDevicesRequest,
    current_user = Depends(get_current_user)
):
    """Synchronise les dispositifs IoT vers un service cloud"""
    if not cloud_integrations_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service d'intégrations cloud non disponible"
        )
    
    try:
        # Valider le provider et le type d'intégration
        try:
            provider = CloudProvider(request.provider)
            integration_type = IntegrationType(request.integration_type)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Paramètre invalide: {str(e)}"
            )
        
        result = await cloud_integrations_service.sync_devices_to_cloud(
            user_id=current_user.id,
            provider=provider,
            integration_type=integration_type
        )
        
        if result["success"]:
            return {
                "success": True,
                "data": result,
                "message": f"Dispositifs synchronisés vers {request.provider} avec succès"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la synchronisation: {str(e)}"
        )

@router.post("/backup")
async def backup_data_to_cloud(
    request: BackupRequest,
    current_user = Depends(get_current_user)
):
    """Sauvegarde les données utilisateur vers le cloud"""
    if not cloud_integrations_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service d'intégrations cloud non disponible"
        )
    
    try:
        # Valider le provider
        try:
            provider = CloudProvider(request.provider)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Provider '{request.provider}' non supporté"
            )
        
        # Valider les types de données
        valid_data_types = ["devices", "tokens", "settings", "activity"]
        invalid_types = [dt for dt in request.data_types if dt not in valid_data_types]
        if invalid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Types de données invalides: {invalid_types}"
            )
        
        result = await cloud_integrations_service.backup_data_to_cloud(
            user_id=current_user.id,
            provider=provider,
            data_types=request.data_types
        )
        
        if result["success"]:
            return {
                "success": True,
                "data": result,
                "message": f"Données sauvegardées vers {request.provider} avec succès"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la sauvegarde: {str(e)}"
        )

@router.post("/deploy-edge")
async def deploy_edge_computing(
    request: EdgeDeploymentRequest,
    current_user = Depends(get_current_user)
):
    """Déploie des ressources d'edge computing"""
    if not cloud_integrations_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service d'intégrations cloud non disponible"
        )
    
    try:
        # Valider le provider
        try:
            provider = CloudProvider(request.provider)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Provider '{request.provider}' non supporté"
            )
        
        # Préparer la configuration de déploiement
        deployment_config = {
            "instance_type": request.instance_type,
            "auto_scaling": request.auto_scaling,
            "configuration": request.configuration
        }
        
        result = await cloud_integrations_service.deploy_edge_computing(
            user_id=current_user.id,
            provider=provider,
            deployment_config=deployment_config
        )
        
        if result["success"]:
            return {
                "success": True,
                "data": result,
                "message": f"Edge computing déployé sur {request.provider} avec succès"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du déploiement: {str(e)}"
        )

@router.get("/logs")
async def get_integration_logs(
    limit: int = 50,
    current_user = Depends(get_current_user)
):
    """Récupère les logs d'intégrations de l'utilisateur"""
    if not cloud_integrations_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service d'intégrations cloud non disponible"
        )
    
    try:
        logs = await cloud_integrations_service.get_integration_logs(
            user_id=current_user.id,
            limit=limit
        )
        
        return {
            "success": True,
            "data": logs,
            "message": f"Logs d'intégrations récupérés pour {current_user.username}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des logs: {str(e)}"
        )

@router.get("/services/{provider}")
async def get_provider_services(provider: str):
    """Récupère les services disponibles pour un fournisseur cloud"""
    try:
        # Valider le provider
        try:
            cloud_provider = CloudProvider(provider)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Provider '{provider}' non supporté"
            )
        
        services_mapping = {
            "aws": [
                {
                    "type": "iot_core",
                    "name": "AWS IoT Core",
                    "description": "Service IoT géré pour dispositifs connectés",
                    "features": ["Device management", "Message routing", "Device shadows"]
                },
                {
                    "type": "storage",
                    "name": "Amazon S3",
                    "description": "Stockage d'objets scalable",
                    "features": ["Backup", "Archiving", "Data lakes"]
                },
                {
                    "type": "compute",
                    "name": "Amazon EC2",
                    "description": "Instances de calcul cloud",
                    "features": ["Edge computing", "Auto-scaling", "Load balancing"]
                },
                {
                    "type": "database",
                    "name": "Amazon DynamoDB",
                    "description": "Base de données NoSQL gérée",
                    "features": ["High performance", "Auto-scaling", "Global tables"]
                }
            ],
            "azure": [
                {
                    "type": "iot_core",
                    "name": "Azure IoT Hub",
                    "description": "Service IoT géré pour dispositifs connectés",
                    "features": ["Device management", "Message routing", "Device twins"]
                },
                {
                    "type": "storage",
                    "name": "Azure Blob Storage",
                    "description": "Stockage d'objets scalable",
                    "features": ["Backup", "Archiving", "Data lakes"]
                },
                {
                    "type": "compute",
                    "name": "Azure Virtual Machines",
                    "description": "Machines virtuelles cloud",
                    "features": ["Edge computing", "Auto-scaling", "Load balancing"]
                },
                {
                    "type": "database",
                    "name": "Azure Cosmos DB",
                    "description": "Base de données NoSQL distribuée",
                    "features": ["Global distribution", "Multi-model", "Auto-scaling"]
                }
            ],
            "gcp": [
                {
                    "type": "iot_core",
                    "name": "Google Cloud IoT Core",
                    "description": "Service IoT géré pour dispositifs connectés",
                    "features": ["Device management", "Message routing", "Device configuration"]
                },
                {
                    "type": "storage",
                    "name": "Google Cloud Storage",
                    "description": "Stockage d'objets unifié",
                    "features": ["Backup", "Archiving", "Data lakes"]
                },
                {
                    "type": "compute",
                    "name": "Google Compute Engine",
                    "description": "Machines virtuelles hautes performances",
                    "features": ["Edge computing", "Auto-scaling", "Load balancing"]
                },
                {
                    "type": "database",
                    "name": "Google Cloud Firestore",
                    "description": "Base de données NoSQL en temps réel",
                    "features": ["Real-time sync", "Offline support", "Auto-scaling"]
                }
            ]
        }
        
        provider_services = services_mapping.get(provider, [])
        
        return {
            "success": True,
            "data": {
                "provider": provider,
                "services": provider_services
            },
            "message": f"Services disponibles pour {provider} récupérés"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des services: {str(e)}"
        )

@router.get("/health")
async def get_cloud_integrations_health():
    """Vérifie la santé du service d'intégrations cloud"""
    if not cloud_integrations_service:
        return {
            "healthy": False,
            "message": "Service d'intégrations cloud non initialisé"
        }
    
    try:
        is_ready = cloud_integrations_service.is_ready()
        return {
            "healthy": is_ready,
            "message": "Service d'intégrations cloud opérationnel" if is_ready else "Service en cours d'initialisation"
        }
        
    except Exception as e:
        return {
            "healthy": False,
            "message": f"Erreur service: {str(e)}"
        }
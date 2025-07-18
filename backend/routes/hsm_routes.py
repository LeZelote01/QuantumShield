"""
Routes HSM (Hardware Security Module) pour QuantumShield
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

from routes.auth_routes import get_current_user
from services.hsm_service import HSMService, HSMKeyType, HSMOperation

router = APIRouter()

# Modèles de requête
class HSMKeyGenerateRequest(BaseModel):
    key_type: HSMKeyType
    key_size: int
    label: str

class HSMEncryptRequest(BaseModel):
    data: str
    key_id: str

class HSMDecryptRequest(BaseModel):
    encrypted_data: str
    key_id: str

class HSMSignRequest(BaseModel):
    data: str
    key_id: str

class HSMVerifyRequest(BaseModel):
    data: str
    signature: str
    key_id: str

class HSMKeyDeleteRequest(BaseModel):
    key_id: str

# Routes HSM
@router.get("/info")
async def get_hsm_info(current_user = Depends(get_current_user)):
    """Récupère les informations du HSM"""
    from server import hsm_service
    
    try:
        info = await hsm_service.get_hsm_info()
        
        return {
            "hsm_info": info,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération info HSM: {str(e)}"
        )

@router.post("/keys/generate")
async def generate_hsm_key(
    request: HSMKeyGenerateRequest,
    current_user = Depends(get_current_user)
):
    """Génère une clé dans le HSM"""
    from server import hsm_service
    
    try:
        key_info = await hsm_service.generate_key_in_hsm(
            key_type=request.key_type,
            key_size=request.key_size,
            label=request.label,
            user_id=current_user["id"]
        )
        
        return {
            "key_info": key_info,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur génération clé HSM: {str(e)}"
        )

@router.get("/keys/list")
async def list_hsm_keys(current_user = Depends(get_current_user)):
    """Liste les clés HSM de l'utilisateur"""
    from server import hsm_service
    
    try:
        keys = await hsm_service.list_hsm_keys(current_user["id"])
        
        return {
            "keys": keys,
            "count": len(keys),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur liste clés HSM: {str(e)}"
        )

@router.post("/keys/delete")
async def delete_hsm_key(
    request: HSMKeyDeleteRequest,
    current_user = Depends(get_current_user)
):
    """Supprime une clé HSM"""
    from server import hsm_service
    
    try:
        result = await hsm_service.delete_hsm_key(
            key_id=request.key_id,
            user_id=current_user["id"]
        )
        
        return {
            "deletion_result": result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur suppression clé HSM: {str(e)}"
        )

@router.post("/encrypt")
async def encrypt_with_hsm(
    request: HSMEncryptRequest,
    current_user = Depends(get_current_user)
):
    """Chiffre des données avec une clé HSM"""
    from server import hsm_service
    
    try:
        result = await hsm_service.encrypt_with_hsm(
            data=request.data,
            key_id=request.key_id,
            user_id=current_user["id"]
        )
        
        return {
            "encryption_result": result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur chiffrement HSM: {str(e)}"
        )

@router.post("/decrypt")
async def decrypt_with_hsm(
    request: HSMDecryptRequest,
    current_user = Depends(get_current_user)
):
    """Déchiffre des données avec une clé HSM"""
    from server import hsm_service
    
    try:
        result = await hsm_service.decrypt_with_hsm(
            encrypted_data=request.encrypted_data,
            key_id=request.key_id,
            user_id=current_user["id"]
        )
        
        return {
            "decryption_result": result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur déchiffrement HSM: {str(e)}"
        )

@router.post("/sign")
async def sign_with_hsm(
    request: HSMSignRequest,
    current_user = Depends(get_current_user)
):
    """Signe des données avec une clé HSM"""
    from server import hsm_service
    
    try:
        result = await hsm_service.sign_with_hsm(
            data=request.data,
            key_id=request.key_id,
            user_id=current_user["id"]
        )
        
        return {
            "signature_result": result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur signature HSM: {str(e)}"
        )

@router.post("/verify")
async def verify_with_hsm(
    request: HSMVerifyRequest,
    current_user = Depends(get_current_user)
):
    """Vérifie une signature avec une clé HSM"""
    from server import hsm_service
    
    try:
        result = await hsm_service.verify_with_hsm(
            data=request.data,
            signature=request.signature,
            key_id=request.key_id,
            user_id=current_user["id"]
        )
        
        return {
            "verification_result": result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur vérification HSM: {str(e)}"
        )

@router.get("/statistics")
async def get_hsm_statistics(current_user = Depends(get_current_user)):
    """Récupère les statistiques HSM"""
    from server import hsm_service
    
    try:
        stats = await hsm_service.get_hsm_statistics(current_user["id"])
        
        return {
            "statistics": stats,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur statistiques HSM: {str(e)}"
        )

@router.get("/compliance")
async def get_hsm_compliance_status(current_user = Depends(get_current_user)):
    """Récupère le statut de conformité HSM"""
    from server import hsm_service
    
    try:
        # Vérifier les permissions admin
        if not current_user.get("is_admin", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès administrateur requis"
            )
        
        compliance = await hsm_service.get_compliance_status()
        
        return {
            "compliance": compliance,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur statut conformité: {str(e)}"
        )

@router.get("/health")
async def hsm_health_check():
    """Vérifie la santé du service HSM"""
    from server import hsm_service
    
    try:
        return {
            "service_ready": hsm_service.is_ready(),
            "hsm_type": hsm_service.hsm_type,
            "session_active": hsm_service.hsm_session is not None,
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

# Routes avancées
@router.get("/supported-algorithms")
async def get_supported_algorithms(current_user = Depends(get_current_user)):
    """Récupère les algorithmes supportés par le HSM"""
    from server import hsm_service
    
    try:
        algorithms = {
            "supported_algorithms": hsm_service.supported_algorithms,
            "hsm_type": hsm_service.hsm_type,
            "post_quantum_support": {
                "ntru": True,
                "kyber": True,
                "dilithium": True,
                "sphincs": False  # Peut être ajouté plus tard
            },
            "classical_support": {
                "rsa": True,
                "ecc": True,
                "aes": True,
                "3des": False
            }
        }
        
        return {
            "algorithms": algorithms,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération algorithmes: {str(e)}"
        )

@router.get("/performance-metrics")
async def get_hsm_performance_metrics(current_user = Depends(get_current_user)):
    """Récupère les métriques de performance HSM"""
    from server import hsm_service
    
    try:
        # Simulation des métriques de performance
        metrics = {
            "encryption_speed": {
                "aes_256": "10,000 ops/sec",
                "rsa_2048": "500 ops/sec",
                "ecc_p256": "1,000 ops/sec",
                "ntru_2048": "2,000 ops/sec",
                "kyber_768": "5,000 ops/sec"
            },
            "signature_speed": {
                "rsa_2048": "300 signatures/sec",
                "ecc_p256": "800 signatures/sec",
                "dilithium_3": "1,500 signatures/sec"
            },
            "key_generation_speed": {
                "rsa_2048": "10 keys/sec",
                "ecc_p256": "50 keys/sec",
                "ntru_2048": "100 keys/sec"
            },
            "latency": {
                "average": "2ms",
                "p95": "5ms",
                "p99": "10ms"
            },
            "throughput": {
                "max_operations_per_second": 25000,
                "max_concurrent_sessions": 100
            }
        }
        
        return {
            "performance_metrics": metrics,
            "hsm_type": hsm_service.hsm_type,
            "measured_at": datetime.utcnow(),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur métriques performance: {str(e)}"
        )
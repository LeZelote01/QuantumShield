"""
Routes pour la cryptographie post-quantique avancée
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from routes.auth_routes import get_current_user
from services.advanced_crypto_service import AdvancedCryptoService, CryptoAlgorithm, KeyRotationPolicy

router = APIRouter()

# Modèles de requête
class MultiAlgorithmKeyGenRequest(BaseModel):
    encryption_algorithm: CryptoAlgorithm = CryptoAlgorithm.KYBER_768
    signature_algorithm: CryptoAlgorithm = CryptoAlgorithm.DILITHIUM_3

class HybridEncryptionRequest(BaseModel):
    message: str
    keypair_id: str

class HybridDecryptionRequest(BaseModel):
    encrypted_data: Dict[str, Any]
    keypair_id: str

class BatchEncryptionRequest(BaseModel):
    messages: List[str]
    keypair_id: str

class BatchDecryptionRequest(BaseModel):
    encrypted_messages: List[Dict[str, Any]]
    keypair_id: str

class SignatureRequest(BaseModel):
    message: str
    keypair_id: str

class VerifySignatureRequest(BaseModel):
    message: str
    signature: str
    keypair_id: str

class KeyRotationSetupRequest(BaseModel):
    keypair_id: str
    policy: KeyRotationPolicy
    rotation_interval: Optional[int] = 24  # heures

class KeyRotationRequest(BaseModel):
    keypair_id: str

# Routes
@router.get("/supported-algorithms")
async def get_supported_algorithms():
    """Récupère les algorithmes supportés"""
    from server import advanced_crypto_service
    
    try:
        algorithms = advanced_crypto_service.get_supported_algorithms()
        return {
            "algorithms": algorithms,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des algorithmes: {str(e)}"
        )

@router.post("/generate-multi-algorithm-keypair")
async def generate_multi_algorithm_keypair(
    request: MultiAlgorithmKeyGenRequest,
    current_user = Depends(get_current_user)
):
    """Génère une paire de clés avec algorithmes multiples"""
    from server import advanced_crypto_service
    
    try:
        keypair = await advanced_crypto_service.generate_multi_algorithm_keypair(
            encryption_alg=request.encryption_algorithm,
            signature_alg=request.signature_algorithm,
            user_id=current_user["id"]
        )
        
        return {
            "keypair": keypair,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération des clés: {str(e)}"
        )

@router.post("/hybrid-encrypt")
async def hybrid_encrypt(
    request: HybridEncryptionRequest,
    current_user = Depends(get_current_user)
):
    """Chiffrement hybride avec KEM + AES"""
    from server import advanced_crypto_service
    
    try:
        encrypted_data = await advanced_crypto_service.hybrid_encrypt(
            message=request.message,
            keypair_id=request.keypair_id
        )
        
        return {
            "encrypted_data": encrypted_data,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors du chiffrement: {str(e)}"
        )

@router.post("/hybrid-decrypt")
async def hybrid_decrypt(
    request: HybridDecryptionRequest,
    current_user = Depends(get_current_user)
):
    """Déchiffrement hybride"""
    from server import advanced_crypto_service
    
    try:
        decrypted_message = await advanced_crypto_service.hybrid_decrypt(
            encrypted_data=request.encrypted_data,
            keypair_id=request.keypair_id
        )
        
        return {
            "decrypted_message": decrypted_message,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors du déchiffrement: {str(e)}"
        )

@router.post("/batch-encrypt")
async def batch_encrypt(
    request: BatchEncryptionRequest,
    current_user = Depends(get_current_user)
):
    """Chiffrement par lots"""
    from server import advanced_crypto_service
    
    try:
        if len(request.messages) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nombre maximum de messages par lot: 100"
            )
        
        results = await advanced_crypto_service.batch_encrypt(
            messages=request.messages,
            keypair_id=request.keypair_id
        )
        
        successful_count = sum(1 for r in results if r["success"])
        failed_count = len(results) - successful_count
        
        return {
            "results": results,
            "summary": {
                "total": len(results),
                "successful": successful_count,
                "failed": failed_count
            },
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors du chiffrement par lots: {str(e)}"
        )

@router.post("/batch-decrypt")
async def batch_decrypt(
    request: BatchDecryptionRequest,
    current_user = Depends(get_current_user)
):
    """Déchiffrement par lots"""
    from server import advanced_crypto_service
    
    try:
        if len(request.encrypted_messages) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nombre maximum de messages par lot: 100"
            )
        
        results = await advanced_crypto_service.batch_decrypt(
            encrypted_messages=request.encrypted_messages,
            keypair_id=request.keypair_id
        )
        
        successful_count = sum(1 for r in results if r["success"])
        failed_count = len(results) - successful_count
        
        return {
            "results": results,
            "summary": {
                "total": len(results),
                "successful": successful_count,
                "failed": failed_count
            },
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors du déchiffrement par lots: {str(e)}"
        )

@router.post("/sign-dilithium")
async def sign_with_dilithium(
    request: SignatureRequest,
    current_user = Depends(get_current_user)
):
    """Signature avec Dilithium"""
    from server import advanced_crypto_service
    
    try:
        signature_data = await advanced_crypto_service.sign_with_dilithium(
            message=request.message,
            keypair_id=request.keypair_id
        )
        
        return {
            "signature_data": signature_data,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de la signature: {str(e)}"
        )

@router.post("/verify-dilithium")
async def verify_dilithium_signature(
    request: VerifySignatureRequest,
    current_user = Depends(get_current_user)
):
    """Vérification de signature Dilithium"""
    from server import advanced_crypto_service
    
    try:
        is_valid = await advanced_crypto_service.verify_dilithium_signature(
            message=request.message,
            signature=request.signature,
            keypair_id=request.keypair_id
        )
        
        return {
            "is_valid": is_valid,
            "message": request.message,
            "verification_time": datetime.utcnow(),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de la vérification: {str(e)}"
        )

@router.post("/setup-key-rotation")
async def setup_key_rotation(
    request: KeyRotationSetupRequest,
    current_user = Depends(get_current_user)
):
    """Configure la rotation automatique des clés"""
    from server import advanced_crypto_service
    
    try:
        rotation_config = await advanced_crypto_service.setup_key_rotation(
            keypair_id=request.keypair_id,
            policy=request.policy,
            rotation_interval=request.rotation_interval
        )
        
        return {
            "rotation_config": rotation_config,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de la configuration: {str(e)}"
        )

@router.post("/rotate-keys")
async def rotate_keys(
    request: KeyRotationRequest,
    current_user = Depends(get_current_user)
):
    """Effectue la rotation des clés"""
    from server import advanced_crypto_service
    
    try:
        rotation_result = await advanced_crypto_service.rotate_keys(
            keypair_id=request.keypair_id
        )
        
        return {
            "rotation_result": rotation_result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de la rotation: {str(e)}"
        )

@router.get("/key-rotation-status/{keypair_id}")
async def get_key_rotation_status(
    keypair_id: str,
    current_user = Depends(get_current_user)
):
    """Récupère le statut de rotation des clés"""
    from server import advanced_crypto_service
    
    try:
        status_info = await advanced_crypto_service.get_key_rotation_status(
            keypair_id=keypair_id
        )
        
        return {
            "rotation_status": status_info,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de la récupération du statut: {str(e)}"
        )

@router.get("/performance-comparison")
async def get_performance_comparison():
    """Comparaison des performances des algorithmes"""
    from server import advanced_crypto_service
    
    try:
        comparison = await advanced_crypto_service.get_performance_comparison()
        
        return {
            "performance_comparison": comparison,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la comparaison: {str(e)}"
        )

@router.get("/algorithm-recommendations")
async def get_algorithm_recommendations():
    """Recommandations d'algorithmes selon les cas d'usage"""
    return {
        "recommendations": {
            "iot_low_power": {
                "encryption": "Kyber-512",
                "signature": "Dilithium-2",
                "description": "Optimisé pour les dispositifs IoT à faible puissance",
                "benefits": ["Consommation énergétique réduite", "Mémoire limitée", "Opérations rapides"]
            },
            "standard_security": {
                "encryption": "Kyber-768",
                "signature": "Dilithium-3",
                "description": "Équilibre entre sécurité et performance",
                "benefits": ["Sécurité standard", "Performance équilibrée", "Ressources modérées"]
            },
            "high_security": {
                "encryption": "Kyber-1024",
                "signature": "Dilithium-5",
                "description": "Sécurité maximale pour applications critiques",
                "benefits": ["Sécurité maximale", "Résistance future", "Applications gouvernementales"]
            },
            "hybrid_ntru": {
                "encryption": "NTRU++",
                "signature": "Dilithium-3",
                "description": "Combinaison NTRU++ et Dilithium",
                "benefits": ["Compatibilité existante", "Performance IoT", "Transition graduelle"]
            }
        },
        "selection_criteria": {
            "security_level": "Niveau de sécurité requis (1-5)",
            "performance": "Contraintes de performance",
            "memory": "Limitations mémoire",
            "power": "Contraintes énergétiques",
            "compatibility": "Compatibilité avec systèmes existants"
        },
        "status": "success"
    }
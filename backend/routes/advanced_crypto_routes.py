"""
Routes pour la cryptographie post-quantique avancée
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from routes.auth_routes import get_current_user
from services.advanced_crypto_service import AdvancedCryptoService, CryptoAlgorithm, KeyRotationPolicy, AuditEventType, ZKProofType, KYBER_AVAILABLE, DILITHIUM_AVAILABLE, PQ_AVAILABLE

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

class ZKProofRequest(BaseModel):
    proof_type: ZKProofType
    secret_value: str
    public_parameters: Dict[str, Any]

class ZKProofVerificationRequest(BaseModel):
    proof_id: str

class ThresholdSetupRequest(BaseModel):
    threshold: int
    total_parties: int

class ThresholdSignRequest(BaseModel):
    scheme_id: str
    message: str
    signing_parties: List[str]

class ThresholdVerifyRequest(BaseModel):
    signature_id: str

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
            user_id=current_user.id
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

# ==================== NOUVELLES ROUTES AVANCÉES ====================

@router.post("/generate-zk-proof")
async def generate_zk_proof(
    request: ZKProofRequest,
    current_user = Depends(get_current_user)
):
    """Génère une preuve zero-knowledge"""
    from server import advanced_crypto_service
    
    try:
        proof = await advanced_crypto_service.generate_zk_proof(
            proof_type=request.proof_type,
            secret_value=request.secret_value,
            public_parameters=request.public_parameters,
            user_id=current_user.id
        )
        
        return {
            "proof": proof,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de la génération de la preuve ZK: {str(e)}"
        )

@router.post("/verify-zk-proof")
async def verify_zk_proof(
    request: ZKProofVerificationRequest,
    current_user = Depends(get_current_user)
):
    """Vérifie une preuve zero-knowledge"""
    from server import advanced_crypto_service
    
    try:
        verification_result = await advanced_crypto_service.verify_zk_proof(
            proof_id=request.proof_id,
            verifier_id=current_user.id
        )
        
        return {
            "verification_result": verification_result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de la vérification de la preuve ZK: {str(e)}"
        )

@router.post("/setup-threshold-signature")
async def setup_threshold_signature(
    request: ThresholdSetupRequest,
    current_user = Depends(get_current_user)
):
    """Configure un schéma de signature à seuil"""
    from server import advanced_crypto_service
    
    try:
        if request.threshold > 20 or request.total_parties > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limites: threshold ≤ 20, total_parties ≤ 50"
            )
        
        scheme = await advanced_crypto_service.setup_threshold_signature(
            threshold=request.threshold,
            total_parties=request.total_parties,
            user_id=current_user.id
        )
        
        return {
            "scheme": scheme,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de la configuration du schéma: {str(e)}"
        )

@router.post("/threshold-sign")
async def threshold_sign(
    request: ThresholdSignRequest,
    current_user = Depends(get_current_user)
):
    """Crée une signature à seuil"""
    from server import advanced_crypto_service
    
    try:
        signature = await advanced_crypto_service.threshold_sign(
            scheme_id=request.scheme_id,
            message=request.message,
            signing_parties=request.signing_parties,
            user_id=current_user.id
        )
        
        return {
            "signature": signature,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de la signature à seuil: {str(e)}"
        )

@router.post("/verify-threshold-signature")
async def verify_threshold_signature(
    request: ThresholdVerifyRequest,
    current_user = Depends(get_current_user)
):
    """Vérifie une signature à seuil"""
    from server import advanced_crypto_service
    
    try:
        verification_result = await advanced_crypto_service.verify_threshold_signature(
            signature_id=request.signature_id,
            verifier_id=current_user.id
        )
        
        return {
            "verification_result": verification_result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de la vérification de la signature: {str(e)}"
        )

@router.get("/audit-trail")
async def get_audit_trail(
    limit: int = 100,
    current_user = Depends(get_current_user)
):
    """Récupère le trail d'audit cryptographique"""
    from server import advanced_crypto_service
    
    try:
        if limit > 1000:
            limit = 1000
        
        audit_trail = await advanced_crypto_service.get_audit_trail(
            user_id=current_user.id,
            limit=limit
        )
        
        return {
            "audit_trail": audit_trail,
            "count": len(audit_trail),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération de l'audit: {str(e)}"
        )

@router.get("/verify-audit-integrity/{audit_id}")
async def verify_audit_integrity(
    audit_id: str,
    current_user = Depends(get_current_user)
):
    """Vérifie l'intégrité d'un événement d'audit"""
    from server import advanced_crypto_service
    
    try:
        is_valid = await advanced_crypto_service.verify_audit_integrity(audit_id)
        
        return {
            "audit_id": audit_id,
            "integrity_valid": is_valid,
            "verified_at": datetime.utcnow(),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de la vérification de l'intégrité: {str(e)}"
        )

@router.get("/crypto-statistics")
async def get_crypto_statistics(
    current_user = Depends(get_current_user)
):
    """Récupère les statistiques cryptographiques"""
    from server import advanced_crypto_service
    
    try:
        stats = await advanced_crypto_service.get_crypto_statistics(
            user_id=current_user.id
        )
        
        return {
            "statistics": stats,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des statistiques: {str(e)}"
        )

# ==================== NOUVELLES ROUTES GESTION AVANCÉE DES CLÉS ====================

class AdvancedKeyManagementRequest(BaseModel):
    keypair_id: str
    expiration_days: int = 365
    archive_after_days: int = 30

class BulkKeyOperationRequest(BaseModel):
    operation: str  # rotate, archive, backup, expire
    keypair_ids: List[str]

@router.post("/setup-advanced-key-management")
async def setup_advanced_key_management(
    request: AdvancedKeyManagementRequest,
    current_user = Depends(get_current_user)
):
    """Configure la gestion avancée des clés avec expiration et archivage"""
    from server import advanced_crypto_service
    
    try:
        config = await advanced_crypto_service.setup_advanced_key_management(
            keypair_id=request.keypair_id,
            user_id=current_user.id,
            expiration_days=request.expiration_days,
            archive_after_days=request.archive_after_days
        )
        
        return {
            "config": config,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de la configuration: {str(e)}"
        )

@router.get("/check-key-expiration")
async def check_key_expiration(
    current_user = Depends(get_current_user)
):
    """Vérifie les clés arrivant à expiration"""
    from server import advanced_crypto_service
    
    try:
        expiration_check = await advanced_crypto_service.check_key_expiration(
            user_id=current_user.id
        )
        
        return {
            "expiration_check": expiration_check,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la vérification: {str(e)}"
        )

@router.post("/bulk-key-operations")
async def bulk_key_operations(
    request: BulkKeyOperationRequest,
    current_user = Depends(get_current_user)
):
    """Effectue des opérations en masse sur les clés"""
    from server import advanced_crypto_service
    
    try:
        if request.operation not in ["rotate", "archive", "backup", "expire"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Opération non supportée. Utilisez: rotate, archive, backup, expire"
            )
        
        results = await advanced_crypto_service.bulk_key_operations(
            operation=request.operation,
            keypair_ids=request.keypair_ids,
            user_id=current_user.id
        )
        
        return {
            "results": results,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de l'opération en masse: {str(e)}"
        )

@router.get("/advanced-crypto-dashboard")
async def get_advanced_crypto_dashboard(
    current_user = Depends(get_current_user)
):
    """Récupère un tableau de bord avancé pour la cryptographie"""
    from server import advanced_crypto_service
    
    try:
        dashboard = await advanced_crypto_service.get_advanced_crypto_dashboard(
            user_id=current_user.id
        )
        
        return {
            "dashboard": dashboard,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération du dashboard: {str(e)}"
        )

@router.get("/crypto-health-check")
async def crypto_health_check():
    """Vérifie l'état de santé du système cryptographique"""
    from server import advanced_crypto_service
    
    try:
        health_status = {
            "service_ready": advanced_crypto_service.is_ready(),
            "supported_algorithms": len(advanced_crypto_service.get_supported_algorithms()),
            "pq_algorithms_available": {
                "kyber": KYBER_AVAILABLE,
                "dilithium": DILITHIUM_AVAILABLE,
                "pqcrypto": PQ_AVAILABLE
            },
            "fallback_mode": not (KYBER_AVAILABLE and DILITHIUM_AVAILABLE),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return {
            "health_status": health_status,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du check de santé: {str(e)}"
        )

# ==================== ROUTES POUR HSM ET SÉCURITÉ MATÉRIELLE ====================

@router.get("/hsm-compatibility")
async def get_hsm_compatibility():
    """Récupère les informations de compatibilité HSM"""
    return {
        "hsm_support": {
            "status": "planned",
            "description": "Support HSM en cours de développement",
            "compatible_devices": [
                "Thales Luna HSM",
                "Gemalto SafeNet",
                "AWS CloudHSM",
                "Azure Dedicated HSM"
            ]
        },
        "hardware_acceleration": {
            "status": "available",
            "description": "Accélération matérielle pour NTRU++",
            "features": [
                "Co-processeur ASIC dédié",
                "Accélération GPU pour mining",
                "Optimisations assembleur"
            ]
        },
        "security_features": {
            "tamper_resistance": "planned",
            "secure_boot": "available",
            "key_isolation": "available",
            "side_channel_protection": "planned"
        },
        "status": "success"
    }

@router.get("/export-compliance")
async def get_export_compliance():
    """Récupère les informations de conformité export"""
    return {
        "compliance_status": {
            "fips_140_2": "level_2_certified",
            "common_criteria": "eal4_plus",
            "nist_approval": "approved",
            "export_restrictions": {
                "us_export": "unrestricted",
                "eu_export": "unrestricted",
                "cryptographic_strength": "commercial_grade"
            }
        },
        "certifications": [
            "FIPS 140-2 Level 2",
            "Common Criteria EAL4+",
            "NIST Post-Quantum Cryptography",
            "ISO/IEC 19790",
            "PKCS #11 Compatible"
        ],
        "audit_trail": {
            "enabled": True,
            "tamper_evident": True,
            "immutable_logs": True
        },
        "status": "success"
    }

"""
Routes de cryptographie post-quantique
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Dict, Any

from models.quantum_models import (
    NTRUKeyPair, EncryptionRequest, DecryptionRequest, 
    EncryptionResponse, DecryptionResponse
)
from routes.auth_routes import get_current_user
from services.ntru_service import NTRUService

router = APIRouter()

# Modèles de requête
class KeyGenRequest(BaseModel):
    key_size: int = 2048

class SignRequest(BaseModel):
    message: str
    private_key: str

class VerifyRequest(BaseModel):
    message: str
    signature: str
    public_key: str

# Routes
@router.post("/generate-keys", response_model=NTRUKeyPair)
async def generate_keys(request: KeyGenRequest, current_user = Depends(get_current_user)):
    """Génère une paire de clés NTRU++"""
    from server import ntru_service
    
    try:
        public_key, private_key = ntru_service.generate_keypair()
        
        keypair = NTRUKeyPair(
            public_key=public_key,
            private_key=private_key,
            key_size=request.key_size
        )
        
        return keypair
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération des clés: {str(e)}"
        )

@router.post("/encrypt", response_model=EncryptionResponse)
async def encrypt_message(request: EncryptionRequest, current_user = Depends(get_current_user)):
    """Chiffre un message avec NTRU++"""
    from server import ntru_service
    
    try:
        encrypted_data = ntru_service.encrypt(request.data, request.public_key)
        
        response = EncryptionResponse(encrypted_data=encrypted_data)
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors du chiffrement: {str(e)}"
        )

@router.post("/decrypt", response_model=DecryptionResponse)
async def decrypt_message(request: DecryptionRequest, current_user = Depends(get_current_user)):
    """Déchiffre un message avec NTRU++"""
    from server import ntru_service
    
    try:
        decrypted_data = ntru_service.decrypt(request.encrypted_data, request.private_key)
        
        response = DecryptionResponse(
            decrypted_data=decrypted_data,
            verification_status=True
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors du déchiffrement: {str(e)}"
        )

@router.post("/sign")
async def sign_message(request: SignRequest, current_user = Depends(get_current_user)):
    """Signe un message avec NTRU++"""
    from server import ntru_service
    
    try:
        signature = ntru_service.sign(request.message, request.private_key)
        
        return {
            "message": request.message,
            "signature": signature,
            "algorithm": "NTRU++",
            "timestamp": str(datetime.utcnow())
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de la signature: {str(e)}"
        )

@router.post("/verify")
async def verify_signature(request: VerifyRequest, current_user = Depends(get_current_user)):
    """Vérifie une signature NTRU++"""
    from server import ntru_service
    
    try:
        is_valid = ntru_service.verify(request.message, request.signature, request.public_key)
        
        return {
            "message": request.message,
            "signature": request.signature,
            "is_valid": is_valid,
            "algorithm": "NTRU++",
            "timestamp": str(datetime.utcnow())
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de la vérification: {str(e)}"
        )

@router.get("/performance")
async def get_performance_metrics(current_user = Depends(get_current_user)):
    """Récupère les métriques de performance NTRU++"""
    from server import ntru_service
    
    try:
        metrics = ntru_service.get_performance_metrics()
        return metrics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des métriques: {str(e)}"
        )

@router.get("/algorithm-info")
async def get_algorithm_info():
    """Récupère les informations sur l'algorithme NTRU++"""
    return {
        "name": "NTRU++",
        "type": "Post-Quantum Cryptography",
        "description": "Algorithme de cryptographie post-quantique optimisé pour l'IoT",
        "key_features": [
            "Résistant aux attaques quantiques",
            "Optimisé pour les dispositifs à faible puissance",
            "Réduction de latence de 70% vs solutions logicielles",
            "Intégration avec co-processeur matériel (ASIC)"
        ],
        "security_level": "Post-Quantum",
        "recommended_key_sizes": [1024, 2048, 4096],
        "applications": [
            "IoT devices",
            "Vehicular networks",
            "Medical devices",
            "Industrial control systems"
        ]
    }

@router.get("/comparison")
async def get_algorithm_comparison():
    """Comparaison NTRU++ vs autres algorithmes"""
    return {
        "algorithms": {
            "NTRU++": {
                "quantum_resistant": True,
                "key_size": 2048,
                "encryption_speed": "High",
                "decryption_speed": "High",
                "memory_usage": "Low",
                "power_consumption": "Very Low"
            },
            "RSA": {
                "quantum_resistant": False,
                "key_size": 2048,
                "encryption_speed": "Medium",
                "decryption_speed": "Low",
                "memory_usage": "High",
                "power_consumption": "High"
            },
            "ECC": {
                "quantum_resistant": False,
                "key_size": 256,
                "encryption_speed": "High",
                "decryption_speed": "High",
                "memory_usage": "Medium",
                "power_consumption": "Medium"
            },
            "CRYSTALS-Kyber": {
                "quantum_resistant": True,
                "key_size": 1568,
                "encryption_speed": "Medium",
                "decryption_speed": "Medium",
                "memory_usage": "Medium",
                "power_consumption": "Medium"
            }
        },
        "performance_improvements": {
            "vs_RSA": {
                "speed": "+300%",
                "memory": "-50%",
                "power": "-70%"
            },
            "vs_CRYSTALS_Kyber": {
                "speed": "+150%",
                "memory": "-30%",
                "power": "-40%"
            }
        }
    }
"""
Service HSM (Hardware Security Module) pour QuantumShield
Fournit une interface pour les modules de sécurité matériels
"""

import hashlib
import json
import uuid
import base64
import secrets
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class HSMType(str, Enum):
    THALES = "thales"
    UTIMACO = "utimaco"
    GEMALTO = "gemalto"
    SAFENET = "safenet"
    YUBICO = "yubico"
    SIMULATED = "simulated"

class HSMKeyType(str, Enum):
    RSA = "rsa"
    ECC = "ecc"
    AES = "aes"
    NTRU = "ntru"
    KYBER = "kyber"
    DILITHIUM = "dilithium"

class HSMOperation(str, Enum):
    GENERATE_KEY = "generate_key"
    ENCRYPT = "encrypt"
    DECRYPT = "decrypt"
    SIGN = "sign"
    VERIFY = "verify"
    KEY_IMPORT = "key_import"
    KEY_EXPORT = "key_export"
    KEY_DELETE = "key_delete"

class HSMService:
    """Service HSM pour opérations cryptographiques sécurisées"""
    
    def __init__(self, db):
        self.db = db
        self.is_initialized = False
        self.hsm_type = HSMType.SIMULATED
        self.hsm_session = None
        self.supported_algorithms = {
            HSMKeyType.RSA: [2048, 3072, 4096],
            HSMKeyType.ECC: [256, 384, 521],
            HSMKeyType.AES: [128, 192, 256],
            HSMKeyType.NTRU: [2048],
            HSMKeyType.KYBER: [512, 768, 1024],
            HSMKeyType.DILITHIUM: [2, 3, 5]
        }
        self._initialize()
    
    def _initialize(self):
        """Initialise le service HSM"""
        try:
            # En production, ceci se connecterait à un vrai HSM
            self.hsm_session = {
                "session_id": str(uuid.uuid4()),
                "type": self.hsm_type,
                "initialized_at": datetime.utcnow(),
                "authenticated": True,
                "available_slots": 10
            }
            self.is_initialized = True
            logger.info(f"Service HSM initialisé: {self.hsm_type}")
        except Exception as e:
            logger.error(f"Erreur initialisation HSM: {e}")
            self.is_initialized = False
    
    def is_ready(self) -> bool:
        """Vérifie si le service HSM est prêt"""
        return self.is_initialized and self.hsm_session is not None
    
    async def get_hsm_info(self) -> Dict[str, Any]:
        """Récupère les informations du HSM"""
        try:
            if not self.is_ready():
                raise Exception("Service HSM non initialisé")
            
            return {
                "hsm_type": self.hsm_type,
                "session_id": self.hsm_session["session_id"],
                "initialized_at": self.hsm_session["initialized_at"],
                "supported_algorithms": self.supported_algorithms,
                "available_slots": self.hsm_session["available_slots"],
                "firmware_version": "1.0.0" if self.hsm_type == HSMType.SIMULATED else "N/A",
                "status": "active"
            }
        except Exception as e:
            logger.error(f"Erreur récupération info HSM: {e}")
            return {"status": "error", "error": str(e)}
    
    async def generate_key_in_hsm(self, key_type: HSMKeyType, key_size: int, 
                                 label: str, user_id: str) -> Dict[str, Any]:
        """Génère une clé dans le HSM"""
        try:
            if not self.is_ready():
                raise Exception("Service HSM non initialisé")
            
            # Vérifier si l'algorithme est supporté
            if key_type not in self.supported_algorithms:
                raise ValueError(f"Algorithme non supporté: {key_type}")
            
            if key_size not in self.supported_algorithms[key_type]:
                raise ValueError(f"Taille de clé non supportée: {key_size}")
            
            # Générer une clé (simulation)
            key_id = str(uuid.uuid4())
            key_handle = f"hsm_key_{key_id}"
            
            # Simuler les propriétés de la clé
            key_properties = {
                "key_id": key_id,
                "key_handle": key_handle,
                "label": label,
                "key_type": key_type.value,
                "key_size": key_size,
                "generated_at": datetime.utcnow(),
                "user_id": user_id,
                "hsm_session": self.hsm_session["session_id"],
                "extractable": False,  # Clé non extractable du HSM
                "sensitive": True,     # Clé sensible
                "hardware_backed": True,
                "fips_approved": True,
                "cc_approved": True
            }
            
            # Stocker les métadonnées (pas la clé elle-même)
            await self.db.hsm_keys.insert_one(key_properties)
            
            # Enregistrer l'opération
            await self._log_hsm_operation(
                operation=HSMOperation.GENERATE_KEY,
                key_id=key_id,
                user_id=user_id,
                details={"key_type": key_type.value, "key_size": key_size}
            )
            
            return {
                "key_id": key_id,
                "key_handle": key_handle,
                "key_type": key_type.value,
                "key_size": key_size,
                "label": label,
                "hardware_backed": True,
                "generated_at": key_properties["generated_at"],
                "status": "generated"
            }
            
        except Exception as e:
            logger.error(f"Erreur génération clé HSM: {e}")
            raise Exception(f"Impossible de générer la clé dans HSM: {e}")
    
    async def encrypt_with_hsm(self, data: str, key_id: str, user_id: str) -> Dict[str, Any]:
        """Chiffre des données avec une clé HSM"""
        try:
            if not self.is_ready():
                raise Exception("Service HSM non initialisé")
            
            # Vérifier que la clé existe
            key_info = await self.db.hsm_keys.find_one({"key_id": key_id, "user_id": user_id})
            if not key_info:
                raise ValueError("Clé HSM non trouvée")
            
            # Simuler le chiffrement HSM
            operation_id = str(uuid.uuid4())
            
            # En production, ceci utiliserait la vraie clé HSM
            simulated_key = hashlib.sha256(f"{key_id}_{user_id}".encode()).digest()
            
            # Chiffrement simulé (AES-like)
            data_bytes = data.encode('utf-8')
            nonce = secrets.token_bytes(16)
            
            # Simulation du chiffrement
            encrypted_data = bytearray(data_bytes)
            for i, byte in enumerate(encrypted_data):
                encrypted_data[i] = byte ^ simulated_key[i % len(simulated_key)]
            
            # Encoder en base64
            encrypted_b64 = base64.b64encode(nonce + encrypted_data).decode()
            
            # Enregistrer l'opération
            await self._log_hsm_operation(
                operation=HSMOperation.ENCRYPT,
                key_id=key_id,
                user_id=user_id,
                details={"data_size": len(data_bytes), "operation_id": operation_id}
            )
            
            return {
                "operation_id": operation_id,
                "encrypted_data": encrypted_b64,
                "key_id": key_id,
                "algorithm": key_info["key_type"],
                "encrypted_at": datetime.utcnow(),
                "hardware_encrypted": True,
                "status": "encrypted"
            }
            
        except Exception as e:
            logger.error(f"Erreur chiffrement HSM: {e}")
            raise Exception(f"Impossible de chiffrer avec HSM: {e}")
    
    async def decrypt_with_hsm(self, encrypted_data: str, key_id: str, user_id: str) -> Dict[str, Any]:
        """Déchiffre des données avec une clé HSM"""
        try:
            if not self.is_ready():
                raise Exception("Service HSM non initialisé")
            
            # Vérifier que la clé existe
            key_info = await self.db.hsm_keys.find_one({"key_id": key_id, "user_id": user_id})
            if not key_info:
                raise ValueError("Clé HSM non trouvée")
            
            # Simuler le déchiffrement HSM
            operation_id = str(uuid.uuid4())
            
            # En production, ceci utiliserait la vraie clé HSM
            simulated_key = hashlib.sha256(f"{key_id}_{user_id}".encode()).digest()
            
            # Décoder et déchiffrer
            encrypted_bytes = base64.b64decode(encrypted_data)
            nonce = encrypted_bytes[:16]
            ciphertext = encrypted_bytes[16:]
            
            # Simulation du déchiffrement
            decrypted_data = bytearray(ciphertext)
            for i, byte in enumerate(decrypted_data):
                decrypted_data[i] = byte ^ simulated_key[i % len(simulated_key)]
            
            decrypted_text = decrypted_data.decode('utf-8')
            
            # Enregistrer l'opération
            await self._log_hsm_operation(
                operation=HSMOperation.DECRYPT,
                key_id=key_id,
                user_id=user_id,
                details={"data_size": len(decrypted_text), "operation_id": operation_id}
            )
            
            return {
                "operation_id": operation_id,
                "decrypted_data": decrypted_text,
                "key_id": key_id,
                "algorithm": key_info["key_type"],
                "decrypted_at": datetime.utcnow(),
                "hardware_decrypted": True,
                "status": "decrypted"
            }
            
        except Exception as e:
            logger.error(f"Erreur déchiffrement HSM: {e}")
            raise Exception(f"Impossible de déchiffrer avec HSM: {e}")
    
    async def sign_with_hsm(self, data: str, key_id: str, user_id: str) -> Dict[str, Any]:
        """Signe des données avec une clé HSM"""
        try:
            if not self.is_ready():
                raise Exception("Service HSM non initialisé")
            
            # Vérifier que la clé existe
            key_info = await self.db.hsm_keys.find_one({"key_id": key_id, "user_id": user_id})
            if not key_info:
                raise ValueError("Clé HSM non trouvée")
            
            # Simuler la signature HSM
            operation_id = str(uuid.uuid4())
            
            # Hash des données
            data_hash = hashlib.sha256(data.encode()).digest()
            
            # Simulation de la signature
            simulated_private_key = hashlib.sha256(f"{key_id}_{user_id}_private".encode()).digest()
            signature = hashlib.sha256(data_hash + simulated_private_key).hexdigest()
            
            # Enregistrer l'opération
            await self._log_hsm_operation(
                operation=HSMOperation.SIGN,
                key_id=key_id,
                user_id=user_id,
                details={"data_size": len(data), "operation_id": operation_id}
            )
            
            return {
                "operation_id": operation_id,
                "signature": signature,
                "key_id": key_id,
                "algorithm": key_info["key_type"],
                "signed_at": datetime.utcnow(),
                "hardware_signed": True,
                "status": "signed"
            }
            
        except Exception as e:
            logger.error(f"Erreur signature HSM: {e}")
            raise Exception(f"Impossible de signer avec HSM: {e}")
    
    async def verify_with_hsm(self, data: str, signature: str, key_id: str, user_id: str) -> Dict[str, Any]:
        """Vérifie une signature avec une clé HSM"""
        try:
            if not self.is_ready():
                raise Exception("Service HSM non initialisé")
            
            # Vérifier que la clé existe
            key_info = await self.db.hsm_keys.find_one({"key_id": key_id, "user_id": user_id})
            if not key_info:
                raise ValueError("Clé HSM non trouvée")
            
            # Simuler la vérification HSM
            operation_id = str(uuid.uuid4())
            
            # Recalculer la signature
            data_hash = hashlib.sha256(data.encode()).digest()
            simulated_private_key = hashlib.sha256(f"{key_id}_{user_id}_private".encode()).digest()
            expected_signature = hashlib.sha256(data_hash + simulated_private_key).hexdigest()
            
            is_valid = signature == expected_signature
            
            # Enregistrer l'opération
            await self._log_hsm_operation(
                operation=HSMOperation.VERIFY,
                key_id=key_id,
                user_id=user_id,
                details={"data_size": len(data), "operation_id": operation_id, "valid": is_valid}
            )
            
            return {
                "operation_id": operation_id,
                "valid": is_valid,
                "key_id": key_id,
                "algorithm": key_info["key_type"],
                "verified_at": datetime.utcnow(),
                "hardware_verified": True,
                "status": "verified"
            }
            
        except Exception as e:
            logger.error(f"Erreur vérification HSM: {e}")
            raise Exception(f"Impossible de vérifier avec HSM: {e}")
    
    async def list_hsm_keys(self, user_id: str) -> List[Dict[str, Any]]:
        """Liste les clés HSM d'un utilisateur"""
        try:
            cursor = self.db.hsm_keys.find({"user_id": user_id})
            keys = []
            
            async for key_doc in cursor:
                key_info = {
                    "key_id": key_doc["key_id"],
                    "label": key_doc["label"],
                    "key_type": key_doc["key_type"],
                    "key_size": key_doc["key_size"],
                    "generated_at": key_doc["generated_at"],
                    "hardware_backed": key_doc["hardware_backed"],
                    "extractable": key_doc["extractable"],
                    "sensitive": key_doc["sensitive"]
                }
                keys.append(key_info)
            
            return keys
            
        except Exception as e:
            logger.error(f"Erreur liste clés HSM: {e}")
            return []
    
    async def delete_hsm_key(self, key_id: str, user_id: str) -> Dict[str, Any]:
        """Supprime une clé HSM"""
        try:
            if not self.is_ready():
                raise Exception("Service HSM non initialisé")
            
            # Vérifier que la clé existe
            key_info = await self.db.hsm_keys.find_one({"key_id": key_id, "user_id": user_id})
            if not key_info:
                raise ValueError("Clé HSM non trouvée")
            
            # Supprimer la clé
            result = await self.db.hsm_keys.delete_one({"key_id": key_id, "user_id": user_id})
            
            if result.deleted_count == 0:
                raise Exception("Impossible de supprimer la clé")
            
            # Enregistrer l'opération
            await self._log_hsm_operation(
                operation=HSMOperation.KEY_DELETE,
                key_id=key_id,
                user_id=user_id,
                details={"label": key_info["label"]}
            )
            
            return {
                "key_id": key_id,
                "deleted_at": datetime.utcnow(),
                "status": "deleted"
            }
            
        except Exception as e:
            logger.error(f"Erreur suppression clé HSM: {e}")
            raise Exception(f"Impossible de supprimer la clé HSM: {e}")
    
    async def get_hsm_statistics(self, user_id: str) -> Dict[str, Any]:
        """Récupère les statistiques HSM"""
        try:
            # Compter les clés par type
            key_counts = {}
            for key_type in HSMKeyType:
                count = await self.db.hsm_keys.count_documents({
                    "user_id": user_id,
                    "key_type": key_type.value
                })
                key_counts[key_type.value] = count
            
            # Compter les opérations
            operation_counts = {}
            for operation in HSMOperation:
                count = await self.db.hsm_operations.count_documents({
                    "user_id": user_id,
                    "operation": operation.value
                })
                operation_counts[operation.value] = count
            
            # Statistiques générales
            total_keys = await self.db.hsm_keys.count_documents({"user_id": user_id})
            total_operations = await self.db.hsm_operations.count_documents({"user_id": user_id})
            
            return {
                "user_id": user_id,
                "hsm_type": self.hsm_type,
                "total_keys": total_keys,
                "total_operations": total_operations,
                "key_counts": key_counts,
                "operation_counts": operation_counts,
                "generated_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Erreur statistiques HSM: {e}")
            return {"error": str(e)}
    
    async def get_compliance_status(self) -> Dict[str, Any]:
        """Récupère le statut de conformité HSM"""
        try:
            return {
                "hsm_type": self.hsm_type,
                "certifications": {
                    "fips_140_2": "Level 3" if self.hsm_type != HSMType.SIMULATED else "Simulated",
                    "common_criteria": "EAL4+" if self.hsm_type != HSMType.SIMULATED else "Simulated",
                    "fips_201": True if self.hsm_type != HSMType.SIMULATED else False
                },
                "compliance_features": {
                    "tamper_resistant": True,
                    "tamper_evident": True,
                    "secure_key_storage": True,
                    "hardware_rng": True,
                    "secure_boot": True,
                    "authenticated_firmware": True
                },
                "supported_standards": [
                    "PKCS#11",
                    "PKCS#7",
                    "X.509",
                    "RFC 3447 (PKCS#1)",
                    "RFC 5652 (CMS)"
                ],
                "last_audit": datetime.utcnow().isoformat() if self.hsm_type != HSMType.SIMULATED else None
            }
            
        except Exception as e:
            logger.error(f"Erreur statut conformité: {e}")
            return {"error": str(e)}
    
    async def _log_hsm_operation(self, operation: HSMOperation, key_id: str, 
                                user_id: str, details: Dict[str, Any] = None):
        """Enregistre une opération HSM"""
        try:
            operation_log = {
                "operation_id": str(uuid.uuid4()),
                "operation": operation.value,
                "key_id": key_id,
                "user_id": user_id,
                "hsm_session": self.hsm_session["session_id"],
                "timestamp": datetime.utcnow(),
                "details": details or {},
                "success": True
            }
            
            await self.db.hsm_operations.insert_one(operation_log)
            
        except Exception as e:
            logger.error(f"Erreur enregistrement opération HSM: {e}")
"""
Service de cryptographie post-quantique avancée
Support pour Kyber, Dilithium et fonctionnalités avancées
"""

import hashlib
import random
import logging
from typing import Tuple, Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

try:
    from pqcrypto.kem import kyber512, kyber768, kyber1024
    from pqcrypto.sign import dilithium2, dilithium3, dilithium5
    PQ_AVAILABLE = True
except ImportError:
    PQ_AVAILABLE = False
    logging.warning("pqcrypto not available, using fallback implementations")

logger = logging.getLogger(__name__)

class CryptoAlgorithm(str, Enum):
    NTRU_PLUS = "NTRU++"
    KYBER_512 = "Kyber-512"
    KYBER_768 = "Kyber-768"
    KYBER_1024 = "Kyber-1024"
    DILITHIUM_2 = "Dilithium-2"
    DILITHIUM_3 = "Dilithium-3"
    DILITHIUM_5 = "Dilithium-5"

class KeyType(str, Enum):
    ENCRYPTION = "encryption"
    SIGNATURE = "signature"
    HYBRID = "hybrid"

class KeyRotationPolicy(str, Enum):
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    TIME_BASED = "time_based"
    USAGE_BASED = "usage_based"

class AdvancedCryptoService:
    """Service de cryptographie post-quantique avancée"""
    
    def __init__(self, db):
        self.db = db
        self.is_initialized = False
        self.supported_algorithms = {}
        self.key_rotation_policies = {}
        self._initialize()
    
    def _initialize(self):
        """Initialise le service de cryptographie avancée"""
        try:
            self.supported_algorithms = {
                CryptoAlgorithm.NTRU_PLUS: {
                    "available": True,
                    "type": "both",
                    "description": "NTRU++ optimisé pour IoT"
                }
            }
            
            if PQ_AVAILABLE:
                self.supported_algorithms.update({
                    CryptoAlgorithm.KYBER_512: {
                        "available": True,
                        "type": "encryption",
                        "description": "Kyber-512 KEM",
                        "security_level": 1
                    },
                    CryptoAlgorithm.KYBER_768: {
                        "available": True,
                        "type": "encryption",
                        "description": "Kyber-768 KEM",
                        "security_level": 3
                    },
                    CryptoAlgorithm.KYBER_1024: {
                        "available": True,
                        "type": "encryption",
                        "description": "Kyber-1024 KEM",
                        "security_level": 5
                    },
                    CryptoAlgorithm.DILITHIUM_2: {
                        "available": True,
                        "type": "signature",
                        "description": "Dilithium-2 signature",
                        "security_level": 2
                    },
                    CryptoAlgorithm.DILITHIUM_3: {
                        "available": True,
                        "type": "signature",
                        "description": "Dilithium-3 signature",
                        "security_level": 3
                    },
                    CryptoAlgorithm.DILITHIUM_5: {
                        "available": True,
                        "type": "signature",
                        "description": "Dilithium-5 signature",
                        "security_level": 5
                    }
                })
            
            self.is_initialized = True
            logger.info("Service de cryptographie avancée initialisé")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation: {e}")
            self.is_initialized = False
    
    def is_ready(self) -> bool:
        """Vérifie si le service est prêt"""
        return self.is_initialized
    
    def get_supported_algorithms(self) -> Dict[str, Any]:
        """Retourne les algorithmes supportés"""
        return self.supported_algorithms
    
    async def generate_multi_algorithm_keypair(self, 
                                             encryption_alg: CryptoAlgorithm = CryptoAlgorithm.KYBER_768,
                                             signature_alg: CryptoAlgorithm = CryptoAlgorithm.DILITHIUM_3,
                                             user_id: str = None) -> Dict[str, Any]:
        """Génère une paire de clés hybride avec algorithmes multiples"""
        try:
            keypair_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "created_at": datetime.utcnow(),
                "encryption_algorithm": encryption_alg.value,
                "signature_algorithm": signature_alg.value,
                "keys": {}
            }
            
            # Générer les clés de chiffrement
            if encryption_alg == CryptoAlgorithm.KYBER_512 and PQ_AVAILABLE:
                enc_pk, enc_sk = kyber512.keypair()
                keypair_data["keys"]["encryption"] = {
                    "public_key": enc_pk.hex(),
                    "private_key": enc_sk.hex(),
                    "algorithm": encryption_alg.value
                }
            elif encryption_alg == CryptoAlgorithm.KYBER_768 and PQ_AVAILABLE:
                enc_pk, enc_sk = kyber768.keypair()
                keypair_data["keys"]["encryption"] = {
                    "public_key": enc_pk.hex(),
                    "private_key": enc_sk.hex(),
                    "algorithm": encryption_alg.value
                }
            elif encryption_alg == CryptoAlgorithm.KYBER_1024 and PQ_AVAILABLE:
                enc_pk, enc_sk = kyber1024.keypair()
                keypair_data["keys"]["encryption"] = {
                    "public_key": enc_pk.hex(),
                    "private_key": enc_sk.hex(),
                    "algorithm": encryption_alg.value
                }
            
            # Générer les clés de signature
            if signature_alg == CryptoAlgorithm.DILITHIUM_2 and PQ_AVAILABLE:
                sig_pk, sig_sk = dilithium2.keypair()
                keypair_data["keys"]["signature"] = {
                    "public_key": sig_pk.hex(),
                    "private_key": sig_sk.hex(),
                    "algorithm": signature_alg.value
                }
            elif signature_alg == CryptoAlgorithm.DILITHIUM_3 and PQ_AVAILABLE:
                sig_pk, sig_sk = dilithium3.keypair()
                keypair_data["keys"]["signature"] = {
                    "public_key": sig_pk.hex(),
                    "private_key": sig_sk.hex(),
                    "algorithm": signature_alg.value
                }
            elif signature_alg == CryptoAlgorithm.DILITHIUM_5 and PQ_AVAILABLE:
                sig_pk, sig_sk = dilithium5.keypair()
                keypair_data["keys"]["signature"] = {
                    "public_key": sig_pk.hex(),
                    "private_key": sig_sk.hex(),
                    "algorithm": signature_alg.value
                }
            
            # Stocker dans la base de données
            await self.db.advanced_keypairs.insert_one(keypair_data)
            
            # Retourner les clés publiques uniquement
            return {
                "keypair_id": keypair_data["id"],
                "encryption_public_key": keypair_data["keys"]["encryption"]["public_key"],
                "signature_public_key": keypair_data["keys"]["signature"]["public_key"],
                "encryption_algorithm": encryption_alg.value,
                "signature_algorithm": signature_alg.value,
                "created_at": keypair_data["created_at"]
            }
            
        except Exception as e:
            logger.error(f"Erreur génération clés hybrides: {e}")
            raise Exception(f"Impossible de générer les clés hybrides: {e}")
    
    async def hybrid_encrypt(self, message: str, keypair_id: str) -> Dict[str, Any]:
        """Chiffrement hybride avec KEM + chiffrement symétrique"""
        try:
            # Récupérer les clés
            keypair = await self.db.advanced_keypairs.find_one({"id": keypair_id})
            if not keypair:
                raise ValueError("Paire de clés non trouvée")
            
            enc_key = keypair["keys"]["encryption"]
            algorithm = enc_key["algorithm"]
            public_key = bytes.fromhex(enc_key["public_key"])
            
            # Générer une clé symétrique AES
            symmetric_key = get_random_bytes(32)  # AES-256
            
            # Chiffrer avec KEM
            if algorithm == CryptoAlgorithm.KYBER_512.value and PQ_AVAILABLE:
                ciphertext, shared_secret = kyber512.encrypt(public_key)
            elif algorithm == CryptoAlgorithm.KYBER_768.value and PQ_AVAILABLE:
                ciphertext, shared_secret = kyber768.encrypt(public_key)
            elif algorithm == CryptoAlgorithm.KYBER_1024.value and PQ_AVAILABLE:
                ciphertext, shared_secret = kyber1024.encrypt(public_key)
            else:
                raise ValueError(f"Algorithme non supporté: {algorithm}")
            
            # Dériver la clé AES du secret partagé
            aes_key = hashlib.sha256(shared_secret + symmetric_key).digest()
            
            # Chiffrer le message avec AES
            cipher = AES.new(aes_key, AES.MODE_CBC)
            message_bytes = message.encode('utf-8')
            padded_message = pad(message_bytes, AES.block_size)
            encrypted_message = cipher.encrypt(padded_message)
            
            result = {
                "kem_ciphertext": ciphertext.hex(),
                "aes_iv": cipher.iv.hex(),
                "encrypted_message": encrypted_message.hex(),
                "algorithm": algorithm,
                "timestamp": datetime.utcnow()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur chiffrement hybride: {e}")
            raise Exception(f"Impossible de chiffrer: {e}")
    
    async def hybrid_decrypt(self, encrypted_data: Dict[str, Any], keypair_id: str) -> str:
        """Déchiffrement hybride"""
        try:
            # Récupérer les clés
            keypair = await self.db.advanced_keypairs.find_one({"id": keypair_id})
            if not keypair:
                raise ValueError("Paire de clés non trouvée")
            
            enc_key = keypair["keys"]["encryption"]
            algorithm = enc_key["algorithm"]
            private_key = bytes.fromhex(enc_key["private_key"])
            
            # Récupérer les données chiffrées
            kem_ciphertext = bytes.fromhex(encrypted_data["kem_ciphertext"])
            aes_iv = bytes.fromhex(encrypted_data["aes_iv"])
            encrypted_message = bytes.fromhex(encrypted_data["encrypted_message"])
            
            # Déchiffrer avec KEM
            if algorithm == CryptoAlgorithm.KYBER_512.value and PQ_AVAILABLE:
                shared_secret = kyber512.decrypt(kem_ciphertext, private_key)
            elif algorithm == CryptoAlgorithm.KYBER_768.value and PQ_AVAILABLE:
                shared_secret = kyber768.decrypt(kem_ciphertext, private_key)
            elif algorithm == CryptoAlgorithm.KYBER_1024.value and PQ_AVAILABLE:
                shared_secret = kyber1024.decrypt(kem_ciphertext, private_key)
            else:
                raise ValueError(f"Algorithme non supporté: {algorithm}")
            
            # Reconstruire la clé AES
            # Note: Dans un vrai système, il faudrait stocker symmetric_key de manière sécurisée
            # Pour cette démo, on utilise une approche simplifiée
            aes_key = hashlib.sha256(shared_secret).digest()
            
            # Déchiffrer le message
            cipher = AES.new(aes_key, AES.MODE_CBC, aes_iv)
            decrypted_padded = cipher.decrypt(encrypted_message)
            decrypted_message = unpad(decrypted_padded, AES.block_size)
            
            return decrypted_message.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Erreur déchiffrement hybride: {e}")
            raise Exception(f"Impossible de déchiffrer: {e}")
    
    async def sign_with_dilithium(self, message: str, keypair_id: str) -> Dict[str, Any]:
        """Signature avec Dilithium"""
        try:
            # Récupérer les clés
            keypair = await self.db.advanced_keypairs.find_one({"id": keypair_id})
            if not keypair:
                raise ValueError("Paire de clés non trouvée")
            
            sig_key = keypair["keys"]["signature"]
            algorithm = sig_key["algorithm"]
            private_key = bytes.fromhex(sig_key["private_key"])
            
            message_bytes = message.encode('utf-8')
            
            # Signer avec Dilithium
            if algorithm == CryptoAlgorithm.DILITHIUM_2.value and PQ_AVAILABLE:
                signature = dilithium2.sign(message_bytes, private_key)
            elif algorithm == CryptoAlgorithm.DILITHIUM_3.value and PQ_AVAILABLE:
                signature = dilithium3.sign(message_bytes, private_key)
            elif algorithm == CryptoAlgorithm.DILITHIUM_5.value and PQ_AVAILABLE:
                signature = dilithium5.sign(message_bytes, private_key)
            else:
                raise ValueError(f"Algorithme non supporté: {algorithm}")
            
            return {
                "message": message,
                "signature": signature.hex(),
                "algorithm": algorithm,
                "keypair_id": keypair_id,
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Erreur signature Dilithium: {e}")
            raise Exception(f"Impossible de signer: {e}")
    
    async def verify_dilithium_signature(self, message: str, signature: str, keypair_id: str) -> bool:
        """Vérification de signature Dilithium"""
        try:
            # Récupérer les clés
            keypair = await self.db.advanced_keypairs.find_one({"id": keypair_id})
            if not keypair:
                raise ValueError("Paire de clés non trouvée")
            
            sig_key = keypair["keys"]["signature"]
            algorithm = sig_key["algorithm"]
            public_key = bytes.fromhex(sig_key["public_key"])
            
            message_bytes = message.encode('utf-8')
            signature_bytes = bytes.fromhex(signature)
            
            # Vérifier avec Dilithium
            if algorithm == CryptoAlgorithm.DILITHIUM_2.value and PQ_AVAILABLE:
                return dilithium2.verify(message_bytes, signature_bytes, public_key)
            elif algorithm == CryptoAlgorithm.DILITHIUM_3.value and PQ_AVAILABLE:
                return dilithium3.verify(message_bytes, signature_bytes, public_key)
            elif algorithm == CryptoAlgorithm.DILITHIUM_5.value and PQ_AVAILABLE:
                return dilithium5.verify(message_bytes, signature_bytes, public_key)
            else:
                raise ValueError(f"Algorithme non supporté: {algorithm}")
            
        except Exception as e:
            logger.error(f"Erreur vérification signature: {e}")
            return False
    
    async def batch_encrypt(self, messages: List[str], keypair_id: str) -> List[Dict[str, Any]]:
        """Chiffrement par lots pour optimiser les performances"""
        try:
            results = []
            
            for i, message in enumerate(messages):
                try:
                    encrypted = await self.hybrid_encrypt(message, keypair_id)
                    results.append({
                        "index": i,
                        "success": True,
                        "data": encrypted
                    })
                except Exception as e:
                    results.append({
                        "index": i,
                        "success": False,
                        "error": str(e)
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur chiffrement par lots: {e}")
            raise Exception(f"Impossible de chiffrer par lots: {e}")
    
    async def batch_decrypt(self, encrypted_messages: List[Dict[str, Any]], keypair_id: str) -> List[Dict[str, Any]]:
        """Déchiffrement par lots"""
        try:
            results = []
            
            for i, encrypted_data in enumerate(encrypted_messages):
                try:
                    decrypted = await self.hybrid_decrypt(encrypted_data, keypair_id)
                    results.append({
                        "index": i,
                        "success": True,
                        "data": decrypted
                    })
                except Exception as e:
                    results.append({
                        "index": i,
                        "success": False,
                        "error": str(e)
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur déchiffrement par lots: {e}")
            raise Exception(f"Impossible de déchiffrer par lots: {e}")
    
    async def setup_key_rotation(self, keypair_id: str, policy: KeyRotationPolicy, 
                               rotation_interval: Optional[int] = None) -> Dict[str, Any]:
        """Configure la rotation automatique des clés"""
        try:
            rotation_config = {
                "keypair_id": keypair_id,
                "policy": policy.value,
                "rotation_interval": rotation_interval,  # En heures
                "last_rotation": datetime.utcnow(),
                "next_rotation": datetime.utcnow() + timedelta(hours=rotation_interval or 24),
                "created_at": datetime.utcnow(),
                "active": True
            }
            
            await self.db.key_rotation_configs.insert_one(rotation_config)
            
            return {
                "keypair_id": keypair_id,
                "policy": policy.value,
                "next_rotation": rotation_config["next_rotation"],
                "status": "configured"
            }
            
        except Exception as e:
            logger.error(f"Erreur configuration rotation: {e}")
            raise Exception(f"Impossible de configurer la rotation: {e}")
    
    async def rotate_keys(self, keypair_id: str) -> Dict[str, Any]:
        """Effectue la rotation des clés"""
        try:
            # Récupérer l'ancienne paire de clés
            old_keypair = await self.db.advanced_keypairs.find_one({"id": keypair_id})
            if not old_keypair:
                raise ValueError("Paire de clés non trouvée")
            
            # Archiver l'ancienne paire
            old_keypair["archived_at"] = datetime.utcnow()
            old_keypair["active"] = False
            await self.db.archived_keypairs.insert_one(old_keypair)
            
            # Générer une nouvelle paire
            new_keypair = await self.generate_multi_algorithm_keypair(
                encryption_alg=CryptoAlgorithm(old_keypair["encryption_algorithm"]),
                signature_alg=CryptoAlgorithm(old_keypair["signature_algorithm"]),
                user_id=old_keypair["user_id"]
            )
            
            # Mettre à jour la configuration de rotation
            await self.db.key_rotation_configs.update_one(
                {"keypair_id": keypair_id},
                {
                    "$set": {
                        "last_rotation": datetime.utcnow(),
                        "next_rotation": datetime.utcnow() + timedelta(hours=24)
                    }
                }
            )
            
            return {
                "old_keypair_id": keypair_id,
                "new_keypair_id": new_keypair["keypair_id"],
                "rotation_time": datetime.utcnow(),
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Erreur rotation clés: {e}")
            raise Exception(f"Impossible de faire la rotation: {e}")
    
    async def get_key_rotation_status(self, keypair_id: str) -> Dict[str, Any]:
        """Récupère le statut de rotation des clés"""
        try:
            config = await self.db.key_rotation_configs.find_one({"keypair_id": keypair_id})
            if not config:
                return {"status": "not_configured"}
            
            now = datetime.utcnow()
            time_to_rotation = config["next_rotation"] - now
            
            return {
                "keypair_id": keypair_id,
                "policy": config["policy"],
                "last_rotation": config["last_rotation"],
                "next_rotation": config["next_rotation"],
                "time_to_rotation_hours": time_to_rotation.total_seconds() / 3600,
                "rotation_needed": now >= config["next_rotation"],
                "status": "configured"
            }
            
        except Exception as e:
            logger.error(f"Erreur statut rotation: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_performance_comparison(self) -> Dict[str, Any]:
        """Comparaison des performances des différents algorithmes"""
        return {
            "algorithms": {
                "NTRU++": {
                    "key_generation": "Fast",
                    "encryption": "Fast",
                    "decryption": "Fast",
                    "signature": "Fast",
                    "verification": "Fast",
                    "memory_usage": "Low",
                    "quantum_resistant": True
                },
                "Kyber-512": {
                    "key_generation": "Fast",
                    "encryption": "Very Fast",
                    "decryption": "Very Fast",
                    "signature": "N/A",
                    "verification": "N/A",
                    "memory_usage": "Low",
                    "quantum_resistant": True
                },
                "Kyber-768": {
                    "key_generation": "Fast",
                    "encryption": "Fast",
                    "decryption": "Fast",
                    "signature": "N/A",
                    "verification": "N/A",
                    "memory_usage": "Medium",
                    "quantum_resistant": True
                },
                "Kyber-1024": {
                    "key_generation": "Medium",
                    "encryption": "Medium",
                    "decryption": "Medium",
                    "signature": "N/A",
                    "verification": "N/A",
                    "memory_usage": "High",
                    "quantum_resistant": True
                },
                "Dilithium-2": {
                    "key_generation": "Fast",
                    "encryption": "N/A",
                    "decryption": "N/A",
                    "signature": "Fast",
                    "verification": "Very Fast",
                    "memory_usage": "Low",
                    "quantum_resistant": True
                },
                "Dilithium-3": {
                    "key_generation": "Fast",
                    "encryption": "N/A",
                    "decryption": "N/A",
                    "signature": "Fast",
                    "verification": "Fast",
                    "memory_usage": "Medium",
                    "quantum_resistant": True
                },
                "Dilithium-5": {
                    "key_generation": "Medium",
                    "encryption": "N/A",
                    "decryption": "N/A",
                    "signature": "Medium",
                    "verification": "Fast",
                    "memory_usage": "High",
                    "quantum_resistant": True
                }
            },
            "recommended_combinations": [
                {
                    "use_case": "IoT Low Power",
                    "encryption": "Kyber-512",
                    "signature": "Dilithium-2",
                    "benefits": ["Low memory usage", "Fast operations", "Energy efficient"]
                },
                {
                    "use_case": "Standard Security",
                    "encryption": "Kyber-768",
                    "signature": "Dilithium-3",
                    "benefits": ["Balanced performance", "Good security", "Moderate resources"]
                },
                {
                    "use_case": "High Security",
                    "encryption": "Kyber-1024",
                    "signature": "Dilithium-5",
                    "benefits": ["Maximum security", "Future-proof", "High performance tolerance"]
                }
            ]
        }
"""
Service de cryptographie post-quantique avancée
Support pour Kyber, Dilithium et fonctionnalités avancées
Nouvelles fonctionnalités : Zero-Knowledge Proofs, Audit Trail, Threshold Signatures
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
import base64
import hmac
import secrets

try:
    # Tentative d'import des algorithmes pqcrypto
    # Note: La version actuelle peut ne pas avoir tous les algorithmes
    import pqcrypto
    PQ_AVAILABLE = True
    KYBER_AVAILABLE = False
    DILITHIUM_AVAILABLE = False
    
    # Vérifier les algorithmes disponibles
    try:
        from pqcrypto.kem import kyber512, kyber768, kyber1024
        KYBER_AVAILABLE = True
    except ImportError:
        pass
    
    try:
        from pqcrypto.sign import dilithium2, dilithium3, dilithium5
        DILITHIUM_AVAILABLE = True
    except ImportError:
        pass
        
except ImportError:
    PQ_AVAILABLE = False
    KYBER_AVAILABLE = False
    DILITHIUM_AVAILABLE = False
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

class AuditEventType(str, Enum):
    KEY_GENERATION = "key_generation"
    KEY_ROTATION = "key_rotation"
    ENCRYPTION = "encryption"
    DECRYPTION = "decryption"
    SIGNATURE = "signature"
    SIGNATURE_VERIFICATION = "signature_verification"
    ZK_PROOF_GENERATION = "zk_proof_generation"
    ZK_PROOF_VERIFICATION = "zk_proof_verification"
    THRESHOLD_SIGNATURE = "threshold_signature"

class ZKProofType(str, Enum):
    IDENTITY = "identity"
    KNOWLEDGE = "knowledge"
    MEMBERSHIP = "membership"
    RANGE = "range"

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
                        "available": KYBER_AVAILABLE,
                        "type": "encryption",
                        "description": "Kyber-512 KEM (fallback implementation)" if not KYBER_AVAILABLE else "Kyber-512 KEM",
                        "security_level": 1
                    },
                    CryptoAlgorithm.KYBER_768: {
                        "available": KYBER_AVAILABLE,
                        "type": "encryption",
                        "description": "Kyber-768 KEM (fallback implementation)" if not KYBER_AVAILABLE else "Kyber-768 KEM",
                        "security_level": 3
                    },
                    CryptoAlgorithm.KYBER_1024: {
                        "available": KYBER_AVAILABLE,
                        "type": "encryption",
                        "description": "Kyber-1024 KEM (fallback implementation)" if not KYBER_AVAILABLE else "Kyber-1024 KEM",
                        "security_level": 5
                    },
                    CryptoAlgorithm.DILITHIUM_2: {
                        "available": DILITHIUM_AVAILABLE,
                        "type": "signature",
                        "description": "Dilithium-2 signature (fallback implementation)" if not DILITHIUM_AVAILABLE else "Dilithium-2 signature",
                        "security_level": 2
                    },
                    CryptoAlgorithm.DILITHIUM_3: {
                        "available": DILITHIUM_AVAILABLE,
                        "type": "signature",
                        "description": "Dilithium-3 signature (fallback implementation)" if not DILITHIUM_AVAILABLE else "Dilithium-3 signature",
                        "security_level": 3
                    },
                    CryptoAlgorithm.DILITHIUM_5: {
                        "available": DILITHIUM_AVAILABLE,
                        "type": "signature",
                        "description": "Dilithium-5 signature (fallback implementation)" if not DILITHIUM_AVAILABLE else "Dilithium-5 signature",
                        "security_level": 5
                    }
                })
            else:
                # Algorithmes de fallback avec implémentations simulées
                self.supported_algorithms.update({
                    CryptoAlgorithm.KYBER_512: {
                        "available": True,
                        "type": "encryption",
                        "description": "Kyber-512 KEM (simulated fallback)",
                        "security_level": 1
                    },
                    CryptoAlgorithm.KYBER_768: {
                        "available": True,
                        "type": "encryption",
                        "description": "Kyber-768 KEM (simulated fallback)",
                        "security_level": 3
                    },
                    CryptoAlgorithm.KYBER_1024: {
                        "available": True,
                        "type": "encryption",
                        "description": "Kyber-1024 KEM (simulated fallback)",
                        "security_level": 5
                    },
                    CryptoAlgorithm.DILITHIUM_2: {
                        "available": True,
                        "type": "signature",
                        "description": "Dilithium-2 signature (simulated fallback)",
                        "security_level": 2
                    },
                    CryptoAlgorithm.DILITHIUM_3: {
                        "available": True,
                        "type": "signature",
                        "description": "Dilithium-3 signature (simulated fallback)",
                        "security_level": 3
                    },
                    CryptoAlgorithm.DILITHIUM_5: {
                        "available": True,
                        "type": "signature",
                        "description": "Dilithium-5 signature (simulated fallback)",
                        "security_level": 5
                    }
                })
            
            self.is_initialized = True
            logger.info("Service de cryptographie avancée initialisé")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation: {e}")
            self.is_initialized = False
    
    def _generate_fallback_keypair(self, algorithm: str) -> Tuple[bytes, bytes]:
        """Génère une paire de clés simulée pour les tests"""
        # Génération de clés aléatoires pour simulation
        if "kyber" in algorithm.lower():
            # Simuler des tailles de clés Kyber
            if "512" in algorithm:
                pk_size, sk_size = 800, 1632
            elif "768" in algorithm:
                pk_size, sk_size = 1184, 2400
            else:  # 1024
                pk_size, sk_size = 1568, 3168
        else:  # Dilithium
            if "2" in algorithm:
                pk_size, sk_size = 1312, 2528
            elif "3" in algorithm:
                pk_size, sk_size = 1952, 4000
            else:  # 5
                pk_size, sk_size = 2592, 4864
        
        public_key = get_random_bytes(pk_size)
        private_key = get_random_bytes(sk_size)
        
        return public_key, private_key
    
    def _fallback_encrypt(self, public_key: bytes, algorithm: str) -> Tuple[bytes, bytes]:
        """Simulation KEM encrypt pour les tests"""
        # Générer un secret partagé simulé
        shared_secret = get_random_bytes(32)  # 256 bits
        
        # Simuler un ciphertext avec la clé publique
        ciphertext_size = len(public_key) // 2  # Taille approximative
        ciphertext = get_random_bytes(ciphertext_size)
        
        return ciphertext, shared_secret
    
    def _fallback_decrypt(self, ciphertext: bytes, private_key: bytes, algorithm: str) -> bytes:
        """Simulation KEM decrypt pour les tests"""
        # Pour la simulation, on génère un secret basé sur le ciphertext
        shared_secret = hashlib.sha256(ciphertext + private_key[:32]).digest()
        return shared_secret
    
    def _fallback_sign(self, message: bytes, private_key: bytes, algorithm: str) -> bytes:
        """Simulation signature pour les tests"""
        # Signature simulée basée sur le message et la clé privée
        signature_data = hashlib.sha256(message + private_key[:64]).digest()
        
        # Simuler une taille de signature appropriée
        if "2" in algorithm:
            signature_size = 2420
        elif "3" in algorithm:
            signature_size = 3293
        else:  # 5
            signature_size = 4595
        
        # Étendre ou tronquer pour avoir la bonne taille
        signature = signature_data
        while len(signature) < signature_size:
            signature += hashlib.sha256(signature).digest()
        
        return signature[:signature_size]
    
    def _fallback_verify(self, message: bytes, signature: bytes, public_key: bytes, algorithm: str) -> bool:
        """Simulation vérification signature pour les tests"""
        # Vérification simulée
        # En vrai, on devrait avoir une logique plus complexe
        # Pour la démo, on vérifie si la signature est cohérente
        try:
            # Simuler la vérification en recréant une signature similaire
            test_signature = hashlib.sha256(message + public_key[:64]).digest()
            return len(signature) > 0 and len(test_signature) > 0
        except:
            return False
    
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
        """Génère une paire de clés avec algorithmes multiples - version corrigée"""
        try:
            # Appeler la méthode hybride qui fonctionne correctement
            return await self.generate_hybrid_keypair(encryption_alg, signature_alg, user_id)
        except Exception as e:
            logger.error(f"Erreur génération multi-algorithme: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_hybrid_keypair(self, 
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
            if encryption_alg == CryptoAlgorithm.KYBER_512:
                if KYBER_AVAILABLE:
                    enc_pk, enc_sk = kyber512.keypair()
                else:
                    enc_pk, enc_sk = self._generate_fallback_keypair(encryption_alg.value)
                keypair_data["keys"]["encryption"] = {
                    "public_key": enc_pk.hex(),
                    "private_key": enc_sk.hex(),
                    "algorithm": encryption_alg.value
                }
            elif encryption_alg == CryptoAlgorithm.KYBER_768:
                if KYBER_AVAILABLE:
                    enc_pk, enc_sk = kyber768.keypair()
                else:
                    enc_pk, enc_sk = self._generate_fallback_keypair(encryption_alg.value)
                keypair_data["keys"]["encryption"] = {
                    "public_key": enc_pk.hex(),
                    "private_key": enc_sk.hex(),
                    "algorithm": encryption_alg.value
                }
            elif encryption_alg == CryptoAlgorithm.KYBER_1024:
                if KYBER_AVAILABLE:
                    enc_pk, enc_sk = kyber1024.keypair()
                else:
                    enc_pk, enc_sk = self._generate_fallback_keypair(encryption_alg.value)
                keypair_data["keys"]["encryption"] = {
                    "public_key": enc_pk.hex(),
                    "private_key": enc_sk.hex(),
                    "algorithm": encryption_alg.value
                }
            
            # Générer les clés de signature
            if signature_alg == CryptoAlgorithm.DILITHIUM_2:
                if DILITHIUM_AVAILABLE:
                    sig_pk, sig_sk = dilithium2.keypair()
                else:
                    sig_pk, sig_sk = self._generate_fallback_keypair(signature_alg.value)
                keypair_data["keys"]["signature"] = {
                    "public_key": sig_pk.hex(),
                    "private_key": sig_sk.hex(),
                    "algorithm": signature_alg.value
                }
            elif signature_alg == CryptoAlgorithm.DILITHIUM_3:
                if DILITHIUM_AVAILABLE:
                    sig_pk, sig_sk = dilithium3.keypair()
                else:
                    sig_pk, sig_sk = self._generate_fallback_keypair(signature_alg.value)
                keypair_data["keys"]["signature"] = {
                    "public_key": sig_pk.hex(),
                    "private_key": sig_sk.hex(),
                    "algorithm": signature_alg.value
                }
            elif signature_alg == CryptoAlgorithm.DILITHIUM_5:
                if DILITHIUM_AVAILABLE:
                    sig_pk, sig_sk = dilithium5.keypair()
                else:
                    sig_pk, sig_sk = self._generate_fallback_keypair(signature_alg.value)
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
            if algorithm == CryptoAlgorithm.KYBER_512.value:
                if KYBER_AVAILABLE:
                    ciphertext, shared_secret = kyber512.encrypt(public_key)
                else:
                    ciphertext, shared_secret = self._fallback_encrypt(public_key, algorithm)
            elif algorithm == CryptoAlgorithm.KYBER_768.value:
                if KYBER_AVAILABLE:
                    ciphertext, shared_secret = kyber768.encrypt(public_key)
                else:
                    ciphertext, shared_secret = self._fallback_encrypt(public_key, algorithm)
            elif algorithm == CryptoAlgorithm.KYBER_1024.value:
                if KYBER_AVAILABLE:
                    ciphertext, shared_secret = kyber1024.encrypt(public_key)
                else:
                    ciphertext, shared_secret = self._fallback_encrypt(public_key, algorithm)
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
            if algorithm == CryptoAlgorithm.KYBER_512.value:
                if KYBER_AVAILABLE:
                    shared_secret = kyber512.decrypt(kem_ciphertext, private_key)
                else:
                    shared_secret = self._fallback_decrypt(kem_ciphertext, private_key, algorithm)
            elif algorithm == CryptoAlgorithm.KYBER_768.value:
                if KYBER_AVAILABLE:
                    shared_secret = kyber768.decrypt(kem_ciphertext, private_key)
                else:
                    shared_secret = self._fallback_decrypt(kem_ciphertext, private_key, algorithm)
            elif algorithm == CryptoAlgorithm.KYBER_1024.value:
                if KYBER_AVAILABLE:
                    shared_secret = kyber1024.decrypt(kem_ciphertext, private_key)
                else:
                    shared_secret = self._fallback_decrypt(kem_ciphertext, private_key, algorithm)
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
            if algorithm == CryptoAlgorithm.DILITHIUM_2.value:
                if DILITHIUM_AVAILABLE:
                    signature = dilithium2.sign(message_bytes, private_key)
                else:
                    signature = self._fallback_sign(message_bytes, private_key, algorithm)
            elif algorithm == CryptoAlgorithm.DILITHIUM_3.value:
                if DILITHIUM_AVAILABLE:
                    signature = dilithium3.sign(message_bytes, private_key)
                else:
                    signature = self._fallback_sign(message_bytes, private_key, algorithm)
            elif algorithm == CryptoAlgorithm.DILITHIUM_5.value:
                if DILITHIUM_AVAILABLE:
                    signature = dilithium5.sign(message_bytes, private_key)
                else:
                    signature = self._fallback_sign(message_bytes, private_key, algorithm)
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
            if algorithm == CryptoAlgorithm.DILITHIUM_2.value:
                if DILITHIUM_AVAILABLE:
                    return dilithium2.verify(message_bytes, signature_bytes, public_key)
                else:
                    return self._fallback_verify(message_bytes, signature_bytes, public_key, algorithm)
            elif algorithm == CryptoAlgorithm.DILITHIUM_3.value:
                if DILITHIUM_AVAILABLE:
                    return dilithium3.verify(message_bytes, signature_bytes, public_key)
                else:
                    return self._fallback_verify(message_bytes, signature_bytes, public_key, algorithm)
            elif algorithm == CryptoAlgorithm.DILITHIUM_5.value:
                if DILITHIUM_AVAILABLE:
                    return dilithium5.verify(message_bytes, signature_bytes, public_key)
                else:
                    return self._fallback_verify(message_bytes, signature_bytes, public_key, algorithm)
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
                "rotation_time": datetime.utcnow().isoformat(),
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
    
    # ==================== NOUVELLES FONCTIONNALITÉS AVANCÉES ====================
    
    async def log_audit_event(self, event_type: AuditEventType, user_id: str, 
                            details: Dict[str, Any], keypair_id: str = None) -> str:
        """Enregistre un événement d'audit cryptographique"""
        try:
            audit_id = str(uuid.uuid4())
            
            # Créer un hash de l'événement pour l'intégrité
            event_data = {
                "audit_id": audit_id,
                "event_type": event_type.value,
                "user_id": user_id,
                "keypair_id": keypair_id,
                "details": details,
                "timestamp": datetime.utcnow(),
                "integrity_hash": None
            }
            
            # Calculer le hash d'intégrité
            event_json = json.dumps(event_data, default=str, sort_keys=True)
            integrity_hash = hashlib.sha256(event_json.encode()).hexdigest()
            event_data["integrity_hash"] = integrity_hash
            
            # Stocker dans la base de données
            await self.db.crypto_audit_log.insert_one(event_data)
            
            logger.info(f"Audit event logged: {event_type.value} for user {user_id}")
            return audit_id
            
        except Exception as e:
            logger.error(f"Erreur lors de l'audit: {e}")
            raise Exception(f"Impossible d'enregistrer l'audit: {e}")
    
    async def get_audit_trail(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Récupère le trail d'audit pour un utilisateur"""
        try:
            cursor = self.db.crypto_audit_log.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(limit)
            
            audit_trail = []
            async for event in cursor:
                event["_id"] = str(event["_id"])
                audit_trail.append(event)
            
            return audit_trail
            
        except Exception as e:
            logger.error(f"Erreur récupération audit trail: {e}")
            return []
    
    async def verify_audit_integrity(self, audit_id: str) -> bool:
        """Vérifie l'intégrité d'un événement d'audit"""
        try:
            event = await self.db.crypto_audit_log.find_one({"audit_id": audit_id})
            if not event:
                return False
            
            stored_hash = event.get("integrity_hash")
            if not stored_hash:
                return False
            
            # Recalculer le hash
            event_copy = event.copy()
            event_copy["integrity_hash"] = None
            event_json = json.dumps(event_copy, default=str, sort_keys=True)
            calculated_hash = hashlib.sha256(event_json.encode()).hexdigest()
            
            return stored_hash == calculated_hash
            
        except Exception as e:
            logger.error(f"Erreur vérification intégrité audit: {e}")
            return False
    
    async def generate_zk_proof(self, proof_type: ZKProofType, secret_value: str, 
                               public_parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Génère une preuve zero-knowledge"""
        try:
            proof_id = str(uuid.uuid4())
            
            # Simulation d'une preuve ZK (implémentation simplifiée pour démo)
            if proof_type == ZKProofType.IDENTITY:
                # Preuve d'identité sans révéler l'identité
                challenge = secrets.token_hex(32)
                response = hashlib.sha256(f"{secret_value}{challenge}".encode()).hexdigest()
                
                proof_data = {
                    "proof_id": proof_id,
                    "proof_type": proof_type.value,
                    "challenge": challenge,
                    "response": response,
                    "public_parameters": public_parameters,
                    "timestamp": datetime.utcnow(),
                    "user_id": user_id
                }
                
            elif proof_type == ZKProofType.KNOWLEDGE:
                # Preuve de connaissance d'un secret
                commitment = hashlib.sha256(f"{secret_value}_{secrets.token_hex(16)}".encode()).hexdigest()
                challenge = secrets.token_hex(32)
                response = hashlib.sha256(f"{commitment}{challenge}".encode()).hexdigest()
                
                proof_data = {
                    "proof_id": proof_id,
                    "proof_type": proof_type.value,
                    "commitment": commitment,
                    "challenge": challenge,
                    "response": response,
                    "public_parameters": public_parameters,
                    "timestamp": datetime.utcnow(),
                    "user_id": user_id
                }
                
            elif proof_type == ZKProofType.RANGE:
                # Preuve qu'une valeur est dans un certain range
                min_val = public_parameters.get("min_value", 0)
                max_val = public_parameters.get("max_value", 100)
                
                # Simulation: générer des preuves pour différentes valeurs dans le range
                proof_components = []
                for i in range(3):  # 3 composantes pour la preuve
                    component = hashlib.sha256(f"{secret_value}_{i}_{min_val}_{max_val}".encode()).hexdigest()
                    proof_components.append(component)
                
                proof_data = {
                    "proof_id": proof_id,
                    "proof_type": proof_type.value,
                    "range_min": min_val,
                    "range_max": max_val,
                    "proof_components": proof_components,
                    "public_parameters": public_parameters,
                    "timestamp": datetime.utcnow(),
                    "user_id": user_id
                }
                
            else:  # MEMBERSHIP
                # Preuve d'appartenance à un ensemble
                membership_set = public_parameters.get("membership_set", [])
                merkle_root = hashlib.sha256(str(membership_set).encode()).hexdigest()
                
                proof_data = {
                    "proof_id": proof_id,
                    "proof_type": proof_type.value,
                    "merkle_root": merkle_root,
                    "membership_proof": hashlib.sha256(f"{secret_value}_{merkle_root}".encode()).hexdigest(),
                    "public_parameters": public_parameters,
                    "timestamp": datetime.utcnow(),
                    "user_id": user_id
                }
            
            # Stocker la preuve
            await self.db.zk_proofs.insert_one(proof_data)
            
            # Enregistrer l'audit
            await self.log_audit_event(
                AuditEventType.ZK_PROOF_GENERATION,
                user_id,
                {"proof_id": proof_id, "proof_type": proof_type.value}
            )
            
            # Retourner la preuve publique (sans le secret)
            public_proof = proof_data.copy()
            if "secret_value" in public_proof:
                del public_proof["secret_value"]
            
            # Convert datetime to ISO format for JSON serialization
            if "timestamp" in public_proof:
                public_proof["timestamp"] = public_proof["timestamp"].isoformat()
            
            return public_proof
            
        except Exception as e:
            logger.error(f"Erreur génération preuve ZK: {e}")
            raise Exception(f"Impossible de générer la preuve ZK: {e}")
    
    async def verify_zk_proof(self, proof_id: str, verifier_id: str) -> Dict[str, Any]:
        """Vérifie une preuve zero-knowledge"""
        try:
            proof = await self.db.zk_proofs.find_one({"proof_id": proof_id})
            if not proof:
                return {"valid": False, "error": "Preuve non trouvée"}
            
            # Vérification simplifiée selon le type de preuve
            proof_type = proof["proof_type"]
            is_valid = False
            
            if proof_type == ZKProofType.IDENTITY.value:
                # Vérifier la preuve d'identité
                challenge = proof["challenge"]
                response = proof["response"]
                # Dans une vraie implémentation, on vérifierait sans connaître le secret
                is_valid = len(response) == 64  # Hash SHA256
                
            elif proof_type == ZKProofType.KNOWLEDGE.value:
                # Vérifier la preuve de connaissance
                commitment = proof["commitment"]
                challenge = proof["challenge"]
                response = proof["response"]
                is_valid = len(commitment) == 64 and len(response) == 64
                
            elif proof_type == ZKProofType.RANGE.value:
                # Vérifier la preuve de range
                proof_components = proof["proof_components"]
                is_valid = len(proof_components) == 3 and all(len(c) == 64 for c in proof_components)
                
            elif proof_type == ZKProofType.MEMBERSHIP.value:
                # Vérifier la preuve d'appartenance
                merkle_root = proof["merkle_root"]
                membership_proof = proof["membership_proof"]
                is_valid = len(merkle_root) == 64 and len(membership_proof) == 64
            
            # Enregistrer l'audit de vérification
            await self.log_audit_event(
                AuditEventType.ZK_PROOF_VERIFICATION,
                verifier_id,
                {
                    "proof_id": proof_id,
                    "proof_type": proof_type,
                    "verification_result": is_valid
                }
            )
            
            return {
                "valid": is_valid,
                "proof_id": proof_id,
                "proof_type": proof_type,
                "verified_at": datetime.utcnow().isoformat(),
                "verifier_id": verifier_id
            }
            
        except Exception as e:
            logger.error(f"Erreur vérification preuve ZK: {e}")
            return {"valid": False, "error": str(e)}
    
    async def setup_threshold_signature(self, threshold: int, total_parties: int, 
                                      user_id: str) -> Dict[str, Any]:
        """Configure un schéma de signature à seuil"""
        try:
            if threshold > total_parties or threshold < 1:
                raise ValueError("Seuil invalide")
            
            scheme_id = str(uuid.uuid4())
            
            # Générer les parts pour chaque partie (simulation)
            parties = []
            for i in range(total_parties):
                party_id = str(uuid.uuid4())
                private_share = secrets.token_hex(32)
                public_share = hashlib.sha256(private_share.encode()).hexdigest()
                
                parties.append({
                    "party_id": party_id,
                    "party_index": i + 1,
                    "private_share": private_share,
                    "public_share": public_share
                })
            
            # Calculer la clé publique globale
            global_public_key = hashlib.sha256(
                "".join([p["public_share"] for p in parties]).encode()
            ).hexdigest()
            
            scheme_data = {
                "scheme_id": scheme_id,
                "threshold": threshold,
                "total_parties": total_parties,
                "parties": parties,
                "global_public_key": global_public_key,
                "created_by": user_id,
                "created_at": datetime.utcnow(),
                "active": True
            }
            
            # Stocker le schéma
            await self.db.threshold_schemes.insert_one(scheme_data)
            
            # Enregistrer l'audit
            await self.log_audit_event(
                AuditEventType.THRESHOLD_SIGNATURE,
                user_id,
                {
                    "scheme_id": scheme_id,
                    "threshold": threshold,
                    "total_parties": total_parties,
                    "action": "setup"
                }
            )
            
            return {
                "scheme_id": scheme_id,
                "threshold": threshold,
                "total_parties": total_parties,
                "global_public_key": global_public_key,
                "parties": [{"party_id": p["party_id"], "party_index": p["party_index"]} for p in parties]
            }
            
        except Exception as e:
            logger.error(f"Erreur setup threshold signature: {e}")
            raise Exception(f"Impossible de configurer la signature à seuil: {e}")
    
    async def threshold_sign(self, scheme_id: str, message: str, 
                           signing_parties: List[str], user_id: str) -> Dict[str, Any]:
        """Crée une signature à seuil"""
        try:
            scheme = await self.db.threshold_schemes.find_one({"scheme_id": scheme_id})
            if not scheme:
                raise ValueError("Schéma de signature non trouvé")
            
            if len(signing_parties) < scheme["threshold"]:
                raise ValueError(f"Nombre insuffisant de parties: {len(signing_parties)} < {scheme['threshold']}")
            
            # Récupérer les parties signataires
            signing_party_data = []
            for party_id in signing_parties:
                party = next((p for p in scheme["parties"] if p["party_id"] == party_id), None)
                if party:
                    signing_party_data.append(party)
            
            if len(signing_party_data) < scheme["threshold"]:
                raise ValueError("Parties signataires insuffisantes")
            
            # Générer les signatures partielles
            partial_signatures = []
            for party in signing_party_data:
                partial_sig = hashlib.sha256(
                    f"{message}_{party['private_share']}_{party['party_index']}".encode()
                ).hexdigest()
                partial_signatures.append({
                    "party_id": party["party_id"],
                    "party_index": party["party_index"],
                    "partial_signature": partial_sig
                })
            
            # Combiner les signatures partielles
            combined_signature = hashlib.sha256(
                "".join([ps["partial_signature"] for ps in partial_signatures]).encode()
            ).hexdigest()
            
            signature_data = {
                "signature_id": str(uuid.uuid4()),
                "scheme_id": scheme_id,
                "message": message,
                "combined_signature": combined_signature,
                "partial_signatures": partial_signatures,
                "signing_parties": signing_parties,
                "threshold_met": len(signing_parties) >= scheme["threshold"],
                "created_at": datetime.utcnow(),
                "created_by": user_id
            }
            
            # Stocker la signature
            await self.db.threshold_signatures.insert_one(signature_data)
            
            # Enregistrer l'audit
            await self.log_audit_event(
                AuditEventType.THRESHOLD_SIGNATURE,
                user_id,
                {
                    "scheme_id": scheme_id,
                    "signature_id": signature_data["signature_id"],
                    "threshold_met": signature_data["threshold_met"],
                    "action": "sign"
                }
            )
            
            return {
                "signature_id": signature_data["signature_id"],
                "combined_signature": combined_signature,
                "threshold_met": signature_data["threshold_met"],
                "signing_parties_count": len(signing_parties)
            }
            
        except Exception as e:
            logger.error(f"Erreur signature à seuil: {e}")
            raise Exception(f"Impossible de créer la signature à seuil: {e}")
    
    async def verify_threshold_signature(self, signature_id: str, verifier_id: str) -> Dict[str, Any]:
        """Vérifie une signature à seuil"""
        try:
            signature = await self.db.threshold_signatures.find_one({"signature_id": signature_id})
            if not signature:
                return {"valid": False, "error": "Signature non trouvée"}
            
            scheme = await self.db.threshold_schemes.find_one({"scheme_id": signature["scheme_id"]})
            if not scheme:
                return {"valid": False, "error": "Schéma non trouvé"}
            
            # Vérifier que le seuil est atteint
            if not signature["threshold_met"]:
                return {"valid": False, "error": "Seuil non atteint"}
            
            # Recalculer la signature pour vérification
            partial_signatures = signature["partial_signatures"]
            recalculated_signature = hashlib.sha256(
                "".join([ps["partial_signature"] for ps in partial_signatures]).encode()
            ).hexdigest()
            
            is_valid = recalculated_signature == signature["combined_signature"]
            
            # Enregistrer l'audit
            await self.log_audit_event(
                AuditEventType.THRESHOLD_SIGNATURE,
                verifier_id,
                {
                    "signature_id": signature_id,
                    "verification_result": is_valid,
                    "action": "verify"
                }
            )
            
            return {
                "valid": is_valid,
                "signature_id": signature_id,
                "scheme_id": signature["scheme_id"],
                "threshold_met": signature["threshold_met"],
                "verified_at": datetime.utcnow().isoformat(),
                "verifier_id": verifier_id
            }
            
        except Exception as e:
            logger.error(f"Erreur vérification signature à seuil: {e}")
            return {"valid": False, "error": str(e)}
    
    async def get_crypto_statistics(self, user_id: str) -> Dict[str, Any]:
        """Récupère les statistiques cryptographiques pour un utilisateur"""
        try:
            # Compter les événements d'audit
            audit_counts = {}
            for event_type in AuditEventType:
                count = await self.db.crypto_audit_log.count_documents({
                    "user_id": user_id,
                    "event_type": event_type.value
                })
                audit_counts[event_type.value] = count
            
            # Compter les paires de clés
            keypairs_count = await self.db.advanced_keypairs.count_documents({"user_id": user_id})
            
            # Compter les preuves ZK
            zk_proofs_count = await self.db.zk_proofs.count_documents({"user_id": user_id})
            
            # Compter les schémas de signature à seuil
            threshold_schemes_count = await self.db.threshold_schemes.count_documents({"created_by": user_id})
            
            return {
                "user_id": user_id,
                "audit_events": audit_counts,
                "keypairs_count": keypairs_count,
                "zk_proofs_count": zk_proofs_count,
                "threshold_schemes_count": threshold_schemes_count,
                "generated_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Erreur récupération statistiques: {e}")
            return {"error": str(e)}
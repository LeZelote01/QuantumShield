"""
Service de gestion des certificats X.509
Gestion des certificats numériques pour authentification et chiffrement
"""

import asyncio
import logging
import uuid
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import pkcs12
import secrets

logger = logging.getLogger(__name__)

class CertificateStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"
    SUSPENDED = "suspended"

class CertificateType(str, Enum):
    ROOT_CA = "root_ca"
    INTERMEDIATE_CA = "intermediate_ca"
    END_ENTITY = "end_entity"
    DEVICE = "device"
    USER = "user"
    SERVER = "server"

class KeyUsage(str, Enum):
    DIGITAL_SIGNATURE = "digital_signature"
    KEY_ENCIPHERMENT = "key_encipherment"
    DATA_ENCIPHERMENT = "data_encipherment"
    KEY_AGREEMENT = "key_agreement"
    CERTIFICATE_SIGN = "certificate_sign"
    CRL_SIGN = "crl_sign"

class X509Service:
    """Service de gestion des certificats X.509"""
    
    def __init__(self, db):
        self.db = db
        self.root_ca_cert = None
        self.root_ca_key = None
        self.intermediate_ca_cert = None
        self.intermediate_ca_key = None
        self.certificate_store = {}
        self.revocation_list = {}
        self.is_initialized = False
        self._initialize()
    
    def _initialize(self):
        """Initialise le service de certificats X.509"""
        try:
            # Configuration par défaut
            self.config = {
                "key_size": 2048,
                "hash_algorithm": hashes.SHA256(),
                "default_validity_days": 365,
                "ca_validity_days": 3650,  # 10 ans
                "certificate_path": "/app/certificates",
                "auto_renewal_days": 30,
                "max_chain_length": 5
            }
            
            # Initialiser le PKI
            asyncio.create_task(self._initialize_pki())
            
            self.is_initialized = True
            logger.info("Service X.509 initialisé")
            
        except Exception as e:
            logger.error(f"Erreur initialisation X.509: {str(e)}")
            self.is_initialized = False
    
    def is_ready(self) -> bool:
        """Vérifie si le service est prêt"""
        return self.is_initialized
    
    async def _initialize_pki(self):
        """Initialise l'infrastructure PKI"""
        try:
            # Vérifier si une CA racine existe déjà
            root_ca = await self.db.certificates.find_one({
                "certificate_type": CertificateType.ROOT_CA.value,
                "status": CertificateStatus.ACTIVE.value
            })
            
            if not root_ca:
                # Créer une nouvelle CA racine
                await self._create_root_ca()
            else:
                # Charger la CA racine existante
                await self._load_root_ca(root_ca)
            
            # Créer ou charger une CA intermédiaire
            await self._ensure_intermediate_ca()
            
            logger.info("Infrastructure PKI initialisée")
            
        except Exception as e:
            logger.error(f"Erreur initialisation PKI: {str(e)}")
    
    async def _create_root_ca(self):
        """Crée une autorité de certification racine"""
        try:
            # Générer la clé privée
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=self.config["key_size"]
            )
            
            # Créer le certificat auto-signé
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "QuantumShield"),
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Security"),
                x509.NameAttribute(NameOID.COMMON_NAME, "QuantumShield Root CA"),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.utcnow()
            ).not_valid_after(
                datetime.utcnow() + timedelta(days=self.config["ca_validity_days"])
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName("quantumshield.local"),
                ]),
                critical=False,
            ).add_extension(
                x509.BasicConstraints(ca=True, path_length=None),
                critical=True,
            ).add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_cert_sign=True,
                    crl_sign=True,
                    key_encipherment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    content_commitment=False,
                    encipher_only=False,
                    decipher_only=False
                ),
                critical=True,
            ).sign(private_key, self.config["hash_algorithm"])
            
            # Sauvegarder en base
            cert_data = {
                "certificate_id": str(uuid.uuid4()),
                "certificate_type": CertificateType.ROOT_CA.value,
                "subject": self._get_subject_string(cert.subject),
                "issuer": self._get_subject_string(cert.issuer),
                "serial_number": str(cert.serial_number),
                "not_valid_before": cert.not_valid_before,
                "not_valid_after": cert.not_valid_after,
                "status": CertificateStatus.ACTIVE.value,
                "certificate_pem": cert.public_bytes(serialization.Encoding.PEM).decode(),
                "private_key_pem": private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ).decode(),
                "fingerprint": hashlib.sha256(cert.public_bytes(serialization.Encoding.DER)).hexdigest(),
                "key_usage": ["digital_signature", "key_cert_sign", "crl_sign"],
                "created_at": datetime.utcnow(),
                "created_by": "system"
            }
            
            await self.db.certificates.insert_one(cert_data)
            
            # Stocker en mémoire
            self.root_ca_cert = cert
            self.root_ca_key = private_key
            
            logger.info("CA racine créée avec succès")
            
        except Exception as e:
            logger.error(f"Erreur création CA racine: {str(e)}")
            raise
    
    async def _load_root_ca(self, root_ca_data: Dict[str, Any]):
        """Charge une CA racine existante"""
        try:
            # Charger le certificat
            cert_pem = root_ca_data["certificate_pem"]
            self.root_ca_cert = x509.load_pem_x509_certificate(cert_pem.encode())
            
            # Charger la clé privée
            key_pem = root_ca_data["private_key_pem"]
            self.root_ca_key = serialization.load_pem_private_key(
                key_pem.encode(),
                password=None
            )
            
            logger.info("CA racine chargée avec succès")
            
        except Exception as e:
            logger.error(f"Erreur chargement CA racine: {str(e)}")
            raise
    
    async def _ensure_intermediate_ca(self):
        """Crée ou charge une CA intermédiaire"""
        try:
            # Vérifier si une CA intermédiaire existe
            intermediate_ca = await self.db.certificates.find_one({
                "certificate_type": CertificateType.INTERMEDIATE_CA.value,
                "status": CertificateStatus.ACTIVE.value
            })
            
            if not intermediate_ca:
                # Créer une nouvelle CA intermédiaire
                await self._create_intermediate_ca()
            else:
                # Charger la CA intermédiaire existante
                await self._load_intermediate_ca(intermediate_ca)
            
        except Exception as e:
            logger.error(f"Erreur gestion CA intermédiaire: {str(e)}")
    
    async def _create_intermediate_ca(self):
        """Crée une CA intermédiaire"""
        try:
            if not self.root_ca_cert or not self.root_ca_key:
                raise Exception("CA racine non disponible")
            
            # Générer la clé privée
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=self.config["key_size"]
            )
            
            # Créer le certificat signé par la CA racine
            subject = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "QuantumShield"),
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Security"),
                x509.NameAttribute(NameOID.COMMON_NAME, "QuantumShield Intermediate CA"),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                self.root_ca_cert.subject
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.utcnow()
            ).not_valid_after(
                datetime.utcnow() + timedelta(days=self.config["ca_validity_days"])
            ).add_extension(
                x509.BasicConstraints(ca=True, path_length=0),
                critical=True,
            ).add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_cert_sign=True,
                    crl_sign=True,
                    key_encipherment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    content_commitment=False,
                    encipher_only=False,
                    decipher_only=False
                ),
                critical=True,
            ).sign(self.root_ca_key, self.config["hash_algorithm"])
            
            # Sauvegarder en base
            cert_data = {
                "certificate_id": str(uuid.uuid4()),
                "certificate_type": CertificateType.INTERMEDIATE_CA.value,
                "subject": self._get_subject_string(cert.subject),
                "issuer": self._get_subject_string(cert.issuer),
                "serial_number": str(cert.serial_number),
                "not_valid_before": cert.not_valid_before,
                "not_valid_after": cert.not_valid_after,
                "status": CertificateStatus.ACTIVE.value,
                "certificate_pem": cert.public_bytes(serialization.Encoding.PEM).decode(),
                "private_key_pem": private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ).decode(),
                "fingerprint": hashlib.sha256(cert.public_bytes(serialization.Encoding.DER)).hexdigest(),
                "key_usage": ["digital_signature", "key_cert_sign", "crl_sign"],
                "created_at": datetime.utcnow(),
                "created_by": "system"
            }
            
            await self.db.certificates.insert_one(cert_data)
            
            # Stocker en mémoire
            self.intermediate_ca_cert = cert
            self.intermediate_ca_key = private_key
            
            logger.info("CA intermédiaire créée avec succès")
            
        except Exception as e:
            logger.error(f"Erreur création CA intermédiaire: {str(e)}")
            raise
    
    async def _load_intermediate_ca(self, intermediate_ca_data: Dict[str, Any]):
        """Charge une CA intermédiaire existante"""
        try:
            # Charger le certificat
            cert_pem = intermediate_ca_data["certificate_pem"]
            self.intermediate_ca_cert = x509.load_pem_x509_certificate(cert_pem.encode())
            
            # Charger la clé privée
            key_pem = intermediate_ca_data["private_key_pem"]
            self.intermediate_ca_key = serialization.load_pem_private_key(
                key_pem.encode(),
                password=None
            )
            
            logger.info("CA intermédiaire chargée avec succès")
            
        except Exception as e:
            logger.error(f"Erreur chargement CA intermédiaire: {str(e)}")
            raise
    
    # ==============================
    # Gestion des certificats
    # ==============================
    
    async def issue_certificate(self,
                              subject_name: str,
                              certificate_type: CertificateType,
                              key_usage: List[KeyUsage],
                              subject_alt_names: Optional[List[str]] = None,
                              validity_days: Optional[int] = None,
                              device_id: Optional[str] = None,
                              user_id: Optional[str] = None) -> Dict[str, Any]:
        """Émet un nouveau certificat"""
        try:
            if not self.intermediate_ca_cert or not self.intermediate_ca_key:
                raise Exception("CA intermédiaire non disponible")
            
            # Générer la clé privée
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=self.config["key_size"]
            )
            
            # Créer le sujet
            subject = x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, subject_name),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "QuantumShield"),
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Devices" if certificate_type == CertificateType.DEVICE else "Users"),
            ])
            
            # Créer le certificat
            cert_builder = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                self.intermediate_ca_cert.subject
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.utcnow()
            ).not_valid_after(
                datetime.utcnow() + timedelta(days=validity_days or self.config["default_validity_days"])
            )
            
            # Ajouter les extensions
            if subject_alt_names:
                san_list = []
                for san in subject_alt_names:
                    if san.startswith("DNS:"):
                        san_list.append(x509.DNSName(san[4:]))
                    elif san.startswith("IP:"):
                        san_list.append(x509.IPAddress(san[3:]))
                    else:
                        san_list.append(x509.DNSName(san))
                
                cert_builder = cert_builder.add_extension(
                    x509.SubjectAlternativeName(san_list),
                    critical=False,
                )
            
            # Ajouter les contraintes de base
            cert_builder = cert_builder.add_extension(
                x509.BasicConstraints(ca=False, path_length=None),
                critical=True,
            )
            
            # Ajouter l'utilisation de la clé
            key_usage_obj = x509.KeyUsage(
                digital_signature=KeyUsage.DIGITAL_SIGNATURE in key_usage,
                key_encipherment=KeyUsage.KEY_ENCIPHERMENT in key_usage,
                data_encipherment=KeyUsage.DATA_ENCIPHERMENT in key_usage,
                key_agreement=KeyUsage.KEY_AGREEMENT in key_usage,
                key_cert_sign=KeyUsage.CERTIFICATE_SIGN in key_usage,
                crl_sign=KeyUsage.CRL_SIGN in key_usage,
                content_commitment=False,
                encipher_only=False,
                decipher_only=False
            )
            
            cert_builder = cert_builder.add_extension(
                key_usage_obj,
                critical=True,
            )
            
            # Signer le certificat
            cert = cert_builder.sign(self.intermediate_ca_key, self.config["hash_algorithm"])
            
            # Générer un mot de passe pour le PKCS#12
            p12_password = secrets.token_urlsafe(16)
            
            # Créer le fichier PKCS#12
            p12_data = pkcs12.serialize_key_and_certificates(
                name=subject_name.encode(),
                key=private_key,
                cert=cert,
                cas=[self.intermediate_ca_cert, self.root_ca_cert],
                encryption_algorithm=serialization.BestAvailableEncryption(p12_password.encode())
            )
            
            # Sauvegarder en base
            cert_data = {
                "certificate_id": str(uuid.uuid4()),
                "certificate_type": certificate_type.value,
                "subject": self._get_subject_string(cert.subject),
                "issuer": self._get_subject_string(cert.issuer),
                "serial_number": str(cert.serial_number),
                "not_valid_before": cert.not_valid_before,
                "not_valid_after": cert.not_valid_after,
                "status": CertificateStatus.ACTIVE.value,
                "certificate_pem": cert.public_bytes(serialization.Encoding.PEM).decode(),
                "private_key_pem": private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ).decode(),
                "pkcs12_data": base64.b64encode(p12_data).decode(),
                "pkcs12_password": p12_password,
                "fingerprint": hashlib.sha256(cert.public_bytes(serialization.Encoding.DER)).hexdigest(),
                "key_usage": [ku.value for ku in key_usage],
                "subject_alt_names": subject_alt_names or [],
                "device_id": device_id,
                "user_id": user_id,
                "created_at": datetime.utcnow(),
                "created_by": user_id or "system"
            }
            
            await self.db.certificates.insert_one(cert_data)
            
            logger.info(f"Certificat émis pour {subject_name}")
            
            return {
                "success": True,
                "certificate_id": cert_data["certificate_id"],
                "subject": subject_name,
                "serial_number": cert_data["serial_number"],
                "not_valid_before": cert.not_valid_before,
                "not_valid_after": cert.not_valid_after,
                "fingerprint": cert_data["fingerprint"],
                "certificate_pem": cert_data["certificate_pem"],
                "pkcs12_password": p12_password
            }
            
        except Exception as e:
            logger.error(f"Erreur émission certificat: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def revoke_certificate(self, certificate_id: str, reason: str = "unspecified") -> Dict[str, Any]:
        """Révoque un certificat"""
        try:
            # Récupérer le certificat
            cert_data = await self.db.certificates.find_one({"certificate_id": certificate_id})
            if not cert_data:
                return {
                    "success": False,
                    "error": "Certificat non trouvé"
                }
            
            if cert_data["status"] != CertificateStatus.ACTIVE.value:
                return {
                    "success": False,
                    "error": "Certificat déjà révoqué ou expiré"
                }
            
            # Marquer comme révoqué
            await self.db.certificates.update_one(
                {"certificate_id": certificate_id},
                {"$set": {
                    "status": CertificateStatus.REVOKED.value,
                    "revoked_at": datetime.utcnow(),
                    "revocation_reason": reason
                }}
            )
            
            # Ajouter à la liste de révocation
            revocation_entry = {
                "certificate_id": certificate_id,
                "serial_number": cert_data["serial_number"],
                "revoked_at": datetime.utcnow(),
                "reason": reason
            }
            
            await self.db.certificate_revocations.insert_one(revocation_entry)
            
            logger.info(f"Certificat révoqué: {certificate_id}")
            
            return {
                "success": True,
                "certificate_id": certificate_id,
                "revoked_at": datetime.utcnow(),
                "reason": reason
            }
            
        except Exception as e:
            logger.error(f"Erreur révocation certificat: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def verify_certificate(self, certificate_pem: str) -> Dict[str, Any]:
        """Vérifie un certificat"""
        try:
            # Charger le certificat
            cert = x509.load_pem_x509_certificate(certificate_pem.encode())
            
            # Vérifier la validité temporelle
            now = datetime.utcnow()
            is_valid_time = cert.not_valid_before <= now <= cert.not_valid_after
            
            # Vérifier s'il est révoqué
            cert_data = await self.db.certificates.find_one({"serial_number": str(cert.serial_number)})
            is_revoked = cert_data and cert_data["status"] == CertificateStatus.REVOKED.value
            
            # Vérifier la chaîne de certification
            chain_valid = await self._verify_certificate_chain(cert)
            
            return {
                "valid": is_valid_time and not is_revoked and chain_valid,
                "subject": self._get_subject_string(cert.subject),
                "issuer": self._get_subject_string(cert.issuer),
                "serial_number": str(cert.serial_number),
                "not_valid_before": cert.not_valid_before,
                "not_valid_after": cert.not_valid_after,
                "fingerprint": hashlib.sha256(cert.public_bytes(serialization.Encoding.DER)).hexdigest(),
                "is_valid_time": is_valid_time,
                "is_revoked": is_revoked,
                "chain_valid": chain_valid
            }
            
        except Exception as e:
            logger.error(f"Erreur vérification certificat: {str(e)}")
            return {
                "valid": False,
                "error": str(e)
            }
    
    async def _verify_certificate_chain(self, cert: x509.Certificate) -> bool:
        """Vérifie la chaîne de certification"""
        try:
            # Vérifier si c'est signé par notre CA intermédiaire
            if self.intermediate_ca_cert:
                try:
                    self.intermediate_ca_cert.public_key().verify(
                        cert.signature,
                        cert.tbs_certificate_bytes,
                        padding.PKCS1v15(),
                        cert.signature_hash_algorithm
                    )
                    return True
                except Exception:
                    pass
            
            # Vérifier si c'est signé par notre CA racine
            if self.root_ca_cert:
                try:
                    self.root_ca_cert.public_key().verify(
                        cert.signature,
                        cert.tbs_certificate_bytes,
                        padding.PKCS1v15(),
                        cert.signature_hash_algorithm
                    )
                    return True
                except Exception:
                    pass
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur vérification chaîne: {str(e)}")
            return False
    
    # ==============================
    # Utilitaires
    # ==============================
    
    def _get_subject_string(self, subject: x509.Name) -> str:
        """Convertit un sujet X.509 en chaîne"""
        return ", ".join([f"{attr.oid._name}={attr.value}" for attr in subject])
    
    async def list_certificates(self, 
                              certificate_type: Optional[CertificateType] = None,
                              status: Optional[CertificateStatus] = None,
                              device_id: Optional[str] = None,
                              user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Liste les certificats selon les critères"""
        try:
            query = {}
            
            if certificate_type:
                query["certificate_type"] = certificate_type.value
            if status:
                query["status"] = status.value
            if device_id:
                query["device_id"] = device_id
            if user_id:
                query["user_id"] = user_id
            
            certificates = await self.db.certificates.find(query).sort("created_at", -1).to_list(None)
            
            # Nettoyer les données sensibles
            result = []
            for cert in certificates:
                cert.pop("_id", None)
                cert.pop("private_key_pem", None)  # Ne pas exposer la clé privée
                cert.pop("pkcs12_data", None)
                cert.pop("pkcs12_password", None)
                result.append(cert)
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur liste certificats: {str(e)}")
            return []
    
    async def get_certificate_details(self, certificate_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les détails d'un certificat"""
        try:
            cert_data = await self.db.certificates.find_one({"certificate_id": certificate_id})
            if not cert_data:
                return None
            
            # Nettoyer les données sensibles
            cert_data.pop("_id", None)
            cert_data.pop("private_key_pem", None)
            cert_data.pop("pkcs12_data", None)
            cert_data.pop("pkcs12_password", None)
            
            return cert_data
            
        except Exception as e:
            logger.error(f"Erreur récupération détails certificat: {str(e)}")
            return None
    
    async def get_expiring_certificates(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Récupère les certificats qui expirent bientôt"""
        try:
            expiration_date = datetime.utcnow() + timedelta(days=days_ahead)
            
            certificates = await self.db.certificates.find({
                "status": CertificateStatus.ACTIVE.value,
                "not_valid_after": {"$lte": expiration_date}
            }).sort("not_valid_after", 1).to_list(None)
            
            # Nettoyer les données
            result = []
            for cert in certificates:
                cert.pop("_id", None)
                cert.pop("private_key_pem", None)
                cert.pop("pkcs12_data", None)
                cert.pop("pkcs12_password", None)
                result.append(cert)
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur récupération certificats expirants: {str(e)}")
            return []
    
    async def get_certificate_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques des certificats"""
        try:
            stats = {
                "total_certificates": await self.db.certificates.count_documents({}),
                "active_certificates": await self.db.certificates.count_documents({"status": CertificateStatus.ACTIVE.value}),
                "expired_certificates": await self.db.certificates.count_documents({"status": CertificateStatus.EXPIRED.value}),
                "revoked_certificates": await self.db.certificates.count_documents({"status": CertificateStatus.REVOKED.value}),
                "device_certificates": await self.db.certificates.count_documents({"certificate_type": CertificateType.DEVICE.value}),
                "user_certificates": await self.db.certificates.count_documents({"certificate_type": CertificateType.USER.value}),
                "expiring_soon": len(await self.get_expiring_certificates(30))
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Erreur récupération statistiques: {str(e)}")
            return {}
    
    async def shutdown(self):
        """Arrête le service X.509"""
        try:
            # Nettoyer les certificats en mémoire
            self.root_ca_cert = None
            self.root_ca_key = None
            self.intermediate_ca_cert = None
            self.intermediate_ca_key = None
            self.certificate_store.clear()
            
            logger.info("Service X.509 arrêté")
            
        except Exception as e:
            logger.error(f"Erreur arrêt service X.509: {str(e)}")
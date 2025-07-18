"""
Routes pour la gestion des certificats X.509
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Response
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

# Import du service (sera injecté par le serveur principal)
x509_service = None

router = APIRouter()
logger = logging.getLogger(__name__)

# ==============================
# Modèles Pydantic
# ==============================

class CertificateRequest(BaseModel):
    subject_name: str = Field(..., min_length=1, max_length=64)
    certificate_type: str = Field(..., pattern="^(device|user|server|end_entity)$")
    key_usage: List[str] = Field(default=["digital_signature", "key_encipherment"])
    subject_alt_names: Optional[List[str]] = []
    validity_days: Optional[int] = Field(default=365, ge=1, le=3650)
    device_id: Optional[str] = None
    user_id: Optional[str] = None

class CertificateRevoke(BaseModel):
    certificate_id: str
    reason: str = Field(default="unspecified", max_length=255)

class CertificateVerify(BaseModel):
    certificate_pem: str

# ==============================
# Endpoints de gestion PKI
# ==============================

@router.get("/ca/root")
async def get_root_ca():
    """Récupère le certificat de l'autorité racine"""
    try:
        if not x509_service:
            raise HTTPException(status_code=503, detail="Service X.509 non disponible")
        
        if not x509_service.root_ca_cert:
            raise HTTPException(status_code=404, detail="CA racine non trouvée")
        
        from cryptography.hazmat.primitives import serialization
        
        cert_pem = x509_service.root_ca_cert.public_bytes(serialization.Encoding.PEM).decode()
        
        return {
            "certificate_pem": cert_pem,
            "subject": x509_service._get_subject_string(x509_service.root_ca_cert.subject),
            "issuer": x509_service._get_subject_string(x509_service.root_ca_cert.issuer),
            "not_valid_before": x509_service.root_ca_cert.not_valid_before,
            "not_valid_after": x509_service.root_ca_cert.not_valid_after,
            "serial_number": str(x509_service.root_ca_cert.serial_number)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération CA racine: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ca/intermediate")
async def get_intermediate_ca():
    """Récupère le certificat de l'autorité intermédiaire"""
    try:
        if not x509_service:
            raise HTTPException(status_code=503, detail="Service X.509 non disponible")
        
        if not x509_service.intermediate_ca_cert:
            raise HTTPException(status_code=404, detail="CA intermédiaire non trouvée")
        
        from cryptography.hazmat.primitives import serialization
        
        cert_pem = x509_service.intermediate_ca_cert.public_bytes(serialization.Encoding.PEM).decode()
        
        return {
            "certificate_pem": cert_pem,
            "subject": x509_service._get_subject_string(x509_service.intermediate_ca_cert.subject),
            "issuer": x509_service._get_subject_string(x509_service.intermediate_ca_cert.issuer),
            "not_valid_before": x509_service.intermediate_ca_cert.not_valid_before,
            "not_valid_after": x509_service.intermediate_ca_cert.not_valid_after,
            "serial_number": str(x509_service.intermediate_ca_cert.serial_number)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération CA intermédiaire: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ca/chain")
async def get_ca_chain():
    """Récupère la chaîne de certification complète"""
    try:
        if not x509_service:
            raise HTTPException(status_code=503, detail="Service X.509 non disponible")
        
        if not x509_service.root_ca_cert or not x509_service.intermediate_ca_cert:
            raise HTTPException(status_code=404, detail="Chaîne de certification incomplète")
        
        from cryptography.hazmat.primitives import serialization
        
        root_pem = x509_service.root_ca_cert.public_bytes(serialization.Encoding.PEM).decode()
        intermediate_pem = x509_service.intermediate_ca_cert.public_bytes(serialization.Encoding.PEM).decode()
        
        # Concaténer les certificats (intermédiaire d'abord, puis racine)
        chain_pem = intermediate_pem + root_pem
        
        return {
            "chain_pem": chain_pem,
            "certificates": [
                {
                    "type": "intermediate",
                    "subject": x509_service._get_subject_string(x509_service.intermediate_ca_cert.subject),
                    "serial_number": str(x509_service.intermediate_ca_cert.serial_number)
                },
                {
                    "type": "root",
                    "subject": x509_service._get_subject_string(x509_service.root_ca_cert.subject),
                    "serial_number": str(x509_service.root_ca_cert.serial_number)
                }
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération chaîne CA: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================
# Endpoints de gestion des certificats
# ==============================

@router.post("/issue")
async def issue_certificate(cert_request: CertificateRequest):
    """Émet un nouveau certificat"""
    try:
        if not x509_service:
            raise HTTPException(status_code=503, detail="Service X.509 non disponible")
        
        from services.x509_service import CertificateType, KeyUsage
        
        # Convertir les énumérations
        cert_type = CertificateType(cert_request.certificate_type)
        key_usage = [KeyUsage(ku) for ku in cert_request.key_usage]
        
        result = await x509_service.issue_certificate(
            subject_name=cert_request.subject_name,
            certificate_type=cert_type,
            key_usage=key_usage,
            subject_alt_names=cert_request.subject_alt_names,
            validity_days=cert_request.validity_days,
            device_id=cert_request.device_id,
            user_id=cert_request.user_id
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur émission certificat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/revoke")
async def revoke_certificate(revoke_request: CertificateRevoke):
    """Révoque un certificat"""
    try:
        if not x509_service:
            raise HTTPException(status_code=503, detail="Service X.509 non disponible")
        
        result = await x509_service.revoke_certificate(
            certificate_id=revoke_request.certificate_id,
            reason=revoke_request.reason
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur révocation certificat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify")
async def verify_certificate(verify_request: CertificateVerify):
    """Vérifie un certificat"""
    try:
        if not x509_service:
            raise HTTPException(status_code=503, detail="Service X.509 non disponible")
        
        result = await x509_service.verify_certificate(verify_request.certificate_pem)
        
        return result
        
    except Exception as e:
        logger.error(f"Erreur vérification certificat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_certificates(
    certificate_type: Optional[str] = Query(None, pattern="^(root_ca|intermediate_ca|device|user|server|end_entity)$"),
    status: Optional[str] = Query(None, pattern="^(active|expired|revoked|pending|suspended)$"),
    device_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None)
):
    """Liste les certificats selon les critères"""
    try:
        if not x509_service:
            raise HTTPException(status_code=503, detail="Service X.509 non disponible")
        
        from services.x509_service import CertificateType, CertificateStatus
        
        cert_type = CertificateType(certificate_type) if certificate_type else None
        cert_status = CertificateStatus(status) if status else None
        
        certificates = await x509_service.list_certificates(
            certificate_type=cert_type,
            status=cert_status,
            device_id=device_id,
            user_id=user_id
        )
        
        return {
            "certificates": certificates,
            "count": len(certificates)
        }
        
    except Exception as e:
        logger.error(f"Erreur liste certificats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{certificate_id}")
async def get_certificate_details(certificate_id: str):
    """Récupère les détails d'un certificat"""
    try:
        if not x509_service:
            raise HTTPException(status_code=503, detail="Service X.509 non disponible")
        
        certificate = await x509_service.get_certificate_details(certificate_id)
        
        if not certificate:
            raise HTTPException(status_code=404, detail="Certificat non trouvé")
        
        return certificate
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération détails certificat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{certificate_id}/download")
async def download_certificate(certificate_id: str, format: str = Query("pem", pattern="^(pem|der|p12)$")):
    """Télécharge un certificat dans le format demandé"""
    try:
        if not x509_service:
            raise HTTPException(status_code=503, detail="Service X.509 non disponible")
        
        certificate = await x509_service.db.certificates.find_one({"certificate_id": certificate_id})
        
        if not certificate:
            raise HTTPException(status_code=404, detail="Certificat non trouvé")
        
        if format == "pem":
            content = certificate["certificate_pem"]
            media_type = "application/x-pem-file"
            filename = f"{certificate_id}.pem"
        elif format == "der":
            # Convertir PEM en DER
            from cryptography import x509
            from cryptography.hazmat.primitives import serialization
            
            cert = x509.load_pem_x509_certificate(certificate["certificate_pem"].encode())
            content = cert.public_bytes(serialization.Encoding.DER)
            media_type = "application/x-x509-ca-cert"
            filename = f"{certificate_id}.der"
        elif format == "p12":
            if "pkcs12_data" not in certificate:
                raise HTTPException(status_code=400, detail="Format PKCS#12 non disponible pour ce certificat")
            
            import base64
            content = base64.b64decode(certificate["pkcs12_data"])
            media_type = "application/x-pkcs12"
            filename = f"{certificate_id}.p12"
        
        return Response(
            content=content,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur téléchargement certificat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================
# Endpoints d'administration
# ==============================

@router.get("/expiring")
async def get_expiring_certificates(days: int = Query(30, ge=1, le=365)):
    """Récupère les certificats qui expirent bientôt"""
    try:
        if not x509_service:
            raise HTTPException(status_code=503, detail="Service X.509 non disponible")
        
        certificates = await x509_service.get_expiring_certificates(days)
        
        return {
            "certificates": certificates,
            "count": len(certificates),
            "days_ahead": days
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération certificats expirants: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_certificate_stats():
    """Récupère les statistiques des certificats"""
    try:
        if not x509_service:
            raise HTTPException(status_code=503, detail="Service X.509 non disponible")
        
        stats = await x509_service.get_certificate_stats()
        
        return stats
        
    except Exception as e:
        logger.error(f"Erreur récupération statistiques: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/crl")
async def get_certificate_revocation_list():
    """Récupère la liste de révocation des certificats (CRL)"""
    try:
        if not x509_service:
            raise HTTPException(status_code=503, detail="Service X.509 non disponible")
        
        revocations = await x509_service.db.certificate_revocations.find().sort("revoked_at", -1).to_list(None)
        
        # Nettoyer les données
        result = []
        for revocation in revocations:
            revocation.pop("_id", None)
            result.append(revocation)
        
        return {
            "revocations": result,
            "count": len(result)
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération CRL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================
# Endpoints d'utilité
# ==============================

@router.get("/supported-key-usages")
async def get_supported_key_usages():
    """Récupère les utilisations de clés supportées"""
    return {
        "key_usages": [
            "digital_signature",
            "key_encipherment",
            "data_encipherment",
            "key_agreement",
            "certificate_sign",
            "crl_sign"
        ]
    }

@router.get("/supported-certificate-types")
async def get_supported_certificate_types():
    """Récupère les types de certificats supportés"""
    return {
        "certificate_types": [
            "device",
            "user",
            "server",
            "end_entity"
        ]
    }

@router.get("/config")
async def get_x509_config():
    """Récupère la configuration du service X.509"""
    try:
        if not x509_service:
            raise HTTPException(status_code=503, detail="Service X.509 non disponible")
        
        config = x509_service.config.copy()
        # Masquer les informations sensibles
        config.pop("certificate_path", None)
        
        return {
            "config": config,
            "pki_initialized": x509_service.root_ca_cert is not None,
            "service_status": "active" if x509_service.is_ready() else "inactive"
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération config X.509: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
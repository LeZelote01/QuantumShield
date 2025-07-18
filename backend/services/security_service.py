"""
Service de sécurité renforcée pour QuantumShield
Inclut: 2FA/MFA, audit de sécurité, analyse comportementale
"""

import hashlib
import hmac
import base64
import qrcode
import io
import pyotp
import json
import uuid
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets

logger = logging.getLogger(__name__)

class SecurityEventType(str, Enum):
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    PASSWORD_CHANGE = "password_change"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    ACCOUNT_LOCKED = "account_locked"
    DEVICE_REGISTERED = "device_registered"
    ANOMALY_DETECTED = "anomaly_detected"
    CRYPTO_OPERATION = "crypto_operation"
    API_ACCESS = "api_access"
    
class SecurityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatType(str, Enum):
    BRUTE_FORCE = "brute_force"
    UNUSUAL_LOCATION = "unusual_location"
    UNUSUAL_TIME = "unusual_time"
    MULTIPLE_FAILED_ATTEMPTS = "multiple_failed_attempts"
    DEVICE_ANOMALY = "device_anomaly"
    CRYPTO_ATTACK = "crypto_attack"
    PRIVILEGE_ESCALATION = "privilege_escalation"

class MFAMethod(str, Enum):
    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"
    HARDWARE_TOKEN = "hardware_token"
    BIOMETRIC = "biometric"

class SecurityService:
    """Service de sécurité renforcée"""
    
    def __init__(self, db):
        self.db = db
        self.is_initialized = False
        self.security_key = None
        self.risk_thresholds = {
            SecurityLevel.LOW: 0.3,
            SecurityLevel.MEDIUM: 0.6,
            SecurityLevel.HIGH: 0.8,
            SecurityLevel.CRITICAL: 0.9
        }
        self._initialize()
    
    def _initialize(self):
        """Initialise le service de sécurité"""
        try:
            # Générer une clé de sécurité pour le chiffrement interne
            self.security_key = Fernet.generate_key()
            self.cipher_suite = Fernet(self.security_key)
            self.is_initialized = True
            logger.info("Service de sécurité initialisé")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation: {e}")
            self.is_initialized = False
    
    def is_ready(self) -> bool:
        """Vérifie si le service est prêt"""
        return self.is_initialized
    
    # ===== AUTHENTIFICATION MULTI-FACTEUR =====
    
    async def setup_totp_mfa(self, user_id: str, service_name: str = "QuantumShield") -> Dict[str, Any]:
        """Configure l'authentification TOTP (Time-based One-Time Password)"""
        try:
            # Générer un secret unique pour l'utilisateur
            secret = pyotp.random_base32()
            
            # Récupérer les infos utilisateur
            user = await self.db.users.find_one({"id": user_id})
            if not user:
                raise ValueError("Utilisateur non trouvé")
            
            # Créer l'URI TOTP
            totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
                name=user.email,
                issuer_name=service_name
            )
            
            # Générer le QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(totp_uri)
            qr.make(fit=True)
            
            # Convertir en base64
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            # Stocker la configuration MFA
            mfa_config = {
                "user_id": user_id,
                "method": MFAMethod.TOTP.value,
                "secret": self.cipher_suite.encrypt(secret.encode()).decode(),
                "backup_codes": [secrets.token_hex(4) for _ in range(10)],
                "enabled": False,  # L'utilisateur doit confirmer
                "created_at": datetime.utcnow(),
                "verified_at": None
            }
            
            await self.db.mfa_configs.insert_one(mfa_config)
            
            return {
                "totp_uri": totp_uri,
                "qr_code": qr_code_base64,
                "secret": secret,
                "backup_codes": mfa_config["backup_codes"],
                "manual_entry_key": secret,
                "status": "setup_required"
            }
            
        except Exception as e:
            logger.error(f"Erreur configuration TOTP: {e}")
            raise Exception(f"Impossible de configurer TOTP: {e}")
    
    async def verify_totp_setup(self, user_id: str, totp_code: str) -> Dict[str, Any]:
        """Vérifie et active la configuration TOTP"""
        try:
            # Récupérer la configuration MFA
            mfa_config = await self.db.mfa_configs.find_one({"user_id": user_id, "method": MFAMethod.TOTP.value})
            if not mfa_config:
                raise ValueError("Configuration MFA non trouvée")
            
            # Déchiffrer le secret
            secret = self.cipher_suite.decrypt(mfa_config["secret"].encode()).decode()
            
            # Vérifier le code TOTP
            totp = pyotp.TOTP(secret)
            if not totp.verify(totp_code, valid_window=2):
                raise ValueError("Code TOTP invalide")
            
            # Activer la MFA
            await self.db.mfa_configs.update_one(
                {"user_id": user_id, "method": MFAMethod.TOTP.value},
                {
                    "$set": {
                        "enabled": True,
                        "verified_at": datetime.utcnow()
                    }
                }
            )
            
            # Enregistrer l'événement de sécurité
            await self.log_security_event(
                user_id=user_id,
                event_type=SecurityEventType.MFA_ENABLED,
                details={"method": MFAMethod.TOTP.value}
            )
            
            return {
                "status": "verified",
                "mfa_enabled": True,
                "backup_codes": mfa_config["backup_codes"]
            }
            
        except Exception as e:
            logger.error(f"Erreur vérification TOTP: {e}")
            raise Exception(f"Impossible de vérifier TOTP: {e}")
    
    async def verify_totp_code(self, user_id: str, totp_code: str) -> bool:
        """Vérifie un code TOTP lors de la connexion"""
        try:
            # Récupérer la configuration MFA
            mfa_config = await self.db.mfa_configs.find_one(
                {"user_id": user_id, "method": MFAMethod.TOTP.value, "enabled": True}
            )
            if not mfa_config:
                return False
            
            # Déchiffrer le secret
            secret = self.cipher_suite.decrypt(mfa_config["secret"].encode()).decode()
            
            # Vérifier le code TOTP
            totp = pyotp.TOTP(secret)
            is_valid = totp.verify(totp_code, valid_window=2)
            
            if is_valid:
                # Mettre à jour la dernière utilisation
                await self.db.mfa_configs.update_one(
                    {"user_id": user_id, "method": MFAMethod.TOTP.value},
                    {"$set": {"last_used": datetime.utcnow()}}
                )
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Erreur vérification TOTP: {e}")
            return False
    
    async def disable_mfa(self, user_id: str, method: MFAMethod) -> Dict[str, Any]:
        """Désactive la MFA pour un utilisateur"""
        try:
            # Désactiver la configuration MFA
            result = await self.db.mfa_configs.update_one(
                {"user_id": user_id, "method": method.value},
                {"$set": {"enabled": False, "disabled_at": datetime.utcnow()}}
            )
            
            if result.matched_count == 0:
                raise ValueError("Configuration MFA non trouvée")
            
            # Enregistrer l'événement de sécurité
            await self.log_security_event(
                user_id=user_id,
                event_type=SecurityEventType.MFA_DISABLED,
                details={"method": method.value}
            )
            
            return {
                "status": "disabled",
                "method": method.value,
                "disabled_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Erreur désactivation MFA: {e}")
            raise Exception(f"Impossible de désactiver MFA: {e}")
    
    async def get_mfa_status(self, user_id: str) -> Dict[str, Any]:
        """Récupère le statut MFA d'un utilisateur"""
        try:
            mfa_configs = await self.db.mfa_configs.find({"user_id": user_id}).to_list(None)
            
            status = {
                "user_id": user_id,
                "mfa_enabled": False,
                "methods": [],
                "last_used": None
            }
            
            for config in mfa_configs:
                if config.get("enabled", False):
                    status["mfa_enabled"] = True
                    status["methods"].append({
                        "method": config["method"],
                        "enabled": True,
                        "created_at": config["created_at"],
                        "verified_at": config.get("verified_at"),
                        "last_used": config.get("last_used")
                    })
                    
                    # Mettre à jour la dernière utilisation
                    if config.get("last_used") and (not status["last_used"] or config["last_used"] > status["last_used"]):
                        status["last_used"] = config["last_used"]
            
            return status
            
        except Exception as e:
            logger.error(f"Erreur récupération statut MFA: {e}")
            return {"user_id": user_id, "mfa_enabled": False, "methods": []}
    
    # ===== ANALYSE COMPORTEMENTALE =====
    
    async def analyze_user_behavior(self, user_id: str, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse le comportement utilisateur pour détecter des anomalies"""
        try:
            # Récupérer l'historique des actions
            history = await self.db.user_behavior.find(
                {"user_id": user_id, "action": action}
            ).sort("timestamp", -1).limit(100).to_list(None)
            
            # Analyser les patterns
            risk_score = 0.0
            anomalies = []
            
            # Vérifier la localisation
            if "ip_address" in context:
                ip_locations = [item.get("ip_address") for item in history if item.get("ip_address")]
                if ip_locations and context["ip_address"] not in ip_locations[-10:]:
                    risk_score += 0.3
                    anomalies.append({
                        "type": ThreatType.UNUSUAL_LOCATION.value,
                        "description": "Connexion depuis une nouvelle localisation",
                        "severity": SecurityLevel.MEDIUM.value
                    })
            
            # Vérifier l'heure
            current_hour = datetime.utcnow().hour
            historical_hours = [item["timestamp"].hour for item in history if "timestamp" in item]
            if historical_hours:
                usual_hours = set(historical_hours)
                if current_hour not in usual_hours:
                    risk_score += 0.2
                    anomalies.append({
                        "type": ThreatType.UNUSUAL_TIME.value,
                        "description": "Activité à une heure inhabituelle",
                        "severity": SecurityLevel.LOW.value
                    })
            
            # Vérifier la fréquence
            recent_actions = [item for item in history if item["timestamp"] > datetime.utcnow() - timedelta(minutes=5)]
            if len(recent_actions) > 10:
                risk_score += 0.4
                anomalies.append({
                    "type": ThreatType.MULTIPLE_FAILED_ATTEMPTS.value,
                    "description": "Nombreuses tentatives récentes",
                    "severity": SecurityLevel.HIGH.value
                })
            
            # Déterminer le niveau de risque
            security_level = SecurityLevel.LOW
            for level, threshold in self.risk_thresholds.items():
                if risk_score >= threshold:
                    security_level = level
            
            # Enregistrer l'analyse
            behavior_record = {
                "user_id": user_id,
                "action": action,
                "context": context,
                "risk_score": risk_score,
                "security_level": security_level.value,
                "anomalies": anomalies,
                "timestamp": datetime.utcnow()
            }
            
            await self.db.user_behavior.insert_one(behavior_record)
            
            # Si risque élevé, créer une alerte
            if security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
                await self.create_security_alert(
                    user_id=user_id,
                    alert_type="behavioral_anomaly",
                    risk_score=risk_score,
                    anomalies=anomalies
                )
            
            return {
                "risk_score": risk_score,
                "security_level": security_level.value,
                "anomalies": anomalies,
                "recommendations": self._get_security_recommendations(security_level, anomalies)
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse comportementale: {e}")
            return {
                "risk_score": 0.0,
                "security_level": SecurityLevel.LOW.value,
                "anomalies": [],
                "recommendations": []
            }
    
    def _get_security_recommendations(self, security_level: SecurityLevel, anomalies: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur le niveau de sécurité"""
        recommendations = []
        
        if security_level == SecurityLevel.MEDIUM:
            recommendations.append("Activer l'authentification multi-facteur (MFA)")
            recommendations.append("Vérifier les connexions récentes")
        
        elif security_level == SecurityLevel.HIGH:
            recommendations.append("Changer immédiatement le mot de passe")
            recommendations.append("Vérifier les dispositifs connectés")
            recommendations.append("Examiner l'activité récente du compte")
        
        elif security_level == SecurityLevel.CRITICAL:
            recommendations.append("Bloquer temporairement le compte")
            recommendations.append("Contacter l'équipe de sécurité")
            recommendations.append("Effectuer un audit complet du compte")
        
        # Recommandations spécifiques aux anomalies
        for anomaly in anomalies:
            if anomaly["type"] == ThreatType.UNUSUAL_LOCATION.value:
                recommendations.append("Vérifier la localisation de connexion")
            elif anomaly["type"] == ThreatType.MULTIPLE_FAILED_ATTEMPTS.value:
                recommendations.append("Activer la protection anti-brute force")
        
        return list(set(recommendations))  # Éviter les doublons
    
    # ===== AUDIT DE SÉCURITÉ =====
    
    async def log_security_event(self, user_id: str, event_type: SecurityEventType, 
                                details: Dict[str, Any] = None, ip_address: str = None) -> None:
        """Enregistre un événement de sécurité"""
        try:
            event = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "event_type": event_type.value,
                "details": details or {},
                "ip_address": ip_address,
                "timestamp": datetime.utcnow(),
                "user_agent": details.get("user_agent") if details else None,
                "session_id": details.get("session_id") if details else None
            }
            
            await self.db.security_events.insert_one(event)
            
        except Exception as e:
            logger.error(f"Erreur enregistrement événement sécurité: {e}")
    
    async def create_security_alert(self, user_id: str, alert_type: str, 
                                  risk_score: float, anomalies: List[Dict]) -> None:
        """Crée une alerte de sécurité"""
        try:
            alert = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "alert_type": alert_type,
                "risk_score": risk_score,
                "anomalies": anomalies,
                "status": "active",
                "created_at": datetime.utcnow(),
                "acknowledged": False,
                "resolved": False
            }
            
            await self.db.security_alerts.insert_one(alert)
            
            # Envoyer notification (à implémenter selon les besoins)
            logger.warning(f"Alerte sécurité créée pour {user_id}: {alert_type}")
            
        except Exception as e:
            logger.error(f"Erreur création alerte sécurité: {e}")
    
    async def get_security_audit_report(self, user_id: str = None, 
                                       start_date: datetime = None, 
                                       end_date: datetime = None) -> Dict[str, Any]:
        """Génère un rapport d'audit de sécurité"""
        try:
            # Définir les critères de recherche
            criteria = {}
            if user_id:
                criteria["user_id"] = user_id
            if start_date or end_date:
                criteria["timestamp"] = {}
                if start_date:
                    criteria["timestamp"]["$gte"] = start_date
                if end_date:
                    criteria["timestamp"]["$lte"] = end_date
            
            # Récupérer les événements de sécurité
            events = await self.db.security_events.find(criteria).to_list(None)
            
            # Récupérer les alertes
            alerts = await self.db.security_alerts.find(criteria).to_list(None)
            
            # Analyser les statistiques
            event_stats = {}
            for event in events:
                event_type = event["event_type"]
                event_stats[event_type] = event_stats.get(event_type, 0) + 1
            
            alert_stats = {}
            for alert in alerts:
                alert_type = alert["alert_type"]
                alert_stats[alert_type] = alert_stats.get(alert_type, 0) + 1
            
            # Calculer les métriques
            total_events = len(events)
            total_alerts = len(alerts)
            active_alerts = len([a for a in alerts if a["status"] == "active"])
            
            return {
                "audit_period": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "generated_at": datetime.utcnow()
                },
                "summary": {
                    "total_events": total_events,
                    "total_alerts": total_alerts,
                    "active_alerts": active_alerts,
                    "resolved_alerts": total_alerts - active_alerts
                },
                "event_statistics": event_stats,
                "alert_statistics": alert_stats,
                "recent_events": events[-50:] if events else [],
                "active_alerts": [a for a in alerts if a["status"] == "active"][:20]
            }
            
        except Exception as e:
            logger.error(f"Erreur génération rapport audit: {e}")
            return {
                "summary": {"total_events": 0, "total_alerts": 0},
                "event_statistics": {},
                "alert_statistics": {}
            }
    
    async def get_security_dashboard(self) -> Dict[str, Any]:
        """Récupère les données du tableau de bord sécurité"""
        try:
            # Événements des dernières 24h
            last_24h = datetime.utcnow() - timedelta(hours=24)
            recent_events = await self.db.security_events.find(
                {"timestamp": {"$gte": last_24h}}
            ).to_list(None)
            
            # Alertes actives
            active_alerts = await self.db.security_alerts.find(
                {"status": "active"}
            ).to_list(None)
            
            # Statistiques MFA
            mfa_stats = await self.db.mfa_configs.aggregate([
                {"$group": {
                    "_id": "$method",
                    "total": {"$sum": 1},
                    "enabled": {"$sum": {"$cond": ["$enabled", 1, 0]}}
                }}
            ]).to_list(None)
            
            # Top des menaces
            threat_analysis = {}
            for alert in active_alerts:
                for anomaly in alert.get("anomalies", []):
                    threat_type = anomaly["type"]
                    if threat_type not in threat_analysis:
                        threat_analysis[threat_type] = {
                            "count": 0,
                            "severity": anomaly["severity"]
                        }
                    threat_analysis[threat_type]["count"] += 1
            
            return {
                "overview": {
                    "events_last_24h": len(recent_events),
                    "active_alerts": len(active_alerts),
                    "mfa_enabled_users": sum(stat["enabled"] for stat in mfa_stats),
                    "total_users_with_mfa": sum(stat["total"] for stat in mfa_stats)
                },
                "mfa_statistics": mfa_stats,
                "threat_analysis": threat_analysis,
                "recent_events": recent_events[-20:],
                "active_alerts": active_alerts[:10],
                "security_score": self._calculate_security_score(active_alerts, mfa_stats)
            }
            
        except Exception as e:
            logger.error(f"Erreur tableau de bord sécurité: {e}")
            return {
                "overview": {
                    "events_last_24h": 0,
                    "active_alerts": 0,
                    "mfa_enabled_users": 0,
                    "total_users_with_mfa": 0
                },
                "security_score": 0.0
            }
    
    def _calculate_security_score(self, active_alerts: List[Dict], mfa_stats: List[Dict]) -> float:
        """Calcule un score de sécurité global"""
        try:
            base_score = 100.0
            
            # Réduire pour les alertes actives
            critical_alerts = len([a for a in active_alerts if a.get("risk_score", 0) >= self.risk_thresholds[SecurityLevel.CRITICAL]])
            high_alerts = len([a for a in active_alerts if a.get("risk_score", 0) >= self.risk_thresholds[SecurityLevel.HIGH]])
            
            base_score -= (critical_alerts * 20)
            base_score -= (high_alerts * 10)
            
            # Bonus pour la MFA
            total_mfa_users = sum(stat["total"] for stat in mfa_stats)
            enabled_mfa_users = sum(stat["enabled"] for stat in mfa_stats)
            
            if total_mfa_users > 0:
                mfa_ratio = enabled_mfa_users / total_mfa_users
                base_score += (mfa_ratio * 10)
            
            return max(0.0, min(100.0, base_score))
            
        except Exception as e:
            logger.error(f"Erreur calcul score sécurité: {e}")
            return 50.0
    
    # ===== HONEYPOTS ET PIÈGES =====
    
    async def create_honeypot(self, honeypot_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un piège pour détecter les attaques"""
        try:
            honeypot = {
                "id": str(uuid.uuid4()),
                "type": honeypot_type,
                "config": config,
                "created_at": datetime.utcnow(),
                "active": True,
                "interactions": 0,
                "last_triggered": None
            }
            
            await self.db.honeypots.insert_one(honeypot)
            
            return {
                "honeypot_id": honeypot["id"],
                "type": honeypot_type,
                "status": "active",
                "created_at": honeypot["created_at"]
            }
            
        except Exception as e:
            logger.error(f"Erreur création honeypot: {e}")
            raise Exception(f"Impossible de créer le honeypot: {e}")
    
    async def trigger_honeypot(self, honeypot_id: str, interaction_data: Dict[str, Any]) -> None:
        """Déclenche un piège et enregistre l'interaction"""
        try:
            # Mettre à jour le honeypot
            await self.db.honeypots.update_one(
                {"id": honeypot_id},
                {
                    "$inc": {"interactions": 1},
                    "$set": {"last_triggered": datetime.utcnow()}
                }
            )
            
            # Enregistrer l'interaction
            interaction = {
                "id": str(uuid.uuid4()),
                "honeypot_id": honeypot_id,
                "data": interaction_data,
                "timestamp": datetime.utcnow(),
                "threat_level": "high"
            }
            
            await self.db.honeypot_interactions.insert_one(interaction)
            
            # Créer une alerte critique
            await self.create_security_alert(
                user_id=interaction_data.get("user_id", "unknown"),
                alert_type="honeypot_triggered",
                risk_score=0.95,
                anomalies=[{
                    "type": "honeypot_interaction",
                    "description": f"Interaction avec honeypot {honeypot_id}",
                    "severity": SecurityLevel.CRITICAL.value
                }]
            )
            
        except Exception as e:
            logger.error(f"Erreur déclenchement honeypot: {e}")
    
    async def get_honeypot_report(self) -> Dict[str, Any]:
        """Génère un rapport sur les honeypots"""
        try:
            # Récupérer tous les honeypots
            honeypots = await self.db.honeypots.find({"active": True}).to_list(None)
            
            # Récupérer les interactions récentes
            recent_interactions = await self.db.honeypot_interactions.find(
                {"timestamp": {"$gte": datetime.utcnow() - timedelta(hours=24)}}
            ).to_list(None)
            
            # Analyser les statistiques
            total_interactions = await self.db.honeypot_interactions.count_documents({})
            
            return {
                "active_honeypots": len(honeypots),
                "total_interactions": total_interactions,
                "recent_interactions": len(recent_interactions),
                "honeypots": honeypots,
                "recent_activity": recent_interactions[:10]
            }
            
        except Exception as e:
            logger.error(f"Erreur rapport honeypots: {e}")
            return {"active_honeypots": 0, "total_interactions": 0}
    
    # ===== BACKUP ET RÉCUPÉRATION =====
    
    async def create_security_backup(self, backup_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée une sauvegarde sécurisée"""
        try:
            # Chiffrer les données sensibles
            encrypted_data = self.cipher_suite.encrypt(json.dumps(data).encode())
            
            backup = {
                "id": str(uuid.uuid4()),
                "type": backup_type,
                "encrypted_data": encrypted_data.decode(),
                "created_at": datetime.utcnow(),
                "checksum": hashlib.sha256(encrypted_data).hexdigest(),
                "size": len(encrypted_data),
                "status": "active"
            }
            
            await self.db.security_backups.insert_one(backup)
            
            return {
                "backup_id": backup["id"],
                "type": backup_type,
                "created_at": backup["created_at"],
                "checksum": backup["checksum"],
                "status": "created"
            }
            
        except Exception as e:
            logger.error(f"Erreur création backup: {e}")
            raise Exception(f"Impossible de créer la sauvegarde: {e}")
    
    async def restore_security_backup(self, backup_id: str) -> Dict[str, Any]:
        """Restaure une sauvegarde sécurisée"""
        try:
            # Récupérer la sauvegarde
            backup = await self.db.security_backups.find_one({"id": backup_id})
            if not backup:
                raise ValueError("Sauvegarde non trouvée")
            
            # Déchiffrer les données
            encrypted_data = backup["encrypted_data"].encode()
            
            # Vérifier l'intégrité
            if hashlib.sha256(encrypted_data).hexdigest() != backup["checksum"]:
                raise ValueError("Intégrité de la sauvegarde compromise")
            
            # Déchiffrer
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            data = json.loads(decrypted_data.decode())
            
            return {
                "backup_id": backup_id,
                "type": backup["type"],
                "data": data,
                "restored_at": datetime.utcnow(),
                "status": "restored"
            }
            
        except Exception as e:
            logger.error(f"Erreur restauration backup: {e}")
            raise Exception(f"Impossible de restaurer la sauvegarde: {e}")
    
    async def get_backup_report(self) -> Dict[str, Any]:
        """Génère un rapport sur les sauvegardes"""
        try:
            # Récupérer toutes les sauvegardes
            backups = await self.db.security_backups.find({}).to_list(None)
            
            # Analyser par type
            backup_stats = {}
            total_size = 0
            
            for backup in backups:
                backup_type = backup["type"]
                if backup_type not in backup_stats:
                    backup_stats[backup_type] = {
                        "count": 0,
                        "size": 0
                    }
                backup_stats[backup_type]["count"] += 1
                backup_stats[backup_type]["size"] += backup["size"]
                total_size += backup["size"]
            
            return {
                "total_backups": len(backups),
                "total_size": total_size,
                "backup_types": backup_stats,
                "recent_backups": sorted(backups, key=lambda x: x["created_at"], reverse=True)[:10]
            }
            
        except Exception as e:
            logger.error(f"Erreur rapport sauvegardes: {e}")
            return {"total_backups": 0, "total_size": 0}
    
    # ===== CONFORMITÉ RÉGLEMENTAIRE =====
    
    async def generate_gdpr_report(self, user_id: str) -> Dict[str, Any]:
        """Génère un rapport GDPR pour un utilisateur"""
        try:
            # Récupérer toutes les données personnelles
            user_data = await self.db.users.find_one({"id": user_id})
            if not user_data:
                raise ValueError("Utilisateur non trouvé")
            
            # Récupérer les données associées
            mfa_configs = await self.db.mfa_configs.find({"user_id": user_id}).to_list(None)
            security_events = await self.db.security_events.find({"user_id": user_id}).to_list(None)
            behavior_data = await self.db.user_behavior.find({"user_id": user_id}).to_list(None)
            
            # Compilation des données
            gdpr_data = {
                "user_profile": {
                    "id": user_data["id"],
                    "email": user_data["email"],
                    "created_at": user_data.get("created_at"),
                    "last_login": user_data.get("last_login")
                },
                "security_data": {
                    "mfa_configurations": len(mfa_configs),
                    "security_events": len(security_events),
                    "behavior_records": len(behavior_data)
                },
                "data_processing": {
                    "purposes": ["authentication", "security", "fraud_prevention"],
                    "legal_basis": "legitimate_interest",
                    "retention_period": "3 years"
                },
                "rights": {
                    "access": "granted",
                    "rectification": "available",
                    "erasure": "available",
                    "portability": "available"
                }
            }
            
            return {
                "gdpr_report": gdpr_data,
                "generated_at": datetime.utcnow(),
                "status": "complete"
            }
            
        except Exception as e:
            logger.error(f"Erreur rapport GDPR: {e}")
            raise Exception(f"Impossible de générer le rapport GDPR: {e}")
    
    async def delete_user_data(self, user_id: str, verification_code: str) -> Dict[str, Any]:
        """Supprime toutes les données d'un utilisateur (droit à l'effacement)"""
        try:
            # Vérifier le code de vérification (à implémenter selon les besoins)
            # Pour la démo, on accepte tout code non vide
            if not verification_code:
                raise ValueError("Code de vérification requis")
            
            # Supprimer les données utilisateur
            collections_to_clean = [
                "users",
                "mfa_configs", 
                "security_events",
                "user_behavior",
                "security_alerts"
            ]
            
            deleted_records = {}
            
            for collection in collections_to_clean:
                result = await self.db[collection].delete_many({"user_id": user_id})
                deleted_records[collection] = result.deleted_count
            
            # Créer un log de suppression
            deletion_log = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "deleted_records": deleted_records,
                "deletion_date": datetime.utcnow(),
                "verification_code": hashlib.sha256(verification_code.encode()).hexdigest()
            }
            
            await self.db.deletion_logs.insert_one(deletion_log)
            
            return {
                "status": "deleted",
                "deleted_records": deleted_records,
                "deletion_date": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Erreur suppression données utilisateur: {e}")
            raise Exception(f"Impossible de supprimer les données: {e}")
    
    async def get_compliance_report(self) -> Dict[str, Any]:
        """Génère un rapport de conformité global"""
        try:
            # Compter les utilisateurs
            total_users = await self.db.users.count_documents({})
            
            # Compter les consentements (à implémenter selon les besoins)
            # Pour la démo, on simule
            consents = await self.db.users.count_documents({"consent_given": True})
            
            # Compter les suppressions
            deletions = await self.db.deletion_logs.count_documents({})
            
            # Compter les sauvegardes
            backups = await self.db.security_backups.count_documents({})
            
            return {
                "gdpr_compliance": {
                    "total_users": total_users,
                    "consents_given": consents,
                    "data_deletions": deletions,
                    "security_backups": backups,
                    "compliance_score": self._calculate_compliance_score(total_users, consents, backups)
                },
                "ccpa_compliance": {
                    "data_protection_measures": True,
                    "user_rights_implemented": True,
                    "privacy_policy_updated": True
                },
                "generated_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Erreur rapport conformité: {e}")
            return {"gdpr_compliance": {"compliance_score": 0.0}}
    
    def _calculate_compliance_score(self, total_users: int, consents: int, backups: int) -> float:
        """Calcule un score de conformité"""
        try:
            base_score = 0.0
            
            # Score basé sur les consentements
            if total_users > 0:
                consent_ratio = consents / total_users
                base_score += (consent_ratio * 40)
            
            # Score basé sur les sauvegardes
            if backups > 0:
                base_score += 30
            
            # Score basé sur l'implémentation des droits
            base_score += 30  # Droits implémentés
            
            return min(100.0, base_score)
            
        except Exception as e:
            logger.error(f"Erreur calcul score conformité: {e}")
            return 0.0
    
    # ===== FONCTIONS UTILITAIRES =====
    
    async def get_comprehensive_security_report(self) -> Dict[str, Any]:
        """Génère un rapport de sécurité complet"""
        try:
            # Récupérer tous les rapports
            dashboard = await self.get_security_dashboard()
            audit_report = await self.get_security_audit_report()
            honeypot_report = await self.get_honeypot_report()
            backup_report = await self.get_backup_report()
            compliance_report = await self.get_compliance_report()
            
            return {
                "overview": dashboard,
                "audit": audit_report,
                "honeypots": honeypot_report,
                "backups": backup_report,
                "compliance": compliance_report,
                "generated_at": datetime.utcnow(),
                "report_version": "1.0"
            }
            
        except Exception as e:
            logger.error(f"Erreur rapport sécurité complet: {e}")
            return {"status": "error", "message": str(e)}
    
    async def perform_security_health_check(self) -> Dict[str, Any]:
        """Effectue un contrôle de santé sécurité"""
        try:
            health_status = {
                "mfa_service": self.is_ready(),
                "honeypots_active": False,
                "backups_available": False,
                "compliance_ok": False,
                "overall_status": "degraded"
            }
            
            # Vérifier les honeypots
            honeypot_count = await self.db.honeypots.count_documents({"active": True})
            health_status["honeypots_active"] = honeypot_count > 0
            
            # Vérifier les sauvegardes
            backup_count = await self.db.security_backups.count_documents({})
            health_status["backups_available"] = backup_count > 0
            
            # Vérifier la conformité
            compliance = await self.get_compliance_report()
            health_status["compliance_ok"] = compliance["gdpr_compliance"]["compliance_score"] > 70
            
            # Statut global
            all_checks = [
                health_status["mfa_service"],
                health_status["honeypots_active"],
                health_status["backups_available"],
                health_status["compliance_ok"]
            ]
            
            if all(all_checks):
                health_status["overall_status"] = "healthy"
            elif sum(all_checks) >= 3:
                health_status["overall_status"] = "good"
            elif sum(all_checks) >= 2:
                health_status["overall_status"] = "degraded"
            else:
                health_status["overall_status"] = "critical"
            
            return health_status
            
        except Exception as e:
            logger.error(f"Erreur contrôle santé sécurité: {e}")
            return {"overall_status": "error", "error": str(e)}
"""
Service d'authentification avec sécurité post-quantique
"""

import hashlib
import jwt
import bcrypt
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging
from motor.motor_asyncio import AsyncIOMotorCollection
import os

from models.quantum_models import User, UserCreate, UserLogin
from services.ntru_service import NTRUService

logger = logging.getLogger(__name__)

class AuthService:
    """Service d'authentification avec sécurité post-quantique"""
    
    def __init__(self, db):
        self.db = db
        self.users: AsyncIOMotorCollection = db.users
        self.sessions: AsyncIOMotorCollection = db.sessions
        self.ntru_service = NTRUService()
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-here")
        self.token_expiry = timedelta(hours=24)
    
    async def register_user(self, user_data: UserCreate) -> User:
        """Enregistre un nouvel utilisateur"""
        try:
            # Vérifier si l'utilisateur existe déjà
            existing_user = await self.users.find_one({
                "$or": [
                    {"email": user_data.email},
                    {"username": user_data.username}
                ]
            })
            
            if existing_user:
                raise Exception("Utilisateur déjà existant")
            
            # Hacher le mot de passe
            password_hash = bcrypt.hashpw(
                user_data.password.encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')
            
            # Générer une adresse de wallet (clé publique NTRU++)
            public_key, private_key = self.ntru_service.generate_keypair()
            wallet_address = self.generate_wallet_address(public_key)
            
            # Créer l'utilisateur
            user = User(
                email=user_data.email,
                username=user_data.username,
                wallet_address=wallet_address
            )
            
            # Sauvegarder dans la base de données
            user_dict = user.dict()
            user_dict["password_hash"] = password_hash
            user_dict["private_key"] = private_key  # À chiffrer en production
            user_dict["public_key"] = public_key
            
            await self.users.insert_one(user_dict)
            
            logger.info(f"Utilisateur {user.username} enregistré avec succès")
            return user
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement: {e}")
            raise Exception(f"Impossible d'enregistrer l'utilisateur: {e}")
    
    async def authenticate_user(self, login_data: UserLogin) -> Optional[Dict[str, Any]]:
        """Authentifie un utilisateur"""
        try:
            # Récupérer l'utilisateur
            user_doc = await self.users.find_one({"username": login_data.username})
            
            if not user_doc:
                logger.warning(f"Tentative de connexion avec username inexistant: {login_data.username}")
                return None
            
            # Vérifier le mot de passe
            if not bcrypt.checkpw(
                login_data.password.encode('utf-8'),
                user_doc["password_hash"].encode('utf-8')
            ):
                logger.warning(f"Mot de passe incorrect pour: {login_data.username}")
                return None
            
            # Créer le token JWT
            token_payload = {
                "user_id": user_doc["id"],
                "username": user_doc["username"],
                "wallet_address": user_doc["wallet_address"],
                "exp": datetime.utcnow() + self.token_expiry
            }
            
            token = jwt.encode(token_payload, self.secret_key, algorithm="HS256")
            
            # Enregistrer la session
            session_data = {
                "user_id": user_doc["id"],
                "token": token,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + self.token_expiry,
                "is_active": True
            }
            
            await self.sessions.insert_one(session_data)
            
            # Mettre à jour la dernière connexion
            await self.users.update_one(
                {"id": user_doc["id"]},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            
            logger.info(f"Utilisateur {login_data.username} connecté avec succès")
            
            return {
                "user": User(**user_doc),
                "token": token,
                "expires_at": session_data["expires_at"]
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'authentification: {e}")
            return None
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Vérifie un token JWT"""
        try:
            # Décoder le token
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            
            # Vérifier si la session est active
            session = await self.sessions.find_one({
                "token": token,
                "is_active": True,
                "expires_at": {"$gt": datetime.utcnow()}
            })
            
            if not session:
                logger.warning("Token invalide ou expiré")
                return None
            
            # Récupérer l'utilisateur
            user_doc = await self.users.find_one({"id": payload["user_id"]})
            
            if not user_doc or not user_doc.get("is_active", True):
                logger.warning("Utilisateur inactif ou inexistant")
                return None
            
            return {
                "user": User(**user_doc),
                "payload": payload
            }
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expiré")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Token invalide")
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du token: {e}")
            return None
    
    async def logout_user(self, token: str) -> bool:
        """Déconnecte un utilisateur"""
        try:
            # Désactiver la session
            result = await self.sessions.update_one(
                {"token": token},
                {"$set": {"is_active": False}}
            )
            
            if result.modified_count > 0:
                logger.info("Utilisateur déconnecté avec succès")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur lors de la déconnexion: {e}")
            return False
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Récupère un utilisateur par son ID"""
        try:
            user_doc = await self.users.find_one({"id": user_id})
            
            if user_doc:
                return User(**user_doc)
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'utilisateur: {e}")
            return None
    
    async def update_user_profile(self, user_id: str, update_data: Dict[str, Any]) -> Optional[User]:
        """Met à jour le profil d'un utilisateur"""
        try:
            # Champs autorisés à la mise à jour
            allowed_fields = ["email", "username"]
            update_dict = {k: v for k, v in update_data.items() if k in allowed_fields}
            
            if not update_dict:
                return None
            
            # Vérifier l'unicité email/username
            if "email" in update_dict or "username" in update_dict:
                existing_user = await self.users.find_one({
                    "$or": [
                        {"email": update_dict.get("email")},
                        {"username": update_dict.get("username")}
                    ],
                    "id": {"$ne": user_id}
                })
                
                if existing_user:
                    raise Exception("Email ou nom d'utilisateur déjà utilisé")
            
            # Mettre à jour
            result = await self.users.update_one(
                {"id": user_id},
                {"$set": update_dict}
            )
            
            if result.modified_count > 0:
                updated_user = await self.get_user_by_id(user_id)
                logger.info(f"Profil mis à jour pour l'utilisateur {user_id}")
                return updated_user
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du profil: {e}")
            return None
    
    async def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Change le mot de passe d'un utilisateur"""
        try:
            # Récupérer l'utilisateur
            user_doc = await self.users.find_one({"id": user_id})
            
            if not user_doc:
                return False
            
            # Vérifier l'ancien mot de passe
            if not bcrypt.checkpw(
                old_password.encode('utf-8'),
                user_doc["password_hash"].encode('utf-8')
            ):
                logger.warning(f"Ancien mot de passe incorrect pour l'utilisateur {user_id}")
                return False
            
            # Hacher le nouveau mot de passe
            new_password_hash = bcrypt.hashpw(
                new_password.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')
            
            # Mettre à jour
            result = await self.users.update_one(
                {"id": user_id},
                {"$set": {"password_hash": new_password_hash}}
            )
            
            if result.modified_count > 0:
                # Invalider toutes les sessions actives
                await self.sessions.update_many(
                    {"user_id": user_id, "is_active": True},
                    {"$set": {"is_active": False}}
                )
                
                logger.info(f"Mot de passe changé pour l'utilisateur {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur lors du changement de mot de passe: {e}")
            return False
    
    def generate_wallet_address(self, public_key: str) -> str:
        """Génère une adresse de wallet basée sur la clé publique"""
        # Hacher la clé publique
        hash_object = hashlib.sha256(public_key.encode())
        address_hash = hash_object.hexdigest()
        
        # Formatage de l'adresse (style Ethereum)
        wallet_address = "0x" + address_hash[:40]
        
        return wallet_address
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Récupère les statistiques d'un utilisateur"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return {}
            
            # Compter les devices
            device_count = await self.db.devices.count_documents({"owner_id": user_id})
            
            # Compter les récompenses
            reward_count = await self.db.reward_claims.count_documents({"user_id": user_id})
            
            # Calculer les tokens gagnés
            total_rewards = await self.db.reward_claims.aggregate([
                {"$match": {"user_id": user_id}},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
            ]).to_list(length=1)
            
            total_earned = total_rewards[0]["total"] if total_rewards else 0
            
            # Sessions actives
            active_sessions = await self.sessions.count_documents({
                "user_id": user_id,
                "is_active": True,
                "expires_at": {"$gt": datetime.utcnow()}
            })
            
            # Récupérer les détails complets de l'utilisateur
            user_doc = await self.users.find_one({"id": user_id})
            
            return {
                "user_id": user_id,
                "username": user.username,
                "wallet_address": user.wallet_address,
                "qs_balance": user.qs_balance,
                "reputation_score": user.reputation_score,
                "device_count": device_count,
                "total_rewards_claimed": reward_count,
                "total_tokens_earned": total_earned,
                "active_sessions": active_sessions,
                "member_since": user.created_at,
                "last_login": user_doc.get("last_login") if user_doc else None
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques: {e}")
            return {}
    
    async def cleanup_expired_sessions(self):
        """Nettoie les sessions expirées"""
        try:
            result = await self.sessions.delete_many({
                "expires_at": {"$lt": datetime.utcnow()}
            })
            
            if result.deleted_count > 0:
                logger.info(f"{result.deleted_count} sessions expirées supprimées")
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des sessions: {e}")
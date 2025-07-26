"""
Service de gestion des tokens $QS
Écosystème auto-monétisant avec récompenses
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from motor.motor_asyncio import AsyncIOMotorCollection
import asyncio

from models.quantum_models import TokenBalance, TokenTransaction, RewardClaim, TransactionType

logger = logging.getLogger(__name__)

class TokenService:
    """Service de gestion des tokens $QS et système de récompenses"""
    
    def __init__(self, db):
        self.db = db
        self.balances: AsyncIOMotorCollection = db.token_balances
        self.transactions: AsyncIOMotorCollection = db.token_transactions
        self.rewards: AsyncIOMotorCollection = db.reward_claims
        self.reward_rates = {
            "device_registration": 50.0,
            "anomaly_detection": 25.0,
            "firmware_validation": 10.0,
            "network_participation": 5.0,
            "data_sharing": 15.0,
            "mining_participation": 100.0
        }
        self.initial_supply = 1000000  # 1M tokens
        self.max_supply = 10000000    # 10M tokens
    
    async def initialize_token_system(self):
        """Initialise le système de tokens"""
        try:
            # Vérifier si le système est déjà initialisé
            system_balance = await self.balances.find_one({"user_id": "system"})
            
            if not system_balance:
                # Créer le balance système avec l'offre initiale
                system_balance = TokenBalance(
                    user_id="system",
                    balance=self.initial_supply
                )
                
                await self.balances.insert_one(system_balance.dict())
                
                # Transaction de création des tokens
                creation_tx = TokenTransaction(
                    from_user="genesis",
                    to_user="system",
                    amount=self.initial_supply,
                    transaction_type=TransactionType.REWARD,
                    description="Création initiale des tokens $QS"
                )
                
                await self.transactions.insert_one(creation_tx.dict())
                
                logger.info(f"Système de tokens initialisé avec {self.initial_supply} QS")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du système de tokens: {e}")
    
    async def get_balance(self, user_id: str) -> float:
        """Récupère le solde d'un utilisateur"""
        try:
            balance_doc = await self.balances.find_one({"user_id": user_id})
            
            if balance_doc:
                return balance_doc["balance"]
            else:
                # Créer un nouveau balance à zéro
                new_balance = TokenBalance(user_id=user_id, balance=0.0)
                await self.balances.insert_one(new_balance.dict())
                return 0.0
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du solde: {e}")
            return 0.0
    
    async def transfer_tokens(self, from_user: str, to_user: str, amount: float, 
                             transaction_type: TransactionType = TransactionType.REWARD,
                             description: str = "") -> bool:
        """Transfère des tokens entre utilisateurs"""
        try:
            # Vérifier le solde de l'expéditeur
            from_balance = await self.get_balance(from_user)
            
            if from_balance < amount:
                logger.warning(f"Solde insuffisant pour {from_user}: {from_balance} < {amount}")
                return False
            
            # Débiter l'expéditeur
            await self.balances.update_one(
                {"user_id": from_user},
                {"$inc": {"balance": -amount}, "$set": {"last_updated": datetime.utcnow()}}
            )
            
            # Créditer le destinataire
            to_balance = await self.get_balance(to_user)
            await self.balances.update_one(
                {"user_id": to_user},
                {"$inc": {"balance": amount}, "$set": {"last_updated": datetime.utcnow()}},
                upsert=True
            )
            
            # Enregistrer la transaction
            transaction = TokenTransaction(
                from_user=from_user,
                to_user=to_user,
                amount=amount,
                transaction_type=transaction_type,
                description=description
            )
            
            await self.transactions.insert_one(transaction.dict())
            
            logger.info(f"Transfert de {amount} QS: {from_user} -> {to_user}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du transfert: {e}")
            return False
    
    async def reward_user(self, user_id: str, reward_type: str, device_id: str = None, 
                         multiplier: float = 1.0) -> bool:
        """Récompense un utilisateur avec des tokens $QS"""
        try:
            # Vérifier si le type de récompense existe
            if reward_type not in self.reward_rates:
                logger.error(f"Type de récompense inconnu: {reward_type}")
                return False
            
            # Calculer le montant de la récompense
            base_amount = self.reward_rates[reward_type]
            reward_amount = base_amount * multiplier
            
            # Vérifier les récompenses récentes pour éviter l'abus
            if not await self.can_claim_reward(user_id, reward_type, device_id):
                logger.warning(f"Récompense refusée pour {user_id}: trop récente")
                return False
            
            # Transférer les tokens du système vers l'utilisateur
            success = await self.transfer_tokens(
                from_user="system",
                to_user=user_id,
                amount=reward_amount,
                transaction_type=TransactionType.REWARD,
                description=f"Récompense pour {reward_type}"
            )
            
            if success:
                # Enregistrer la réclamation de récompense
                reward_claim = RewardClaim(
                    user_id=user_id,
                    device_id=device_id or "system",
                    reward_type=reward_type,
                    amount=reward_amount
                )
                
                await self.rewards.insert_one(reward_claim.dict())
                
                logger.info(f"Récompense accordée: {reward_amount} QS à {user_id} pour {reward_type}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur lors de la récompense: {e}")
            return False
    
    async def can_claim_reward(self, user_id: str, reward_type: str, device_id: str = None) -> bool:
        """Vérifie si un utilisateur peut réclamer une récompense"""
        try:
            # Définir les limites de temps pour chaque type de récompense
            time_limits = {
                "device_registration": timedelta(hours=24),
                "anomaly_detection": timedelta(hours=1),
                "firmware_validation": timedelta(hours=6),
                "network_participation": timedelta(hours=24),
                "data_sharing": timedelta(hours=12),
                "mining_participation": timedelta(minutes=30)
            }
            
            time_limit = time_limits.get(reward_type, timedelta(hours=1))
            cutoff_time = datetime.utcnow() - time_limit
            
            # Vérifier les réclamations récentes
            query = {
                "user_id": user_id,
                "reward_type": reward_type,
                "timestamp": {"$gte": cutoff_time}
            }
            
            if device_id:
                query["device_id"] = device_id
            
            recent_claim = await self.rewards.find_one(query)
            
            return recent_claim is None
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des récompenses: {e}")
            return False
    
    async def get_user_transactions(self, user_id: str, limit: int = 100) -> List[TokenTransaction]:
        """Récupère les transactions d'un utilisateur"""
        try:
            cursor = self.transactions.find(
                {"$or": [{"from_user": user_id}, {"to_user": user_id}]}
            ).sort("timestamp", -1).limit(limit)
            
            transactions_data = await cursor.to_list(length=limit)
            
            transactions = []
            for tx_data in transactions_data:
                transactions.append(TokenTransaction(**tx_data))
            
            return transactions
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des transactions: {e}")
            return []
    
    async def get_user_rewards(self, user_id: str, limit: int = 100) -> List[RewardClaim]:
        """Récupère les récompenses d'un utilisateur"""
        try:
            cursor = self.rewards.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(limit)
            
            rewards_data = await cursor.to_list(length=limit)
            
            rewards = []
            for reward_data in rewards_data:
                rewards.append(RewardClaim(**reward_data))
            
            return rewards
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des récompenses: {e}")
            return []
    
    async def get_token_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques du système de tokens"""
        try:
            # Calculer l'offre totale en circulation
            total_supply = 0
            cursor = self.balances.find({})
            balances = await cursor.to_list(length=None)
            
            for balance in balances:
                total_supply += balance.get("balance", 0)
            
            # Compter les transactions
            total_transactions = await self.transactions.count_documents({})
            
            # Compter les récompenses
            total_rewards = await self.rewards.count_documents({})
            
            # Calculer les récompenses par type
            pipeline = [
                {
                    "$group": {
                        "_id": "$reward_type",
                        "total_amount": {"$sum": "$amount"},
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            reward_stats = await self.rewards.aggregate(pipeline).to_list(length=None)
            
            # Top holders avec gestion d'erreur et sérialisation
            try:
                top_holders_cursor = self.balances.find({
                    "user_id": {"$ne": "system"}
                }).sort("balance", -1).limit(10)
                top_holders_raw = await top_holders_cursor.to_list(length=10)
                
                # Convertir les ObjectId en strings
                top_holders = []
                for holder in top_holders_raw:
                    holder_data = {
                        "user_id": holder.get("user_id", "unknown"),
                        "balance": holder.get("balance", 0),
                        "wallet_address": holder.get("wallet_address", ""),
                        "last_updated": holder.get("last_updated", datetime.utcnow()).isoformat() if holder.get("last_updated") else datetime.utcnow().isoformat()
                    }
                    top_holders.append(holder_data)
            except:
                top_holders = []
            
            # Calculer l'offre en circulation de manière plus sûre
            circulating_supply = total_supply
            if balances:
                # Trouver le compte système
                system_balance = 0
                for balance in balances:
                    if balance.get("user_id") == "system":
                        system_balance = balance.get("balance", 0)
                        break
                circulating_supply = total_supply - system_balance
            
            return {
                "total_supply": total_supply,
                "max_supply": self.max_supply,
                "circulating_supply": circulating_supply,
                "total_transactions": total_transactions,
                "total_rewards_claimed": total_rewards,
                "reward_distribution": {stat["_id"]: stat for stat in reward_stats},
                "top_holders": top_holders,
                "reward_rates": self.reward_rates
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques: {e}")
            # Retourner des statistiques par défaut
            return {
                "total_supply": self.max_supply,
                "max_supply": self.max_supply,
                "circulating_supply": 50000,
                "total_transactions": 0,
                "total_rewards_claimed": 0,
                "reward_distribution": {},
                "top_holders": [],
                "reward_rates": self.reward_rates
            }
    
    async def calculate_user_score(self, user_id: str) -> Dict[str, Any]:
        """Calcule le score de réputation d'un utilisateur"""
        try:
            # Récupérer les récompenses de l'utilisateur
            rewards = await self.get_user_rewards(user_id)
            
            # Calculer les points par catégorie
            category_scores = {}
            total_score = 0
            
            for reward in rewards:
                category = reward.reward_type
                if category not in category_scores:
                    category_scores[category] = 0
                
                # Points basés sur le montant et l'ancienneté
                days_old = (datetime.utcnow() - reward.timestamp).days
                decay_factor = max(0.1, 1 - (days_old / 365))  # Décroissance annuelle
                
                points = reward.amount * decay_factor
                category_scores[category] += points
                total_score += points
            
            # Calculer le niveau basé sur le score total
            level = min(10, max(1, int(total_score / 100) + 1))
            
            return {
                "user_id": user_id,
                "total_score": total_score,
                "level": level,
                "category_scores": category_scores,
                "total_rewards": len(rewards),
                "current_balance": await self.get_balance(user_id)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul du score: {e}")
            return {}
    
    async def get_leaderboard(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Récupère le classement des utilisateurs"""
        try:
            # Récupérer tous les utilisateurs avec un solde
            cursor = self.balances.find({
                "user_id": {"$ne": "system"},
                "balance": {"$gt": 0}
            }).sort("balance", -1).limit(limit)
            
            balances = await cursor.to_list(length=limit)
            
            leaderboard = []
            for i, balance in enumerate(balances):
                user_id = balance["user_id"]
                
                # Calculer le score de réputation
                score_data = await self.calculate_user_score(user_id)
                
                # Compter les devices de l'utilisateur
                device_count = await self.db.devices.count_documents({"owner_id": user_id})
                
                leaderboard.append({
                    "rank": i + 1,
                    "user_id": user_id,
                    "balance": balance["balance"],
                    "reputation_score": score_data.get("total_score", 0),
                    "level": score_data.get("level", 1),
                    "device_count": device_count,
                    "last_activity": balance["last_updated"]
                })
            
            return leaderboard
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du classement: {e}")
            return []
    
    async def process_daily_rewards(self):
        """Traite les récompenses quotidiennes automatiques"""
        try:
            # Récompenser les utilisateurs actifs
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            # Trouver les utilisateurs avec des devices actifs
            active_devices = await self.db.devices.find({
                "last_heartbeat": {"$gte": cutoff_time},
                "status": "active"
            }).to_list(length=None)
            
            # Grouper par propriétaire
            user_activity = {}
            for device in active_devices:
                owner_id = device["owner_id"]
                if owner_id not in user_activity:
                    user_activity[owner_id] = 0
                user_activity[owner_id] += 1
            
            # Récompenser basé sur l'activité
            for user_id, device_count in user_activity.items():
                reward_multiplier = min(2.0, 1.0 + (device_count / 10))
                
                await self.reward_user(
                    user_id=user_id,
                    reward_type="network_participation",
                    multiplier=reward_multiplier
                )
            
            logger.info(f"Récompenses quotidiennes traitées pour {len(user_activity)} utilisateurs")
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement des récompenses quotidiennes: {e}")

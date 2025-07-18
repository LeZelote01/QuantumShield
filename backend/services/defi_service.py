"""
Service de Staking et DeFi (Finance décentralisée)
Gestion des pools de staking, yield farming, et services financiers décentralisés
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import math

logger = logging.getLogger(__name__)

class StakingPoolStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"
    ENDED = "ended"

class LoanStatus(str, Enum):
    ACTIVE = "active"
    PAID = "paid"
    DEFAULTED = "defaulted"
    LIQUIDATED = "liquidated"

class StakingType(str, Enum):
    FIXED = "fixed"
    FLEXIBLE = "flexible"
    LIQUIDITY_MINING = "liquidity_mining"
    YIELD_FARMING = "yield_farming"

class DeFiService:
    """Service de Finance Décentralisée (DeFi)"""
    
    def __init__(self, db):
        self.db = db
        self.staking_pools = {}
        self.liquidity_pools = {}
        self.loans = {}
        self.yield_strategies = {}
        self.is_initialized = False
        self._initialize()
    
    def _initialize(self):
        """Initialise le service DeFi"""
        try:
            # Configuration par défaut
            self.config = {
                "base_staking_rate": 0.08,  # 8% APY base
                "max_staking_rate": 0.25,   # 25% APY max
                "liquidation_threshold": 0.75,  # 75% loan-to-value
                "loan_fee": 0.005,  # 0.5% frais d'emprunt
                "platform_fee": 0.02,  # 2% frais plateforme
                "min_stake_amount": 10.0,  # Minimum 10 QS
                "max_loan_duration": 365,  # 365 jours max
                "compound_frequency": 24,  # Compound toutes les heures
                "emergency_withdrawal_fee": 0.05,  # 5% frais retrait urgence
                "governance_threshold": 1000.0,  # 1000 QS pour proposer
            }
            
            # Initialiser les pools par défaut
            asyncio.create_task(self._initialize_default_pools())
            
            # Démarrer les processus de calcul des récompenses
            asyncio.create_task(self._start_reward_calculations())
            
            self.is_initialized = True
            logger.info("Service DeFi initialisé")
            
        except Exception as e:
            logger.error(f"Erreur initialisation DeFi: {str(e)}")
            self.is_initialized = False
    
    def is_ready(self) -> bool:
        """Vérifie si le service est prêt"""
        return self.is_initialized
    
    async def _initialize_default_pools(self):
        """Initialise les pools de staking par défaut"""
        try:
            default_pools = [
                {
                    "name": "QS Staking Pool",
                    "token_symbol": "QS",
                    "staking_type": StakingType.FLEXIBLE,
                    "apy": 0.12,  # 12% APY
                    "min_stake": 10.0,
                    "max_stake": 10000.0,
                    "lock_period": 0,  # Flexible
                    "description": "Pool de staking flexible pour tokens QS"
                },
                {
                    "name": "QS Fixed 30 Days",
                    "token_symbol": "QS",
                    "staking_type": StakingType.FIXED,
                    "apy": 0.18,  # 18% APY
                    "min_stake": 100.0,
                    "max_stake": 50000.0,
                    "lock_period": 30,  # 30 jours
                    "description": "Pool de staking fixe 30 jours avec APY élevé"
                },
                {
                    "name": "QS-ETH Liquidity Mining",
                    "token_symbol": "QS-ETH",
                    "staking_type": StakingType.LIQUIDITY_MINING,
                    "apy": 0.35,  # 35% APY
                    "min_stake": 50.0,
                    "max_stake": 25000.0,
                    "lock_period": 90,  # 90 jours
                    "description": "Pool de liquidity mining QS-ETH"
                },
                {
                    "name": "Yield Farming Premium",
                    "token_symbol": "QS",
                    "staking_type": StakingType.YIELD_FARMING,
                    "apy": 0.45,  # 45% APY
                    "min_stake": 1000.0,
                    "max_stake": 100000.0,
                    "lock_period": 180,  # 180 jours
                    "description": "Pool de yield farming haut rendement"
                }
            ]
            
            for pool_data in default_pools:
                existing = await self.db.staking_pools.find_one({"name": pool_data["name"]})
                if not existing:
                    await self._create_staking_pool(pool_data)
            
            logger.info("Pools de staking par défaut initialisés")
            
        except Exception as e:
            logger.error(f"Erreur initialisation pools: {str(e)}")
    
    async def _create_staking_pool(self, pool_data: Dict[str, Any]) -> str:
        """Crée un pool de staking"""
        try:
            pool_id = str(uuid.uuid4())
            
            pool_entry = {
                "pool_id": pool_id,
                "name": pool_data["name"],
                "token_symbol": pool_data["token_symbol"],
                "staking_type": pool_data["staking_type"].value if isinstance(pool_data["staking_type"], StakingType) else pool_data["staking_type"],
                "apy": pool_data["apy"],
                "min_stake": pool_data["min_stake"],
                "max_stake": pool_data["max_stake"],
                "lock_period": pool_data["lock_period"],
                "description": pool_data["description"],
                "status": StakingPoolStatus.ACTIVE.value,
                "created_at": datetime.utcnow(),
                "total_staked": 0.0,
                "total_stakers": 0,
                "total_rewards_distributed": 0.0,
                "current_reward_rate": pool_data["apy"],
                "emergency_withdrawal_enabled": True
            }
            
            await self.db.staking_pools.insert_one(pool_entry)
            
            # Ajouter au cache
            self.staking_pools[pool_id] = pool_entry
            
            return pool_id
            
        except Exception as e:
            logger.error(f"Erreur création pool: {str(e)}")
            raise
    
    # ==============================
    # Staking
    # ==============================
    
    async def stake_tokens(self,
                         user_id: str,
                         pool_id: str,
                         amount: float) -> Dict[str, Any]:
        """Stake des tokens dans un pool"""
        try:
            # Vérifier le pool
            pool = await self.db.staking_pools.find_one({"pool_id": pool_id})
            if not pool:
                return {"success": False, "error": "Pool non trouvé"}
            
            if pool["status"] != StakingPoolStatus.ACTIVE.value:
                return {"success": False, "error": "Pool non actif"}
            
            # Vérifier les montants
            if amount < pool["min_stake"]:
                return {"success": False, "error": f"Montant minimum: {pool['min_stake']} QS"}
            
            if amount > pool["max_stake"]:
                return {"success": False, "error": f"Montant maximum: {pool['max_stake']} QS"}
            
            # Vérifier le solde utilisateur
            user_balance = await self._get_user_balance(user_id)
            if user_balance < amount:
                return {"success": False, "error": "Solde insuffisant"}
            
            # Créer l'entrée de staking
            stake_id = str(uuid.uuid4())
            
            stake_entry = {
                "stake_id": stake_id,
                "user_id": user_id,
                "pool_id": pool_id,
                "amount": amount,
                "staked_at": datetime.utcnow(),
                "last_reward_claim": datetime.utcnow(),
                "unlock_date": datetime.utcnow() + timedelta(days=pool["lock_period"]) if pool["lock_period"] > 0 else None,
                "total_rewards_earned": 0.0,
                "status": "active",
                "apy_at_stake": pool["apy"],
                "compound_enabled": True
            }
            
            await self.db.user_stakes.insert_one(stake_entry)
            
            # Débiter le compte utilisateur
            await self._debit_user_balance(user_id, amount, f"Staking dans {pool['name']}")
            
            # Mettre à jour les statistiques du pool
            await self.db.staking_pools.update_one(
                {"pool_id": pool_id},
                {
                    "$inc": {
                        "total_staked": amount,
                        "total_stakers": 1
                    }
                }
            )
            
            logger.info(f"Staking créé: {user_id} -> {amount} QS dans {pool['name']}")
            
            return {
                "success": True,
                "stake_id": stake_id,
                "amount": amount,
                "pool_name": pool["name"],
                "apy": pool["apy"],
                "unlock_date": stake_entry["unlock_date"]
            }
            
        except Exception as e:
            logger.error(f"Erreur staking: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def unstake_tokens(self,
                           user_id: str,
                           stake_id: str,
                           emergency: bool = False) -> Dict[str, Any]:
        """Unstake des tokens"""
        try:
            # Récupérer le stake
            stake = await self.db.user_stakes.find_one({"stake_id": stake_id, "user_id": user_id})
            if not stake:
                return {"success": False, "error": "Stake non trouvé"}
            
            if stake["status"] != "active":
                return {"success": False, "error": "Stake non actif"}
            
            # Vérifier la période de blocage
            now = datetime.utcnow()
            if stake["unlock_date"] and now < stake["unlock_date"] and not emergency:
                return {"success": False, "error": "Période de blocage non écoulée"}
            
            # Calculer les récompenses
            await self._calculate_stake_rewards(stake_id)
            
            # Récupérer le stake mis à jour
            stake = await self.db.user_stakes.find_one({"stake_id": stake_id})
            
            # Calculer les frais
            withdrawal_fee = 0.0
            if emergency and stake["unlock_date"] and now < stake["unlock_date"]:
                withdrawal_fee = stake["amount"] * self.config["emergency_withdrawal_fee"]
            
            # Montant à rembourser
            amount_to_return = stake["amount"] + stake["total_rewards_earned"] - withdrawal_fee
            
            # Marquer le stake comme terminé
            await self.db.user_stakes.update_one(
                {"stake_id": stake_id},
                {
                    "$set": {
                        "status": "completed",
                        "unstaked_at": now,
                        "withdrawal_fee": withdrawal_fee
                    }
                }
            )
            
            # Créditer le compte utilisateur
            await self._credit_user_balance(user_id, amount_to_return, f"Unstaking de {stake['pool_id']}")
            
            # Mettre à jour les statistiques du pool
            await self.db.staking_pools.update_one(
                {"pool_id": stake["pool_id"]},
                {
                    "$inc": {
                        "total_staked": -stake["amount"],
                        "total_stakers": -1,
                        "total_rewards_distributed": stake["total_rewards_earned"]
                    }
                }
            )
            
            logger.info(f"Unstaking réussi: {user_id} -> {amount_to_return} QS")
            
            return {
                "success": True,
                "amount_returned": amount_to_return,
                "rewards_earned": stake["total_rewards_earned"],
                "withdrawal_fee": withdrawal_fee,
                "emergency": emergency
            }
            
        except Exception as e:
            logger.error(f"Erreur unstaking: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def claim_rewards(self, user_id: str, stake_id: str) -> Dict[str, Any]:
        """Réclame les récompenses d'un stake"""
        try:
            # Calculer les récompenses
            rewards = await self._calculate_stake_rewards(stake_id)
            
            if rewards <= 0:
                return {"success": False, "error": "Aucune récompense disponible"}
            
            # Marquer les récompenses comme réclamées
            await self.db.user_stakes.update_one(
                {"stake_id": stake_id, "user_id": user_id},
                {
                    "$set": {
                        "last_reward_claim": datetime.utcnow(),
                        "total_rewards_earned": 0.0  # Reset après réclamation
                    }
                }
            )
            
            # Créditer le compte utilisateur
            await self._credit_user_balance(user_id, rewards, f"Récompenses staking")
            
            return {
                "success": True,
                "rewards_claimed": rewards
            }
            
        except Exception as e:
            logger.error(f"Erreur réclamation récompenses: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _calculate_stake_rewards(self, stake_id: str) -> float:
        """Calcule les récompenses pour un stake"""
        try:
            stake = await self.db.user_stakes.find_one({"stake_id": stake_id})
            if not stake:
                return 0.0
            
            # Calculer le temps écoulé depuis la dernière réclamation
            now = datetime.utcnow()
            last_claim = stake["last_reward_claim"]
            time_diff = (now - last_claim).total_seconds()
            
            # Calculer les récompenses (APY annuel)
            annual_seconds = 365 * 24 * 3600
            reward_rate = stake["apy_at_stake"]
            
            # Récompenses = Principal * APY * (temps / année)
            rewards = stake["amount"] * reward_rate * (time_diff / annual_seconds)
            
            # Mettre à jour le stake
            await self.db.user_stakes.update_one(
                {"stake_id": stake_id},
                {
                    "$inc": {"total_rewards_earned": rewards},
                    "$set": {"last_reward_claim": now}
                }
            )
            
            return rewards
            
        except Exception as e:
            logger.error(f"Erreur calcul récompenses: {str(e)}")
            return 0.0
    
    # ==============================
    # Prêts/Emprunts
    # ==============================
    
    async def request_loan(self,
                         user_id: str,
                         collateral_amount: float,
                         loan_amount: float,
                         duration_days: int) -> Dict[str, Any]:
        """Demande un prêt avec collatéral"""
        try:
            # Vérifier les paramètres
            if duration_days > self.config["max_loan_duration"]:
                return {"success": False, "error": f"Durée maximale: {self.config['max_loan_duration']} jours"}
            
            # Vérifier le ratio loan-to-value
            ltv_ratio = loan_amount / collateral_amount
            if ltv_ratio > self.config["liquidation_threshold"]:
                return {"success": False, "error": f"Ratio LTV trop élevé (max: {self.config['liquidation_threshold']*100}%)"}
            
            # Vérifier le solde utilisateur pour le collatéral
            user_balance = await self._get_user_balance(user_id)
            if user_balance < collateral_amount:
                return {"success": False, "error": "Solde insuffisant pour le collatéral"}
            
            # Calculer les intérêts
            annual_rate = 0.12  # 12% APR
            interest_amount = loan_amount * annual_rate * (duration_days / 365)
            total_repayment = loan_amount + interest_amount
            
            # Frais de prêt
            loan_fee = loan_amount * self.config["loan_fee"]
            
            # Créer le prêt
            loan_id = str(uuid.uuid4())
            
            loan_entry = {
                "loan_id": loan_id,
                "user_id": user_id,
                "collateral_amount": collateral_amount,
                "loan_amount": loan_amount,
                "duration_days": duration_days,
                "interest_rate": annual_rate,
                "interest_amount": interest_amount,
                "total_repayment": total_repayment,
                "loan_fee": loan_fee,
                "status": LoanStatus.ACTIVE.value,
                "created_at": datetime.utcnow(),
                "due_date": datetime.utcnow() + timedelta(days=duration_days),
                "ltv_ratio": ltv_ratio,
                "liquidation_threshold": self.config["liquidation_threshold"]
            }
            
            await self.db.loans.insert_one(loan_entry)
            
            # Débiter le collatéral
            await self._debit_user_balance(user_id, collateral_amount, f"Collatéral prêt {loan_id}")
            
            # Créditer le montant du prêt (moins les frais)
            net_loan_amount = loan_amount - loan_fee
            await self._credit_user_balance(user_id, net_loan_amount, f"Prêt {loan_id}")
            
            logger.info(f"Prêt créé: {user_id} -> {loan_amount} QS")
            
            return {
                "success": True,
                "loan_id": loan_id,
                "loan_amount": loan_amount,
                "net_amount": net_loan_amount,
                "collateral_amount": collateral_amount,
                "total_repayment": total_repayment,
                "due_date": loan_entry["due_date"],
                "loan_fee": loan_fee
            }
            
        except Exception as e:
            logger.error(f"Erreur création prêt: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def repay_loan(self, user_id: str, loan_id: str, amount: float) -> Dict[str, Any]:
        """Rembourse un prêt"""
        try:
            # Récupérer le prêt
            loan = await self.db.loans.find_one({"loan_id": loan_id, "user_id": user_id})
            if not loan:
                return {"success": False, "error": "Prêt non trouvé"}
            
            if loan["status"] != LoanStatus.ACTIVE.value:
                return {"success": False, "error": "Prêt non actif"}
            
            # Vérifier le solde utilisateur
            user_balance = await self._get_user_balance(user_id)
            if user_balance < amount:
                return {"success": False, "error": "Solde insuffisant"}
            
            # Calculer les intérêts accumulés
            now = datetime.utcnow()
            created_at = loan["created_at"]
            days_elapsed = (now - created_at).days
            
            # Intérêts proportionnels au temps écoulé
            daily_rate = loan["interest_rate"] / 365
            accumulated_interest = loan["loan_amount"] * daily_rate * days_elapsed
            
            current_debt = loan["loan_amount"] + accumulated_interest
            
            # Débiter le montant du remboursement
            await self._debit_user_balance(user_id, amount, f"Remboursement prêt {loan_id}")
            
            # Calculer le nouveau solde de la dette
            new_debt = max(0, current_debt - amount)
            
            if new_debt <= 0:
                # Prêt entièrement remboursé
                await self.db.loans.update_one(
                    {"loan_id": loan_id},
                    {
                        "$set": {
                            "status": LoanStatus.PAID.value,
                            "paid_at": now,
                            "total_paid": loan.get("total_paid", 0) + amount
                        }
                    }
                )
                
                # Rembourser le collatéral
                await self._credit_user_balance(user_id, loan["collateral_amount"], f"Remboursement collatéral prêt {loan_id}")
                
                return {
                    "success": True,
                    "message": "Prêt entièrement remboursé",
                    "collateral_returned": loan["collateral_amount"],
                    "overpayment": -new_debt if new_debt < 0 else 0
                }
            else:
                # Remboursement partiel
                await self.db.loans.update_one(
                    {"loan_id": loan_id},
                    {
                        "$inc": {"total_paid": amount},
                        "$set": {"last_payment": now}
                    }
                )
                
                return {
                    "success": True,
                    "message": "Remboursement partiel effectué",
                    "remaining_debt": new_debt,
                    "amount_paid": amount
                }
            
        except Exception as e:
            logger.error(f"Erreur remboursement prêt: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # ==============================
    # Yield Farming
    # ==============================
    
    async def create_liquidity_pool(self,
                                  token_a: str,
                                  token_b: str,
                                  fee_rate: float = 0.003) -> Dict[str, Any]:
        """Crée un pool de liquidité"""
        try:
            pool_id = str(uuid.uuid4())
            
            pool_entry = {
                "pool_id": pool_id,
                "token_a": token_a,
                "token_b": token_b,
                "fee_rate": fee_rate,
                "total_liquidity": 0.0,
                "reserve_a": 0.0,
                "reserve_b": 0.0,
                "created_at": datetime.utcnow(),
                "total_fees_collected": 0.0,
                "liquidity_providers": 0,
                "status": "active"
            }
            
            await self.db.liquidity_pools.insert_one(pool_entry)
            
            return {
                "success": True,
                "pool_id": pool_id,
                "token_pair": f"{token_a}-{token_b}",
                "fee_rate": fee_rate
            }
            
        except Exception as e:
            logger.error(f"Erreur création pool liquidité: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def add_liquidity(self,
                          user_id: str,
                          pool_id: str,
                          amount_a: float,
                          amount_b: float) -> Dict[str, Any]:
        """Ajoute de la liquidité à un pool"""
        try:
            # Récupérer le pool
            pool = await self.db.liquidity_pools.find_one({"pool_id": pool_id})
            if not pool:
                return {"success": False, "error": "Pool non trouvé"}
            
            # Vérifier les soldes utilisateur
            user_balance = await self._get_user_balance(user_id)
            total_required = amount_a + amount_b  # Simplification pour QS
            
            if user_balance < total_required:
                return {"success": False, "error": "Solde insuffisant"}
            
            # Calculer les LP tokens à attribuer
            if pool["total_liquidity"] == 0:
                # Premier dépôt
                lp_tokens = math.sqrt(amount_a * amount_b)
            else:
                # Calcul proportionnel
                lp_tokens = min(
                    (amount_a / pool["reserve_a"]) * pool["total_liquidity"],
                    (amount_b / pool["reserve_b"]) * pool["total_liquidity"]
                )
            
            # Créer l'entrée de liquidité
            liquidity_id = str(uuid.uuid4())
            
            liquidity_entry = {
                "liquidity_id": liquidity_id,
                "user_id": user_id,
                "pool_id": pool_id,
                "amount_a": amount_a,
                "amount_b": amount_b,
                "lp_tokens": lp_tokens,
                "added_at": datetime.utcnow(),
                "rewards_earned": 0.0,
                "status": "active"
            }
            
            await self.db.user_liquidity.insert_one(liquidity_entry)
            
            # Débiter les montants
            await self._debit_user_balance(user_id, total_required, f"Liquidité pool {pool_id}")
            
            # Mettre à jour le pool
            await self.db.liquidity_pools.update_one(
                {"pool_id": pool_id},
                {
                    "$inc": {
                        "total_liquidity": lp_tokens,
                        "reserve_a": amount_a,
                        "reserve_b": amount_b,
                        "liquidity_providers": 1
                    }
                }
            )
            
            return {
                "success": True,
                "liquidity_id": liquidity_id,
                "lp_tokens": lp_tokens,
                "amount_a": amount_a,
                "amount_b": amount_b
            }
            
        except Exception as e:
            logger.error(f"Erreur ajout liquidité: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # ==============================
    # Utilitaires
    # ==============================
    
    async def _get_user_balance(self, user_id: str) -> float:
        """Récupère le solde utilisateur"""
        try:
            user = await self.db.users.find_one({"id": user_id})
            return user.get("qs_balance", 0.0) if user else 0.0
        except Exception as e:
            logger.error(f"Erreur récupération solde: {str(e)}")
            return 0.0
    
    async def _debit_user_balance(self, user_id: str, amount: float, description: str):
        """Débite le solde utilisateur"""
        try:
            await self.db.users.update_one(
                {"id": user_id},
                {"$inc": {"qs_balance": -amount}}
            )
            
            # Enregistrer la transaction
            await self.db.defi_transactions.insert_one({
                "transaction_id": str(uuid.uuid4()),
                "user_id": user_id,
                "amount": -amount,
                "type": "debit",
                "description": description,
                "timestamp": datetime.utcnow()
            })
            
        except Exception as e:
            logger.error(f"Erreur débit solde: {str(e)}")
    
    async def _credit_user_balance(self, user_id: str, amount: float, description: str):
        """Crédite le solde utilisateur"""
        try:
            await self.db.users.update_one(
                {"id": user_id},
                {"$inc": {"qs_balance": amount}}
            )
            
            # Enregistrer la transaction
            await self.db.defi_transactions.insert_one({
                "transaction_id": str(uuid.uuid4()),
                "user_id": user_id,
                "amount": amount,
                "type": "credit",
                "description": description,
                "timestamp": datetime.utcnow()
            })
            
        except Exception as e:
            logger.error(f"Erreur crédit solde: {str(e)}")
    
    async def _start_reward_calculations(self):
        """Démarre les calculs de récompenses périodiques"""
        try:
            while True:
                await asyncio.sleep(3600)  # Toutes les heures
                
                # Calculer les récompenses pour tous les stakes actifs
                active_stakes = await self.db.user_stakes.find({"status": "active"}).to_list(None)
                
                for stake in active_stakes:
                    await self._calculate_stake_rewards(stake["stake_id"])
                
                logger.info(f"Récompenses calculées pour {len(active_stakes)} stakes")
                
        except Exception as e:
            logger.error(f"Erreur calcul récompenses périodiques: {str(e)}")
    
    async def get_user_defi_portfolio(self, user_id: str) -> Dict[str, Any]:
        """Récupère le portfolio DeFi d'un utilisateur"""
        try:
            # Stakes actifs
            stakes = await self.db.user_stakes.find({"user_id": user_id, "status": "active"}).to_list(None)
            
            # Prêts actifs
            loans = await self.db.loans.find({"user_id": user_id, "status": LoanStatus.ACTIVE.value}).to_list(None)
            
            # Liquidités
            liquidity = await self.db.user_liquidity.find({"user_id": user_id, "status": "active"}).to_list(None)
            
            # Calculer les totaux
            total_staked = sum(stake["amount"] for stake in stakes)
            total_rewards = sum(stake["total_rewards_earned"] for stake in stakes)
            total_borrowed = sum(loan["loan_amount"] for loan in loans)
            total_collateral = sum(loan["collateral_amount"] for loan in loans)
            
            return {
                "user_id": user_id,
                "total_staked": total_staked,
                "total_rewards": total_rewards,
                "total_borrowed": total_borrowed,
                "total_collateral": total_collateral,
                "active_stakes": len(stakes),
                "active_loans": len(loans),
                "liquidity_positions": len(liquidity),
                "stakes": stakes,
                "loans": loans,
                "liquidity": liquidity
            }
            
        except Exception as e:
            logger.error(f"Erreur récupération portfolio: {str(e)}")
            return {}
    
    async def get_defi_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques DeFi"""
        try:
            # Statistiques staking
            total_staked = await self.db.user_stakes.aggregate([
                {"$match": {"status": "active"}},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
            ]).to_list(None)
            
            total_staked_amount = total_staked[0]["total"] if total_staked else 0.0
            
            # Statistiques prêts
            total_loans = await self.db.loans.aggregate([
                {"$match": {"status": LoanStatus.ACTIVE.value}},
                {"$group": {"_id": None, "total": {"$sum": "$loan_amount"}}}
            ]).to_list(None)
            
            total_loan_amount = total_loans[0]["total"] if total_loans else 0.0
            
            # Compter les utilisateurs
            active_stakers = await self.db.user_stakes.distinct("user_id", {"status": "active"})
            active_borrowers = await self.db.loans.distinct("user_id", {"status": LoanStatus.ACTIVE.value})
            
            return {
                "total_value_locked": total_staked_amount + total_loan_amount,
                "total_staked": total_staked_amount,
                "total_borrowed": total_loan_amount,
                "active_stakers": len(active_stakers),
                "active_borrowers": len(active_borrowers),
                "staking_pools": await self.db.staking_pools.count_documents({"status": StakingPoolStatus.ACTIVE.value}),
                "liquidity_pools": await self.db.liquidity_pools.count_documents({"status": "active"}),
                "average_apy": self.config["base_staking_rate"]
            }
            
        except Exception as e:
            logger.error(f"Erreur récupération statistiques DeFi: {str(e)}")
            return {}
    
    async def shutdown(self):
        """Arrête le service DeFi"""
        try:
            self.staking_pools.clear()
            self.liquidity_pools.clear()
            self.loans.clear()
            
            logger.info("Service DeFi arrêté")
            
        except Exception as e:
            logger.error(f"Erreur arrêt service DeFi: {str(e)}")
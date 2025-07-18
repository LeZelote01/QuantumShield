"""
Service d'économie avancée pour QuantumShield
Inclut: Marketplace, Staking, DeFi, Assurance décentralisée, Tokenisation d'actifs
"""

import json
import uuid
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from decimal import Decimal
import hashlib
import asyncio

logger = logging.getLogger(__name__)

class ServiceType(str, Enum):
    DEVICE_MONITORING = "device_monitoring"
    SECURITY_AUDIT = "security_audit"
    CRYPTO_ACCELERATION = "crypto_acceleration"
    DATA_ANALYTICS = "data_analytics"
    MAINTENANCE = "maintenance"
    CONSULTING = "consulting"
    FIRMWARE_UPDATE = "firmware_update"
    CUSTOM_INTEGRATION = "custom_integration"

class ServiceStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SOLD_OUT = "sold_out"
    MAINTENANCE = "maintenance"

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class StakingType(str, Enum):
    FLEXIBLE = "flexible"
    FIXED_30_DAYS = "fixed_30_days"
    FIXED_90_DAYS = "fixed_90_days"
    FIXED_180_DAYS = "fixed_180_days"
    FIXED_365_DAYS = "fixed_365_days"
    VALIDATOR = "validator"

class LoanStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    REPAID = "repaid"
    DEFAULTED = "defaulted"
    LIQUIDATED = "liquidated"

class InsuranceType(str, Enum):
    DEVICE_PROTECTION = "device_protection"
    CYBER_SECURITY = "cyber_security"
    BUSINESS_INTERRUPTION = "business_interruption"
    SMART_CONTRACT = "smart_contract"
    ORACLE_FAILURE = "oracle_failure"

class AssetType(str, Enum):
    REAL_ESTATE = "real_estate"
    EQUIPMENT = "equipment"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    RENEWABLE_ENERGY = "renewable_energy"
    CARBON_CREDITS = "carbon_credits"
    COMMODITY = "commodity"

class ProposalType(str, Enum):
    PARAMETER_CHANGE = "parameter_change"
    FEATURE_REQUEST = "feature_request"
    TOKENOMICS = "tokenomics"
    GOVERNANCE = "governance"
    EMERGENCY = "emergency"
    GENERAL = "general"

class ProposalStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PASSED = "passed"
    REJECTED = "rejected"
    EXECUTED = "executed"
    EXPIRED = "expired"

class VoteOption(str, Enum):
    YES = "yes"
    NO = "no"
    ABSTAIN = "abstain"

class AdvancedEconomyService:
    """Service d'économie avancée"""
    
    def __init__(self, db):
        self.db = db
        self.is_initialized = False
        self.marketplace_fee = 0.025  # 2.5% commission
        self.staking_rewards = {
            StakingType.FLEXIBLE: 0.05,      # 5% APY
            StakingType.FIXED_30_DAYS: 0.08,  # 8% APY
            StakingType.FIXED_90_DAYS: 0.12,  # 12% APY
            StakingType.FIXED_180_DAYS: 0.18, # 18% APY
            StakingType.FIXED_365_DAYS: 0.25, # 25% APY
            StakingType.VALIDATOR: 0.30       # 30% APY
        }
        self._initialize()
    
    def _initialize(self):
        """Initialise le service d'économie avancée"""
        try:
            self.is_initialized = True
            logger.info("Service d'économie avancée initialisé")
        except Exception as e:
            logger.error(f"Erreur initialisation économie avancée: {e}")
            self.is_initialized = False
    
    def is_ready(self) -> bool:
        """Vérifie si le service est prêt"""
        return self.is_initialized
    
    # ===== MARKETPLACE DE SERVICES =====
    
    async def create_service_listing(self, provider_id: str, service_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée une offre de service sur la marketplace"""
        try:
            listing = {
                "id": str(uuid.uuid4()),
                "provider_id": provider_id,
                "service_type": service_data["service_type"],
                "title": service_data["title"],
                "description": service_data["description"],
                "price": float(service_data["price"]),
                "currency": service_data.get("currency", "QS"),
                "duration": service_data.get("duration", "1 hour"),
                "max_clients": service_data.get("max_clients", 1),
                "current_clients": 0,
                "tags": service_data.get("tags", []),
                "requirements": service_data.get("requirements", []),
                "deliverables": service_data.get("deliverables", []),
                "status": ServiceStatus.ACTIVE.value,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "rating": 0.0,
                "reviews_count": 0,
                "sales_count": 0
            }
            
            await self.db.service_listings.insert_one(listing)
            
            return {
                "listing_id": listing["id"],
                "status": "created",
                "marketplace_fee": self.marketplace_fee * 100,
                "estimated_earnings": listing["price"] * (1 - self.marketplace_fee)
            }
            
        except Exception as e:
            logger.error(f"Erreur création offre service: {e}")
            raise Exception(f"Impossible de créer l'offre: {e}")
    
    async def search_services(self, query: Optional[str] = None, 
                            service_type: Optional[ServiceType] = None,
                            max_price: Optional[float] = None,
                            min_rating: Optional[float] = None) -> List[Dict[str, Any]]:
        """Recherche des services sur la marketplace"""
        try:
            # Construire les critères de recherche
            criteria = {"status": ServiceStatus.ACTIVE.value}
            
            if service_type:
                criteria["service_type"] = service_type.value
            
            if max_price:
                criteria["price"] = {"$lte": max_price}
            
            if min_rating:
                criteria["rating"] = {"$gte": min_rating}
            
            if query:
                criteria["$or"] = [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}},
                    {"tags": {"$in": [query.lower()]}}
                ]
            
            # Récupérer les services
            services = await self.db.service_listings.find(criteria).sort("rating", -1).limit(50).to_list(None)
            
            # Enrichir avec les informations du provider
            enriched_services = []
            for service in services:
                provider = await self.db.users.find_one({"id": service["provider_id"]})
                
                enriched_service = {
                    "id": service["id"],
                    "title": service["title"],
                    "description": service["description"],
                    "price": service["price"],
                    "currency": service["currency"],
                    "duration": service["duration"],
                    "service_type": service["service_type"],
                    "rating": service["rating"],
                    "reviews_count": service["reviews_count"],
                    "sales_count": service["sales_count"],
                    "availability": service["max_clients"] - service["current_clients"],
                    "tags": service["tags"],
                    "provider": {
                        "id": provider["id"] if provider else None,
                        "username": provider["username"] if provider else "Unknown",
                        "reputation_score": provider.get("reputation_score", 0) if provider else 0
                    }
                }
                enriched_services.append(enriched_service)
            
            return enriched_services
            
        except Exception as e:
            logger.error(f"Erreur recherche services: {e}")
            return []
    
    async def purchase_service(self, buyer_id: str, service_id: str, 
                             custom_requirements: Optional[str] = None) -> Dict[str, Any]:
        """Achète un service sur la marketplace"""
        try:
            # Récupérer le service
            service = await self.db.service_listings.find_one({"id": service_id})
            if not service:
                raise ValueError("Service non trouvé")
            
            if service["status"] != ServiceStatus.ACTIVE.value:
                raise ValueError("Service non disponible")
            
            if service["current_clients"] >= service["max_clients"]:
                raise ValueError("Service complet")
            
            # Vérifier le solde de l'acheteur
            buyer = await self.db.users.find_one({"id": buyer_id})
            if not buyer:
                raise ValueError("Acheteur non trouvé")
            
            if buyer["qs_balance"] < service["price"]:
                raise ValueError("Solde insuffisant")
            
            # Créer la commande
            order = {
                "id": str(uuid.uuid4()),
                "buyer_id": buyer_id,
                "provider_id": service["provider_id"],
                "service_id": service_id,
                "service_title": service["title"],
                "price": service["price"],
                "marketplace_fee": service["price"] * self.marketplace_fee,
                "provider_earnings": service["price"] * (1 - self.marketplace_fee),
                "custom_requirements": custom_requirements,
                "status": OrderStatus.PENDING.value,
                "created_at": datetime.utcnow(),
                "expected_completion": datetime.utcnow() + timedelta(hours=24)
            }
            
            await self.db.service_orders.insert_one(order)
            
            # Effectuer la transaction
            await self.db.users.update_one(
                {"id": buyer_id},
                {"$inc": {"qs_balance": -service["price"]}}
            )
            
            # Mettre à jour le service
            await self.db.service_listings.update_one(
                {"id": service_id},
                {
                    "$inc": {"current_clients": 1, "sales_count": 1},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            return {
                "order_id": order["id"],
                "status": "confirmed",
                "total_paid": service["price"],
                "expected_completion": order["expected_completion"]
            }
            
        except Exception as e:
            logger.error(f"Erreur achat service: {e}")
            raise Exception(f"Impossible d'acheter le service: {e}")
    
    # ===== STAKING ET DEFI =====
    
    async def create_staking_pool(self, pool_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un pool de staking"""
        try:
            pool = {
                "id": str(uuid.uuid4()),
                "name": pool_data["name"],
                "staking_type": pool_data["staking_type"],
                "apy": self.staking_rewards[StakingType(pool_data["staking_type"])],
                "min_stake": float(pool_data.get("min_stake", 100)),
                "max_stake": float(pool_data.get("max_stake", 10000)),
                "total_staked": 0.0,
                "total_rewards_distributed": 0.0,
                "participants_count": 0,
                "lock_period_days": self._get_lock_period(pool_data["staking_type"]),
                "created_at": datetime.utcnow(),
                "active": True
            }
            
            await self.db.staking_pools.insert_one(pool)
            
            return {
                "pool_id": pool["id"],
                "apy": pool["apy"] * 100,
                "lock_period_days": pool["lock_period_days"],
                "status": "created"
            }
            
        except Exception as e:
            logger.error(f"Erreur création pool staking: {e}")
            raise Exception(f"Impossible de créer le pool: {e}")
    
    async def stake_tokens(self, user_id: str, pool_id: str, amount: float) -> Dict[str, Any]:
        """Mise en stake de tokens"""
        try:
            # Vérifier le pool
            pool = await self.db.staking_pools.find_one({"id": pool_id, "active": True})
            if not pool:
                raise ValueError("Pool de staking non trouvé")
            
            if amount < pool["min_stake"] or amount > pool["max_stake"]:
                raise ValueError(f"Montant invalide (min: {pool['min_stake']}, max: {pool['max_stake']})")
            
            # Vérifier le solde utilisateur
            user = await self.db.users.find_one({"id": user_id})
            if not user or user["qs_balance"] < amount:
                raise ValueError("Solde insuffisant")
            
            # Créer la position de staking
            stake = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "pool_id": pool_id,
                "amount": amount,
                "apy": pool["apy"],
                "staked_at": datetime.utcnow(),
                "unlock_date": datetime.utcnow() + timedelta(days=pool["lock_period_days"]),
                "rewards_earned": 0.0,
                "last_reward_calculation": datetime.utcnow(),
                "active": True
            }
            
            await self.db.staking_positions.insert_one(stake)
            
            # Mettre à jour le solde utilisateur
            await self.db.users.update_one(
                {"id": user_id},
                {"$inc": {"qs_balance": -amount}}
            )
            
            # Mettre à jour le pool
            await self.db.staking_pools.update_one(
                {"id": pool_id},
                {
                    "$inc": {"total_staked": amount, "participants_count": 1},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            return {
                "stake_id": stake["id"],
                "amount_staked": amount,
                "apy": pool["apy"] * 100,
                "unlock_date": stake["unlock_date"],
                "estimated_yearly_rewards": amount * pool["apy"]
            }
            
        except Exception as e:
            logger.error(f"Erreur staking tokens: {e}")
            raise Exception(f"Impossible de staker: {e}")
    
    async def unstake_tokens(self, user_id: str, stake_id: str) -> Dict[str, Any]:
        """Retire les tokens du staking"""
        try:
            # Récupérer la position
            stake = await self.db.staking_positions.find_one({"id": stake_id, "user_id": user_id, "active": True})
            if not stake:
                raise ValueError("Position de staking non trouvée")
            
            # Vérifier la période de lock
            if datetime.utcnow() < stake["unlock_date"]:
                penalty_rate = 0.1  # 10% de pénalité
                penalty = stake["amount"] * penalty_rate
                return_amount = stake["amount"] - penalty
                
                # Calculer les récompenses partielles
                days_staked = (datetime.utcnow() - stake["staked_at"]).days
                partial_rewards = self._calculate_rewards(stake["amount"], stake["apy"], days_staked)
                
                total_return = return_amount + partial_rewards
                
                result = {
                    "early_withdrawal": True,
                    "penalty": penalty,
                    "penalty_rate": penalty_rate * 100,
                    "partial_rewards": partial_rewards,
                    "total_return": total_return
                }
            else:
                # Calculer les récompenses complètes
                total_rewards = self._calculate_rewards(
                    stake["amount"], 
                    stake["apy"], 
                    (datetime.utcnow() - stake["staked_at"]).days
                )
                
                total_return = stake["amount"] + total_rewards
                
                result = {
                    "early_withdrawal": False,
                    "penalty": 0.0,
                    "total_rewards": total_rewards,
                    "total_return": total_return
                }
            
            # Mettre à jour la position
            await self.db.staking_positions.update_one(
                {"id": stake_id},
                {
                    "$set": {
                        "active": False,
                        "unstaked_at": datetime.utcnow(),
                        "final_amount": result["total_return"]
                    }
                }
            )
            
            # Rembourser l'utilisateur
            await self.db.users.update_one(
                {"id": user_id},
                {"$inc": {"qs_balance": result["total_return"]}}
            )
            
            # Mettre à jour le pool
            pool = await self.db.staking_pools.find_one({"id": stake["pool_id"]})
            if pool:
                await self.db.staking_pools.update_one(
                    {"id": stake["pool_id"]},
                    {
                        "$inc": {
                            "total_staked": -stake["amount"],
                            "participants_count": -1,
                            "total_rewards_distributed": result.get("total_rewards", result.get("partial_rewards", 0))
                        }
                    }
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur unstaking: {e}")
            raise Exception(f"Impossible de retirer le stake: {e}")
    
    async def get_staking_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Récupère le tableau de bord staking d'un utilisateur"""
        try:
            # Récupérer les positions actives
            active_stakes = await self.db.staking_positions.find({"user_id": user_id, "active": True}).to_list(None)
            
            # Calculer les statistiques
            total_staked = sum(stake["amount"] for stake in active_stakes)
            total_rewards_pending = 0.0
            
            enriched_stakes = []
            for stake in active_stakes:
                # Calculer les récompenses accumulées
                days_staked = (datetime.utcnow() - stake["staked_at"]).days
                rewards = self._calculate_rewards(stake["amount"], stake["apy"], days_staked)
                total_rewards_pending += rewards
                
                enriched_stakes.append({
                    "stake_id": stake["id"],
                    "pool_id": stake["pool_id"],
                    "amount": stake["amount"],
                    "apy": stake["apy"] * 100,
                    "staked_at": stake["staked_at"],
                    "unlock_date": stake["unlock_date"],
                    "rewards_pending": rewards,
                    "days_until_unlock": max(0, (stake["unlock_date"] - datetime.utcnow()).days),
                    "can_unstake": datetime.utcnow() >= stake["unlock_date"]
                })
            
            return {
                "user_id": user_id,
                "total_staked": total_staked,
                "total_rewards_pending": total_rewards_pending,
                "active_positions": len(active_stakes),
                "stakes": enriched_stakes,
                "estimated_yearly_earnings": sum(stake["amount"] * stake["apy"] for stake in active_stakes)
            }
            
        except Exception as e:
            logger.error(f"Erreur dashboard staking: {e}")
            return {
                "user_id": user_id,
                "total_staked": 0.0,
                "total_rewards_pending": 0.0,
                "active_positions": 0,
                "stakes": []
            }
    
    # ===== PRÊTS ET EMPRUNTS =====
    
    async def create_loan_request(self, borrower_id: str, loan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée une demande de prêt"""
        try:
            loan = {
                "id": str(uuid.uuid4()),
                "borrower_id": borrower_id,
                "amount": float(loan_data["amount"]),
                "interest_rate": float(loan_data["interest_rate"]),
                "duration_days": int(loan_data["duration_days"]),
                "collateral_amount": float(loan_data["collateral_amount"]),
                "collateral_type": loan_data.get("collateral_type", "QS"),
                "purpose": loan_data.get("purpose", ""),
                "status": LoanStatus.PENDING.value,
                "created_at": datetime.utcnow(),
                "funded_amount": 0.0,
                "lenders": [],
                "repayment_schedule": []
            }
            
            # Calculer le montant total à rembourser
            total_repayment = loan["amount"] * (1 + loan["interest_rate"] * loan["duration_days"] / 365)
            loan["total_repayment"] = total_repayment
            
            await self.db.loan_requests.insert_one(loan)
            
            return {
                "loan_id": loan["id"],
                "amount": loan["amount"],
                "interest_rate": loan["interest_rate"] * 100,
                "total_repayment": total_repayment,
                "status": "pending"
            }
            
        except Exception as e:
            logger.error(f"Erreur création demande prêt: {e}")
            raise Exception(f"Impossible de créer la demande: {e}")
    
    async def fund_loan(self, lender_id: str, loan_id: str, amount: float) -> Dict[str, Any]:
        """Finance un prêt"""
        try:
            # Récupérer le prêt
            loan = await self.db.loan_requests.find_one({"id": loan_id, "status": LoanStatus.PENDING.value})
            if not loan:
                raise ValueError("Prêt non trouvé ou non disponible")
            
            # Vérifier le solde du prêteur
            lender = await self.db.users.find_one({"id": lender_id})
            if not lender or lender["qs_balance"] < amount:
                raise ValueError("Solde insuffisant")
            
            # Vérifier que le montant ne dépasse pas le besoin
            remaining_amount = loan["amount"] - loan["funded_amount"]
            if amount > remaining_amount:
                amount = remaining_amount
            
            # Ajouter le prêteur
            lender_entry = {
                "lender_id": lender_id,
                "amount": amount,
                "funded_at": datetime.utcnow()
            }
            
            # Mettre à jour le prêt
            await self.db.loan_requests.update_one(
                {"id": loan_id},
                {
                    "$push": {"lenders": lender_entry},
                    "$inc": {"funded_amount": amount}
                }
            )
            
            # Déduire du solde du prêteur
            await self.db.users.update_one(
                {"id": lender_id},
                {"$inc": {"qs_balance": -amount}}
            )
            
            # Vérifier si le prêt est entièrement financé
            updated_loan = await self.db.loan_requests.find_one({"id": loan_id})
            if updated_loan["funded_amount"] >= updated_loan["amount"]:
                # Activer le prêt
                await self.db.loan_requests.update_one(
                    {"id": loan_id},
                    {"$set": {"status": LoanStatus.ACTIVE.value, "activated_at": datetime.utcnow()}}
                )
                
                # Transférer les fonds à l'emprunteur
                await self.db.users.update_one(
                    {"id": loan["borrower_id"]},
                    {"$inc": {"qs_balance": updated_loan["amount"]}}
                )
                
                status = "loan_activated"
            else:
                status = "partially_funded"
            
            return {
                "funding_amount": amount,
                "total_funded": updated_loan["funded_amount"],
                "loan_amount": loan["amount"],
                "funding_progress": (updated_loan["funded_amount"] / loan["amount"]) * 100,
                "status": status
            }
            
        except Exception as e:
            logger.error(f"Erreur financement prêt: {e}")
            raise Exception(f"Impossible de financer le prêt: {e}")
    
    # ===== ASSURANCE DÉCENTRALISÉE =====
    
    async def create_insurance_pool(self, pool_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un pool d'assurance décentralisée"""
        try:
            pool = {
                "id": str(uuid.uuid4()),
                "name": pool_data["name"],
                "insurance_type": pool_data["insurance_type"],
                "coverage_amount": float(pool_data["coverage_amount"]),
                "premium_rate": float(pool_data["premium_rate"]),
                "minimum_pool_size": float(pool_data.get("minimum_pool_size", 10000)),
                "current_pool_size": 0.0,
                "active_policies": 0,
                "claims_paid": 0.0,
                "created_at": datetime.utcnow(),
                "active": True
            }
            
            await self.db.insurance_pools.insert_one(pool)
            
            return {
                "pool_id": pool["id"],
                "insurance_type": pool["insurance_type"],
                "coverage_amount": pool["coverage_amount"],
                "premium_rate": pool["premium_rate"] * 100,
                "status": "created"
            }
            
        except Exception as e:
            logger.error(f"Erreur création pool assurance: {e}")
            raise Exception(f"Impossible de créer le pool: {e}")
    
    async def purchase_insurance(self, user_id: str, pool_id: str, coverage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Achète une police d'assurance"""
        try:
            # Récupérer le pool
            pool = await self.db.insurance_pools.find_one({"id": pool_id, "active": True})
            if not pool:
                raise ValueError("Pool d'assurance non trouvé")
            
            # Calculer la prime
            coverage_amount = float(coverage_data["coverage_amount"])
            duration_days = int(coverage_data.get("duration_days", 365))
            premium = coverage_amount * pool["premium_rate"] * (duration_days / 365)
            
            # Vérifier le solde utilisateur
            user = await self.db.users.find_one({"id": user_id})
            if not user or user["qs_balance"] < premium:
                raise ValueError("Solde insuffisant pour payer la prime")
            
            # Créer la police
            policy = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "pool_id": pool_id,
                "coverage_amount": coverage_amount,
                "premium_paid": premium,
                "start_date": datetime.utcnow(),
                "end_date": datetime.utcnow() + timedelta(days=duration_days),
                "status": "active",
                "claims": []
            }
            
            await self.db.insurance_policies.insert_one(policy)
            
            # Déduire la prime
            await self.db.users.update_one(
                {"id": user_id},
                {"$inc": {"qs_balance": -premium}}
            )
            
            # Mettre à jour le pool
            await self.db.insurance_pools.update_one(
                {"id": pool_id},
                {
                    "$inc": {"current_pool_size": premium, "active_policies": 1}
                }
            )
            
            return {
                "policy_id": policy["id"],
                "coverage_amount": coverage_amount,
                "premium_paid": premium,
                "valid_until": policy["end_date"],
                "status": "active"
            }
            
        except Exception as e:
            logger.error(f"Erreur achat assurance: {e}")
            raise Exception(f"Impossible d'acheter l'assurance: {e}")
    
    # ===== TOKENISATION D'ACTIFS =====
    
    async def tokenize_asset(self, owner_id: str, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tokenise un actif physique"""
        try:
            # Créer l'actif tokenisé
            asset = {
                "id": str(uuid.uuid4()),
                "owner_id": owner_id,
                "asset_type": asset_data["asset_type"],
                "name": asset_data["name"],
                "description": asset_data["description"],
                "total_value": float(asset_data["total_value"]),
                "total_tokens": int(asset_data["total_tokens"]),
                "token_price": float(asset_data["total_value"]) / int(asset_data["total_tokens"]),
                "tokens_sold": 0,
                "revenue_generated": 0.0,
                "documents": asset_data.get("documents", []),
                "verification_status": "pending",
                "created_at": datetime.utcnow(),
                "active": True
            }
            
            await self.db.tokenized_assets.insert_one(asset)
            
            return {
                "asset_id": asset["id"],
                "total_tokens": asset["total_tokens"],
                "token_price": asset["token_price"],
                "total_value": asset["total_value"],
                "status": "tokenized"
            }
            
        except Exception as e:
            logger.error(f"Erreur tokenisation actif: {e}")
            raise Exception(f"Impossible de tokeniser l'actif: {e}")
    
    async def buy_asset_tokens(self, buyer_id: str, asset_id: str, token_count: int) -> Dict[str, Any]:
        """Achète des tokens d'un actif"""
        try:
            # Récupérer l'actif
            asset = await self.db.tokenized_assets.find_one({"id": asset_id, "active": True})
            if not asset:
                raise ValueError("Actif non trouvé")
            
            # Vérifier la disponibilité
            available_tokens = asset["total_tokens"] - asset["tokens_sold"]
            if token_count > available_tokens:
                raise ValueError(f"Seulement {available_tokens} tokens disponibles")
            
            # Calculer le coût
            total_cost = token_count * asset["token_price"]
            
            # Vérifier le solde
            buyer = await self.db.users.find_one({"id": buyer_id})
            if not buyer or buyer["qs_balance"] < total_cost:
                raise ValueError("Solde insuffisant")
            
            # Créer la propriété
            ownership = {
                "id": str(uuid.uuid4()),
                "buyer_id": buyer_id,
                "asset_id": asset_id,
                "token_count": token_count,
                "purchase_price": asset["token_price"],
                "total_paid": total_cost,
                "purchase_date": datetime.utcnow(),
                "dividends_received": 0.0
            }
            
            await self.db.asset_ownerships.insert_one(ownership)
            
            # Mettre à jour l'actif
            await self.db.tokenized_assets.update_one(
                {"id": asset_id},
                {"$inc": {"tokens_sold": token_count, "revenue_generated": total_cost}}
            )
            
            # Traiter le paiement
            await self.db.users.update_one(
                {"id": buyer_id},
                {"$inc": {"qs_balance": -total_cost}}
            )
            
            # Créditer le propriétaire de l'actif
            await self.db.users.update_one(
                {"id": asset["owner_id"]},
                {"$inc": {"qs_balance": total_cost}}
            )
            
            return {
                "ownership_id": ownership["id"],
                "tokens_purchased": token_count,
                "total_cost": total_cost,
                "ownership_percentage": (token_count / asset["total_tokens"]) * 100,
                "status": "purchased"
            }
            
        except Exception as e:
            logger.error(f"Erreur achat tokens actif: {e}")
            raise Exception(f"Impossible d'acheter les tokens: {e}")
    
    # ===== MÉTHODES UTILITAIRES =====
    
    def _get_lock_period(self, staking_type: str) -> int:
        """Retourne la période de lock en jours"""
        periods = {
            StakingType.FLEXIBLE.value: 0,
            StakingType.FIXED_30_DAYS.value: 30,
            StakingType.FIXED_90_DAYS.value: 90,
            StakingType.FIXED_180_DAYS.value: 180,
            StakingType.FIXED_365_DAYS.value: 365,
            StakingType.VALIDATOR.value: 365
        }
        return periods.get(staking_type, 0)
    
    def _calculate_rewards(self, amount: float, apy: float, days: int) -> float:
        """Calcule les récompenses de staking"""
        return amount * apy * (days / 365)
    
    async def get_economy_dashboard(self) -> Dict[str, Any]:
        """Récupère le tableau de bord économique"""
        try:
            # Statistiques marketplace
            active_services = await self.db.service_listings.count_documents({"status": ServiceStatus.ACTIVE.value})
            total_orders = await self.db.service_orders.count_documents({})
            
            # Statistiques staking
            total_staked = await self.db.staking_positions.aggregate([
                {"$match": {"active": True}},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
            ]).to_list(None)
            total_staked_amount = total_staked[0]["total"] if total_staked else 0
            
            # Statistiques prêts
            active_loans = await self.db.loan_requests.count_documents({"status": LoanStatus.ACTIVE.value})
            
            # Statistiques assurance
            active_policies = await self.db.insurance_policies.count_documents({"status": "active"})
            
            # Statistiques tokenisation
            tokenized_assets = await self.db.tokenized_assets.count_documents({"active": True})
            
            return {
                "marketplace": {
                    "active_services": active_services,
                    "total_orders": total_orders,
                    "marketplace_fee": self.marketplace_fee * 100
                },
                "staking": {
                    "total_staked": total_staked_amount,
                    "available_pools": len(self.staking_rewards),
                    "highest_apy": max(self.staking_rewards.values()) * 100
                },
                "lending": {
                    "active_loans": active_loans
                },
                "insurance": {
                    "active_policies": active_policies
                },
                "tokenization": {
                    "tokenized_assets": tokenized_assets
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur dashboard économique: {e}")
            return {
                "marketplace": {"active_services": 0, "total_orders": 0},
                "staking": {"total_staked": 0, "available_pools": 0},
                "lending": {"active_loans": 0},
                "insurance": {"active_policies": 0},
                "tokenization": {"tokenized_assets": 0}
            }
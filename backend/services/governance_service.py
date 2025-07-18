"""
Service de gouvernance décentralisée pour QuantumShield
Gestion des propositions, votes et décisions communautaires
"""

import json
import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
from decimal import Decimal

logger = logging.getLogger(__name__)

class ProposalType(str, Enum):
    PARAMETER_CHANGE = "parameter_change"
    FEATURE_ADDITION = "feature_addition"
    SYSTEM_UPGRADE = "system_upgrade"
    FUND_ALLOCATION = "fund_allocation"

class ProposalStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    PASSED = "passed"
    REJECTED = "rejected"
    EXECUTED = "executed"

class VoteType(str, Enum):
    FOR = "for"
    AGAINST = "against"
    ABSTAIN = "abstain"

class GovernanceService:
    """Service de gouvernance décentralisée"""
    
    def __init__(self, db):
        self.db = db
        self.is_initialized = False
        self.min_proposal_stake = 1000.0  # Minimum QS pour créer une proposition
        self.min_voting_power = 100.0     # Minimum QS pour voter
        self.default_voting_period = 7    # Jours par défaut
        self.default_quorum = 0.1         # 10% de quorum par défaut
        self._initialize()
    
    def _initialize(self):
        """Initialise le service de gouvernance"""
        try:
            self.is_initialized = True
            logger.info("Service de gouvernance initialisé")
        except Exception as e:
            logger.error(f"Erreur initialisation gouvernance: {e}")
            self.is_initialized = False
    
    def is_ready(self) -> bool:
        """Vérifie si le service est prêt"""
        return self.is_initialized
    
    # ===== GESTION DES PROPOSITIONS =====
    
    async def create_proposal(self, proposer_id: str, proposal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée une nouvelle proposition"""
        try:
            # Vérifier que le proposant a suffisamment de QS
            user = await self.db.users.find_one({"id": proposer_id})
            if not user:
                raise ValueError("Utilisateur non trouvé")
            
            if user["qs_balance"] < self.min_proposal_stake:
                raise ValueError(f"Solde insuffisant (minimum: {self.min_proposal_stake} QS)")
            
            # Créer la proposition
            proposal = {
                "id": str(uuid.uuid4()),
                "proposer_id": proposer_id,
                "proposal_type": proposal_data["proposal_type"],
                "title": proposal_data["title"],
                "description": proposal_data["description"],
                "parameters": proposal_data.get("parameters", {}),
                "voting_period_days": proposal_data.get("voting_period_days", self.default_voting_period),
                "required_quorum": proposal_data.get("required_quorum", self.default_quorum),
                "status": ProposalStatus.PENDING.value,
                "created_at": datetime.utcnow(),
                "voting_start_date": None,
                "voting_end_date": None,
                "votes_for": 0,
                "votes_against": 0,
                "votes_abstain": 0,
                "total_votes": 0,
                "unique_voters": 0,
                "execution_date": None,
                "execution_result": None
            }
            
            await self.db.governance_proposals.insert_one(proposal)
            
            # Déduire le stake de proposition
            await self.db.users.update_one(
                {"id": proposer_id},
                {"$inc": {"qs_balance": -self.min_proposal_stake}}
            )
            
            # Enregistrer le stake
            stake_record = {
                "id": str(uuid.uuid4()),
                "user_id": proposer_id,
                "proposal_id": proposal["id"],
                "stake_amount": self.min_proposal_stake,
                "staked_at": datetime.utcnow(),
                "returned": False
            }
            
            await self.db.governance_stakes.insert_one(stake_record)
            
            return {
                "proposal_id": proposal["id"],
                "stake_amount": self.min_proposal_stake,
                "status": "pending_review",
                "review_period_days": 3
            }
            
        except Exception as e:
            logger.error(f"Erreur création proposition: {e}")
            raise Exception(f"Impossible de créer la proposition: {e}")
    
    async def approve_proposal(self, proposal_id: str, admin_id: str) -> Dict[str, Any]:
        """Approuve une proposition pour mise au vote"""
        try:
            # Récupérer la proposition
            proposal = await self.db.governance_proposals.find_one({"id": proposal_id})
            if not proposal:
                raise ValueError("Proposition non trouvée")
            
            if proposal["status"] != ProposalStatus.PENDING.value:
                raise ValueError("Proposition non en attente")
            
            # Calculer les dates de vote
            voting_start = datetime.utcnow()
            voting_end = voting_start + timedelta(days=proposal["voting_period_days"])
            
            # Mettre à jour la proposition
            await self.db.governance_proposals.update_one(
                {"id": proposal_id},
                {
                    "$set": {
                        "status": ProposalStatus.ACTIVE.value,
                        "voting_start_date": voting_start,
                        "voting_end_date": voting_end,
                        "approved_by": admin_id,
                        "approved_at": datetime.utcnow()
                    }
                }
            )
            
            return {
                "proposal_id": proposal_id,
                "voting_start": voting_start,
                "voting_end": voting_end,
                "status": "active"
            }
            
        except Exception as e:
            logger.error(f"Erreur approbation proposition: {e}")
            raise Exception(f"Impossible d'approuver la proposition: {e}")
    
    async def get_proposals(self, status: Optional[ProposalStatus] = None, 
                          limit: int = 50) -> List[Dict[str, Any]]:
        """Récupère les propositions"""
        try:
            # Construire les critères de recherche
            criteria = {}
            if status:
                criteria["status"] = status.value
            
            # Récupérer les propositions
            proposals = await self.db.governance_proposals.find(criteria).sort(
                "created_at", -1
            ).limit(limit).to_list(None)
            
            # Enrichir avec les informations du proposant
            enriched_proposals = []
            for proposal in proposals:
                proposer = await self.db.users.find_one({"id": proposal["proposer_id"]})
                
                # Calculer le quorum actuel
                total_voting_power = await self._get_total_voting_power()
                current_quorum = proposal["total_votes"] / total_voting_power if total_voting_power > 0 else 0
                
                enriched_proposal = {
                    "id": proposal["id"],
                    "title": proposal["title"],
                    "description": proposal["description"],
                    "proposal_type": proposal["proposal_type"],
                    "status": proposal["status"],
                    "proposer": {
                        "id": proposal["proposer_id"],
                        "username": proposer["username"] if proposer else "Unknown"
                    },
                    "created_at": proposal["created_at"],
                    "voting_start_date": proposal.get("voting_start_date"),
                    "voting_end_date": proposal.get("voting_end_date"),
                    "votes_for": proposal["votes_for"],
                    "votes_against": proposal["votes_against"],
                    "votes_abstain": proposal["votes_abstain"],
                    "total_votes": proposal["total_votes"],
                    "unique_voters": proposal["unique_voters"],
                    "required_quorum": proposal["required_quorum"],
                    "current_quorum": current_quorum,
                    "parameters": proposal.get("parameters", {}),
                    "voting_period_days": proposal["voting_period_days"]
                }
                
                enriched_proposals.append(enriched_proposal)
            
            return enriched_proposals
            
        except Exception as e:
            logger.error(f"Erreur récupération propositions: {e}")
            return []
    
    async def get_proposal_details(self, proposal_id: str) -> Dict[str, Any]:
        """Récupère les détails d'une proposition"""
        try:
            proposal = await self.db.governance_proposals.find_one({"id": proposal_id})
            if not proposal:
                raise ValueError("Proposition non trouvée")
            
            # Récupérer les votes
            votes = await self.db.governance_votes.find({"proposal_id": proposal_id}).to_list(None)
            
            # Enrichir avec les informations des votants
            enriched_votes = []
            for vote in votes:
                voter = await self.db.users.find_one({"id": vote["voter_id"]})
                enriched_vote = {
                    "voter_id": vote["voter_id"],
                    "voter_username": voter["username"] if voter else "Unknown",
                    "vote_type": vote["vote_type"],
                    "voting_power": vote["voting_power"],
                    "voted_at": vote["voted_at"]
                }
                enriched_votes.append(enriched_vote)
            
            return {
                "proposal": proposal,
                "votes": enriched_votes,
                "vote_distribution": {
                    "for": proposal["votes_for"],
                    "against": proposal["votes_against"],
                    "abstain": proposal["votes_abstain"]
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur récupération détails proposition: {e}")
            raise Exception(f"Impossible de récupérer les détails: {e}")
    
    # ===== GESTION DES VOTES =====
    
    async def cast_vote(self, voter_id: str, proposal_id: str, vote_type: VoteType) -> Dict[str, Any]:
        """Enregistre un vote"""
        try:
            # Récupérer la proposition
            proposal = await self.db.governance_proposals.find_one({"id": proposal_id})
            if not proposal:
                raise ValueError("Proposition non trouvée")
            
            if proposal["status"] != ProposalStatus.ACTIVE.value:
                raise ValueError("Proposition non active")
            
            # Vérifier que le vote est encore possible
            if datetime.utcnow() > proposal["voting_end_date"]:
                raise ValueError("Période de vote terminée")
            
            # Vérifier que l'utilisateur n'a pas déjà voté
            existing_vote = await self.db.governance_votes.find_one({
                "voter_id": voter_id,
                "proposal_id": proposal_id
            })
            
            if existing_vote:
                raise ValueError("Vous avez déjà voté sur cette proposition")
            
            # Calculer le pouvoir de vote
            voting_power = await self._get_user_voting_power(voter_id)
            
            if voting_power < self.min_voting_power:
                raise ValueError(f"Pouvoir de vote insuffisant (minimum: {self.min_voting_power} QS)")
            
            # Enregistrer le vote
            vote = {
                "id": str(uuid.uuid4()),
                "voter_id": voter_id,
                "proposal_id": proposal_id,
                "vote_type": vote_type.value,
                "voting_power": voting_power,
                "voted_at": datetime.utcnow()
            }
            
            await self.db.governance_votes.insert_one(vote)
            
            # Mettre à jour la proposition
            update_fields = {
                "$inc": {
                    "total_votes": voting_power,
                    "unique_voters": 1
                }
            }
            
            if vote_type == VoteType.FOR:
                update_fields["$inc"]["votes_for"] = voting_power
            elif vote_type == VoteType.AGAINST:
                update_fields["$inc"]["votes_against"] = voting_power
            elif vote_type == VoteType.ABSTAIN:
                update_fields["$inc"]["votes_abstain"] = voting_power
            
            await self.db.governance_proposals.update_one(
                {"id": proposal_id},
                update_fields
            )
            
            return {
                "vote_id": vote["id"],
                "voting_power": voting_power,
                "vote_type": vote_type.value,
                "status": "recorded"
            }
            
        except Exception as e:
            logger.error(f"Erreur enregistrement vote: {e}")
            raise Exception(f"Impossible d'enregistrer le vote: {e}")
    
    async def finalize_proposal(self, proposal_id: str) -> Dict[str, Any]:
        """Finalise une proposition après la fin du vote"""
        try:
            # Récupérer la proposition
            proposal = await self.db.governance_proposals.find_one({"id": proposal_id})
            if not proposal:
                raise ValueError("Proposition non trouvée")
            
            if proposal["status"] != ProposalStatus.ACTIVE.value:
                raise ValueError("Proposition non active")
            
            # Vérifier si le vote est terminé
            if datetime.utcnow() <= proposal["voting_end_date"]:
                raise ValueError("Période de vote non terminée")
            
            # Calculer le résultat
            total_voting_power = await self._get_total_voting_power()
            quorum_reached = proposal["total_votes"] / total_voting_power >= proposal["required_quorum"]
            
            # Déterminer le résultat
            if not quorum_reached:
                result = ProposalStatus.REJECTED.value
                reason = "Quorum non atteint"
            elif proposal["votes_for"] > proposal["votes_against"]:
                result = ProposalStatus.PASSED.value
                reason = "Majorité en faveur"
            else:
                result = ProposalStatus.REJECTED.value
                reason = "Majorité contre"
            
            # Mettre à jour la proposition
            await self.db.governance_proposals.update_one(
                {"id": proposal_id},
                {
                    "$set": {
                        "status": result,
                        "finalized_at": datetime.utcnow(),
                        "result_reason": reason
                    }
                }
            )
            
            # Rembourser le stake si la proposition est acceptée
            if result == ProposalStatus.PASSED.value:
                await self._return_proposal_stake(proposal_id)
            
            return {
                "proposal_id": proposal_id,
                "result": result,
                "reason": reason,
                "votes_for": proposal["votes_for"],
                "votes_against": proposal["votes_against"],
                "quorum_reached": quorum_reached,
                "current_quorum": proposal["total_votes"] / total_voting_power
            }
            
        except Exception as e:
            logger.error(f"Erreur finalisation proposition: {e}")
            raise Exception(f"Impossible de finaliser la proposition: {e}")
    
    # ===== MÉTHODES UTILITAIRES =====
    
    async def _get_user_voting_power(self, user_id: str) -> float:
        """Calcule le pouvoir de vote d'un utilisateur"""
        try:
            user = await self.db.users.find_one({"id": user_id})
            if not user:
                return 0.0
            
            # Le pouvoir de vote est basé sur le solde QS
            return user["qs_balance"]
            
        except Exception as e:
            logger.error(f"Erreur calcul pouvoir de vote: {e}")
            return 0.0
    
    async def _get_total_voting_power(self) -> float:
        """Calcule le pouvoir de vote total"""
        try:
            # Somme des soldes QS de tous les utilisateurs
            pipeline = [
                {"$group": {"_id": None, "total": {"$sum": "$qs_balance"}}}
            ]
            
            result = await self.db.users.aggregate(pipeline).to_list(None)
            return result[0]["total"] if result else 0.0
            
        except Exception as e:
            logger.error(f"Erreur calcul pouvoir de vote total: {e}")
            return 0.0
    
    async def _return_proposal_stake(self, proposal_id: str) -> bool:
        """Rembourse le stake d'une proposition"""
        try:
            # Récupérer le stake
            stake = await self.db.governance_stakes.find_one({
                "proposal_id": proposal_id,
                "returned": False
            })
            
            if not stake:
                return False
            
            # Rembourser l'utilisateur
            await self.db.users.update_one(
                {"id": stake["user_id"]},
                {"$inc": {"qs_balance": stake["stake_amount"]}}
            )
            
            # Marquer comme remboursé
            await self.db.governance_stakes.update_one(
                {"id": stake["id"]},
                {"$set": {"returned": True, "returned_at": datetime.utcnow()}}
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur remboursement stake: {e}")
            return False
    
    async def get_governance_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques de gouvernance"""
        try:
            # Compter les propositions par statut
            total_proposals = await self.db.governance_proposals.count_documents({})
            active_proposals = await self.db.governance_proposals.count_documents({"status": ProposalStatus.ACTIVE.value})
            passed_proposals = await self.db.governance_proposals.count_documents({"status": ProposalStatus.PASSED.value})
            rejected_proposals = await self.db.governance_proposals.count_documents({"status": ProposalStatus.REJECTED.value})
            
            # Compter les votants uniques
            unique_voters = len(await self.db.governance_votes.distinct("voter_id"))
            
            # Calculer le pouvoir de vote total
            total_voting_power = await self._get_total_voting_power()
            
            return {
                "total_proposals": total_proposals,
                "active_proposals": active_proposals,
                "passed_proposals": passed_proposals,
                "rejected_proposals": rejected_proposals,
                "pending_proposals": total_proposals - active_proposals - passed_proposals - rejected_proposals,
                "total_voters": unique_voters,
                "total_voting_power": total_voting_power,
                "min_proposal_stake": self.min_proposal_stake,
                "min_voting_power": self.min_voting_power
            }
            
        except Exception as e:
            logger.error(f"Erreur statistiques gouvernance: {e}")
            return {
                "total_proposals": 0,
                "active_proposals": 0,
                "passed_proposals": 0,
                "rejected_proposals": 0,
                "pending_proposals": 0,
                "total_voters": 0,
                "total_voting_power": 0.0
            }
    
    async def get_user_voting_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Récupère l'historique de vote d'un utilisateur"""
        try:
            votes = await self.db.governance_votes.find({"voter_id": user_id}).sort("voted_at", -1).to_list(None)
            
            enriched_votes = []
            for vote in votes:
                proposal = await self.db.governance_proposals.find_one({"id": vote["proposal_id"]})
                
                enriched_vote = {
                    "vote_id": vote["id"],
                    "proposal_id": vote["proposal_id"],
                    "proposal_title": proposal["title"] if proposal else "Unknown",
                    "vote_type": vote["vote_type"],
                    "voting_power": vote["voting_power"],
                    "voted_at": vote["voted_at"],
                    "proposal_status": proposal["status"] if proposal else "unknown"
                }
                enriched_votes.append(enriched_vote)
            
            return enriched_votes
            
        except Exception as e:
            logger.error(f"Erreur historique votes utilisateur: {e}")
            return []
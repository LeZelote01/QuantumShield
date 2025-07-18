"""
Service avancé pour la blockchain améliorée
Implémente les smart contracts, consensus hybride, gouvernance et interopérabilité
"""

import hashlib
import json
import time
import gzip
import zlib
import lzma
import brotli
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from motor.motor_asyncio import AsyncIOMotorCollection
import asyncio
import random
from collections import defaultdict

from models.blockchain_models import (
    SmartContract, SmartContractExecution, SmartContractTemplate,
    Validator, StakePool, ConsensusRound, ConsensusType,
    GovernanceProposal, Vote, VotingPower, ProposalStatus, VoteType,
    CompressedBlock, ArchivePeriod, BlockchainSnapshot, CompressionAlgorithm,
    CrossChainBridge, CrossChainTransaction, NetworkSync, BlockchainNetwork,
    BlockchainMetrics, NetworkHealth, SmartContractStatus
)
from models.quantum_models import Block, Transaction, User

logger = logging.getLogger(__name__)

class AdvancedBlockchainService:
    """Service avancé pour la blockchain améliorée"""
    
    def __init__(self, db, blockchain_service):
        self.db = db
        self.blockchain_service = blockchain_service
        
        # Collections pour les nouvelles fonctionnalités
        self.smart_contracts: AsyncIOMotorCollection = db.smart_contracts
        self.contract_executions: AsyncIOMotorCollection = db.contract_executions
        self.contract_templates: AsyncIOMotorCollection = db.contract_templates
        
        self.validators: AsyncIOMotorCollection = db.validators
        self.stake_pools: AsyncIOMotorCollection = db.stake_pools
        self.consensus_rounds: AsyncIOMotorCollection = db.consensus_rounds
        
        self.governance_proposals: AsyncIOMotorCollection = db.governance_proposals
        self.votes: AsyncIOMotorCollection = db.votes
        self.voting_powers: AsyncIOMotorCollection = db.voting_powers
        
        self.compressed_blocks: AsyncIOMotorCollection = db.compressed_blocks
        self.archive_periods: AsyncIOMotorCollection = db.archive_periods
        self.blockchain_snapshots: AsyncIOMotorCollection = db.blockchain_snapshots
        
        self.cross_chain_bridges: AsyncIOMotorCollection = db.cross_chain_bridges
        self.cross_chain_transactions: AsyncIOMotorCollection = db.cross_chain_transactions
        self.network_syncs: AsyncIOMotorCollection = db.network_syncs
        
        # Configuration
        self.consensus_type = ConsensusType.HYBRID_POW_POS
        self.pow_weight = 0.6  # 60% PoW, 40% PoS
        self.pos_weight = 0.4
        self.min_stake = 1000.0
        self.compression_threshold = 1000  # Compresser les blocs > 1000 blocks
        self.archive_threshold = 10000  # Archiver les blocs > 10000 blocks
        
        # État du service
        self.is_initialized = False
        self.compression_tasks = {}
        self.archive_tasks = {}
        
    async def initialize(self):
        """Initialise le service avancé"""
        try:
            await self._initialize_smart_contract_templates()
            await self._initialize_validators()
            await self._initialize_cross_chain_bridges()
            await self._start_background_tasks()
            
            self.is_initialized = True
            logger.info("Service blockchain avancé initialisé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du service avancé: {e}")
            self.is_initialized = False
    
    async def is_ready(self) -> bool:
        """Vérifie si le service est prêt"""
        return self.is_initialized and await self.blockchain_service.is_ready()
    
    # === SMART CONTRACTS ===
    
    async def _initialize_smart_contract_templates(self):
        """Initialise les templates de smart contracts"""
        try:
            # Vérifier si les templates existent déjà
            existing_templates = await self.contract_templates.count_documents({})
            
            if existing_templates == 0:
                # Créer les templates par défaut
                default_templates = [
                    {
                        "name": "Token Standard",
                        "description": "Template pour créer des tokens ERC-20 like",
                        "category": "token",
                        "template_code": """
contract TokenStandard {
    string public name;
    string public symbol;
    uint256 public totalSupply;
    mapping(address => uint256) public balanceOf;
    
    function transfer(address to, uint256 amount) public {
        require(balanceOf[msg.sender] >= amount, "Insufficient balance");
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;
    }
}
                        """,
                        "parameters": [
                            {"name": "name", "type": "string", "description": "Nom du token"},
                            {"name": "symbol", "type": "string", "description": "Symbole du token"},
                            {"name": "totalSupply", "type": "uint256", "description": "Supply totale"}
                        ],
                        "created_by": "system"
                    },
                    {
                        "name": "Voting Contract",
                        "description": "Template pour les contrats de vote",
                        "category": "governance",
                        "template_code": """
contract VotingContract {
    struct Proposal {
        string description;
        uint256 yesVotes;
        uint256 noVotes;
        bool executed;
        uint256 deadline;
    }
    
    mapping(uint256 => Proposal) public proposals;
    mapping(address => mapping(uint256 => bool)) public hasVoted;
    
    function vote(uint256 proposalId, bool support) public {
        require(!hasVoted[msg.sender][proposalId], "Already voted");
        require(block.timestamp < proposals[proposalId].deadline, "Voting ended");
        
        hasVoted[msg.sender][proposalId] = true;
        if (support) {
            proposals[proposalId].yesVotes++;
        } else {
            proposals[proposalId].noVotes++;
        }
    }
}
                        """,
                        "parameters": [
                            {"name": "votingDuration", "type": "uint256", "description": "Durée du vote en secondes"}
                        ],
                        "created_by": "system"
                    },
                    {
                        "name": "IoT Device Registry",
                        "description": "Template pour l'enregistrement de dispositifs IoT",
                        "category": "iot",
                        "template_code": """
contract IoTDeviceRegistry {
    struct Device {
        string deviceId;
        address owner;
        string firmwareHash;
        bool isActive;
        uint256 lastUpdate;
    }
    
    mapping(string => Device) public devices;
    
    function registerDevice(string memory deviceId, string memory firmwareHash) public {
        devices[deviceId] = Device(deviceId, msg.sender, firmwareHash, true, block.timestamp);
    }
    
    function updateFirmware(string memory deviceId, string memory newFirmwareHash) public {
        require(devices[deviceId].owner == msg.sender, "Not device owner");
        devices[deviceId].firmwareHash = newFirmwareHash;
        devices[deviceId].lastUpdate = block.timestamp;
    }
}
                        """,
                        "parameters": [
                            {"name": "registrationFee", "type": "uint256", "description": "Frais d'enregistrement"}
                        ],
                        "created_by": "system"
                    }
                ]
                
                for template_data in default_templates:
                    template = SmartContractTemplate(**template_data)
                    await self.contract_templates.insert_one(template.dict())
                
                logger.info(f"Initialisé {len(default_templates)} templates de smart contracts")
        
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation des templates: {e}")
    
    async def deploy_smart_contract(self, user_address: str, contract_data: Dict[str, Any]) -> SmartContract:
        """Déploie un nouveau smart contract"""
        try:
            # Simuler la compilation du contrat
            bytecode = self._compile_contract(contract_data["code"])
            abi = self._extract_abi(contract_data["code"])
            contract_address = self._generate_contract_address(user_address)
            
            # Créer le contrat
            contract = SmartContract(
                name=contract_data["name"],
                description=contract_data["description"],
                code=contract_data["code"],
                bytecode=bytecode,
                abi=abi,
                creator_address=user_address,
                contract_address=contract_address,
                status=SmartContractStatus.DEPLOYED,
                deployed_at=datetime.utcnow(),
                metadata=contract_data.get("metadata", {})
            )
            
            # Sauvegarder dans la base de données
            await self.smart_contracts.insert_one(contract.dict())
            
            # Créer une transaction de déploiement
            deploy_transaction = Transaction(
                from_address=user_address,
                to_address=contract_address,
                amount=0,
                transaction_type="smart_contract_deploy",
                data={
                    "contract_name": contract.name,
                    "contract_address": contract_address,
                    "bytecode_size": len(bytecode),
                    "gas_used": self._estimate_gas(bytecode)
                },
                signature="contract_deploy_signature"
            )
            
            await self.blockchain_service.add_transaction(deploy_transaction)
            
            logger.info(f"Smart contract déployé: {contract.name} à {contract_address}")
            return contract
            
        except Exception as e:
            logger.error(f"Erreur lors du déploiement du contrat: {e}")
            raise Exception(f"Impossible de déployer le contrat: {e}")
    
    async def execute_smart_contract(self, contract_id: str, function_name: str, 
                                   parameters: Dict[str, Any], caller_address: str) -> SmartContractExecution:
        """Exécute une fonction d'un smart contract"""
        try:
            # Récupérer le contrat
            contract_data = await self.smart_contracts.find_one({"id": contract_id})
            if not contract_data:
                raise Exception(f"Contrat {contract_id} non trouvé")
            
            contract = SmartContract(**contract_data)
            
            # Simuler l'exécution
            result = await self._execute_contract_function(
                contract, function_name, parameters, caller_address
            )
            
            # Créer l'enregistrement d'exécution
            execution = SmartContractExecution(
                contract_id=contract_id,
                function_name=function_name,
                parameters=parameters,
                caller_address=caller_address,
                transaction_hash="",  # Sera mis à jour
                result=result,
                gas_used=self._estimate_gas_usage(function_name, parameters),
                status=SmartContractStatus.COMPLETED
            )
            
            # Créer une transaction d'exécution
            exec_transaction = Transaction(
                from_address=caller_address,
                to_address=contract.contract_address,
                amount=0,
                transaction_type="smart_contract_execution",
                data={
                    "contract_id": contract_id,
                    "function_name": function_name,
                    "parameters": parameters,
                    "result": result,
                    "gas_used": execution.gas_used
                },
                signature="contract_execution_signature"
            )
            
            tx_hash = await self.blockchain_service.add_transaction(exec_transaction)
            execution.transaction_hash = tx_hash
            
            # Sauvegarder l'exécution
            await self.contract_executions.insert_one(execution.dict())
            
            logger.info(f"Fonction {function_name} exécutée sur contrat {contract_id}")
            return execution
            
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution du contrat: {e}")
            # Créer un enregistrement d'exécution échouée
            execution = SmartContractExecution(
                contract_id=contract_id,
                function_name=function_name,
                parameters=parameters,
                caller_address=caller_address,
                transaction_hash="",
                status=SmartContractStatus.FAILED,
                error_message=str(e)
            )
            await self.contract_executions.insert_one(execution.dict())
            raise Exception(f"Impossible d'exécuter le contrat: {e}")
    
    def _compile_contract(self, code: str) -> str:
        """Simule la compilation d'un contrat (retourne un bytecode factice)"""
        return hashlib.sha256(code.encode()).hexdigest()
    
    def _extract_abi(self, code: str) -> List[Dict[str, Any]]:
        """Extrait l'ABI d'un contrat (simulation)"""
        # Simulation d'extraction d'ABI
        return [
            {
                "name": "transfer",
                "type": "function",
                "inputs": [
                    {"name": "to", "type": "address"},
                    {"name": "amount", "type": "uint256"}
                ],
                "outputs": [{"name": "", "type": "bool"}]
            }
        ]
    
    def _generate_contract_address(self, creator_address: str) -> str:
        """Génère une adresse de contrat"""
        nonce = str(int(time.time() * 1000000))
        address_data = creator_address + nonce
        return "0x" + hashlib.sha256(address_data.encode()).hexdigest()[:40]
    
    def _estimate_gas(self, bytecode: str) -> int:
        """Estime le gas nécessaire pour le déploiement"""
        return len(bytecode) * 100 + 21000
    
    def _estimate_gas_usage(self, function_name: str, parameters: Dict[str, Any]) -> int:
        """Estime le gas nécessaire pour l'exécution d'une fonction"""
        base_gas = 21000
        param_gas = len(str(parameters)) * 10
        return base_gas + param_gas
    
    async def _execute_contract_function(self, contract: SmartContract, function_name: str, 
                                        parameters: Dict[str, Any], caller_address: str) -> Any:
        """Simule l'exécution d'une fonction de contrat"""
        # Simulation d'exécution basée sur le nom de la fonction
        if function_name == "transfer":
            return {"success": True, "transferred": parameters.get("amount", 0)}
        elif function_name == "balanceOf":
            return {"balance": 1000}
        elif function_name == "vote":
            return {"voted": True, "proposal_id": parameters.get("proposalId", 0)}
        elif function_name == "registerDevice":
            return {"registered": True, "device_id": parameters.get("deviceId", "")}
        else:
            return {"executed": True, "function": function_name}
    
    # === CONSENSUS HYBRIDE ===
    
    async def _initialize_validators(self):
        """Initialise les validateurs pour le consensus PoS"""
        try:
            # Créer des validateurs par défaut si aucun n'existe
            validator_count = await self.validators.count_documents({})
            
            if validator_count == 0:
                # Créer des validateurs de base
                default_validators = [
                    {
                        "address": "0x1234567890123456789012345678901234567890",
                        "stake_amount": 10000.0,
                        "reputation_score": 1.0,
                        "is_active": True
                    },
                    {
                        "address": "0x2345678901234567890123456789012345678901",
                        "stake_amount": 8000.0,
                        "reputation_score": 0.9,
                        "is_active": True
                    },
                    {
                        "address": "0x3456789012345678901234567890123456789012",
                        "stake_amount": 5000.0,
                        "reputation_score": 0.8,
                        "is_active": True
                    }
                ]
                
                for validator_data in default_validators:
                    validator = Validator(**validator_data)
                    await self.validators.insert_one(validator.dict())
                
                logger.info(f"Initialisé {len(default_validators)} validateurs par défaut")
        
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation des validateurs: {e}")
    
    async def select_block_proposer(self, block_number: int) -> str:
        """Sélectionne le proposeur de bloc selon le consensus hybride"""
        try:
            # Récupérer les validateurs actifs
            cursor = self.validators.find({"is_active": True})
            validators = await cursor.to_list(length=None)
            
            if not validators:
                # Fallback sur PoW pur
                return "0x0000000000000000000000000000000000000000"
            
            # Calculer les poids de sélection
            selection_weights = []
            for validator_data in validators:
                validator = Validator(**validator_data)
                # Poids basé sur le stake et la réputation
                weight = validator.stake_amount * validator.reputation_score
                selection_weights.append((validator.address, weight))
            
            # Sélection pondérée basée sur le hash du bloc précédent
            total_weight = sum(weight for _, weight in selection_weights)
            random.seed(block_number)  # Déterministe basé sur le numéro de bloc
            selection_point = random.uniform(0, total_weight)
            
            cumulative_weight = 0
            for address, weight in selection_weights:
                cumulative_weight += weight
                if cumulative_weight >= selection_point:
                    return address
            
            return selection_weights[0][0]  # Fallback
            
        except Exception as e:
            logger.error(f"Erreur lors de la sélection du proposeur: {e}")
            return "0x0000000000000000000000000000000000000000"
    
    async def validate_block_consensus(self, block: Block) -> bool:
        """Valide un bloc selon le consensus hybride"""
        try:
            # Vérifier le PoW (60% du poids)
            pow_valid = self.blockchain_service.is_valid_proof_of_work(block.hash, block.difficulty)
            
            # Vérifier le PoS (40% du poids)
            pos_valid = await self._validate_pos_consensus(block)
            
            # Consensus hybride
            if self.consensus_type == ConsensusType.HYBRID_POW_POS:
                return pow_valid and pos_valid
            elif self.consensus_type == ConsensusType.PROOF_OF_WORK:
                return pow_valid
            elif self.consensus_type == ConsensusType.PROOF_OF_STAKE:
                return pos_valid
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur lors de la validation du consensus: {e}")
            return False
    
    async def _validate_pos_consensus(self, block: Block) -> bool:
        """Valide la partie PoS du consensus"""
        try:
            # Vérifier que le proposeur est un validateur actif
            validator = await self.validators.find_one({"address": block.miner_address})
            if not validator:
                return False
            
            validator_obj = Validator(**validator)
            if not validator_obj.is_active or validator_obj.stake_amount < self.min_stake:
                return False
            
            # Vérifier que le proposeur était sélectionné pour ce bloc
            expected_proposer = await self.select_block_proposer(block.block_number)
            if expected_proposer != block.miner_address:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la validation PoS: {e}")
            return False
    
    async def stake_tokens(self, user_address: str, validator_address: str, amount: float) -> bool:
        """Stake des tokens auprès d'un validateur"""
        try:
            # Vérifier que le validateur existe
            validator = await self.validators.find_one({"address": validator_address})
            if not validator:
                raise Exception(f"Validateur {validator_address} non trouvé")
            
            # Créer ou mettre à jour le stake pool
            stake_pool = await self.stake_pools.find_one({"validator_address": validator_address})
            
            if not stake_pool:
                # Créer un nouveau stake pool
                stake_pool = StakePool(
                    validator_address=validator_address,
                    total_stake=amount,
                    delegators=[{"address": user_address, "stake": amount}]
                )
                await self.stake_pools.insert_one(stake_pool.dict())
            else:
                # Mettre à jour le stake pool existant
                stake_pool_obj = StakePool(**stake_pool)
                
                # Chercher si l'utilisateur a déjà staké
                user_found = False
                for delegator in stake_pool_obj.delegators:
                    if delegator["address"] == user_address:
                        delegator["stake"] += amount
                        user_found = True
                        break
                
                if not user_found:
                    stake_pool_obj.delegators.append({"address": user_address, "stake": amount})
                
                stake_pool_obj.total_stake += amount
                
                await self.stake_pools.replace_one(
                    {"validator_address": validator_address},
                    stake_pool_obj.dict()
                )
            
            # Mettre à jour le stake du validateur
            await self.validators.update_one(
                {"address": validator_address},
                {"$inc": {"stake_amount": amount}}
            )
            
            # Créer une transaction de staking
            stake_transaction = Transaction(
                from_address=user_address,
                to_address=validator_address,
                amount=amount,
                transaction_type="staking",
                data={
                    "validator_address": validator_address,
                    "stake_amount": amount,
                    "stake_type": "delegation"
                },
                signature="staking_signature"
            )
            
            await self.blockchain_service.add_transaction(stake_transaction)
            
            logger.info(f"Stake de {amount} tokens vers {validator_address} par {user_address}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du staking: {e}")
            return False
    
    # === GOUVERNANCE ===
    
    async def create_proposal(self, proposer_address: str, proposal_data: Dict[str, Any]) -> GovernanceProposal:
        """Crée une nouvelle proposition de gouvernance"""
        try:
            # Calculer les dates de vote
            voting_start = datetime.utcnow()
            voting_end = voting_start + timedelta(seconds=proposal_data.get("voting_duration", 604800))
            
            # Créer la proposition
            proposal = GovernanceProposal(
                title=proposal_data["title"],
                description=proposal_data["description"],
                proposer_address=proposer_address,
                proposal_type=proposal_data["proposal_type"],
                target_parameter=proposal_data.get("target_parameter"),
                proposed_value=proposal_data.get("proposed_value"),
                voting_start=voting_start,
                voting_end=voting_end,
                status=ProposalStatus.ACTIVE,
                metadata=proposal_data.get("metadata", {})
            )
            
            # Sauvegarder la proposition
            await self.governance_proposals.insert_one(proposal.dict())
            
            # Créer une transaction de proposition
            proposal_transaction = Transaction(
                from_address=proposer_address,
                to_address="governance_contract",
                amount=0,
                transaction_type="governance_proposal",
                data={
                    "proposal_id": proposal.id,
                    "title": proposal.title,
                    "proposal_type": proposal.proposal_type,
                    "voting_end": voting_end.isoformat()
                },
                signature="proposal_signature"
            )
            
            await self.blockchain_service.add_transaction(proposal_transaction)
            
            logger.info(f"Proposition de gouvernance créée: {proposal.title}")
            return proposal
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de la proposition: {e}")
            raise Exception(f"Impossible de créer la proposition: {e}")
    
    async def vote_on_proposal(self, proposal_id: str, voter_address: str, 
                              vote_type: VoteType, justification: str = None) -> Vote:
        """Vote sur une proposition de gouvernance"""
        try:
            # Vérifier que la proposition existe et est active
            proposal_data = await self.governance_proposals.find_one({"id": proposal_id})
            if not proposal_data:
                raise Exception(f"Proposition {proposal_id} non trouvée")
            
            proposal = GovernanceProposal(**proposal_data)
            
            if proposal.status != ProposalStatus.ACTIVE:
                raise Exception(f"Proposition {proposal_id} n'est pas active")
            
            if datetime.utcnow() > proposal.voting_end:
                raise Exception("Période de vote terminée")
            
            # Vérifier que l'utilisateur n'a pas déjà voté
            existing_vote = await self.votes.find_one({
                "proposal_id": proposal_id,
                "voter_address": voter_address
            })
            
            if existing_vote:
                raise Exception("Vous avez déjà voté sur cette proposition")
            
            # Calculer le pouvoir de vote
            voting_power = await self._calculate_voting_power(voter_address)
            
            # Créer le vote
            vote = Vote(
                proposal_id=proposal_id,
                voter_address=voter_address,
                vote_type=vote_type,
                voting_power=voting_power,
                justification=justification
            )
            
            # Sauvegarder le vote
            await self.votes.insert_one(vote.dict())
            
            # Créer une transaction de vote
            vote_transaction = Transaction(
                from_address=voter_address,
                to_address="governance_contract",
                amount=0,
                transaction_type="governance_vote",
                data={
                    "proposal_id": proposal_id,
                    "vote_type": vote_type.value,
                    "voting_power": voting_power,
                    "justification": justification
                },
                signature="vote_signature"
            )
            
            await self.blockchain_service.add_transaction(vote_transaction)
            
            logger.info(f"Vote enregistré: {vote_type.value} sur proposition {proposal_id}")
            return vote
            
        except Exception as e:
            logger.error(f"Erreur lors du vote: {e}")
            raise Exception(f"Impossible de voter: {e}")
    
    async def _calculate_voting_power(self, voter_address: str) -> float:
        """Calcule le pouvoir de vote d'un utilisateur"""
        try:
            # Récupérer le pouvoir de vote existant ou calculer
            voting_power_data = await self.voting_powers.find_one({"address": voter_address})
            
            if voting_power_data:
                voting_power = VotingPower(**voting_power_data)
                
                # Vérifier si la mise à jour est nécessaire
                if datetime.utcnow() - voting_power.last_updated > timedelta(hours=1):
                    # Recalculer le pouvoir de vote
                    voting_power = await self._recalculate_voting_power(voter_address)
                
                return voting_power.total_power
            else:
                # Première fois - calculer le pouvoir de vote
                voting_power = await self._recalculate_voting_power(voter_address)
                return voting_power.total_power
                
        except Exception as e:
            logger.error(f"Erreur lors du calcul du pouvoir de vote: {e}")
            return 1.0  # Pouvoir de vote par défaut
    
    async def _recalculate_voting_power(self, voter_address: str) -> VotingPower:
        """Recalcule le pouvoir de vote d'un utilisateur"""
        try:
            # Pouvoir de base (basé sur les tokens possédés)
            # Simulation - dans la réalité, cela viendrait du service de tokens
            base_power = 100.0  # Par défaut
            
            # Multiplicateur de stake
            stake_multiplier = 1.0
            stake_pools = await self.stake_pools.find({}).to_list(length=None)
            
            for pool_data in stake_pools:
                pool = StakePool(**pool_data)
                for delegator in pool.delegators:
                    if delegator["address"] == voter_address:
                        stake_multiplier += delegator["stake"] / 10000.0  # 1% par 10k tokens stakés
            
            # Bonus de réputation
            reputation_bonus = 0.0
            validator = await self.validators.find_one({"address": voter_address})
            if validator:
                validator_obj = Validator(**validator)
                reputation_bonus = validator_obj.reputation_score * 0.1
            
            # Pouvoir total
            total_power = base_power * stake_multiplier + reputation_bonus
            
            # Créer ou mettre à jour le pouvoir de vote
            voting_power = VotingPower(
                address=voter_address,
                base_power=base_power,
                stake_multiplier=stake_multiplier,
                reputation_bonus=reputation_bonus,
                total_power=total_power
            )
            
            # Sauvegarder
            await self.voting_powers.replace_one(
                {"address": voter_address},
                voting_power.dict(),
                upsert=True
            )
            
            return voting_power
            
        except Exception as e:
            logger.error(f"Erreur lors du recalcul du pouvoir de vote: {e}")
            return VotingPower(
                address=voter_address,
                base_power=1.0,
                stake_multiplier=1.0,
                reputation_bonus=0.0,
                total_power=1.0
            )
    
    async def execute_proposal(self, proposal_id: str) -> bool:
        """Exécute une proposition approuvée"""
        try:
            # Récupérer la proposition
            proposal_data = await self.governance_proposals.find_one({"id": proposal_id})
            if not proposal_data:
                raise Exception(f"Proposition {proposal_id} non trouvée")
            
            proposal = GovernanceProposal(**proposal_data)
            
            # Vérifier que la proposition peut être exécutée
            if proposal.status != ProposalStatus.PASSED:
                raise Exception("Proposition non approuvée")
            
            # Vérifier le délai d'exécution
            execution_time = proposal.voting_end + timedelta(seconds=proposal.execution_delay)
            if datetime.utcnow() < execution_time:
                raise Exception("Délai d'exécution non atteint")
            
            # Exécuter la proposition selon son type
            success = await self._execute_proposal_action(proposal)
            
            if success:
                # Marquer comme exécutée
                await self.governance_proposals.update_one(
                    {"id": proposal_id},
                    {
                        "$set": {
                            "status": ProposalStatus.EXECUTED.value,
                            "executed_at": datetime.utcnow()
                        }
                    }
                )
                
                # Créer une transaction d'exécution
                execution_transaction = Transaction(
                    from_address="governance_contract",
                    to_address="system",
                    amount=0,
                    transaction_type="governance_execution",
                    data={
                        "proposal_id": proposal_id,
                        "proposal_type": proposal.proposal_type,
                        "executed_at": datetime.utcnow().isoformat()
                    },
                    signature="execution_signature"
                )
                
                await self.blockchain_service.add_transaction(execution_transaction)
                
                logger.info(f"Proposition {proposal_id} exécutée avec succès")
                return True
            else:
                logger.error(f"Échec de l'exécution de la proposition {proposal_id}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de la proposition: {e}")
            return False
    
    async def _execute_proposal_action(self, proposal: GovernanceProposal) -> bool:
        """Exécute l'action spécifiée par une proposition"""
        try:
            if proposal.proposal_type == "parameter_change":
                # Changer un paramètre du système
                if proposal.target_parameter == "mining_difficulty":
                    self.blockchain_service.difficulty = int(proposal.proposed_value)
                elif proposal.target_parameter == "mining_reward":
                    self.blockchain_service.mining_reward = float(proposal.proposed_value)
                elif proposal.target_parameter == "min_stake":
                    self.min_stake = float(proposal.proposed_value)
                
                return True
                
            elif proposal.proposal_type == "upgrade":
                # Mettre à jour le système
                logger.info(f"Mise à jour du système: {proposal.description}")
                return True
                
            elif proposal.proposal_type == "treasury":
                # Gestion du trésor
                logger.info(f"Action du trésor: {proposal.description}")
                return True
                
            elif proposal.proposal_type == "general":
                # Proposition générale
                logger.info(f"Proposition générale approuvée: {proposal.description}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de l'action: {e}")
            return False
    
    # === COMPRESSION ET ARCHIVAGE ===
    
    async def compress_old_blocks(self, threshold_blocks: int = None) -> int:
        """Compresse les anciens blocs"""
        try:
            if threshold_blocks is None:
                threshold_blocks = self.compression_threshold
            
            # Récupérer les blocs anciens non compressés
            cutoff_block = await self._get_last_block_number() - threshold_blocks
            
            if cutoff_block <= 0:
                return 0
            
            # Récupérer les blocs à compresser
            blocks_cursor = self.blockchain_service.blocks.find(
                {"block_number": {"$lte": cutoff_block}}
            ).sort("block_number", 1)
            
            blocks_to_compress = await blocks_cursor.to_list(length=None)
            
            if not blocks_to_compress:
                return 0
            
            compressed_count = 0
            
            for block_data in blocks_to_compress:
                try:
                    # Vérifier si déjà compressé
                    existing_compressed = await self.compressed_blocks.find_one(
                        {"original_block_id": block_data["id"]}
                    )
                    
                    if existing_compressed:
                        continue
                    
                    # Compresser le bloc
                    original_data = json.dumps(block_data, sort_keys=True)
                    compressed_data = await self._compress_data(original_data, CompressionAlgorithm.GZIP)
                    
                    # Calculer les ratios
                    original_size = len(original_data.encode('utf-8'))
                    compressed_size = len(compressed_data.encode('utf-8'))
                    compression_ratio = compressed_size / original_size
                    
                    # Sauvegarder le bloc compressé
                    compressed_block = CompressedBlock(
                        original_block_id=block_data["id"],
                        block_number=block_data["block_number"],
                        compression_algorithm=CompressionAlgorithm.GZIP,
                        original_size=original_size,
                        compressed_size=compressed_size,
                        compression_ratio=compression_ratio,
                        compressed_data=compressed_data,
                        checksum=hashlib.sha256(original_data.encode()).hexdigest()
                    )
                    
                    await self.compressed_blocks.insert_one(compressed_block.dict())
                    compressed_count += 1
                    
                except Exception as e:
                    logger.error(f"Erreur lors de la compression du bloc {block_data['block_number']}: {e}")
                    continue
            
            logger.info(f"Compressé {compressed_count} blocs")
            return compressed_count
            
        except Exception as e:
            logger.error(f"Erreur lors de la compression des blocs: {e}")
            return 0
    
    async def _compress_data(self, data: str, algorithm: CompressionAlgorithm) -> str:
        """Compresse des données selon l'algorithme spécifié"""
        try:
            data_bytes = data.encode('utf-8')
            
            if algorithm == CompressionAlgorithm.GZIP:
                compressed_bytes = gzip.compress(data_bytes)
            elif algorithm == CompressionAlgorithm.ZLIB:
                compressed_bytes = zlib.compress(data_bytes)
            elif algorithm == CompressionAlgorithm.LZMA:
                compressed_bytes = lzma.compress(data_bytes)
            elif algorithm == CompressionAlgorithm.BROTLI:
                compressed_bytes = brotli.compress(data_bytes)
            else:
                raise Exception(f"Algorithme de compression non supporté: {algorithm}")
            
            # Encoder en base64 pour le stockage
            import base64
            return base64.b64encode(compressed_bytes).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Erreur lors de la compression: {e}")
            return data
    
    async def archive_old_blocks(self, threshold_blocks: int = None) -> str:
        """Archive les anciens blocs compressés"""
        try:
            if threshold_blocks is None:
                threshold_blocks = self.archive_threshold
            
            # Récupérer les blocs compressés anciens
            cutoff_block = await self._get_last_block_number() - threshold_blocks
            
            if cutoff_block <= 0:
                return ""
            
            # Récupérer les blocs compressés à archiver
            compressed_blocks_cursor = self.compressed_blocks.find(
                {"block_number": {"$lte": cutoff_block}}
            ).sort("block_number", 1)
            
            compressed_blocks = await compressed_blocks_cursor.to_list(length=None)
            
            if not compressed_blocks:
                return ""
            
            # Créer l'archive
            archive_data = {
                "start_block": compressed_blocks[0]["block_number"],
                "end_block": compressed_blocks[-1]["block_number"],
                "blocks": compressed_blocks
            }
            
            # Compresser l'archive
            archive_json = json.dumps(archive_data, sort_keys=True)
            archive_compressed = await self._compress_data(archive_json, CompressionAlgorithm.LZMA)
            
            # Générer un nom de fichier d'archive
            archive_id = str(uuid.uuid4())
            archive_location = f"archive_{archive_data['start_block']}_{archive_data['end_block']}_{archive_id}.lzma"
            
            # Créer l'enregistrement d'archive
            archive_period = ArchivePeriod(
                start_block=archive_data["start_block"],
                end_block=archive_data["end_block"],
                total_blocks=len(compressed_blocks),
                archive_location=archive_location,
                compression_algorithm=CompressionAlgorithm.LZMA,
                total_size=len(archive_compressed.encode('utf-8')),
                integrity_hash=hashlib.sha256(archive_json.encode()).hexdigest()
            )
            
            # Sauvegarder l'enregistrement d'archive
            await self.archive_periods.insert_one(archive_period.dict())
            
            # Supprimer les blocs compressés individuels (optionnel)
            block_ids = [block["id"] for block in compressed_blocks]
            await self.compressed_blocks.delete_many({"id": {"$in": block_ids}})
            
            logger.info(f"Archivé {len(compressed_blocks)} blocs dans {archive_location}")
            return archive_location
            
        except Exception as e:
            logger.error(f"Erreur lors de l'archivage: {e}")
            return ""
    
    async def _get_last_block_number(self) -> int:
        """Récupère le numéro du dernier bloc"""
        try:
            last_block = await self.blockchain_service.blocks.find_one(
                {},
                sort=[("block_number", -1)]
            )
            return last_block["block_number"] if last_block else 0
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du dernier bloc: {e}")
            return 0
    
    # === INTEROPÉRABILITÉ ===
    
    async def _initialize_cross_chain_bridges(self):
        """Initialise les ponts cross-chain"""
        try:
            # Vérifier si des ponts existent déjà
            bridge_count = await self.cross_chain_bridges.count_documents({})
            
            if bridge_count == 0:
                # Créer des ponts par défaut
                default_bridges = [
                    {
                        "source_network": BlockchainNetwork.ETHEREUM,
                        "target_network": BlockchainNetwork.POLYGON,
                        "bridge_address": "0xbridge_eth_polygon",
                        "supported_tokens": ["QS", "ETH", "USDT"],
                        "fee_rate": 0.001,
                        "daily_limit": 1000000.0
                    },
                    {
                        "source_network": BlockchainNetwork.BINANCE_SMART_CHAIN,
                        "target_network": BlockchainNetwork.AVALANCHE,
                        "bridge_address": "0xbridge_bsc_avax",
                        "supported_tokens": ["QS", "BNB", "USDC"],
                        "fee_rate": 0.0015,
                        "daily_limit": 500000.0
                    }
                ]
                
                for bridge_data in default_bridges:
                    bridge = CrossChainBridge(**bridge_data)
                    await self.cross_chain_bridges.insert_one(bridge.dict())
                
                logger.info(f"Initialisé {len(default_bridges)} ponts cross-chain")
        
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation des ponts: {e}")
    
    async def initiate_cross_chain_transfer(self, bridge_id: str, from_address: str, 
                                          to_address: str, amount: float, token_symbol: str) -> CrossChainTransaction:
        """Initie un transfert cross-chain"""
        try:
            # Récupérer le pont
            bridge_data = await self.cross_chain_bridges.find_one({"id": bridge_id})
            if not bridge_data:
                raise Exception(f"Pont {bridge_id} non trouvé")
            
            bridge = CrossChainBridge(**bridge_data)
            
            # Vérifier les limites et conditions
            if token_symbol not in bridge.supported_tokens:
                raise Exception(f"Token {token_symbol} non supporté sur ce pont")
            
            if amount > bridge.daily_limit:
                raise Exception(f"Montant {amount} dépasse la limite quotidienne")
            
            # Calculer les frais
            fees = amount * bridge.fee_rate
            
            # Créer la transaction cross-chain
            cross_tx = CrossChainTransaction(
                bridge_id=bridge_id,
                source_tx_hash="",  # Sera mis à jour
                from_address=from_address,
                to_address=to_address,
                amount=amount,
                token_symbol=token_symbol,
                fees_paid=fees
            )
            
            # Créer une transaction source
            source_transaction = Transaction(
                from_address=from_address,
                to_address=bridge.bridge_address,
                amount=amount,
                transaction_type="cross_chain_transfer",
                data={
                    "cross_chain_tx_id": cross_tx.id,
                    "target_network": bridge.target_network.value,
                    "target_address": to_address,
                    "token_symbol": token_symbol,
                    "fees": fees
                },
                signature="cross_chain_signature"
            )
            
            # Ajouter la transaction à la blockchain
            tx_hash = await self.blockchain_service.add_transaction(source_transaction)
            cross_tx.source_tx_hash = tx_hash
            
            # Sauvegarder la transaction cross-chain
            await self.cross_chain_transactions.insert_one(cross_tx.dict())
            
            # Simuler le traitement asynchrone
            asyncio.create_task(self._process_cross_chain_transfer(cross_tx.id))
            
            logger.info(f"Transfert cross-chain initié: {cross_tx.id}")
            return cross_tx
            
        except Exception as e:
            logger.error(f"Erreur lors du transfert cross-chain: {e}")
            raise Exception(f"Impossible d'initier le transfert: {e}")
    
    async def _process_cross_chain_transfer(self, cross_tx_id: str):
        """Traite un transfert cross-chain de manière asynchrone"""
        try:
            # Simuler un délai de traitement
            await asyncio.sleep(30)  # 30 secondes de traitement
            
            # Récupérer la transaction
            cross_tx_data = await self.cross_chain_transactions.find_one({"id": cross_tx_id})
            if not cross_tx_data:
                return
            
            cross_tx = CrossChainTransaction(**cross_tx_data)
            
            # Simuler le succès/échec (90% de succès)
            import random
            success = random.random() < 0.9
            
            if success:
                # Générer un hash de transaction cible
                target_tx_hash = "0x" + hashlib.sha256(
                    f"{cross_tx.id}_target_{time.time()}".encode()
                ).hexdigest()
                
                # Mettre à jour la transaction
                await self.cross_chain_transactions.update_one(
                    {"id": cross_tx_id},
                    {
                        "$set": {
                            "target_tx_hash": target_tx_hash,
                            "status": "confirmed",
                            "completed_at": datetime.utcnow()
                        }
                    }
                )
                
                logger.info(f"Transfert cross-chain terminé avec succès: {cross_tx_id}")
            else:
                # Marquer comme échoué
                await self.cross_chain_transactions.update_one(
                    {"id": cross_tx_id},
                    {
                        "$set": {
                            "status": "failed",
                            "completed_at": datetime.utcnow()
                        }
                    }
                )
                
                logger.error(f"Transfert cross-chain échoué: {cross_tx_id}")
                
        except Exception as e:
            logger.error(f"Erreur lors du traitement cross-chain: {e}")
    
    # === TÂCHES D'ARRIÈRE-PLAN ===
    
    async def _start_background_tasks(self):
        """Démarre les tâches d'arrière-plan"""
        try:
            # Tâche de compression périodique
            asyncio.create_task(self._compression_task())
            
            # Tâche d'archivage périodique
            asyncio.create_task(self._archiving_task())
            
            # Tâche de mise à jour des propositions
            asyncio.create_task(self._governance_task())
            
            logger.info("Tâches d'arrière-plan démarrées")
            
        except Exception as e:
            logger.error(f"Erreur lors du démarrage des tâches d'arrière-plan: {e}")
    
    async def _compression_task(self):
        """Tâche de compression périodique"""
        try:
            while True:
                await asyncio.sleep(3600)  # Toutes les heures
                
                if self.is_initialized:
                    try:
                        await self.compress_old_blocks()
                    except Exception as e:
                        logger.error(f"Erreur lors de la compression périodique: {e}")
                        
        except asyncio.CancelledError:
            logger.info("Tâche de compression annulée")
    
    async def _archiving_task(self):
        """Tâche d'archivage périodique"""
        try:
            while True:
                await asyncio.sleep(86400)  # Tous les jours
                
                if self.is_initialized:
                    try:
                        await self.archive_old_blocks()
                    except Exception as e:
                        logger.error(f"Erreur lors de l'archivage périodique: {e}")
                        
        except asyncio.CancelledError:
            logger.info("Tâche d'archivage annulée")
    
    async def _governance_task(self):
        """Tâche de mise à jour des propositions de gouvernance"""
        try:
            while True:
                await asyncio.sleep(300)  # Toutes les 5 minutes
                
                if self.is_initialized:
                    try:
                        await self._update_proposals_status()
                    except Exception as e:
                        logger.error(f"Erreur lors de la mise à jour des propositions: {e}")
                        
        except asyncio.CancelledError:
            logger.info("Tâche de gouvernance annulée")
    
    async def _update_proposals_status(self):
        """Met à jour le statut des propositions actives"""
        try:
            # Récupérer les propositions actives
            active_proposals = await self.governance_proposals.find(
                {"status": ProposalStatus.ACTIVE.value}
            ).to_list(length=None)
            
            for proposal_data in active_proposals:
                proposal = GovernanceProposal(**proposal_data)
                
                # Vérifier si la période de vote est terminée
                if datetime.utcnow() > proposal.voting_end:
                    # Calculer les résultats
                    votes_cursor = self.votes.find({"proposal_id": proposal.id})
                    votes = await votes_cursor.to_list(length=None)
                    
                    yes_votes = sum(vote["voting_power"] for vote in votes if vote["vote_type"] == "yes")
                    no_votes = sum(vote["voting_power"] for vote in votes if vote["vote_type"] == "no")
                    abstain_votes = sum(vote["voting_power"] for vote in votes if vote["vote_type"] == "abstain")
                    
                    total_votes = yes_votes + no_votes + abstain_votes
                    
                    # Vérifier le quorum
                    if total_votes >= proposal.min_quorum:
                        # Déterminer le résultat
                        if yes_votes > no_votes:
                            new_status = ProposalStatus.PASSED
                        else:
                            new_status = ProposalStatus.REJECTED
                    else:
                        new_status = ProposalStatus.REJECTED  # Quorum non atteint
                    
                    # Mettre à jour le statut
                    await self.governance_proposals.update_one(
                        {"id": proposal.id},
                        {"$set": {"status": new_status.value}}
                    )
                    
                    logger.info(f"Proposition {proposal.id} mise à jour: {new_status.value}")
                    
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des propositions: {e}")
    
    # === MÉTHODES UTILITAIRES ===
    
    async def get_blockchain_metrics(self) -> BlockchainMetrics:
        """Récupère les métriques avancées de la blockchain"""
        try:
            # Calculer les métriques
            total_validators = await self.validators.count_documents({"is_active": True})
            total_stake = 0
            
            stake_pools = await self.stake_pools.find({}).to_list(length=None)
            for pool_data in stake_pools:
                pool = StakePool(**pool_data)
                total_stake += pool.total_stake
            
            # Calculer le hash rate (simulation)
            network_hash_rate = self.blockchain_service.difficulty * 1000000  # Simulation
            
            # Calculer le temps de bloc moyen
            recent_blocks = await self.blockchain_service.blocks.find().sort(
                "block_number", -1
            ).limit(10).to_list(length=10)
            
            if len(recent_blocks) > 1:
                time_diffs = []
                for i in range(1, len(recent_blocks)):
                    time_diff = (
                        datetime.fromisoformat(recent_blocks[i-1]["timestamp"]) -
                        datetime.fromisoformat(recent_blocks[i]["timestamp"])
                    ).total_seconds()
                    time_diffs.append(time_diff)
                
                average_block_time = sum(time_diffs) / len(time_diffs)
            else:
                average_block_time = 300.0  # 5 minutes par défaut
            
            # Calculer le débit de transactions
            total_transactions = await self.blockchain_service.transactions.count_documents({})
            blockchain_age_days = max(1, (datetime.utcnow() - datetime(2024, 1, 1)).days)
            transaction_throughput = total_transactions / (blockchain_age_days * 86400)
            
            # Index de décentralisation (simulation)
            decentralization_index = min(1.0, total_validators / 100.0)
            
            # Consommation d'énergie (simulation)
            energy_consumption = network_hash_rate * 0.001  # kWh
            carbon_footprint = energy_consumption * 0.5  # kg CO2
            
            return BlockchainMetrics(
                network_hash_rate=network_hash_rate,
                total_stake=total_stake,
                active_validators=total_validators,
                average_block_time=average_block_time,
                transaction_throughput=transaction_throughput,
                network_decentralization_index=decentralization_index,
                energy_consumption=energy_consumption,
                carbon_footprint=carbon_footprint
            )
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des métriques: {e}")
            return BlockchainMetrics(
                network_hash_rate=0,
                total_stake=0,
                active_validators=0,
                average_block_time=300,
                transaction_throughput=0,
                network_decentralization_index=0,
                energy_consumption=0,
                carbon_footprint=0
            )
    
    async def get_network_health(self) -> NetworkHealth:
        """Évalue la santé du réseau"""
        try:
            # Santé du consensus
            active_validators = await self.validators.count_documents({"is_active": True})
            consensus_health = min(1.0, active_validators / 10.0)  # 10 validateurs = 100%
            
            # Participation des validateurs
            recent_blocks = await self.blockchain_service.blocks.find().sort(
                "block_number", -1
            ).limit(100).to_list(length=100)
            
            if recent_blocks:
                unique_miners = set(block["miner_address"] for block in recent_blocks)
                validator_participation = len(unique_miners) / max(1, active_validators)
            else:
                validator_participation = 0
            
            # Taux de succès des transactions
            total_transactions = await self.blockchain_service.transactions.count_documents({})
            failed_executions = await self.contract_executions.count_documents(
                {"status": SmartContractStatus.FAILED.value}
            )
            
            if total_transactions > 0:
                transaction_success_rate = 1.0 - (failed_executions / total_transactions)
            else:
                transaction_success_rate = 1.0
            
            # Uptime du réseau (simulation)
            network_uptime = 0.999  # 99.9% par défaut
            
            # Participation à la gouvernance
            total_proposals = await self.governance_proposals.count_documents({})
            total_votes = await self.votes.count_documents({})
            
            if total_proposals > 0:
                governance_participation = min(1.0, total_votes / (total_proposals * 10))
            else:
                governance_participation = 0
            
            # Score global
            weights = [0.3, 0.2, 0.2, 0.2, 0.1]  # Poids pour chaque métrique
            scores = [
                consensus_health,
                validator_participation,
                transaction_success_rate,
                network_uptime,
                governance_participation
            ]
            
            overall_score = sum(w * s for w, s in zip(weights, scores))
            
            # Recommandations
            recommendations = []
            if consensus_health < 0.7:
                recommendations.append("Augmenter le nombre de validateurs actifs")
            if validator_participation < 0.5:
                recommendations.append("Améliorer la participation des validateurs")
            if transaction_success_rate < 0.95:
                recommendations.append("Optimiser les smart contracts pour réduire les échecs")
            if governance_participation < 0.3:
                recommendations.append("Encourager la participation à la gouvernance")
            
            return NetworkHealth(
                consensus_health=consensus_health,
                validator_participation=validator_participation,
                transaction_success_rate=transaction_success_rate,
                network_uptime=network_uptime,
                governance_participation=governance_participation,
                overall_score=overall_score,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de l'évaluation de la santé du réseau: {e}")
            return NetworkHealth(
                consensus_health=0,
                validator_participation=0,
                transaction_success_rate=0,
                network_uptime=0,
                governance_participation=0,
                overall_score=0,
                recommendations=["Erreur lors de l'évaluation - vérifier les logs"]
            )
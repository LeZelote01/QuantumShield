"""
Modèles avancés pour la blockchain améliorée
Inclut les smart contracts, consensus hybride, gouvernance et interopérabilité
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import uuid
from enum import Enum

# Énumérations pour la blockchain améliorée
class ConsensusType(str, Enum):
    PROOF_OF_WORK = "proof_of_work"
    PROOF_OF_STAKE = "proof_of_stake"
    HYBRID_POW_POS = "hybrid_pow_pos"

class SmartContractStatus(str, Enum):
    PENDING = "pending"
    DEPLOYED = "deployed"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class ProposalStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PASSED = "passed"
    REJECTED = "rejected"
    EXECUTED = "executed"
    CANCELLED = "cancelled"

class VoteType(str, Enum):
    YES = "yes"
    NO = "no"
    ABSTAIN = "abstain"

class BlockchainNetwork(str, Enum):
    ETHEREUM = "ethereum"
    BITCOIN = "bitcoin"
    BINANCE_SMART_CHAIN = "binance_smart_chain"
    POLYGON = "polygon"
    AVALANCHE = "avalanche"
    SOLANA = "solana"
    CARDANO = "cardano"

class CompressionAlgorithm(str, Enum):
    GZIP = "gzip"
    ZLIB = "zlib"
    LZMA = "lzma"
    BROTLI = "brotli"

# Smart Contracts
class SmartContract(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    code: str
    bytecode: str
    abi: List[Dict[str, Any]]
    creator_address: str
    contract_address: str
    status: SmartContractStatus = SmartContractStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    deployed_at: Optional[datetime] = None
    gas_used: int = 0
    storage_used: int = 0
    version: str = "1.0.0"
    metadata: Dict[str, Any] = {}

class SmartContractExecution(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    contract_id: str
    function_name: str
    parameters: Dict[str, Any]
    caller_address: str
    transaction_hash: str
    result: Optional[Any] = None
    gas_used: int = 0
    status: SmartContractStatus
    executed_at: datetime = Field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None

class SmartContractTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    category: str
    template_code: str
    parameters: List[Dict[str, Any]]
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    usage_count: int = 0

# Consensus Hybride
class Validator(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    address: str
    stake_amount: float
    reputation_score: float
    is_active: bool = True
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    blocks_validated: int = 0
    slashing_events: int = 0

class StakePool(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    validator_address: str
    total_stake: float
    delegators: List[Dict[str, Any]] = []
    commission_rate: float = 0.05  # 5% par défaut
    rewards_earned: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class ConsensusRound(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    round_number: int
    consensus_type: ConsensusType
    pow_difficulty: int
    pos_threshold: float
    selected_validators: List[str]
    block_proposer: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    success: bool = False

# Gouvernance
class GovernanceProposal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    proposer_address: str
    proposal_type: str  # "parameter_change", "upgrade", "treasury", "general"
    target_parameter: Optional[str] = None
    proposed_value: Optional[Any] = None
    voting_start: datetime
    voting_end: datetime
    execution_delay: int = 86400  # 24 heures en secondes
    min_quorum: float = 0.1  # 10% minimum
    status: ProposalStatus = ProposalStatus.DRAFT
    created_at: datetime = Field(default_factory=datetime.utcnow)
    executed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}

class Vote(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    proposal_id: str
    voter_address: str
    vote_type: VoteType
    voting_power: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    justification: Optional[str] = None

class VotingPower(BaseModel):
    address: str
    base_power: float  # Basé sur les tokens possédés
    stake_multiplier: float  # Multiplicateur basé sur le staking
    reputation_bonus: float  # Bonus basé sur la réputation
    total_power: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)

# Compression et Archivage
class CompressedBlock(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_block_id: str
    block_number: int
    compression_algorithm: CompressionAlgorithm
    original_size: int
    compressed_size: int
    compression_ratio: float
    compressed_data: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    checksum: str

class ArchivePeriod(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    start_block: int
    end_block: int
    total_blocks: int
    archive_location: str
    compression_algorithm: CompressionAlgorithm
    total_size: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    integrity_hash: str

class BlockchainSnapshot(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    block_height: int
    state_root: str
    accounts_snapshot: str
    contracts_snapshot: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    file_size: int
    checksum: str

# Interopérabilité
class CrossChainBridge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_network: BlockchainNetwork
    target_network: BlockchainNetwork
    bridge_address: str
    is_active: bool = True
    supported_tokens: List[str] = []
    fee_rate: float = 0.001  # 0.1%
    daily_limit: float = 1000000.0
    total_volume: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CrossChainTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    bridge_id: str
    source_tx_hash: str
    target_tx_hash: Optional[str] = None
    from_address: str
    to_address: str
    amount: float
    token_symbol: str
    status: str = "pending"  # pending, confirmed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    fees_paid: float = 0.0

class NetworkSync(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    target_network: BlockchainNetwork
    last_synced_block: int
    sync_status: str = "active"  # active, paused, failed
    last_sync_time: datetime = Field(default_factory=datetime.utcnow)
    sync_errors: List[str] = []

# Métriques avancées
class BlockchainMetrics(BaseModel):
    network_hash_rate: float
    total_stake: float
    active_validators: int
    average_block_time: float
    transaction_throughput: float
    network_decentralization_index: float
    energy_consumption: float
    carbon_footprint: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class NetworkHealth(BaseModel):
    consensus_health: float  # 0-1
    validator_participation: float  # 0-1
    transaction_success_rate: float  # 0-1
    network_uptime: float  # 0-1
    governance_participation: float  # 0-1
    overall_score: float  # 0-1
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    recommendations: List[str] = []

# Modèles de requête
class CreateSmartContractRequest(BaseModel):
    name: str
    description: str
    code: str
    metadata: Dict[str, Any] = {}

class ExecuteSmartContractRequest(BaseModel):
    contract_id: str
    function_name: str
    parameters: Dict[str, Any]

class CreateProposalRequest(BaseModel):
    title: str
    description: str
    proposal_type: str
    target_parameter: Optional[str] = None
    proposed_value: Optional[Any] = None
    voting_duration: int = 604800  # 7 jours en secondes
    metadata: Dict[str, Any] = {}

class VoteRequest(BaseModel):
    proposal_id: str
    vote_type: VoteType
    justification: Optional[str] = None

class StakeRequest(BaseModel):
    validator_address: str
    amount: float
    
    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Le montant doit être positif')
        if v < 1.0:
            raise ValueError('Le montant minimum de staking est de 1.0 QS')
        return v
    
    @validator('validator_address')
    def validator_address_must_be_valid(cls, v):
        if not v or len(v) < 10:
            raise ValueError('Adresse de validateur invalide')
        return v

class BridgeTransferRequest(BaseModel):
    target_network: BlockchainNetwork
    to_address: str
    amount: float
    token_symbol: str
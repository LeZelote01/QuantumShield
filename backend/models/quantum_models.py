from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from enum import Enum

class DeviceStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPROMISED = "compromised"
    MAINTENANCE = "maintenance"

class TransactionType(str, Enum):
    REWARD = "reward"
    DETECTION = "detection"
    FIRMWARE_UPDATE = "firmware_update"
    DEVICE_REGISTRATION = "device_registration"

class BlockType(str, Enum):
    TRANSACTION = "transaction"
    FIRMWARE = "firmware"
    DEVICE_REGISTRATION = "device_registration"

class CryptoAlgorithm(str, Enum):
    NTRU_PLUS = "NTRU++"
    KYBER_512 = "Kyber-512"
    KYBER_768 = "Kyber-768"
    KYBER_1024 = "Kyber-1024"
    DILITHIUM_2 = "Dilithium-2"
    DILITHIUM_3 = "Dilithium-3"
    DILITHIUM_5 = "Dilithium-5"

class KeyType(str, Enum):
    ENCRYPTION = "encryption"
    SIGNATURE = "signature"
    HYBRID = "hybrid"

class KeyRotationPolicy(str, Enum):
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    TIME_BASED = "time_based"
    USAGE_BASED = "usage_based"

# User Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    username: str
    wallet_address: str
    qs_balance: float = 0.0
    reputation_score: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class UserCreate(BaseModel):
    email: str
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

# Cryptography Models
class NTRUKeyPair(BaseModel):
    public_key: str
    private_key: str
    key_size: int = 2048
    created_at: datetime = Field(default_factory=datetime.utcnow)

class EncryptionRequest(BaseModel):
    data: str
    public_key: str

class DecryptionRequest(BaseModel):
    encrypted_data: str
    private_key: str

class EncryptionResponse(BaseModel):
    encrypted_data: str
    algorithm: str = "NTRU++"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class DecryptionResponse(BaseModel):
    decrypted_data: str
    verification_status: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Device Models
class Device(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str
    device_name: str
    device_type: str
    owner_id: str
    status: DeviceStatus = DeviceStatus.ACTIVE
    firmware_hash: str
    public_key: str
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    location: Optional[str] = None
    capabilities: List[str] = []

class DeviceCreate(BaseModel):
    device_id: str
    device_name: str
    device_type: str
    location: Optional[str] = None
    capabilities: List[str] = []

class DeviceUpdate(BaseModel):
    device_name: Optional[str] = None
    status: Optional[DeviceStatus] = None
    location: Optional[str] = None
    capabilities: Optional[List[str]] = None

class DeviceHeartbeat(BaseModel):
    device_id: str
    status: DeviceStatus
    firmware_hash: str
    anomaly_detected: bool = False
    sensor_data: Dict[str, Any] = {}

# Blockchain Models
class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_address: str
    to_address: str
    amount: float
    transaction_type: TransactionType
    data: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    signature: str
    hash: str

class Block(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    block_number: int
    previous_hash: str
    merkle_root: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    transactions: List[Transaction] = []
    nonce: int = 0
    difficulty: int = 4
    miner_address: str
    block_type: BlockType = BlockType.TRANSACTION
    hash: str

class BlockchainStats(BaseModel):
    total_blocks: int
    total_transactions: int
    last_block_time: datetime
    current_difficulty: int
    pending_transactions: int

# Token Models
class TokenBalance(BaseModel):
    user_id: str
    balance: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class TokenTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_user: str
    to_user: str
    amount: float
    transaction_type: TransactionType
    description: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    block_hash: Optional[str] = None

class RewardClaim(BaseModel):
    user_id: str
    device_id: str
    reward_type: str
    amount: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Mining Models
class MiningTask(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    block_data: Dict[str, Any]
    difficulty: int
    target_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed: bool = False
    miner_address: Optional[str] = None

class MiningResult(BaseModel):
    task_id: str
    nonce: int
    hash: str
    miner_address: str
    computation_time: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Dashboard Models
class DashboardStats(BaseModel):
    total_devices: int
    active_devices: int
    total_blocks: int
    total_transactions: int
    total_qs_supply: float
    recent_activity: List[Dict[str, Any]]

class DeviceMetrics(BaseModel):
    device_id: str
    uptime_percentage: float
    anomalies_detected: int
    last_firmware_update: datetime
    rewards_earned: float
    status_history: List[Dict[str, Any]]

# Anomaly Detection Models
class AnomalyDetection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str
    anomaly_type: str
    severity: str
    description: str
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolution_notes: Optional[str] = None

class AnomalyReport(BaseModel):
    device_id: str
    anomaly_type: str
    severity: str
    description: str
    sensor_data: Dict[str, Any] = {}

# Advanced Cryptography Models
class AdvancedKeyPair(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    encryption_algorithm: CryptoAlgorithm
    signature_algorithm: CryptoAlgorithm
    encryption_public_key: str
    signature_public_key: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    active: bool = True

class HybridEncryptionData(BaseModel):
    kem_ciphertext: str
    aes_iv: str
    encrypted_message: str
    algorithm: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class KeyRotationConfig(BaseModel):
    keypair_id: str
    policy: KeyRotationPolicy
    rotation_interval: int  # hours
    last_rotation: datetime = Field(default_factory=datetime.utcnow)
    next_rotation: datetime
    active: bool = True

class BatchOperationResult(BaseModel):
    index: int
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
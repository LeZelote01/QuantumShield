"""
Modèles de données pour l'API Gateway de QuantumShield
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

class RateLimitType(str, Enum):
    PER_MINUTE = "per_minute"
    PER_HOUR = "per_hour"
    PER_DAY = "per_day"
    PER_MONTH = "per_month"

class APITier(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class RequestStatus(str, Enum):
    ALLOWED = "allowed"
    BLOCKED = "blocked"
    RATE_LIMITED = "rate_limited"

# ===== MODÈLES API GATEWAY =====

class APIKeyCreateRequest(BaseModel):
    tier: APITier
    description: Optional[str] = None

class APIKeyResponse(BaseModel):
    api_key: str
    api_secret: str
    tier: str
    rate_limits: Dict[str, int]
    created_at: datetime

class APIKeyValidationRequest(BaseModel):
    api_key: str
    api_secret: Optional[str] = None

class APIKeyRevokeRequest(BaseModel):
    api_key: str

class RateLimitConfig(BaseModel):
    per_minute: Optional[int] = None
    per_hour: Optional[int] = None
    per_day: Optional[int] = None
    per_month: Optional[int] = None

class TierLimitsUpdateRequest(BaseModel):
    tier: APITier
    new_limits: Dict[str, int]

class SensitiveEndpointRequest(BaseModel):
    endpoint: str
    limits: Dict[str, int]

class IPBlockRequest(BaseModel):
    ip_address: str
    reason: str
    duration_hours: int = 24

class IPUnblockRequest(BaseModel):
    ip_address: str

class ProxyRequest(BaseModel):
    target_service: str
    endpoint: str
    method: str = "GET"
    headers: Optional[Dict[str, str]] = {}
    data: Optional[Dict[str, Any]] = None

class RateLimitInfo(BaseModel):
    identifier: str
    endpoint: str
    tier: str
    limits: Dict[str, int]
    current_usage: Dict[str, int]
    reset_times: Dict[str, int]

class RateLimitResponse(BaseModel):
    allowed: bool
    status: RequestStatus
    rate_limit_info: Optional[RateLimitInfo] = None
    error: Optional[str] = None
    retry_after: Optional[int] = None

# ===== MODÈLES DE STATISTIQUES =====

class APIUsageStats(BaseModel):
    total_requests: int
    successful_requests: int
    failed_requests: int
    rate_limited_requests: int

class TierStats(BaseModel):
    count: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    rate_limited_requests: int

class APIUsageOverview(BaseModel):
    total_keys: int
    active_keys: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    rate_limited_requests: int

class APIUsageStatsResponse(BaseModel):
    overview: APIUsageOverview
    by_tier: Dict[str, TierStats]
    top_api_keys: List[Dict[str, Any]]

class GatewayHealth(BaseModel):
    status: str
    current_time: datetime
    recent_requests_5min: int
    blocked_ips: int
    active_api_keys: int
    cache_size: int
    memory_usage: Dict[str, int]

class RateLimitViolation(BaseModel):
    identifier: str
    endpoint: str
    violation_time: datetime
    limit_type: RateLimitType
    limit_value: int
    actual_usage: int

# ===== MODÈLES DE CONFIGURATION =====

class GatewayConfig(BaseModel):
    enabled: bool = True
    default_tier: APITier = APITier.FREE
    auto_block_threshold: int = 100
    cache_cleanup_interval: int = 300  # 5 minutes
    log_all_requests: bool = True

class EndpointConfig(BaseModel):
    path: str
    methods: List[str]
    rate_limits: RateLimitConfig
    requires_auth: bool = True
    bypass_rate_limit: bool = False

class ServiceConfig(BaseModel):
    name: str
    base_url: str
    health_check_path: str = "/health"
    timeout: int = 30
    retry_count: int = 3

# ===== MODÈLES DE MONITORING =====

class RequestLog(BaseModel):
    request_id: str
    api_key: Optional[str] = None
    ip_address: str
    endpoint: str
    method: str
    status_code: int
    response_time: float
    timestamp: datetime
    user_agent: Optional[str] = None
    rate_limited: bool = False

class AlertConfig(BaseModel):
    enabled: bool = True
    threshold_exceeded_alert: bool = True
    unusual_traffic_alert: bool = True
    security_threat_alert: bool = True
    email_notifications: bool = False
    webhook_url: Optional[str] = None

class SecurityMetrics(BaseModel):
    blocked_ips_count: int
    rate_limit_violations_24h: int
    suspicious_patterns_detected: int
    brute_force_attempts: int
    last_security_scan: datetime

# ===== MODÈLES DE RÉPONSE =====

class StandardResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(BaseModel):
    error: str
    error_code: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PaginatedResponse(BaseModel):
    items: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_prev: bool

# ===== MODÈLES DE LOAD BALANCING =====

class BackendService(BaseModel):
    id: str
    name: str
    url: str
    weight: int = 100
    health_status: str = "unknown"
    last_health_check: Optional[datetime] = None
    response_time: Optional[float] = None

class LoadBalancerConfig(BaseModel):
    strategy: str = "round_robin"  # round_robin, weighted, least_connections
    health_check_interval: int = 30
    failure_threshold: int = 3
    recovery_threshold: int = 2

class HealthCheckResult(BaseModel):
    service_id: str
    is_healthy: bool
    response_time: float
    status_code: Optional[int] = None
    error: Optional[str] = None
    checked_at: datetime = Field(default_factory=datetime.utcnow)

# ===== MODÈLES DE CACHE =====

class CacheConfig(BaseModel):
    enabled: bool = True
    default_ttl: int = 300  # 5 minutes
    max_entries: int = 10000
    cleanup_interval: int = 600  # 10 minutes

class CacheEntry(BaseModel):
    key: str
    value: Any
    created_at: datetime
    expires_at: datetime
    hit_count: int = 0
    last_accessed: datetime

class CacheStats(BaseModel):
    total_entries: int
    hit_rate: float
    miss_rate: float
    memory_usage_mb: float
    oldest_entry: Optional[datetime] = None
    newest_entry: Optional[datetime] = None
from fastapi import FastAPI, APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(
    title="QuantumShield API",
    description="Cryptographie post-quantique pour l'IoT",
    version="1.0.0"
)

# Create API router
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()

# Initialize services
from services.ntru_service import NTRUService
from services.blockchain_service import BlockchainService
from services.device_service import DeviceService
from services.token_service import TokenService
from services.auth_service import AuthService
from services.mining_service import MiningService
from services.advanced_crypto_service import AdvancedCryptoService
from services.security_service import SecurityService
from services.ai_analytics_service import AIAnalyticsService
from services.advanced_economy_service import AdvancedEconomyService
from services.iot_protocol_service import IoTProtocolService
from services.ota_update_service import OTAUpdateService
from services.geolocation_service import GeolocationService
from services.x509_service import X509Service
from services.marketplace_service import MarketplaceService

ntru_service = NTRUService()
blockchain_service = BlockchainService(db)
device_service = DeviceService(db)
token_service = TokenService(db)
auth_service = AuthService(db)
mining_service = MiningService(db, blockchain_service)
advanced_crypto_service = AdvancedCryptoService(db)
security_service = SecurityService(db)
ai_analytics_service = AIAnalyticsService(db)
advanced_economy_service = AdvancedEconomyService(db)
iot_protocol_service = IoTProtocolService(db)
ota_update_service = OTAUpdateService(db)
geolocation_service = GeolocationService(db)
x509_service = X509Service(db)
marketplace_service = MarketplaceService(db)

# Include routers
from routes.auth_routes import router as auth_router
from routes.crypto_routes import router as crypto_router
from routes.advanced_crypto_routes import router as advanced_crypto_router
from routes.blockchain_routes import router as blockchain_router
from routes.device_routes import router as device_router
from routes.token_routes import router as token_router
from routes.mining_routes import router as mining_router
from routes.security_routes import router as security_router
from routes.ai_analytics_routes import router as ai_analytics_router
from routes.advanced_economy_routes import router as advanced_economy_router
from routes.iot_protocol_routes import router as iot_protocol_router
from routes.ota_routes import router as ota_router
from routes.dashboard_routes import router as dashboard_router

# Inject services into routes
import routes.iot_protocol_routes
import routes.ota_routes
routes.iot_protocol_routes.iot_protocol_service = iot_protocol_service
routes.ota_routes.ota_service = ota_update_service

api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(crypto_router, prefix="/crypto", tags=["cryptography"])
api_router.include_router(advanced_crypto_router, prefix="/advanced-crypto", tags=["advanced-cryptography"])
api_router.include_router(blockchain_router, prefix="/blockchain", tags=["blockchain"])
api_router.include_router(device_router, prefix="/devices", tags=["devices"])
api_router.include_router(token_router, prefix="/tokens", tags=["tokens"])
api_router.include_router(mining_router, prefix="/mining", tags=["mining"])
api_router.include_router(security_router, prefix="/security", tags=["security"])
api_router.include_router(ai_analytics_router, prefix="/ai-analytics", tags=["ai-analytics"])
api_router.include_router(advanced_economy_router, prefix="/advanced-economy", tags=["advanced-economy"])
api_router.include_router(iot_protocol_router, prefix="/iot-protocol", tags=["iot-protocol"])
api_router.include_router(ota_router, prefix="/ota", tags=["ota-updates"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])

# Health check endpoint
@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "services": {
            "ntru": ntru_service.is_ready(),
            "blockchain": await blockchain_service.is_ready(),
            "advanced_crypto": advanced_crypto_service.is_ready(),
            "security": security_service.is_ready(),
            "ai_analytics": ai_analytics_service.is_ready(),
            "advanced_economy": advanced_economy_service.is_ready(),
            "iot_protocol": iot_protocol_service.is_ready(),
            "ota_update": ota_update_service.is_ready(),
            "database": True
        }
    }

# Include the router in the main app
app.include_router(api_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting QuantumShield API...")
    # Initialize token system
    await token_service.initialize_token_system()
    # Initialize blockchain if needed
    await blockchain_service.initialize_genesis_block()
    # Start mining process
    asyncio.create_task(mining_service.start_mining())

@app.on_event("shutdown")
async def shutdown_db_client():
    await mining_service.stop_mining()
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
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

# Import custom modules
from models.quantum_models import *
from services.ntru_service import NTRUService
from services.blockchain_service import BlockchainService
from services.device_service import DeviceService
from services.token_service import TokenService
from services.auth_service import AuthService
from services.mining_service import MiningService
from routes.auth_routes import auth_router
from routes.crypto_routes import crypto_router
from routes.blockchain_routes import blockchain_router
from routes.device_routes import device_router
from routes.token_routes import token_router
from routes.mining_routes import mining_router
from routes.dashboard_routes import dashboard_router

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
ntru_service = NTRUService()
blockchain_service = BlockchainService(db)
device_service = DeviceService(db)
token_service = TokenService(db)
auth_service = AuthService(db)
mining_service = MiningService(db, blockchain_service)

# Include routers
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(crypto_router, prefix="/crypto", tags=["cryptography"])
api_router.include_router(blockchain_router, prefix="/blockchain", tags=["blockchain"])
api_router.include_router(device_router, prefix="/devices", tags=["devices"])
api_router.include_router(token_router, prefix="/tokens", tags=["tokens"])
api_router.include_router(mining_router, prefix="/mining", tags=["mining"])
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
    # Initialize blockchain if needed
    await blockchain_service.initialize_genesis_block()
    # Start mining process
    asyncio.create_task(mining_service.start_mining())

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
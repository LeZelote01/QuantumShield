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
from services.advanced_blockchain_service import AdvancedBlockchainService
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
from services.hsm_service import HSMService
from services.graphql_service import GraphQLService
from services.webhook_service import WebhookService
from services.personalized_recommendations_service import PersonalizedRecommendationsService
from services.personalizable_dashboard_service import PersonalizableDashboardService
from services.cloud_integrations_service import CloudIntegrationsService
from services.erp_crm_connectors_service import ERPCRMConnectorsService
from services.compliance_service import ComplianceService
from services.api_gateway_service import APIGatewayService

ntru_service = NTRUService()
blockchain_service = BlockchainService(db)
advanced_blockchain_service = AdvancedBlockchainService(db, blockchain_service)
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
hsm_service = HSMService(db)
personalized_recommendations_service = PersonalizedRecommendationsService(db)
personalizable_dashboard_service = PersonalizableDashboardService(db)
cloud_integrations_service = CloudIntegrationsService(db)
erp_crm_service = ERPCRMConnectorsService(db)
compliance_service = ComplianceService(db)
api_gateway_service = APIGatewayService(db)

# Initialiser les nouveaux services
services_dict = {
    'device_service': device_service,
    'blockchain_service': blockchain_service,
    'marketplace_service': marketplace_service,
    'advanced_economy_service': advanced_economy_service,
    'ai_analytics_service': ai_analytics_service,
    'x509_service': x509_service,
    'auth_service': auth_service
}

webhook_service = WebhookService(db)

# Include routers
from routes.auth_routes import router as auth_router
from routes.crypto_routes import router as crypto_router
from routes.advanced_crypto_routes import router as advanced_crypto_router
from routes.blockchain_routes import router as blockchain_router
from routes.advanced_blockchain_routes import router as advanced_blockchain_router
from routes.device_routes import router as device_router
from routes.token_routes import router as token_router
from routes.mining_routes import router as mining_router
from routes.security_routes import router as security_router
from routes.ai_analytics_routes import router as ai_analytics_router
from routes.advanced_economy_routes import router as advanced_economy_router
from routes.iot_protocol_routes import router as iot_protocol_router
from routes.ota_routes import router as ota_router
from routes.geolocation_routes import router as geolocation_router
from routes.x509_routes import router as x509_router
from routes.marketplace_routes import router as marketplace_router
from routes.dashboard_routes import router as dashboard_router
from routes.hsm_routes import router as hsm_router
from routes.graphql_routes import router as graphql_router
from routes.webhook_routes import router as webhook_router
from routes.personalized_recommendations_routes import router as personalized_recommendations_router
from routes.personalizable_dashboard_routes import router as personalizable_dashboard_router
from routes.api_gateway_routes import router as api_gateway_router
from routes.cloud_integrations_routes import router as cloud_integrations_router
from routes.erp_crm_routes import router as erp_crm_router
from routes.compliance_routes import router as compliance_router

# Inject services into routes
import routes.iot_protocol_routes
import routes.ota_routes
import routes.geolocation_routes
import routes.x509_routes
import routes.marketplace_routes
import routes.graphql_routes
import routes.webhook_routes
import routes.personalized_recommendations_routes
import routes.personalizable_dashboard_routes
import routes.cloud_integrations_routes
import routes.erp_crm_routes
import routes.compliance_routes
import routes.api_gateway_routes
routes.iot_protocol_routes.iot_protocol_service = iot_protocol_service
routes.ota_routes.ota_service = ota_update_service
routes.geolocation_routes.geolocation_service = geolocation_service
routes.x509_routes.x509_service = x509_service
routes.marketplace_routes.marketplace_service = marketplace_service
routes.graphql_routes.init_graphql_service(db, services_dict)
routes.webhook_routes.init_webhook_service(db)
routes.personalized_recommendations_routes.init_recommendations_service(personalized_recommendations_service)
routes.personalizable_dashboard_routes.init_dashboard_service(personalizable_dashboard_service)
routes.cloud_integrations_routes.init_cloud_integrations_service(cloud_integrations_service)
routes.erp_crm_routes.init_erp_crm_service(erp_crm_service)
routes.api_gateway_routes.init_api_gateway_service(api_gateway_service)

api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(crypto_router, prefix="/crypto", tags=["cryptography"])
api_router.include_router(advanced_crypto_router, prefix="/advanced-crypto", tags=["advanced-cryptography"])
api_router.include_router(blockchain_router, prefix="/blockchain", tags=["blockchain"])
api_router.include_router(advanced_blockchain_router, prefix="/advanced-blockchain", tags=["advanced-blockchain"])
api_router.include_router(device_router, prefix="/devices", tags=["devices"])
api_router.include_router(token_router, prefix="/tokens", tags=["tokens"])
api_router.include_router(mining_router, prefix="/mining", tags=["mining"])
api_router.include_router(security_router, prefix="/security", tags=["security"])
api_router.include_router(ai_analytics_router, prefix="/ai-analytics", tags=["ai-analytics"])
api_router.include_router(advanced_economy_router, prefix="/advanced-economy", tags=["advanced-economy"])
api_router.include_router(iot_protocol_router, prefix="/iot-protocol", tags=["iot-protocol"])
api_router.include_router(ota_router, prefix="/ota", tags=["ota-updates"])
api_router.include_router(geolocation_router, prefix="/geolocation", tags=["geolocation"])
api_router.include_router(x509_router, prefix="/x509", tags=["x509-certificates"])
api_router.include_router(marketplace_router, prefix="/marketplace", tags=["marketplace"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(hsm_router, prefix="/hsm", tags=["hsm"])
api_router.include_router(graphql_router, tags=["graphql"])
api_router.include_router(webhook_router, tags=["webhooks"])
api_router.include_router(personalized_recommendations_router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(personalizable_dashboard_router, prefix="/custom-dashboards", tags=["custom-dashboards"])
api_router.include_router(cloud_integrations_router, prefix="/cloud-integrations", tags=["cloud-integrations"])
api_router.include_router(erp_crm_router, prefix="/erp-crm", tags=["erp-crm"])
api_router.include_router(compliance_router, prefix="/compliance", tags=["compliance"])
api_router.include_router(api_gateway_router, prefix="/api-gateway", tags=["api-gateway"])

# Health check endpoint
@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "services": {
            "ntru": ntru_service.is_ready(),
            "blockchain": await blockchain_service.is_ready(),
            "advanced_blockchain": await advanced_blockchain_service.is_ready(),
            "advanced_crypto": advanced_crypto_service.is_ready(),
            "security": security_service.is_ready(),
            "ai_analytics": ai_analytics_service.is_ready(),
            "advanced_economy": advanced_economy_service.is_ready(),
            "iot_protocol": iot_protocol_service.is_ready(),
            "ota_update": ota_update_service.is_ready(),
            "geolocation": geolocation_service.is_ready(),
            "x509": x509_service.is_ready(),
            "marketplace": marketplace_service.is_ready(),
            "hsm": hsm_service.is_ready(),
            "webhook": webhook_service.is_ready(),
            "recommendations": personalized_recommendations_service.is_ready(),
            "custom_dashboards": personalizable_dashboard_service.is_ready(),
            "api_gateway": api_gateway_service.is_ready(),
            "database": True
        }
    }

# Include the router in the main app
app.include_router(api_router)

# Configure API Gateway middleware
from middleware.api_gateway_middleware import setup_api_gateway_middleware
setup_api_gateway_middleware(app, api_gateway_service)

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
    # Initialize advanced blockchain service
    await advanced_blockchain_service.initialize()
    # Start mining process
    asyncio.create_task(mining_service.start_mining())

@app.on_event("shutdown")
async def shutdown_db_client():
    await mining_service.stop_mining()
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
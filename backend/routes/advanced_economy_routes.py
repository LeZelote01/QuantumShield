"""
Routes pour l'économie avancée
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

from routes.auth_routes import get_current_user
from services.advanced_economy_service import AdvancedEconomyService, ServiceType, StakingType, InsuranceType, AssetType

router = APIRouter()

# ===== MODÈLES DE REQUÊTE =====

# Marketplace
class ServiceListingRequest(BaseModel):
    service_type: ServiceType
    title: str
    description: str
    price: float
    currency: str = "QS"
    duration: str = "1 hour"
    max_clients: int = 1
    tags: List[str] = []
    requirements: List[str] = []
    deliverables: List[str] = []

class ServiceSearchRequest(BaseModel):
    query: Optional[str] = None
    service_type: Optional[ServiceType] = None
    max_price: Optional[float] = None
    min_rating: Optional[float] = None

class ServicePurchaseRequest(BaseModel):
    service_id: str
    custom_requirements: Optional[str] = None

# Staking
class StakingPoolRequest(BaseModel):
    name: str
    staking_type: StakingType
    min_stake: float = 100
    max_stake: float = 10000

class StakeTokensRequest(BaseModel):
    pool_id: str
    amount: float

class UnstakeTokensRequest(BaseModel):
    stake_id: str

# Loans
class LoanRequest(BaseModel):
    amount: float
    interest_rate: float
    duration_days: int
    collateral_amount: float
    collateral_type: str = "QS"
    purpose: str = ""

class FundLoanRequest(BaseModel):
    loan_id: str
    amount: float

# Insurance
class InsurancePoolRequest(BaseModel):
    name: str
    insurance_type: InsuranceType
    coverage_amount: float
    premium_rate: float
    minimum_pool_size: float = 10000

class InsurancePurchaseRequest(BaseModel):
    pool_id: str
    coverage_amount: float
    duration_days: int = 365

# Tokenization
class TokenizeAssetRequest(BaseModel):
    asset_type: AssetType
    name: str
    description: str
    total_value: float
    total_tokens: int
    documents: List[str] = []

class BuyAssetTokensRequest(BaseModel):
    asset_id: str
    token_count: int

# ===== ROUTES MARKETPLACE =====

@router.post("/marketplace/services/create")
async def create_service_listing(
    request: ServiceListingRequest,
    current_user = Depends(get_current_user)
):
    """Crée une offre de service"""
    from server import advanced_economy_service
    
    try:
        service_data = request.dict()
        result = await advanced_economy_service.create_service_listing(
            provider_id=current_user["id"],
            service_data=service_data
        )
        
        return {
            "service_listing": result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur création service: {str(e)}"
        )

@router.post("/marketplace/services/search")
async def search_services(request: ServiceSearchRequest):
    """Recherche des services"""
    from server import advanced_economy_service
    
    try:
        services = await advanced_economy_service.search_services(
            query=request.query,
            service_type=request.service_type,
            max_price=request.max_price,
            min_rating=request.min_rating
        )
        
        return {
            "services": services,
            "total_results": len(services),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur recherche services: {str(e)}"
        )

@router.post("/marketplace/services/purchase")
async def purchase_service(
    request: ServicePurchaseRequest,
    current_user = Depends(get_current_user)
):
    """Achète un service"""
    from server import advanced_economy_service
    
    try:
        result = await advanced_economy_service.purchase_service(
            buyer_id=current_user["id"],
            service_id=request.service_id,
            custom_requirements=request.custom_requirements
        )
        
        return {
            "purchase": result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur achat service: {str(e)}"
        )

# ===== ROUTES STAKING =====

@router.post("/staking/pools/create")
async def create_staking_pool(
    request: StakingPoolRequest,
    current_user = Depends(get_current_user)
):
    """Crée un pool de staking"""
    from server import advanced_economy_service
    
    try:
        pool_data = request.dict()
        result = await advanced_economy_service.create_staking_pool(pool_data)
        
        return {
            "staking_pool": result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur création pool staking: {str(e)}"
        )

@router.post("/staking/stake")
async def stake_tokens(
    request: StakeTokensRequest,
    current_user = Depends(get_current_user)
):
    """Mise en stake de tokens"""
    from server import advanced_economy_service
    
    try:
        result = await advanced_economy_service.stake_tokens(
            user_id=current_user["id"],
            pool_id=request.pool_id,
            amount=request.amount
        )
        
        return {
            "stake": result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur staking: {str(e)}"
        )

@router.post("/staking/unstake")
async def unstake_tokens(
    request: UnstakeTokensRequest,
    current_user = Depends(get_current_user)
):
    """Retire les tokens du staking"""
    from server import advanced_economy_service
    
    try:
        result = await advanced_economy_service.unstake_tokens(
            user_id=current_user["id"],
            stake_id=request.stake_id
        )
        
        return {
            "unstake": result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur unstaking: {str(e)}"
        )

@router.get("/staking/dashboard")
async def get_staking_dashboard(current_user = Depends(get_current_user)):
    """Tableau de bord staking"""
    from server import advanced_economy_service
    
    try:
        dashboard = await advanced_economy_service.get_staking_dashboard(current_user["id"])
        
        return {
            "dashboard": dashboard,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur dashboard staking: {str(e)}"
        )

# ===== ROUTES LOANS =====

@router.post("/loans/create")
async def create_loan_request(
    request: LoanRequest,
    current_user = Depends(get_current_user)
):
    """Crée une demande de prêt"""
    from server import advanced_economy_service
    
    try:
        loan_data = request.dict()
        result = await advanced_economy_service.create_loan_request(
            borrower_id=current_user["id"],
            loan_data=loan_data
        )
        
        return {
            "loan_request": result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur création prêt: {str(e)}"
        )

@router.post("/loans/fund")
async def fund_loan(
    request: FundLoanRequest,
    current_user = Depends(get_current_user)
):
    """Finance un prêt"""
    from server import advanced_economy_service
    
    try:
        result = await advanced_economy_service.fund_loan(
            lender_id=current_user["id"],
            loan_id=request.loan_id,
            amount=request.amount
        )
        
        return {
            "funding": result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur financement prêt: {str(e)}"
        )

# ===== ROUTES INSURANCE =====

@router.post("/insurance/pools/create")
async def create_insurance_pool(
    request: InsurancePoolRequest,
    current_user = Depends(get_current_user)
):
    """Crée un pool d'assurance"""
    from server import advanced_economy_service
    
    try:
        pool_data = request.dict()
        result = await advanced_economy_service.create_insurance_pool(pool_data)
        
        return {
            "insurance_pool": result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur création pool assurance: {str(e)}"
        )

@router.post("/insurance/purchase")
async def purchase_insurance(
    request: InsurancePurchaseRequest,
    current_user = Depends(get_current_user)
):
    """Achète une assurance"""
    from server import advanced_economy_service
    
    try:
        coverage_data = request.dict()
        result = await advanced_economy_service.purchase_insurance(
            user_id=current_user["id"],
            pool_id=request.pool_id,
            coverage_data=coverage_data
        )
        
        return {
            "insurance_policy": result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur achat assurance: {str(e)}"
        )

# ===== ROUTES TOKENIZATION =====

@router.post("/tokenization/assets/create")
async def tokenize_asset(
    request: TokenizeAssetRequest,
    current_user = Depends(get_current_user)
):
    """Tokenise un actif"""
    from server import advanced_economy_service
    
    try:
        asset_data = request.dict()
        result = await advanced_economy_service.tokenize_asset(
            owner_id=current_user["id"],
            asset_data=asset_data
        )
        
        return {
            "tokenized_asset": result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur tokenisation actif: {str(e)}"
        )

@router.post("/tokenization/assets/buy")
async def buy_asset_tokens(
    request: BuyAssetTokensRequest,
    current_user = Depends(get_current_user)
):
    """Achète des tokens d'actif"""
    from server import advanced_economy_service
    
    try:
        result = await advanced_economy_service.buy_asset_tokens(
            buyer_id=current_user["id"],
            asset_id=request.asset_id,
            token_count=request.token_count
        )
        
        return {
            "asset_purchase": result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur achat tokens: {str(e)}"
        )

@router.get("/tokenization/assets")
async def get_tokenized_assets():
    """Récupère tous les actifs tokenisés"""
    from server import advanced_economy_service
    
    try:
        assets = await advanced_economy_service.db.tokenized_assets.find({"active": True}).to_list(None)
        
        total_value = sum(asset["total_value"] for asset in assets)
        available_tokens = sum(asset["total_tokens"] - asset["tokens_sold"] for asset in assets)
        
        return {
            "tokenized_assets": assets,
            "total_value": total_value,
            "available_tokens": available_tokens,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération actifs: {str(e)}"
        )

@router.get("/tokenization/ownerships/{user_id}")
async def get_asset_ownerships(
    user_id: str,
    current_user = Depends(get_current_user)
):
    """Récupère les propriétés d'actifs d'un utilisateur"""
    from server import advanced_economy_service
    
    try:
        # Vérifier que l'utilisateur peut voir ces propriétés
        if current_user["id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé"
            )
        
        ownerships = await advanced_economy_service.db.asset_ownerships.find({"buyer_id": user_id}).to_list(None)
        
        # Enrichir avec les informations des actifs
        enriched_ownerships = []
        for ownership in ownerships:
            asset = await advanced_economy_service.db.tokenized_assets.find_one({"id": ownership["asset_id"]})
            if asset:
                enriched_ownership = {
                    "id": ownership["id"],
                    "asset_id": ownership["asset_id"],
                    "asset_name": asset["name"],
                    "token_count": ownership["token_count"],
                    "purchase_price": ownership["purchase_price"],
                    "current_price": asset["token_price"],
                    "ownership_percentage": (ownership["token_count"] / asset["total_tokens"]) * 100,
                    "dividends_received": ownership.get("dividends_received", 0),
                    "purchase_date": ownership["purchase_date"]
                }
                enriched_ownerships.append(enriched_ownership)
        
        return {
            "ownerships": enriched_ownerships,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération propriétés: {str(e)}"
        )

# ===== ROUTES DASHBOARD =====

@router.get("/dashboard")
async def get_economy_dashboard(current_user = Depends(get_current_user)):
    """Tableau de bord économique"""
    from server import advanced_economy_service
    
    try:
        dashboard = await advanced_economy_service.get_economy_dashboard()
        
        return {
            "dashboard": dashboard,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur dashboard économique: {str(e)}"
        )

@router.get("/health")
async def economy_health_check():
    """Vérification de santé du service économique"""
    from server import advanced_economy_service
    
    try:
        return {
            "service_ready": advanced_economy_service.is_ready(),
            "marketplace_fee": advanced_economy_service.marketplace_fee * 100,
            "staking_pools_available": len(advanced_economy_service.staking_rewards),
            "timestamp": datetime.utcnow(),
            "status": "healthy"
        }
        
    except Exception as e:
        return {
            "service_ready": False,
            "error": str(e),
            "timestamp": datetime.utcnow(),
            "status": "unhealthy"
        }

# ===== ROUTES UTILITAIRES =====

@router.get("/staking/pools")
async def get_staking_pools():
    """Récupère les pools de staking disponibles"""
    from server import advanced_economy_service
    
    try:
        pools = await advanced_economy_service.db.staking_pools.find({"active": True}).to_list(None)
        
        return {
            "pools": pools,
            "staking_rewards": {
                pool_type.value: apy * 100 
                for pool_type, apy in advanced_economy_service.staking_rewards.items()
            },
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération pools: {str(e)}"
        )

@router.get("/marketplace/stats")
async def get_marketplace_stats():
    """Statistiques de la marketplace"""
    from server import advanced_economy_service
    
    try:
        # Récupérer les statistiques
        total_services = await advanced_economy_service.db.service_listings.count_documents({})
        active_services = await advanced_economy_service.db.service_listings.count_documents({"status": "active"})
        total_orders = await advanced_economy_service.db.service_orders.count_documents({})
        
        # Statistiques par type de service
        service_stats = await advanced_economy_service.db.service_listings.aggregate([
            {"$group": {"_id": "$service_type", "count": {"$sum": 1}}}
        ]).to_list(None)
        
        return {
            "marketplace_stats": {
                "total_services": total_services,
                "active_services": active_services,
                "total_orders": total_orders,
                "marketplace_fee": advanced_economy_service.marketplace_fee * 100,
                "service_types": {stat["_id"]: stat["count"] for stat in service_stats}
            },
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur statistiques marketplace: {str(e)}"
        )

@router.get("/recommendations")
async def get_economy_recommendations(current_user = Depends(get_current_user)):
    """Recommandations économiques personnalisées"""
    from server import advanced_economy_service
    
    try:
        user = await advanced_economy_service.db.users.find_one({"id": current_user["id"]})
        balance = user.get("qs_balance", 0) if user else 0
        
        recommendations = []
        
        # Recommandations basées sur le solde
        if balance > 1000:
            recommendations.append({
                "type": "staking",
                "priority": "high",
                "title": "Staking de tokens recommandé",
                "description": f"Avec {balance} QS, vous pourriez gagner jusqu'à 25% APY",
                "action": "explore_staking"
            })
        
        if balance > 500:
            recommendations.append({
                "type": "marketplace",
                "priority": "medium",
                "title": "Créer une offre de service",
                "description": "Monétisez vos compétences sur la marketplace",
                "action": "create_service"
            })
        
        if balance > 100:
            recommendations.append({
                "type": "insurance",
                "priority": "low",
                "title": "Protéger vos actifs",
                "description": "Souscrire une assurance décentralisée",
                "action": "explore_insurance"
            })
        
        recommendations.append({
            "type": "tokenization",
            "priority": "low",
            "title": "Tokeniser des actifs",
            "description": "Transformer vos actifs physiques en tokens",
            "action": "explore_tokenization"
        })
        
        return {
            "recommendations": recommendations,
            "user_balance": balance,
            "generated_at": datetime.utcnow(),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur recommandations: {str(e)}"
        )
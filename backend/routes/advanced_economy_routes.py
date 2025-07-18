"""
Routes pour l'économie avancée
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

from routes.auth_routes import get_current_user
from services.advanced_economy_service import AdvancedEconomyService, ServiceType, StakingType, InsuranceType, AssetType, ProposalType, VoteOption

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

# Governance
class ProposalRequest(BaseModel):
    proposal_type: ProposalType
    title: str
    description: str
    voting_power_required: float = 0.1
    execution_delay_hours: int = 24
    voting_duration_hours: int = 168
    parameters: Dict[str, Any] = {}

class VoteRequest(BaseModel):
    proposal_id: str
    vote_option: VoteOption
    voting_power: Optional[float] = None

class ExecuteProposalRequest(BaseModel):
    proposal_id: str

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

# ===== ROUTES GOVERNANCE =====

@router.post("/governance/proposals/create")
async def create_proposal(
    request: ProposalRequest,
    current_user = Depends(get_current_user)
):
    """Crée une proposition de gouvernance"""
    from server import advanced_economy_service
    
    try:
        result = await advanced_economy_service.create_proposal(
            proposer_id=current_user["user_id"],
            proposal_data=request.dict()
        )
        return result
    except Exception as e:
        logger.error(f"Erreur création proposition: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur création proposition: {str(e)}"
        )

@router.post("/governance/proposals/vote")
async def vote_on_proposal(
    request: VoteRequest,
    current_user = Depends(get_current_user)
):
    """Vote sur une proposition"""
    from server import advanced_economy_service
    
    try:
        result = await advanced_economy_service.vote_on_proposal(
            voter_id=current_user["user_id"],
            proposal_id=request.proposal_id,
            vote_option=request.vote_option,
            voting_power=request.voting_power
        )
        return result
    except Exception as e:
        logger.error(f"Erreur vote proposition: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur vote proposition: {str(e)}"
        )

@router.post("/governance/proposals/execute")
async def execute_proposal(
    request: ExecuteProposalRequest,
    current_user = Depends(get_current_user)
):
    """Exécute une proposition approuvée"""
    from server import advanced_economy_service
    
    try:
        result = await advanced_economy_service.execute_proposal(
            proposal_id=request.proposal_id,
            executor_id=current_user["user_id"]
        )
        return result
    except Exception as e:
        logger.error(f"Erreur exécution proposition: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur exécution proposition: {str(e)}"
        )

@router.get("/governance/proposals")
async def get_proposals(
    status: Optional[str] = Query(None, description="Statut des propositions"),
    current_user = Depends(get_current_user)
):
    """Liste les propositions de gouvernance"""
    from server import advanced_economy_service
    
    try:
        proposals = await advanced_economy_service.get_proposals(status=status)
        return {"proposals": proposals}
    except Exception as e:
        logger.error(f"Erreur récupération propositions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur récupération propositions: {str(e)}"
        )

@router.get("/governance/proposals/{proposal_id}")
async def get_proposal(
    proposal_id: str,
    current_user = Depends(get_current_user)
):
    """Récupère une proposition spécifique"""
    from server import advanced_economy_service
    
    try:
        proposal = await advanced_economy_service.get_proposal(proposal_id=proposal_id)
        return proposal
    except Exception as e:
        logger.error(f"Erreur récupération proposition: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur récupération proposition: {str(e)}"
        )

@router.get("/governance/dashboard")
async def get_governance_dashboard(current_user = Depends(get_current_user)):
    """Dashboard de gouvernance"""
    from server import advanced_economy_service
    
    try:
        dashboard = await advanced_economy_service.get_governance_dashboard()
        return dashboard
    except Exception as e:
        logger.error(f"Erreur dashboard gouvernance: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur dashboard gouvernance: {str(e)}"
        )

@router.get("/governance/user/{user_id}/voting-power")
async def get_user_voting_power(
    user_id: str,
    current_user = Depends(get_current_user)
):
    """Calcule le pouvoir de vote d'un utilisateur"""
    from server import advanced_economy_service
    
    try:
        voting_power = await advanced_economy_service.calculate_voting_power(user_id=user_id)
        return {"user_id": user_id, "voting_power": voting_power}
    except Exception as e:
        logger.error(f"Erreur calcul pouvoir vote: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur calcul pouvoir vote: {str(e)}"
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
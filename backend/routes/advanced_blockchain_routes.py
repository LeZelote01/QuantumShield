"""
Routes pour les fonctionnalités avancées de la blockchain
Smart contracts, gouvernance, consensus hybride, interopérabilité
"""

from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from models.blockchain_models import (
    SmartContract, SmartContractExecution, SmartContractTemplate,
    GovernanceProposal, Vote, VotingPower, ProposalStatus, VoteType,
    Validator, StakePool, CrossChainBridge, CrossChainTransaction,
    BlockchainMetrics, NetworkHealth, CompressedBlock, ArchivePeriod,
    CreateSmartContractRequest, ExecuteSmartContractRequest,
    CreateProposalRequest, VoteRequest, StakeRequest, BridgeTransferRequest,
    ConsensusType, BlockchainNetwork, CompressionAlgorithm
)
from routes.auth_routes import get_current_user
from models.quantum_models import User

router = APIRouter()

# === HEALTH CHECK ===

@router.get("/health")
async def advanced_blockchain_health():
    """Health check pour le service blockchain avancé"""
    from server import advanced_blockchain_service
    
    try:
        is_ready = await advanced_blockchain_service.is_ready()
        
        return {
            "status": "healthy" if is_ready else "degraded",
            "service": "advanced_blockchain",
            "ready": is_ready,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        return {
            "status": "error",
            "service": "advanced_blockchain", 
            "ready": False,
            "error": str(e),
            "timestamp": datetime.utcnow()
        }

# === SMART CONTRACTS ===

@router.get("/smart-contracts", response_model=List[SmartContract])
async def get_smart_contracts(
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Récupère la liste des smart contracts"""
    from server import advanced_blockchain_service
    
    try:
        query = {}
        if status:
            query["status"] = status
        
        cursor = advanced_blockchain_service.smart_contracts.find(query).skip(offset).limit(limit)
        contracts_data = await cursor.to_list(length=limit)
        
        contracts = []
        for contract_data in contracts_data:
            contracts.append(SmartContract(**contract_data))
        
        return contracts
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des contrats: {str(e)}"
        )

@router.post("/smart-contracts", response_model=SmartContract)
async def deploy_smart_contract(
    contract_data: CreateSmartContractRequest,
    current_user: User = Depends(get_current_user)
):
    """Déploie un nouveau smart contract"""
    from server import advanced_blockchain_service
    
    try:
        contract = await advanced_blockchain_service.deploy_smart_contract(
            user_address=current_user.wallet_address,
            contract_data=contract_data.dict()
        )
        
        return contract
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors du déploiement: {str(e)}"
        )

@router.get("/smart-contracts/{contract_id}", response_model=SmartContract)
async def get_smart_contract(
    contract_id: str,
    current_user: User = Depends(get_current_user)
):
    """Récupère un smart contract spécifique"""
    from server import advanced_blockchain_service
    
    try:
        contract_data = await advanced_blockchain_service.smart_contracts.find_one({"id": contract_id})
        
        if not contract_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contrat {contract_id} non trouvé"
            )
        
        return SmartContract(**contract_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération du contrat: {str(e)}"
        )

@router.post("/smart-contracts/{contract_id}/execute", response_model=SmartContractExecution)
async def execute_smart_contract(
    contract_id: str,
    execution_data: ExecuteSmartContractRequest,
    current_user: User = Depends(get_current_user)
):
    """Exécute une fonction d'un smart contract"""
    from server import advanced_blockchain_service
    
    try:
        execution = await advanced_blockchain_service.execute_smart_contract(
            contract_id=contract_id,
            function_name=execution_data.function_name,
            parameters=execution_data.parameters,
            caller_address=current_user.wallet_address
        )
        
        return execution
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de l'exécution: {str(e)}"
        )

@router.get("/smart-contracts/{contract_id}/executions", response_model=List[SmartContractExecution])
async def get_contract_executions(
    contract_id: str,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """Récupère les exécutions d'un smart contract"""
    from server import advanced_blockchain_service
    
    try:
        cursor = advanced_blockchain_service.contract_executions.find(
            {"contract_id": contract_id}
        ).sort("executed_at", -1).limit(limit)
        
        executions_data = await cursor.to_list(length=limit)
        
        executions = []
        for execution_data in executions_data:
            executions.append(SmartContractExecution(**execution_data))
        
        return executions
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des exécutions: {str(e)}"
        )

@router.get("/smart-contracts/templates", response_model=List[SmartContractTemplate])
async def get_contract_templates(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Récupère les templates de smart contracts"""
    from server import advanced_blockchain_service
    
    try:
        query = {}
        if category:
            query["category"] = category
        
        cursor = advanced_blockchain_service.contract_templates.find(query)
        templates_data = await cursor.to_list(length=None)
        
        templates = []
        for template_data in templates_data:
            templates.append(SmartContractTemplate(**template_data))
        
        return templates
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des templates: {str(e)}"
        )

# === GOUVERNANCE ===

@router.get("/governance/proposals", response_model=List[GovernanceProposal])
async def get_governance_proposals(
    status_filter: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Récupère les propositions de gouvernance"""
    from server import advanced_blockchain_service
    
    try:
        query = {}
        if status_filter:
            query["status"] = status_filter
        
        cursor = advanced_blockchain_service.governance_proposals.find(query).sort("created_at", -1).limit(limit)
        proposals_data = await cursor.to_list(length=limit)
        
        proposals = []
        for proposal_data in proposals_data:
            proposals.append(GovernanceProposal(**proposal_data))
        
        return proposals
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des propositions: {str(e)}"
        )

@router.post("/governance/proposals", response_model=GovernanceProposal)
async def create_governance_proposal(
    proposal_data: CreateProposalRequest,
    current_user: User = Depends(get_current_user)
):
    """Crée une nouvelle proposition de gouvernance"""
    from server import advanced_blockchain_service
    
    try:
        proposal = await advanced_blockchain_service.create_proposal(
            proposer_address=current_user.wallet_address,
            proposal_data=proposal_data.dict()
        )
        
        return proposal
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de la création de la proposition: {str(e)}"
        )

@router.get("/governance/proposals/{proposal_id}", response_model=GovernanceProposal)
async def get_governance_proposal(
    proposal_id: str,
    current_user: User = Depends(get_current_user)
):
    """Récupère une proposition spécifique"""
    from server import advanced_blockchain_service
    
    try:
        proposal_data = await advanced_blockchain_service.governance_proposals.find_one({"id": proposal_id})
        
        if not proposal_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proposition {proposal_id} non trouvée"
            )
        
        return GovernanceProposal(**proposal_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération de la proposition: {str(e)}"
        )

@router.post("/governance/proposals/{proposal_id}/vote", response_model=Vote)
async def vote_on_proposal(
    proposal_id: str,
    vote_data: VoteRequest,
    current_user: User = Depends(get_current_user)
):
    """Vote sur une proposition de gouvernance"""
    from server import advanced_blockchain_service
    
    try:
        vote = await advanced_blockchain_service.vote_on_proposal(
            proposal_id=proposal_id,
            voter_address=current_user.wallet_address,
            vote_type=vote_data.vote_type,
            justification=vote_data.justification
        )
        
        return vote
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors du vote: {str(e)}"
        )

@router.get("/governance/proposals/{proposal_id}/votes", response_model=List[Vote])
async def get_proposal_votes(
    proposal_id: str,
    current_user: User = Depends(get_current_user)
):
    """Récupère les votes d'une proposition"""
    from server import advanced_blockchain_service
    
    try:
        cursor = advanced_blockchain_service.votes.find({"proposal_id": proposal_id}).sort("timestamp", -1)
        votes_data = await cursor.to_list(length=None)
        
        votes = []
        for vote_data in votes_data:
            votes.append(Vote(**vote_data))
        
        return votes
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des votes: {str(e)}"
        )

@router.post("/governance/proposals/{proposal_id}/execute")
async def execute_proposal(
    proposal_id: str,
    current_user: User = Depends(get_current_user)
):
    """Exécute une proposition approuvée"""
    from server import advanced_blockchain_service
    
    try:
        success = await advanced_blockchain_service.execute_proposal(proposal_id)
        
        if success:
            return {"message": "Proposition exécutée avec succès", "proposal_id": proposal_id}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Impossible d'exécuter la proposition"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de l'exécution: {str(e)}"
        )

@router.get("/governance/voting-power/{address}", response_model=VotingPower)
async def get_voting_power(
    address: str,
    current_user: User = Depends(get_current_user)
):
    """Récupère le pouvoir de vote d'une adresse"""
    from server import advanced_blockchain_service
    
    try:
        voting_power = await advanced_blockchain_service._calculate_voting_power(address)
        
        voting_power_data = await advanced_blockchain_service.voting_powers.find_one({"address": address})
        
        if voting_power_data:
            return VotingPower(**voting_power_data)
        else:
            return VotingPower(
                address=address,
                base_power=1.0,
                stake_multiplier=1.0,
                reputation_bonus=0.0,
                total_power=voting_power
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération du pouvoir de vote: {str(e)}"
        )

# === CONSENSUS HYBRIDE ===

@router.get("/consensus/validators", response_model=List[Validator])
async def get_validators(
    active_only: bool = True,
    current_user: User = Depends(get_current_user)
):
    """Récupère la liste des validateurs"""
    from server import advanced_blockchain_service
    
    try:
        query = {}
        if active_only:
            query["is_active"] = True
        
        cursor = advanced_blockchain_service.validators.find(query).sort("stake_amount", -1)
        validators_data = await cursor.to_list(length=None)
        
        validators = []
        for validator_data in validators_data:
            validators.append(Validator(**validator_data))
        
        return validators
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des validateurs: {str(e)}"
        )

@router.post("/consensus/stake")
async def stake_tokens(
    stake_data: StakeRequest,
    current_user: User = Depends(get_current_user)
):
    """Stake des tokens auprès d'un validateur"""
    from server import advanced_blockchain_service
    
    try:
        success = await advanced_blockchain_service.stake_tokens(
            user_address=current_user.wallet_address,
            validator_address=stake_data.validator_address,
            amount=stake_data.amount
        )
        
        if success:
            return {
                "message": "Staking effectué avec succès",
                "validator_address": stake_data.validator_address,
                "amount": stake_data.amount
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Impossible d'effectuer le staking"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors du staking: {str(e)}"
        )

@router.get("/consensus/stake-pools", response_model=List[StakePool])
async def get_stake_pools(
    current_user: User = Depends(get_current_user)
):
    """Récupère les pools de staking"""
    from server import advanced_blockchain_service
    
    try:
        cursor = advanced_blockchain_service.stake_pools.find({"is_active": True}).sort("total_stake", -1)
        pools_data = await cursor.to_list(length=None)
        
        pools = []
        for pool_data in pools_data:
            pools.append(StakePool(**pool_data))
        
        return pools
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des pools: {str(e)}"
        )

@router.get("/consensus/status")
async def get_consensus_status(
    current_user: User = Depends(get_current_user)
):
    """Récupère le statut du consensus"""
    from server import advanced_blockchain_service
    
    try:
        # Récupérer les informations de consensus
        total_validators = await advanced_blockchain_service.validators.count_documents({"is_active": True})
        total_stake = 0
        
        pools = await advanced_blockchain_service.stake_pools.find({}).to_list(length=None)
        for pool_data in pools:
            pool = StakePool(**pool_data)
            total_stake += pool.total_stake
        
        return {
            "consensus_type": advanced_blockchain_service.consensus_type.value,
            "pow_weight": advanced_blockchain_service.pow_weight,
            "pos_weight": advanced_blockchain_service.pos_weight,
            "total_validators": total_validators,
            "total_stake": total_stake,
            "min_stake": advanced_blockchain_service.min_stake,
            "current_difficulty": advanced_blockchain_service.blockchain_service.difficulty
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération du statut: {str(e)}"
        )

# === COMPRESSION ET ARCHIVAGE ===

@router.post("/management/compress-blocks")
async def compress_blocks(
    threshold_blocks: Optional[int] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user)
):
    """Lance la compression des anciens blocs"""
    from server import advanced_blockchain_service
    
    try:
        # Lancer la compression en arrière-plan
        background_tasks.add_task(
            advanced_blockchain_service.compress_old_blocks,
            threshold_blocks
        )
        
        return {
            "message": "Compression des blocs lancée en arrière-plan",
            "threshold_blocks": threshold_blocks or advanced_blockchain_service.compression_threshold
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du lancement de la compression: {str(e)}"
        )

@router.post("/management/archive-blocks")
async def archive_blocks(
    threshold_blocks: Optional[int] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user)
):
    """Lance l'archivage des anciens blocs"""
    from server import advanced_blockchain_service
    
    try:
        # Lancer l'archivage en arrière-plan
        background_tasks.add_task(
            advanced_blockchain_service.archive_old_blocks,
            threshold_blocks
        )
        
        return {
            "message": "Archivage des blocs lancé en arrière-plan",
            "threshold_blocks": threshold_blocks or advanced_blockchain_service.archive_threshold
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du lancement de l'archivage: {str(e)}"
        )

@router.get("/management/compressed-blocks", response_model=List[CompressedBlock])
async def get_compressed_blocks(
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Récupère les blocs compressés"""
    from server import advanced_blockchain_service
    
    try:
        cursor = advanced_blockchain_service.compressed_blocks.find().sort("block_number", -1).limit(limit)
        compressed_data = await cursor.to_list(length=limit)
        
        compressed_blocks = []
        for block_data in compressed_data:
            compressed_blocks.append(CompressedBlock(**block_data))
        
        return compressed_blocks
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des blocs compressés: {str(e)}"
        )

@router.get("/management/archive-periods", response_model=List[ArchivePeriod])
async def get_archive_periods(
    current_user: User = Depends(get_current_user)
):
    """Récupère les périodes d'archivage"""
    from server import advanced_blockchain_service
    
    try:
        cursor = advanced_blockchain_service.archive_periods.find().sort("created_at", -1)
        periods_data = await cursor.to_list(length=None)
        
        periods = []
        for period_data in periods_data:
            periods.append(ArchivePeriod(**period_data))
        
        return periods
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des périodes d'archivage: {str(e)}"
        )

# === INTEROPÉRABILITÉ ===

@router.get("/interoperability/bridges", response_model=List[CrossChainBridge])
async def get_cross_chain_bridges(
    current_user: User = Depends(get_current_user)
):
    """Récupère les ponts cross-chain"""
    from server import advanced_blockchain_service
    
    try:
        cursor = advanced_blockchain_service.cross_chain_bridges.find({"is_active": True})
        bridges_data = await cursor.to_list(length=None)
        
        bridges = []
        for bridge_data in bridges_data:
            bridges.append(CrossChainBridge(**bridge_data))
        
        return bridges
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des ponts: {str(e)}"
        )

@router.post("/interoperability/bridge-transfer", response_model=CrossChainTransaction)
async def initiate_bridge_transfer(
    transfer_data: BridgeTransferRequest,
    current_user: User = Depends(get_current_user)
):
    """Initie un transfert cross-chain"""
    from server import advanced_blockchain_service
    
    try:
        # Trouver le pont approprié
        bridge = await advanced_blockchain_service.cross_chain_bridges.find_one({
            "target_network": transfer_data.target_network.value,
            "is_active": True
        })
        
        if not bridge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pont vers {transfer_data.target_network.value} non trouvé"
            )
        
        cross_tx = await advanced_blockchain_service.initiate_cross_chain_transfer(
            bridge_id=bridge["id"],
            from_address=current_user.wallet_address,
            to_address=transfer_data.to_address,
            amount=transfer_data.amount,
            token_symbol=transfer_data.token_symbol
        )
        
        return cross_tx
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors du transfert: {str(e)}"
        )

@router.get("/interoperability/transactions", response_model=List[CrossChainTransaction])
async def get_cross_chain_transactions(
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Récupère les transactions cross-chain"""
    from server import advanced_blockchain_service
    
    try:
        cursor = advanced_blockchain_service.cross_chain_transactions.find().sort("created_at", -1).limit(limit)
        transactions_data = await cursor.to_list(length=limit)
        
        transactions = []
        for tx_data in transactions_data:
            transactions.append(CrossChainTransaction(**tx_data))
        
        return transactions
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des transactions: {str(e)}"
        )

@router.get("/interoperability/transactions/{tx_id}", response_model=CrossChainTransaction)
async def get_cross_chain_transaction(
    tx_id: str,
    current_user: User = Depends(get_current_user)
):
    """Récupère une transaction cross-chain spécifique"""
    from server import advanced_blockchain_service
    
    try:
        tx_data = await advanced_blockchain_service.cross_chain_transactions.find_one({"id": tx_id})
        
        if not tx_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transaction {tx_id} non trouvée"
            )
        
        return CrossChainTransaction(**tx_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération de la transaction: {str(e)}"
        )

# === MÉTRIQUES ET SANTÉ ===

@router.get("/metrics", response_model=BlockchainMetrics)
async def get_blockchain_metrics(
    current_user: User = Depends(get_current_user)
):
    """Récupère les métriques avancées de la blockchain"""
    from server import advanced_blockchain_service
    
    try:
        metrics = await advanced_blockchain_service.get_blockchain_metrics()
        return metrics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des métriques: {str(e)}"
        )

@router.get("/network-health", response_model=NetworkHealth)
async def get_network_health(
    current_user: User = Depends(get_current_user)
):
    """Évalue la santé du réseau blockchain"""
    from server import advanced_blockchain_service
    
    try:
        health = await advanced_blockchain_service.get_network_health()
        return health
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'évaluation de la santé: {str(e)}"
        )

@router.get("/overview")
async def get_blockchain_overview(
    current_user: User = Depends(get_current_user)
):
    """Vue d'ensemble de la blockchain améliorée"""
    from server import advanced_blockchain_service
    
    try:
        # Récupérer les statistiques de base
        basic_stats = await advanced_blockchain_service.blockchain_service.get_blockchain_stats()
        
        # Récupérer les métriques avancées
        metrics = await advanced_blockchain_service.get_blockchain_metrics()
        
        # Récupérer la santé du réseau
        health = await advanced_blockchain_service.get_network_health()
        
        # Compter les éléments avancés
        total_contracts = await advanced_blockchain_service.smart_contracts.count_documents({})
        active_proposals = await advanced_blockchain_service.governance_proposals.count_documents(
            {"status": "active"}
        )
        total_validators = await advanced_blockchain_service.validators.count_documents({"is_active": True})
        cross_chain_bridges = await advanced_blockchain_service.cross_chain_bridges.count_documents(
            {"is_active": True}
        )
        
        return {
            "basic_stats": basic_stats,
            "metrics": metrics,
            "health": health,
            "advanced_features": {
                "smart_contracts": total_contracts,
                "active_proposals": active_proposals,
                "active_validators": total_validators,
                "cross_chain_bridges": cross_chain_bridges,
                "consensus_type": advanced_blockchain_service.consensus_type.value,
                "compression_enabled": True,
                "archiving_enabled": True
            },
            "capabilities": [
                "Smart Contracts",
                "Hybrid Consensus (PoW + PoS)",
                "Decentralized Governance",
                "Cross-Chain Interoperability",
                "Block Compression",
                "Automatic Archiving"
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération de l'aperçu: {str(e)}"
        )

# Alias endpoints pour compatibilité avec les tests
@router.get("/validators", response_model=List[Validator])
async def get_validators_alias(
    active_only: bool = True,
    current_user: User = Depends(get_current_user)
):
    """Récupère la liste des validateurs (alias)"""
    return await get_validators(active_only=active_only, current_user=current_user)

@router.post("/stake")
async def stake_tokens_alias(
    stake_data: StakeRequest,
    current_user: User = Depends(get_current_user)
):
    """Stake des tokens auprès d'un validateur (alias)"""
    return await stake_tokens(stake_data=stake_data, current_user=current_user)
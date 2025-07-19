"""
Routes de mining distribué
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Dict, Any, Optional

from models.quantum_models import MiningTask, MiningResult
from routes.auth_routes import get_current_user
from services.mining_service import MiningService

router = APIRouter()

# Modèles de requête
class MiningResultSubmission(BaseModel):
    task_id: str
    nonce: int
    hash_result: str

class MinerRegistration(BaseModel):
    miner_address: str
    hardware_specs: Dict[str, Any] = {}

# Routes
@router.get("/stats")
async def get_mining_stats(current_user = Depends(get_current_user)):
    """Récupère les statistiques de mining"""
    from server import mining_service
    
    try:
        stats = await mining_service.get_mining_stats()
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des statistiques: {str(e)}"
        )

@router.get("/task")
async def get_mining_task(current_user = Depends(get_current_user)):
    """Récupère une tâche de mining pour l'utilisateur"""
    from server import mining_service
    
    try:
        # Utiliser l'adresse wallet de l'utilisateur comme adresse du mineur
        miner_address = current_user.wallet_address
        
        task = await mining_service.get_mining_task(miner_address)
        
        if not task:
            return {
                "message": "Aucune tâche de mining disponible",
                "task": None
            }
        
        return {
            "message": "Tâche de mining disponible",
            "task": task
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération de la tâche: {str(e)}"
        )

@router.post("/submit")
async def submit_mining_result(result_data: MiningResultSubmission, current_user = Depends(get_current_user)):
    """Soumet un résultat de mining"""
    from server import mining_service
    
    try:
        # Utiliser l'adresse wallet de l'utilisateur
        miner_address = current_user.wallet_address
        
        success = await mining_service.submit_mining_result(
            task_id=result_data.task_id,
            nonce=result_data.nonce,
            hash_result=result_data.hash_result,
            miner_address=miner_address
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Résultat de mining invalide ou tâche expirée"
            )
        
        return {
            "message": "Résultat de mining accepté",
            "task_id": result_data.task_id,
            "miner_address": miner_address,
            "status": "accepted"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la soumission: {str(e)}"
        )

@router.get("/history")
async def get_mining_history(current_user = Depends(get_current_user)):
    """Récupère l'historique de mining de l'utilisateur"""
    from server import mining_service
    
    try:
        miner_address = current_user.wallet_address
        miner_stats = await mining_service.get_miner_stats(miner_address)
        
        return {
            "miner_address": miner_address,
            "stats": miner_stats,
            "user_id": current_user.id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération de l'historique: {str(e)}"
        )

@router.post("/register")
async def register_miner(registration_data: MinerRegistration, current_user = Depends(get_current_user)):
    """Enregistre un mineur"""
    from server import mining_service
    
    try:
        # Utiliser l'adresse wallet de l'utilisateur
        miner_address = current_user.wallet_address
        
        await mining_service.register_miner(miner_address)
        
        return {
            "message": "Mineur enregistré avec succès",
            "miner_address": miner_address,
            "user_id": current_user.id,
            "hardware_specs": registration_data.hardware_specs
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'enregistrement: {str(e)}"
        )

@router.get("/difficulty")
async def get_current_difficulty(current_user = Depends(get_current_user)):
    """Récupère la difficulté actuelle du mining"""
    from server import mining_service
    
    try:
        return {
            "current_difficulty": mining_service.difficulty,
            "target_block_time": mining_service.block_time_target,
            "algorithm": "Proof of Work",
            "hash_function": "SHA-256"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération de la difficulté: {str(e)}"
        )

@router.get("/rewards")
async def get_mining_rewards(current_user = Depends(get_current_user)):
    """Récupère les informations sur les récompenses de mining"""
    from server import mining_service
    
    try:
        return {
            "base_reward": mining_service.mining_reward,
            "reward_currency": "QS",
            "additional_rewards": {
                "block_mining": mining_service.mining_reward,
                "network_participation": 5.0,
                "uptime_bonus": "Variable selon uptime"
            },
            "payout_info": {
                "frequency": "Immédiate après validation du bloc",
                "minimum_payout": 0.1,
                "transaction_fee": 0.0
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des récompenses: {str(e)}"
        )

@router.get("/pool-info")
async def get_mining_pool_info(current_user = Depends(get_current_user)):
    """Récupère les informations sur le pool de mining"""
    from server import mining_service
    
    try:
        stats = await mining_service.get_mining_stats()
        
        return {
            "pool_name": "QuantumShield Mining Pool",
            "pool_type": "Distributed",
            "active_miners": stats.get("active_miners", 0),
            "total_miners": stats.get("total_miners", 0),
            "hash_rate": stats.get("estimated_hash_rate", 0),
            "blocks_found": stats.get("total_blocks_mined", 0),
            "success_rate": stats.get("success_rate", 0),
            "fee_structure": {
                "pool_fee": "0%",
                "transaction_fee": "0%",
                "withdrawal_fee": "0%"
            },
            "payout_scheme": "PPS (Pay Per Share)",
            "minimum_payout": 0.1
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des infos pool: {str(e)}"
        )

@router.get("/calculator")
async def mining_calculator(hash_rate: float = 1000, current_user = Depends(get_current_user)):
    """Calculateur de rentabilité du mining"""
    from server import mining_service
    
    try:
        stats = await mining_service.get_mining_stats()
        
        # Calculs simplifiés
        network_hash_rate = stats.get("estimated_hash_rate", 1000)
        block_reward = mining_service.mining_reward
        block_time = mining_service.block_time_target
        
        # Estimation des gains
        user_share = hash_rate / max(network_hash_rate, 1)
        blocks_per_day = 86400 / block_time
        daily_earnings = user_share * blocks_per_day * block_reward
        
        return {
            "input_hash_rate": hash_rate,
            "network_hash_rate": network_hash_rate,
            "user_network_share": user_share * 100,
            "block_reward": block_reward,
            "estimated_earnings": {
                "daily": daily_earnings,
                "weekly": daily_earnings * 7,
                "monthly": daily_earnings * 30,
                "yearly": daily_earnings * 365
            },
            "network_info": {
                "difficulty": mining_service.difficulty,
                "block_time": block_time,
                "blocks_per_day": blocks_per_day
            },
            "disclaimer": "Estimations basées sur les conditions actuelles du réseau"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du calcul: {str(e)}"
        )

@router.get("/leaderboard")
async def get_mining_leaderboard(limit: int = 50, current_user = Depends(get_current_user)):
    """Récupère le classement des mineurs"""
    from server import mining_service
    
    try:
        # Récupérer les mineurs triés par blocs minés
        cursor = mining_service.miners.find().sort("blocks_mined", -1).limit(limit)
        miners = await cursor.to_list(length=limit)
        
        leaderboard = []
        for i, miner in enumerate(miners):
            leaderboard.append({
                "rank": i + 1,
                "miner_address": miner["address"],
                "blocks_mined": miner["blocks_mined"],
                "total_rewards": miner["total_rewards"],
                "hash_rate": miner["hash_rate"],
                "last_activity": miner["last_activity"]
            })
        
        return {
            "leaderboard": leaderboard,
            "total_miners": len(miners),
            "current_user_rank": None  # TODO: Calculer le rang de l'utilisateur actuel
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération du classement: {str(e)}"
        )
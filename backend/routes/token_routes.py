"""
Routes de gestion des tokens $QS
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from models.quantum_models import TokenBalance, TokenTransaction, RewardClaim, TransactionType
from routes.auth_routes import get_current_user
from services.token_service import TokenService

router = APIRouter()

# Modèles de requête
class TransferRequest(BaseModel):
    to_user: str
    amount: float
    description: str = ""

class RewardRequest(BaseModel):
    user_id: str
    reward_type: str
    device_id: Optional[str] = None
    multiplier: float = 1.0

# Routes
@router.get("/balance")
async def get_balance(current_user = Depends(get_current_user)):
    """Récupère le solde de l'utilisateur"""
    from server import token_service
    
    try:
        balance = await token_service.get_balance(current_user.id)
        
        return {
            "user_id": current_user.id,
            "balance": balance,
            "wallet_address": current_user.wallet_address,
            "symbol": "QS",
            "decimals": 2
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération du solde: {str(e)}"
        )

@router.post("/transfer")
async def transfer_tokens(transfer_data: TransferRequest, current_user = Depends(get_current_user)):
    """Transfère des tokens vers un autre utilisateur"""
    from server import token_service
    
    try:
        # Vérifier que l'utilisateur ne transfère pas à lui-même
        if transfer_data.to_user == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Impossible de transférer des tokens vers soi-même"
            )
        
        # Vérifier que le destinataire existe
        from server import auth_service
        recipient = await auth_service.get_user_by_id(transfer_data.to_user)
        if not recipient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur destinataire non trouvé"
            )
        
        # Effectuer le transfert
        success = await token_service.transfer_tokens(
            from_user=current_user.id,
            to_user=transfer_data.to_user,
            amount=transfer_data.amount,
            transaction_type=TransactionType.REWARD,
            description=transfer_data.description
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transfert échoué - solde insuffisant"
            )
        
        return {
            "message": "Transfert effectué avec succès",
            "from_user": current_user.id,
            "to_user": transfer_data.to_user,
            "amount": transfer_data.amount,
            "description": transfer_data.description
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du transfert: {str(e)}"
        )

@router.get("/transactions", response_model=List[TokenTransaction])
async def get_transactions(limit: int = 100, current_user = Depends(get_current_user)):
    """Récupère les transactions de l'utilisateur"""
    from server import token_service
    
    try:
        transactions = await token_service.get_user_transactions(current_user.id, limit)
        return transactions
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des transactions: {str(e)}"
        )

@router.get("/rewards", response_model=List[RewardClaim])
async def get_rewards(limit: int = 100, current_user = Depends(get_current_user)):
    """Récupère les récompenses de l'utilisateur"""
    from server import token_service
    
    try:
        rewards = await token_service.get_user_rewards(current_user.id, limit)
        return rewards
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des récompenses: {str(e)}"
        )

@router.get("/stats")
async def get_token_stats(current_user = Depends(get_current_user)):
    """Récupère les statistiques du système de tokens"""
    from server import token_service
    
    try:
        stats = await token_service.get_token_stats()
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des statistiques: {str(e)}"
        )

@router.get("/score")
async def get_user_score(current_user = Depends(get_current_user)):
    """Récupère le score de réputation de l'utilisateur"""
    from server import token_service
    
    try:
        score = await token_service.calculate_user_score(current_user.id)
        return score
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du calcul du score: {str(e)}"
        )

@router.get("/leaderboard")
async def get_leaderboard(limit: int = 50, current_user = Depends(get_current_user)):
    """Récupère le classement des utilisateurs"""
    from server import token_service
    
    try:
        leaderboard = await token_service.get_leaderboard(limit)
        return leaderboard
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération du classement: {str(e)}"
        )

@router.get("/reward-rates")
async def get_reward_rates():
    """Récupère les taux de récompenses disponibles"""
    from server import token_service
    
    try:
        return {
            "reward_rates": token_service.reward_rates,
            "descriptions": {
                "device_registration": "Récompense pour l'enregistrement d'un nouveau device",
                "anomaly_detection": "Récompense pour la détection d'anomalies",
                "firmware_validation": "Récompense pour la validation de firmware",
                "network_participation": "Récompense pour la participation au réseau",
                "data_sharing": "Récompense pour le partage de données",
                "mining_participation": "Récompense pour la participation au mining"
            },
            "time_limits": {
                "device_registration": "24 heures",
                "anomaly_detection": "1 heure",
                "firmware_validation": "6 heures",
                "network_participation": "24 heures",
                "data_sharing": "12 heures",
                "mining_participation": "30 minutes"
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des taux: {str(e)}"
        )

@router.post("/claim-reward")
async def claim_reward(reward_data: RewardRequest, current_user = Depends(get_current_user)):
    """Permet à un utilisateur de réclamer une récompense"""
    from server import token_service
    
    try:
        # Vérifier que l'utilisateur peut réclamer cette récompense
        can_claim = await token_service.can_claim_reward(
            current_user.id,
            reward_data.reward_type,
            reward_data.device_id
        )
        
        if not can_claim:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Récompense déjà réclamée récemment"
            )
        
        # Récompenser l'utilisateur
        success = await token_service.reward_user(
            user_id=current_user.id,
            reward_type=reward_data.reward_type,
            device_id=reward_data.device_id,
            multiplier=reward_data.multiplier
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Impossible de réclamer la récompense"
            )
        
        # Calculer le montant de la récompense
        base_amount = token_service.reward_rates.get(reward_data.reward_type, 0)
        reward_amount = base_amount * reward_data.multiplier
        
        return {
            "message": "Récompense réclamée avec succès",
            "reward_type": reward_data.reward_type,
            "amount": reward_amount,
            "user_id": current_user.id,
            "device_id": reward_data.device_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la réclamation: {str(e)}"
        )

@router.get("/portfolio")
async def get_user_portfolio(current_user = Depends(get_current_user)):
    """Récupère le portfolio complet de l'utilisateur"""
    from server import token_service, device_service
    
    try:
        # Solde actuel
        balance = await token_service.get_balance(current_user.id)
        
        # Score de réputation
        score = await token_service.calculate_user_score(current_user.id)
        
        # Récompenses récentes
        recent_rewards = await token_service.get_user_rewards(current_user.id, 10)
        
        # Transactions récentes
        recent_transactions = await token_service.get_user_transactions(current_user.id, 10)
        
        # Devices de l'utilisateur
        user_devices = await device_service.get_user_devices(current_user.id)
        
        # Statistiques d'activité
        total_rewards = sum(reward.amount for reward in recent_rewards)
        device_count = len(user_devices)
        active_devices = len([d for d in user_devices if d.status == "active"])
        
        return {
            "user_id": current_user.id,
            "wallet_address": current_user.wallet_address,
            "balance": balance,
            "score": score,
            "total_rewards_earned": total_rewards,
            "device_count": device_count,
            "active_devices": active_devices,
            "recent_rewards": recent_rewards,
            "recent_transactions": recent_transactions,
            "devices": user_devices
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération du portfolio: {str(e)}"
        )

@router.get("/market-info")
async def get_market_info():
    """Récupère les informations du marché $QS"""
    from server import token_service
    
    try:
        stats = await token_service.get_token_stats()
        
        # Calculer des métriques supplémentaires
        circulating_supply = stats.get("circulating_supply", 0)
        total_supply = stats.get("total_supply", 0)
        
        return {
            "token_info": {
                "symbol": "QS",
                "name": "QuantumShield Token",
                "type": "Utility Token",
                "blockchain": "QuantumShield Private Chain"
            },
            "supply_info": {
                "total_supply": total_supply,
                "circulating_supply": circulating_supply,
                "max_supply": token_service.max_supply,
                "supply_percentage": (circulating_supply / token_service.max_supply) * 100
            },
            "network_stats": {
                "total_transactions": stats.get("total_transactions", 0),
                "total_rewards_distributed": stats.get("total_rewards_claimed", 0),
                "active_users": len(stats.get("top_holders", [])),
                "reward_categories": len(stats.get("reward_distribution", {}))
            },
            "reward_economy": {
                "reward_rates": token_service.reward_rates,
                "total_rewards_pool": stats.get("total_supply", 0) - circulating_supply
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des infos marché: {str(e)}"
        )
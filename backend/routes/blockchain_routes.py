"""
Routes de la blockchain privée
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from models.quantum_models import Block, Transaction, BlockchainStats, TransactionType
from routes.auth_routes import get_current_user
from services.blockchain_service import BlockchainService

router = APIRouter()

# Modèles de requête
class TransactionCreate(BaseModel):
    to_address: str
    amount: float
    transaction_type: TransactionType
    data: Dict[str, Any] = {}

class FirmwareUpdate(BaseModel):
    device_id: str
    firmware_hash: str
    version: str

# Routes
@router.get("/stats", response_model=BlockchainStats)
async def get_blockchain_stats(current_user = Depends(get_current_user)):
    """Récupère les statistiques de la blockchain"""
    from server import blockchain_service
    
    try:
        stats = await blockchain_service.get_blockchain_stats()
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des statistiques: {str(e)}"
        )

@router.get("/blocks/{block_number}", response_model=Block)
async def get_block(block_number: int, current_user = Depends(get_current_user)):
    """Récupère un bloc par son numéro"""
    from server import blockchain_service
    
    try:
        block = await blockchain_service.get_block_by_number(block_number)
        
        if not block:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bloc {block_number} non trouvé"
            )
        
        return block
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération du bloc: {str(e)}"
        )

@router.get("/blocks")
async def get_recent_blocks(limit: int = 10, current_user = Depends(get_current_user)):
    """Récupère les blocs récents"""
    from server import blockchain_service
    
    try:
        cursor = blockchain_service.blocks.find().sort("block_number", -1).limit(limit)
        blocks_data = await cursor.to_list(length=limit)
        
        blocks = []
        for block_data in blocks_data:
            blocks.append(Block(**block_data))
        
        return blocks
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des blocs: {str(e)}"
        )

@router.get("/transactions/{tx_hash}", response_model=Transaction)
async def get_transaction(tx_hash: str, current_user = Depends(get_current_user)):
    """Récupère une transaction par son hash"""
    from server import blockchain_service
    
    try:
        transaction = await blockchain_service.get_transaction_by_hash(tx_hash)
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transaction {tx_hash} non trouvée"
            )
        
        return transaction
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération de la transaction: {str(e)}"
        )

@router.get("/transactions")
async def get_recent_transactions(limit: int = 50, current_user = Depends(get_current_user)):
    """Récupère les transactions récentes"""
    from server import blockchain_service
    
    try:
        cursor = blockchain_service.transactions.find().sort("timestamp", -1).limit(limit)
        transactions_data = await cursor.to_list(length=limit)
        
        transactions = []
        for tx_data in transactions_data:
            transactions.append(Transaction(**tx_data))
        
        return transactions
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des transactions: {str(e)}"
        )

@router.post("/transactions")
async def create_transaction(transaction_data: TransactionCreate, current_user = Depends(get_current_user)):
    """Crée une nouvelle transaction"""
    from server import blockchain_service
    
    try:
        # Créer la transaction
        transaction = Transaction(
            from_address=current_user.wallet_address,
            to_address=transaction_data.to_address,
            amount=transaction_data.amount,
            transaction_type=transaction_data.transaction_type,
            data=transaction_data.data,
            signature="user_signature"  # À implémenter avec la signature NTRU++
        )
        
        # Ajouter à la blockchain
        tx_hash = await blockchain_service.add_transaction(transaction)
        
        return {
            "transaction_hash": tx_hash,
            "status": "pending",
            "message": "Transaction ajoutée à la pool"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de la création de la transaction: {str(e)}"
        )

@router.get("/pending-transactions")
async def get_pending_transactions(current_user = Depends(get_current_user)):
    """Récupère les transactions en attente"""
    from server import blockchain_service
    
    try:
        pending_transactions = await blockchain_service.get_pending_transactions(limit=100)
        return pending_transactions
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des transactions en attente: {str(e)}"
        )

@router.post("/firmware-update")
async def register_firmware_update(firmware_data: FirmwareUpdate, current_user = Depends(get_current_user)):
    """Enregistre une mise à jour de firmware sur la blockchain"""
    from server import blockchain_service
    
    try:
        tx_hash = await blockchain_service.register_firmware_update(
            firmware_data.device_id,
            firmware_data.firmware_hash,
            firmware_data.version
        )
        
        return {
            "transaction_hash": tx_hash,
            "device_id": firmware_data.device_id,
            "firmware_hash": firmware_data.firmware_hash,
            "version": firmware_data.version,
            "message": "Mise à jour de firmware enregistrée"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de l'enregistrement: {str(e)}"
        )

@router.get("/validate-chain")
async def validate_blockchain(current_user = Depends(get_current_user)):
    """Valide l'intégrité de la blockchain"""
    from server import blockchain_service
    
    try:
        is_valid = await blockchain_service.validate_chain()
        
        return {
            "is_valid": is_valid,
            "message": "Blockchain valide" if is_valid else "Blockchain corrompue",
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la validation: {str(e)}"
        )

@router.get("/explorer")
async def blockchain_explorer(current_user = Depends(get_current_user)):
    """Explorateur de blockchain - aperçu général"""
    from server import blockchain_service
    
    try:
        # Récupérer les statistiques
        stats = await blockchain_service.get_blockchain_stats()
        
        # Récupérer les derniers blocs
        recent_blocks = await blockchain_service.blocks.find().sort(
            "block_number", -1
        ).limit(5).to_list(length=5)
        
        # Récupérer les dernières transactions
        recent_transactions = await blockchain_service.transactions.find().sort(
            "timestamp", -1
        ).limit(10).to_list(length=10)
        
        return {
            "stats": stats,
            "recent_blocks": [Block(**block) for block in recent_blocks],
            "recent_transactions": [Transaction(**tx) for tx in recent_transactions],
            "network_info": {
                "type": "Private Blockchain",
                "consensus": "Proof of Work",
                "current_difficulty": 4,
                "average_block_time": "5 minutes",
                "network_status": "Active"
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des données: {str(e)}"
        )

@router.get("/address/{address}")
async def get_address_info(address: str, current_user = Depends(get_current_user)):
    """Récupère les informations d'une adresse"""
    from server import blockchain_service
    
    try:
        # Transactions envoyées
        sent_cursor = blockchain_service.transactions.find({"from_address": address})
        sent_transactions = await sent_cursor.to_list(length=None)
        
        # Transactions reçues
        received_cursor = blockchain_service.transactions.find({"to_address": address})
        received_transactions = await received_cursor.to_list(length=None)
        
        # Calculer le solde
        balance = 0
        for tx in received_transactions:
            balance += tx["amount"]
        for tx in sent_transactions:
            balance -= tx["amount"]
        
        return {
            "address": address,
            "balance": balance,
            "transaction_count": len(sent_transactions) + len(received_transactions),
            "sent_transactions": len(sent_transactions),
            "received_transactions": len(received_transactions),
            "recent_transactions": (sent_transactions + received_transactions)[-10:]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des informations: {str(e)}"
        )
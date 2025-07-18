"""
Service de blockchain privée pour la confiance matérielle
Implémentation d'une blockchain Hyperledger-style pour IoT
"""

import hashlib
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from motor.motor_asyncio import AsyncIOMotorCollection

from models.quantum_models import Block, Transaction, BlockchainStats, BlockType

logger = logging.getLogger(__name__)

class BlockchainService:
    """Service de blockchain privée pour la confiance matérielle"""
    
    def __init__(self, db):
        self.db = db
        self.blocks: AsyncIOMotorCollection = db.blocks
        self.transactions: AsyncIOMotorCollection = db.transactions
        self.pending_transactions: AsyncIOMotorCollection = db.pending_transactions
        self.difficulty = 4
        self.mining_reward = 10.0
        self.is_initialized = False
    
    async def initialize_genesis_block(self):
        """Initialise le bloc genesis"""
        try:
            # Vérifier si le bloc genesis existe déjà
            genesis_block = await self.blocks.find_one({"block_number": 0})
            
            if not genesis_block:
                # Créer le bloc genesis
                genesis_transaction = Transaction(
                    from_address="0x0000000000000000000000000000000000000000",
                    to_address="0x0000000000000000000000000000000000000000",
                    amount=0,
                    transaction_type="reward",
                    signature="genesis",
                    hash=self.calculate_transaction_hash({
                        "from_address": "0x0000000000000000000000000000000000000000",
                        "to_address": "0x0000000000000000000000000000000000000000",
                        "amount": 0,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                )
                
                genesis_block = Block(
                    block_number=0,
                    previous_hash="0x0000000000000000000000000000000000000000000000000000000000000000",
                    merkle_root=self.calculate_merkle_root([genesis_transaction]),
                    transactions=[genesis_transaction],
                    miner_address="0x0000000000000000000000000000000000000000",
                    hash=""
                )
                
                # Calculer le hash du bloc genesis
                genesis_block.hash = self.calculate_block_hash(genesis_block)
                
                # Sauvegarder dans la base de données
                await self.blocks.insert_one(genesis_block.dict())
                await self.transactions.insert_one(genesis_transaction.dict())
                
                logger.info("Bloc genesis créé avec succès")
            
            self.is_initialized = True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du bloc genesis: {e}")
            self.is_initialized = False
    
    async def is_ready(self) -> bool:
        """Vérifie si le service blockchain est prêt"""
        return self.is_initialized
    
    def calculate_transaction_hash(self, transaction_data: Dict[str, Any]) -> str:
        """Calcule le hash d'une transaction"""
        transaction_string = json.dumps(transaction_data, sort_keys=True)
        return hashlib.sha256(transaction_string.encode()).hexdigest()
    
    def calculate_merkle_root(self, transactions: List[Transaction]) -> str:
        """Calcule la racine de Merkle des transactions"""
        if not transactions:
            return hashlib.sha256(b"").hexdigest()
        
        # Hashes des transactions
        tx_hashes = [tx.hash for tx in transactions]
        
        # Algorithme de Merkle Tree
        while len(tx_hashes) > 1:
            if len(tx_hashes) % 2 == 1:
                tx_hashes.append(tx_hashes[-1])  # Dupliquer le dernier hash si impair
            
            new_hashes = []
            for i in range(0, len(tx_hashes), 2):
                combined = tx_hashes[i] + tx_hashes[i + 1]
                new_hash = hashlib.sha256(combined.encode()).hexdigest()
                new_hashes.append(new_hash)
            
            tx_hashes = new_hashes
        
        return tx_hashes[0]
    
    def calculate_block_hash(self, block: Block) -> str:
        """Calcule le hash d'un bloc"""
        block_data = {
            "block_number": block.block_number,
            "previous_hash": block.previous_hash,
            "merkle_root": block.merkle_root,
            "timestamp": block.timestamp.isoformat(),
            "nonce": block.nonce,
            "difficulty": block.difficulty,
            "miner_address": block.miner_address
        }
        
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def is_valid_proof_of_work(self, block_hash: str, difficulty: int) -> bool:
        """Vérifie si le proof of work est valide"""
        return block_hash.startswith("0" * difficulty)
    
    async def add_transaction(self, transaction: Transaction) -> str:
        """Ajoute une transaction à la pool des transactions en attente"""
        try:
            # Calculer le hash de la transaction
            transaction_data = {
                "from_address": transaction.from_address,
                "to_address": transaction.to_address,
                "amount": transaction.amount,
                "transaction_type": transaction.transaction_type,
                "timestamp": transaction.timestamp.isoformat(),
                "data": transaction.data
            }
            
            transaction.hash = self.calculate_transaction_hash(transaction_data)
            
            # Ajouter à la pool des transactions en attente
            await self.pending_transactions.insert_one(transaction.dict())
            
            logger.info(f"Transaction ajoutée à la pool: {transaction.hash}")
            return transaction.hash
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout de la transaction: {e}")
            raise Exception(f"Impossible d'ajouter la transaction: {e}")
    
    async def get_pending_transactions(self, limit: int = 10) -> List[Transaction]:
        """Récupère les transactions en attente"""
        try:
            cursor = self.pending_transactions.find().limit(limit)
            pending_txs = await cursor.to_list(length=limit)
            
            transactions = []
            for tx_data in pending_txs:
                transactions.append(Transaction(**tx_data))
            
            return transactions
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des transactions: {e}")
            return []
    
    async def mine_block(self, miner_address: str) -> Optional[Block]:
        """Mine un nouveau bloc"""
        try:
            # Récupérer les transactions en attente
            pending_transactions = await self.get_pending_transactions()
            
            if not pending_transactions:
                return None
            
            # Récupérer le dernier bloc
            last_block = await self.blocks.find_one(
                {},
                sort=[("block_number", -1)]
            )
            
            if not last_block:
                return None
            
            # Créer le nouveau bloc
            new_block = Block(
                block_number=last_block["block_number"] + 1,
                previous_hash=last_block["hash"],
                merkle_root=self.calculate_merkle_root(pending_transactions),
                transactions=pending_transactions,
                miner_address=miner_address,
                difficulty=self.difficulty
            )
            
            # Proof of Work
            nonce = 0
            while True:
                new_block.nonce = nonce
                block_hash = self.calculate_block_hash(new_block)
                
                if self.is_valid_proof_of_work(block_hash, self.difficulty):
                    new_block.hash = block_hash
                    break
                
                nonce += 1
                
                # Éviter les boucles infinies
                if nonce > 1000000:
                    logger.warning("Mining abandonné après 1M tentatives")
                    return None
            
            # Sauvegarder le bloc
            await self.blocks.insert_one(new_block.dict())
            
            # Déplacer les transactions vers la collection des transactions confirmées
            for tx in pending_transactions:
                await self.transactions.insert_one(tx.dict())
            
            # Supprimer les transactions de la pool en attente
            tx_ids = [tx.id for tx in pending_transactions]
            await self.pending_transactions.delete_many({"id": {"$in": tx_ids}})
            
            logger.info(f"Nouveau bloc miné: {new_block.block_number}")
            return new_block
            
        except Exception as e:
            logger.error(f"Erreur lors du mining: {e}")
            return None
    
    async def get_blockchain_stats(self) -> BlockchainStats:
        """Récupère les statistiques de la blockchain"""
        try:
            total_blocks = await self.blocks.count_documents({})
            total_transactions = await self.transactions.count_documents({})
            pending_transactions = await self.pending_transactions.count_documents({})
            
            # Récupérer le dernier bloc
            last_block = await self.blocks.find_one(
                {},
                sort=[("block_number", -1)]
            )
            
            last_block_time = datetime.fromisoformat(last_block["timestamp"]) if last_block else datetime.utcnow()
            
            return BlockchainStats(
                total_blocks=total_blocks,
                total_transactions=total_transactions,
                last_block_time=last_block_time,
                current_difficulty=self.difficulty,
                pending_transactions=pending_transactions
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des stats: {e}")
            return BlockchainStats(
                total_blocks=0,
                total_transactions=0,
                last_block_time=datetime.utcnow(),
                current_difficulty=self.difficulty,
                pending_transactions=0
            )
    
    async def get_block_by_number(self, block_number: int) -> Optional[Block]:
        """Récupère un bloc par son numéro"""
        try:
            block_data = await self.blocks.find_one({"block_number": block_number})
            if block_data:
                return Block(**block_data)
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du bloc: {e}")
            return None
    
    async def get_transaction_by_hash(self, tx_hash: str) -> Optional[Transaction]:
        """Récupère une transaction par son hash"""
        try:
            tx_data = await self.transactions.find_one({"hash": tx_hash})
            if tx_data:
                return Transaction(**tx_data)
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la transaction: {e}")
            return None
    
    async def validate_chain(self) -> bool:
        """Valide l'intégrité de la chaîne"""
        try:
            # Récupérer tous les blocs
            cursor = self.blocks.find().sort("block_number", 1)
            blocks = await cursor.to_list(length=None)
            
            if not blocks:
                return True
            
            # Vérifier chaque bloc
            for i, block_data in enumerate(blocks):
                block = Block(**block_data)
                
                # Vérifier le hash du bloc
                calculated_hash = self.calculate_block_hash(block)
                if calculated_hash != block.hash:
                    logger.error(f"Hash invalide pour le bloc {block.block_number}")
                    return False
                
                # Vérifier le lien avec le bloc précédent
                if i > 0:
                    previous_block = Block(**blocks[i-1])
                    if block.previous_hash != previous_block.hash:
                        logger.error(f"Lien rompu entre blocs {i-1} et {i}")
                        return False
                
                # Vérifier le proof of work
                if not self.is_valid_proof_of_work(block.hash, block.difficulty):
                    logger.error(f"Proof of work invalide pour le bloc {block.block_number}")
                    return False
            
            logger.info("Validation de la chaîne: OK")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la validation: {e}")
            return False
    
    async def register_firmware_update(self, device_id: str, firmware_hash: str, version: str) -> str:
        """Enregistre une mise à jour de firmware sur la blockchain"""
        try:
            firmware_transaction = Transaction(
                from_address="system",
                to_address=device_id,
                amount=0,
                transaction_type="firmware_update",
                data={
                    "firmware_hash": firmware_hash,
                    "version": version,
                    "verification_timestamp": datetime.utcnow().isoformat()
                },
                signature="system_signature"
            )
            
            tx_hash = await self.add_transaction(firmware_transaction)
            logger.info(f"Mise à jour firmware enregistrée: {tx_hash}")
            return tx_hash
            
        except Exception as e:
            logger.error(f"Erreur enregistrement firmware: {e}")
            raise Exception(f"Impossible d'enregistrer la mise à jour: {e}")
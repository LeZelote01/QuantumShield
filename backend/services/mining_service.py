"""
Service de mining pour la blockchain QuantumShield
Mining distribué avec récompenses en tokens $QS
"""

import asyncio
import hashlib
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from motor.motor_asyncio import AsyncIOMotorCollection

from models.quantum_models import MiningTask, MiningResult, Block
from services.blockchain_service import BlockchainService
from services.token_service import TokenService

logger = logging.getLogger(__name__)

class MiningService:
    """Service de mining distribué pour la blockchain QuantumShield"""
    
    def __init__(self, db, blockchain_service: BlockchainService):
        self.db = db
        self.blockchain_service = blockchain_service
        self.mining_tasks: AsyncIOMotorCollection = db.mining_tasks
        self.mining_results: AsyncIOMotorCollection = db.mining_results
        self.miners: AsyncIOMotorCollection = db.miners
        
        # Configuration du mining
        self.difficulty = 4
        self.block_time_target = 300  # 5 minutes
        self.max_miners_per_task = 10
        self.mining_reward = 50.0
        self.is_mining = False
        
        # Statistiques
        self.total_blocks_mined = 0
        self.total_hash_rate = 0
        self.active_miners = set()
    
    async def start_mining(self):
        """Démarre le processus de mining"""
        if self.is_mining:
            return
        
        self.is_mining = True
        logger.info("Démarrage du service de mining")
        
        # Démarrer les tâches de mining
        await asyncio.gather(
            self.mining_coordinator(),
            self.difficulty_adjustment(),
            self.reward_distributor()
        )
    
    async def stop_mining(self):
        """Arrête le processus de mining"""
        self.is_mining = False
        logger.info("Arrêt du service de mining")
    
    async def mining_coordinator(self):
        """Coordinateur principal du mining"""
        while self.is_mining:
            try:
                # Vérifier s'il y a des transactions en attente
                pending_transactions = await self.blockchain_service.get_pending_transactions()
                
                if pending_transactions:
                    # Créer une nouvelle tâche de mining
                    mining_task = await self.create_mining_task(pending_transactions)
                    
                    if mining_task:
                        # Attendre qu'un mineur complète la tâche
                        await self.wait_for_mining_completion(mining_task)
                
                # Attendre avant la prochaine vérification
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Erreur dans le coordinateur de mining: {e}")
                await asyncio.sleep(60)
    
    async def create_mining_task(self, pending_transactions) -> Optional[MiningTask]:
        """Crée une nouvelle tâche de mining"""
        try:
            # Récupérer le dernier bloc
            last_block = await self.blockchain_service.blocks.find_one(
                {},
                sort=[("block_number", -1)]
            )
            
            if not last_block:
                logger.error("Aucun bloc trouvé pour créer la tâche de mining")
                return None
            
            # Calculer la racine de Merkle
            merkle_root = self.blockchain_service.calculate_merkle_root(pending_transactions)
            
            # Préparer les données du bloc
            block_data = {
                "block_number": last_block["block_number"] + 1,
                "previous_hash": last_block["hash"],
                "merkle_root": merkle_root,
                "timestamp": datetime.utcnow().isoformat(),
                "transactions": [tx.dict() for tx in pending_transactions],
                "difficulty": self.difficulty
            }
            
            # Calculer le hash cible
            target_hash = "0" * self.difficulty
            
            # Créer la tâche
            mining_task = MiningTask(
                block_data=block_data,
                difficulty=self.difficulty,
                target_hash=target_hash
            )
            
            # Sauvegarder la tâche
            await self.mining_tasks.insert_one(mining_task.dict())
            
            logger.info(f"Tâche de mining créée: {mining_task.id}")
            return mining_task
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de la tâche de mining: {e}")
            return None
    
    async def wait_for_mining_completion(self, mining_task: MiningTask):
        """Attend qu'une tâche de mining soit complétée"""
        try:
            start_time = time.time()
            timeout = 600  # 10 minutes
            
            while time.time() - start_time < timeout:
                # Vérifier si la tâche est complétée
                task_doc = await self.mining_tasks.find_one({"id": mining_task.id})
                
                if task_doc and task_doc.get("completed", False):
                    # Récupérer le résultat
                    result = await self.mining_results.find_one({"task_id": mining_task.id})
                    
                    if result:
                        # Créer le bloc avec le nonce trouvé
                        await self.create_block_from_result(mining_task, result)
                        return
                
                await asyncio.sleep(5)
            
            # Timeout - marquer la tâche comme expirée
            await self.mining_tasks.update_one(
                {"id": mining_task.id},
                {"$set": {"expired": True}}
            )
            
            logger.warning(f"Tâche de mining expirée: {mining_task.id}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'attente de mining: {e}")
    
    async def create_block_from_result(self, mining_task: MiningTask, result: dict):
        """Crée un bloc à partir du résultat de mining"""
        try:
            # Récupérer les données du bloc
            block_data = mining_task.block_data
            
            # Créer le bloc
            block = Block(
                block_number=block_data["block_number"],
                previous_hash=block_data["previous_hash"],
                merkle_root=block_data["merkle_root"],
                timestamp=datetime.fromisoformat(block_data["timestamp"]),
                transactions=[],  # Sera rempli par le service blockchain
                nonce=result["nonce"],
                difficulty=block_data["difficulty"],
                miner_address=result["miner_address"],
                hash=result["hash"]
            )
            
            # Sauvegarder le bloc via le service blockchain
            await self.blockchain_service.blocks.insert_one(block.dict())
            
            # Récompenser le mineur
            await self.reward_miner(result["miner_address"], self.mining_reward)
            
            # Mettre à jour les statistiques
            self.total_blocks_mined += 1
            
            logger.info(f"Bloc miné avec succès: {block.block_number} par {result['miner_address']}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du bloc: {e}")
    
    async def submit_mining_result(self, task_id: str, nonce: int, hash_result: str, miner_address: str) -> bool:
        """Soumission d'un résultat de mining"""
        try:
            # Vérifier que la tâche existe et n'est pas complétée
            task_doc = await self.mining_tasks.find_one({
                "id": task_id,
                "completed": False,
                "expired": {"$ne": True}
            })
            
            if not task_doc:
                logger.warning(f"Tâche invalide ou expirée: {task_id}")
                return False
            
            # Vérifier le proof of work
            if not self.blockchain_service.is_valid_proof_of_work(hash_result, task_doc["difficulty"]):
                logger.warning(f"Proof of work invalide: {hash_result}")
                return False
            
            # Enregistrer le résultat
            mining_result = MiningResult(
                task_id=task_id,
                nonce=nonce,
                hash=hash_result,
                miner_address=miner_address,
                computation_time=0  # Sera calculé
            )
            
            # Vérifier si c'est la première soumission valide
            existing_result = await self.mining_results.find_one({"task_id": task_id})
            
            if existing_result:
                logger.info(f"Résultat déjà soumis pour la tâche {task_id}")
                return False
            
            # Sauvegarder le résultat
            await self.mining_results.insert_one(mining_result.dict())
            
            # Marquer la tâche comme complétée
            await self.mining_tasks.update_one(
                {"id": task_id},
                {"$set": {"completed": True, "miner_address": miner_address}}
            )
            
            logger.info(f"Résultat de mining accepté pour la tâche {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la soumission du résultat: {e}")
            return False
    
    async def get_mining_task(self, miner_address: str) -> Optional[Dict[str, Any]]:
        """Récupère une tâche de mining pour un mineur"""
        try:
            # Enregistrer le mineur
            await self.register_miner(miner_address)
            
            # Trouver une tâche disponible
            task_doc = await self.mining_tasks.find_one({
                "completed": False,
                "expired": {"$ne": True}
            })
            
            if task_doc:
                return {
                    "task_id": task_doc["id"],
                    "block_data": task_doc["block_data"],
                    "difficulty": task_doc["difficulty"],
                    "target_hash": task_doc["target_hash"]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la tâche: {e}")
            return None
    
    async def register_miner(self, miner_address: str):
        """Enregistre un mineur"""
        try:
            # Vérifier si le mineur existe déjà
            existing_miner = await self.miners.find_one({"address": miner_address})
            
            if not existing_miner:
                miner_data = {
                    "address": miner_address,
                    "registered_at": datetime.utcnow(),
                    "last_activity": datetime.utcnow(),
                    "blocks_mined": 0,
                    "total_rewards": 0.0,
                    "hash_rate": 0
                }
                
                await self.miners.insert_one(miner_data)
                logger.info(f"Nouveau mineur enregistré: {miner_address}")
            else:
                # Mettre à jour la dernière activité
                await self.miners.update_one(
                    {"address": miner_address},
                    {"$set": {"last_activity": datetime.utcnow()}}
                )
            
            self.active_miners.add(miner_address)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du mineur: {e}")
    
    async def reward_miner(self, miner_address: str, reward_amount: float):
        """Récompense un mineur"""
        try:
            # Utiliser le service de tokens pour récompenser
            token_service = TokenService(self.db)
            
            success = await token_service.reward_user(
                user_id=miner_address,
                reward_type="mining_participation",
                multiplier=1.0
            )
            
            if success:
                # Mettre à jour les statistiques du mineur
                await self.miners.update_one(
                    {"address": miner_address},
                    {
                        "$inc": {
                            "blocks_mined": 1,
                            "total_rewards": reward_amount
                        }
                    }
                )
                
                logger.info(f"Mineur récompensé: {miner_address} (+{reward_amount} QS)")
            
        except Exception as e:
            logger.error(f"Erreur lors de la récompense du mineur: {e}")
    
    async def difficulty_adjustment(self):
        """Ajuste la difficulté du mining"""
        while self.is_mining:
            try:
                # Vérifier toutes les heures
                await asyncio.sleep(3600)
                
                # Calculer le temps moyen des derniers blocs
                recent_blocks = await self.blockchain_service.blocks.find().sort(
                    "block_number", -1
                ).limit(10).to_list(length=10)
                
                if len(recent_blocks) >= 2:
                    # Calculer le temps moyen entre les blocs
                    total_time = 0
                    for i in range(len(recent_blocks) - 1):
                        current_block = recent_blocks[i]
                        previous_block = recent_blocks[i + 1]
                        
                        current_time = datetime.fromisoformat(current_block["timestamp"])
                        previous_time = datetime.fromisoformat(previous_block["timestamp"])
                        
                        total_time += (current_time - previous_time).total_seconds()
                    
                    average_time = total_time / (len(recent_blocks) - 1)
                    
                    # Ajuster la difficulté
                    if average_time < self.block_time_target * 0.8:
                        self.difficulty += 1
                        logger.info(f"Difficulté augmentée à {self.difficulty}")
                    elif average_time > self.block_time_target * 1.2:
                        self.difficulty = max(1, self.difficulty - 1)
                        logger.info(f"Difficulté diminuée à {self.difficulty}")
                
            except Exception as e:
                logger.error(f"Erreur lors de l'ajustement de difficulté: {e}")
    
    async def reward_distributor(self):
        """Distribue les récompenses périodiques"""
        while self.is_mining:
            try:
                # Distribuer les récompenses toutes les 24 heures
                await asyncio.sleep(86400)
                
                # Récompenser les mineurs actifs
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                
                cursor = self.miners.find({
                    "last_activity": {"$gte": cutoff_time}
                })
                
                active_miners = await cursor.to_list(length=None)
                
                token_service = TokenService(self.db)
                
                for miner in active_miners:
                    # Récompense basée sur l'activité
                    await token_service.reward_user(
                        user_id=miner["address"],
                        reward_type="network_participation",
                        multiplier=0.5
                    )
                
                logger.info(f"Récompenses distribuées à {len(active_miners)} mineurs")
                
            except Exception as e:
                logger.error(f"Erreur lors de la distribution des récompenses: {e}")
    
    async def get_mining_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques de mining"""
        try:
            # Compter les tâches
            total_tasks = await self.mining_tasks.count_documents({})
            completed_tasks = await self.mining_tasks.count_documents({"completed": True})
            
            # Compter les mineurs
            total_miners = await self.miners.count_documents({})
            
            # Mineurs actifs (dernières 24h)
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            active_miners_count = await self.miners.count_documents({
                "last_activity": {"$gte": cutoff_time}
            })
            
            # Hash rate estimé
            estimated_hash_rate = active_miners_count * 1000  # Estimation simplifiée
            
            return {
                "total_blocks_mined": self.total_blocks_mined,
                "current_difficulty": self.difficulty,
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "success_rate": (completed_tasks / max(1, total_tasks)) * 100,
                "total_miners": total_miners,
                "active_miners": active_miners_count,
                "estimated_hash_rate": estimated_hash_rate,
                "block_time_target": self.block_time_target,
                "mining_reward": self.mining_reward,
                "is_mining": self.is_mining
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques: {e}")
            return {}
    
    async def get_miner_stats(self, miner_address: str) -> Dict[str, Any]:
        """Récupère les statistiques d'un mineur"""
        try:
            miner_doc = await self.miners.find_one({"address": miner_address})
            
            if not miner_doc:
                return {}
            
            # Tâches récentes
            recent_tasks = await self.mining_tasks.find({
                "miner_address": miner_address
            }).sort("timestamp", -1).limit(10).to_list(length=10)
            
            return {
                "address": miner_address,
                "registered_at": miner_doc["registered_at"],
                "last_activity": miner_doc["last_activity"],
                "blocks_mined": miner_doc["blocks_mined"],
                "total_rewards": miner_doc["total_rewards"],
                "hash_rate": miner_doc["hash_rate"],
                "recent_tasks": recent_tasks
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques du mineur: {e}")
            return {}
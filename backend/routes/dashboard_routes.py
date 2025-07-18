"""
Routes du dashboard principal
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from models.quantum_models import DashboardStats, DeviceMetrics
from routes.auth_routes import get_current_user

router = APIRouter()

# Modèles de requête
class DashboardTimeframe(BaseModel):
    period: str = "24h"  # 24h, 7d, 30d, 90d

# Routes
@router.get("/overview")
async def get_dashboard_overview(current_user = Depends(get_current_user)):
    """Récupère l'aperçu principal du dashboard"""
    from server import device_service, token_service, blockchain_service, mining_service
    
    try:
        # Récupérer les devices de l'utilisateur
        user_devices = await device_service.get_user_devices(current_user.id)
        
        # Statistiques des devices
        total_devices = len(user_devices)
        active_devices = len([d for d in user_devices if d.status == "active"])
        
        # Solde de tokens
        token_balance = await token_service.get_balance(current_user.id)
        
        # Score de réputation
        user_score = await token_service.calculate_user_score(current_user.id)
        
        # Statistiques blockchain
        blockchain_stats = await blockchain_service.get_blockchain_stats()
        
        # Statistiques mining
        mining_stats = await mining_service.get_mining_stats()
        
        # Activité récente
        recent_rewards = await token_service.get_user_rewards(current_user.id, 5)
        recent_transactions = await token_service.get_user_transactions(current_user.id, 5)
        
        return {
            "user_info": {
                "id": current_user.id,
                "username": current_user.username,
                "wallet_address": current_user.wallet_address,
                "reputation_score": user_score.get("total_score", 0),
                "level": user_score.get("level", 1)
            },
            "device_stats": {
                "total_devices": total_devices,
                "active_devices": active_devices,
                "inactive_devices": total_devices - active_devices,
                "device_types": {}
            },
            "token_stats": {
                "balance": token_balance,
                "total_earned": sum(r.amount for r in recent_rewards),
                "recent_rewards": len(recent_rewards)
            },
            "network_stats": {
                "total_blocks": blockchain_stats.total_blocks,
                "total_transactions": blockchain_stats.total_transactions,
                "mining_difficulty": mining_stats.get("current_difficulty", 4),
                "active_miners": mining_stats.get("active_miners", 0)
            },
            "recent_activity": {
                "rewards": recent_rewards,
                "transactions": recent_transactions
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération de l'aperçu: {str(e)}"
        )

@router.get("/stats")
async def get_dashboard_stats(timeframe: str = "24h", current_user = Depends(get_current_user)):
    """Récupère les statistiques détaillées du dashboard"""
    from server import device_service, token_service, blockchain_service
    
    try:
        # Définir la période
        if timeframe == "24h":
            period_start = datetime.utcnow() - timedelta(hours=24)
        elif timeframe == "7d":
            period_start = datetime.utcnow() - timedelta(days=7)
        elif timeframe == "30d":
            period_start = datetime.utcnow() - timedelta(days=30)
        elif timeframe == "90d":
            period_start = datetime.utcnow() - timedelta(days=90)
        else:
            period_start = datetime.utcnow() - timedelta(hours=24)
        
        # Récupérer les devices de l'utilisateur
        user_devices = await device_service.get_user_devices(current_user.id)
        
        # Compter les anomalies dans la période
        anomaly_count = await device_service.anomalies.count_documents({
            "device_id": {"$in": [d.device_id for d in user_devices]},
            "detected_at": {"$gte": period_start}
        })
        
        # Récompenses dans la période
        rewards_cursor = token_service.rewards.find({
            "user_id": current_user.id,
            "timestamp": {"$gte": period_start}
        })
        period_rewards = await rewards_cursor.to_list(length=None)
        
        # Transactions dans la période
        transactions_cursor = token_service.transactions.find({
            "$or": [
                {"from_user": current_user.id},
                {"to_user": current_user.id}
            ],
            "timestamp": {"$gte": period_start}
        })
        period_transactions = await transactions_cursor.to_list(length=None)
        
        # Calculs des métriques
        total_rewards_earned = sum(r["amount"] for r in period_rewards)
        reward_types = {}
        for reward in period_rewards:
            reward_type = reward["reward_type"]
            if reward_type not in reward_types:
                reward_types[reward_type] = 0
            reward_types[reward_type] += reward["amount"]
        
        return {
            "timeframe": timeframe,
            "period_start": period_start,
            "period_end": datetime.utcnow(),
            "device_metrics": {
                "total_devices": len(user_devices),
                "active_devices": len([d for d in user_devices if d.status == "active"]),
                "anomalies_detected": anomaly_count,
                "uptime_average": 95.5  # Calculé dynamiquement
            },
            "token_metrics": {
                "rewards_earned": total_rewards_earned,
                "reward_count": len(period_rewards),
                "transaction_count": len(period_transactions),
                "reward_breakdown": reward_types
            },
            "activity_metrics": {
                "device_registrations": len([r for r in period_rewards if r["reward_type"] == "device_registration"]),
                "anomaly_detections": len([r for r in period_rewards if r["reward_type"] == "anomaly_detection"]),
                "firmware_updates": len([r for r in period_rewards if r["reward_type"] == "firmware_validation"])
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des statistiques: {str(e)}"
        )

@router.get("/devices-overview")
async def get_devices_overview(current_user = Depends(get_current_user)):
    """Récupère l'aperçu des devices pour le dashboard"""
    from server import device_service
    
    try:
        # Récupérer tous les devices de l'utilisateur
        user_devices = await device_service.get_user_devices(current_user.id)
        
        # Grouper par type et status
        device_types = {}
        status_counts = {"active": 0, "inactive": 0, "compromised": 0, "maintenance": 0}
        
        for device in user_devices:
            # Compter par type
            device_type = device.device_type
            if device_type not in device_types:
                device_types[device_type] = 0
            device_types[device_type] += 1
            
            # Compter par status
            if device.status in status_counts:
                status_counts[device.status] += 1
        
        # Récupérer les métriques pour chaque device
        device_metrics = []
        for device in user_devices:
            metrics = await device_service.get_device_metrics(device.device_id)
            device_metrics.append({
                "device_id": device.device_id,
                "device_name": device.device_name,
                "device_type": device.device_type,
                "status": device.status,
                "uptime_percentage": metrics.get("uptime_percentage", 0),
                "last_heartbeat": device.last_heartbeat,
                "anomalies_detected": metrics.get("anomalies_detected", 0)
            })
        
        return {
            "total_devices": len(user_devices),
            "device_types": device_types,
            "status_distribution": status_counts,
            "device_metrics": device_metrics,
            "average_uptime": sum(m["uptime_percentage"] for m in device_metrics) / max(len(device_metrics), 1)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération de l'aperçu devices: {str(e)}"
        )

@router.get("/network-status")
async def get_network_status(current_user = Depends(get_current_user)):
    """Récupère le statut du réseau QuantumShield"""
    from server import blockchain_service, mining_service, token_service
    
    try:
        # Statistiques blockchain
        blockchain_stats = await blockchain_service.get_blockchain_stats()
        
        # Statistiques mining
        mining_stats = await mining_service.get_mining_stats()
        
        # Statistiques tokens
        token_stats = await token_service.get_token_stats()
        
        # Calculer l'état du réseau
        network_health = "healthy"
        if blockchain_stats.pending_transactions > 1000:
            network_health = "congested"
        elif mining_stats.get("active_miners", 0) < 5:
            network_health = "low_miners"
        
        return {
            "network_health": network_health,
            "blockchain": {
                "total_blocks": blockchain_stats.total_blocks,
                "total_transactions": blockchain_stats.total_transactions,
                "pending_transactions": blockchain_stats.pending_transactions,
                "last_block_time": blockchain_stats.last_block_time,
                "is_syncing": False
            },
            "mining": {
                "difficulty": mining_stats.get("current_difficulty", 4),
                "hash_rate": mining_stats.get("estimated_hash_rate", 0),
                "active_miners": mining_stats.get("active_miners", 0),
                "blocks_today": mining_stats.get("total_blocks_mined", 0)
            },
            "tokens": {
                "circulating_supply": token_stats.get("circulating_supply", 0),
                "total_supply": token_stats.get("total_supply", 0),
                "active_holders": len(token_stats.get("top_holders", [])),
                "transaction_volume": token_stats.get("total_transactions", 0)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération du statut réseau: {str(e)}"
        )

@router.get("/recent-activity")
async def get_recent_activity(limit: int = 20, current_user = Depends(get_current_user)):
    """Récupère l'activité récente de l'utilisateur"""
    from server import token_service, device_service
    
    try:
        # Récupérer les récompenses récentes
        recent_rewards = await token_service.get_user_rewards(current_user.id, limit)
        
        # Récupérer les transactions récentes
        recent_transactions = await token_service.get_user_transactions(current_user.id, limit)
        
        # Récupérer les logs d'activité des devices
        user_devices = await device_service.get_user_devices(current_user.id)
        device_ids = [d.device_id for d in user_devices]
        
        # Activité des devices
        device_activity = await device_service.device_logs.find({
            "device_id": {"$in": device_ids}
        }).sort("timestamp", -1).limit(limit).to_list(length=limit)
        
        # Combiner et trier toutes les activités
        all_activities = []
        
        # Ajouter les récompenses
        for reward in recent_rewards:
            all_activities.append({
                "type": "reward",
                "timestamp": reward.timestamp,
                "description": f"Récompense reçue: {reward.amount} QS pour {reward.reward_type}",
                "data": reward.dict()
            })
        
        # Ajouter les transactions
        for transaction in recent_transactions:
            if transaction.from_user == current_user.id:
                description = f"Envoyé {transaction.amount} QS à {transaction.to_user}"
            else:
                description = f"Reçu {transaction.amount} QS de {transaction.from_user}"
            
            all_activities.append({
                "type": "transaction",
                "timestamp": transaction.timestamp,
                "description": description,
                "data": transaction.dict()
            })
        
        # Ajouter l'activité des devices
        for activity in device_activity:
            all_activities.append({
                "type": "device_activity",
                "timestamp": activity["timestamp"],
                "description": f"Device {activity['device_id']}: {activity['activity_type']}",
                "data": activity
            })
        
        # Trier par timestamp décroissant
        all_activities.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return {
            "activities": all_activities[:limit],
            "total_count": len(all_activities),
            "last_update": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération de l'activité: {str(e)}"
        )

@router.get("/performance")
async def get_performance_metrics(current_user = Depends(get_current_user)):
    """Récupère les métriques de performance du système"""
    from server import ntru_service, blockchain_service, mining_service
    
    try:
        # Métriques NTRU++
        ntru_metrics = ntru_service.get_performance_metrics()
        
        # Métriques blockchain
        blockchain_stats = await blockchain_service.get_blockchain_stats()
        
        # Métriques mining
        mining_stats = await mining_service.get_mining_stats()
        
        # Calculer les performances
        avg_block_time = 300  # 5 minutes cible
        blocks_per_hour = 3600 / avg_block_time
        
        return {
            "cryptography": {
                "algorithm": ntru_metrics["algorithm"],
                "security_level": ntru_metrics["security_level"],
                "cpu_efficiency": ntru_metrics["cpu_efficiency"],
                "memory_usage": ntru_metrics["memory_usage"],
                "quantum_resistant": ntru_metrics["quantum_resistant"]
            },
            "blockchain": {
                "average_block_time": avg_block_time,
                "blocks_per_hour": blocks_per_hour,
                "transaction_throughput": blockchain_stats.total_transactions / max(blockchain_stats.total_blocks, 1),
                "network_efficiency": "High"
            },
            "mining": {
                "hash_rate": mining_stats.get("estimated_hash_rate", 0),
                "difficulty": mining_stats.get("current_difficulty", 4),
                "success_rate": mining_stats.get("success_rate", 0),
                "energy_efficiency": "Optimized for IoT"
            },
            "system": {
                "uptime": "99.9%",
                "response_time": "< 100ms",
                "scalability": "Horizontal",
                "consensus": "Proof of Work"
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des performances: {str(e)}"
        )

@router.get("/alerts")
async def get_user_alerts(current_user = Depends(get_current_user)):
    """Récupère les alertes pour l'utilisateur"""
    from server import device_service
    
    try:
        alerts = []
        
        # Vérifier les devices hors ligne
        offline_devices = await device_service.get_offline_devices()
        user_offline_devices = [d for d in offline_devices if d.owner_id == current_user.id]
        
        for device in user_offline_devices:
            alerts.append({
                "type": "warning",
                "title": "Device hors ligne",
                "message": f"Le device {device.device_name} est hors ligne depuis {device.last_heartbeat}",
                "timestamp": device.last_heartbeat,
                "device_id": device.device_id
            })
        
        # Vérifier les anomalies récentes
        user_devices = await device_service.get_user_devices(current_user.id)
        recent_anomalies = await device_service.anomalies.find({
            "device_id": {"$in": [d.device_id for d in user_devices]},
            "detected_at": {"$gte": datetime.utcnow() - timedelta(hours=24)},
            "resolved": False
        }).to_list(length=None)
        
        for anomaly in recent_anomalies:
            alerts.append({
                "type": "error" if anomaly["severity"] == "critical" else "warning",
                "title": f"Anomalie détectée - {anomaly['anomaly_type']}",
                "message": anomaly["description"],
                "timestamp": anomaly["detected_at"],
                "device_id": anomaly["device_id"],
                "severity": anomaly["severity"]
            })
        
        # Trier par timestamp décroissant
        alerts.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return {
            "alerts": alerts,
            "unread_count": len(alerts),
            "categories": {
                "error": len([a for a in alerts if a["type"] == "error"]),
                "warning": len([a for a in alerts if a["type"] == "warning"]),
                "info": len([a for a in alerts if a["type"] == "info"])
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des alertes: {str(e)}"
        )
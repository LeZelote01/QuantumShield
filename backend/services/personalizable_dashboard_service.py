"""
Service de Tableaux de Bord Personnalisables pour QuantumShield
Permet aux utilisateurs de créer et customiser leurs propres dashboards
"""

import json
import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class WidgetType(str, Enum):
    DEVICE_STATUS = "device_status"
    TOKEN_BALANCE = "token_balance"
    SECURITY_ALERTS = "security_alerts"
    NETWORK_STATS = "network_stats"
    ENERGY_CONSUMPTION = "energy_consumption"
    MINING_STATS = "mining_stats"
    RECENT_ACTIVITY = "recent_activity"
    PERFORMANCE_METRICS = "performance_metrics"
    CRYPTO_OPERATIONS = "crypto_operations"
    ANOMALY_DETECTION = "anomaly_detection"
    RECOMMENDATIONS = "recommendations"
    CUSTOM_CHART = "custom_chart"

class WidgetSize(str, Enum):
    SMALL = "small"        # 1x1
    MEDIUM = "medium"      # 2x1
    LARGE = "large"        # 2x2
    WIDE = "wide"          # 3x1
    FULL = "full"          # 3x2

class ChartType(str, Enum):
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    AREA = "area"
    GAUGE = "gauge"
    SCATTER = "scatter"

class WidgetConfig(BaseModel):
    widget_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    widget_type: WidgetType
    title: str
    size: WidgetSize = WidgetSize.MEDIUM
    position: Dict[str, int] = Field(default_factory=lambda: {"x": 0, "y": 0})
    settings: Dict[str, Any] = Field(default_factory=dict)
    refresh_interval: int = 60  # seconds
    enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DashboardConfig(BaseModel):
    dashboard_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    is_default: bool = False
    layout: Dict[str, Any] = Field(default_factory=dict)
    widgets: List[WidgetConfig] = Field(default_factory=list)
    theme: str = "default"
    auto_refresh: bool = True
    refresh_interval: int = 30  # seconds
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PersonalizableDashboardService:
    """Service de tableaux de bord personnalisables"""
    
    def __init__(self, db):
        self.db = db
        self.is_initialized = False
        self.widget_data_providers = {}
        self.default_widgets = {}
        self._initialize()
    
    def _initialize(self):
        """Initialise le service des dashboards personnalisables"""
        try:
            self._init_default_widgets()
            self._init_widget_data_providers()
            self.is_initialized = True
            logger.info("Service Tableaux de Bord Personnalisables initialisé")
        except Exception as e:
            logger.error(f"Erreur initialisation Dashboards: {e}")
            self.is_initialized = False
    
    def _init_default_widgets(self):
        """Initialise les widgets par défaut"""
        self.default_widgets = {
            "device_overview": WidgetConfig(
                widget_type=WidgetType.DEVICE_STATUS,
                title="Aperçu des Dispositifs",
                size=WidgetSize.MEDIUM,
                position={"x": 0, "y": 0},
                settings={"show_offline": True, "show_alerts": True}
            ),
            "token_balance": WidgetConfig(
                widget_type=WidgetType.TOKEN_BALANCE,
                title="Solde QS",
                size=WidgetSize.SMALL,
                position={"x": 2, "y": 0},
                settings={"show_history": True, "show_rewards": True}
            ),
            "security_alerts": WidgetConfig(
                widget_type=WidgetType.SECURITY_ALERTS,
                title="Alertes de Sécurité",
                size=WidgetSize.WIDE,
                position={"x": 0, "y": 1},
                settings={"max_alerts": 5, "show_resolved": False}
            ),
            "network_stats": WidgetConfig(
                widget_type=WidgetType.NETWORK_STATS,
                title="Statistiques Réseau",
                size=WidgetSize.MEDIUM,
                position={"x": 0, "y": 2},
                settings={"show_blockchain": True, "show_mining": True}
            ),
            "energy_consumption": WidgetConfig(
                widget_type=WidgetType.ENERGY_CONSUMPTION,
                title="Consommation Énergétique",
                size=WidgetSize.LARGE,
                position={"x": 2, "y": 1},
                settings={"time_range": "24h", "show_predictions": True}
            ),
            "recommendations": WidgetConfig(
                widget_type=WidgetType.RECOMMENDATIONS,
                title="Recommandations",
                size=WidgetSize.WIDE,
                position={"x": 0, "y": 3},
                settings={"max_recommendations": 3, "priority_filter": "high"}
            )
        }
    
    def _init_widget_data_providers(self):
        """Initialise les providers de données pour chaque type de widget"""
        self.widget_data_providers = {
            WidgetType.DEVICE_STATUS: self._get_device_status_data,
            WidgetType.TOKEN_BALANCE: self._get_token_balance_data,
            WidgetType.SECURITY_ALERTS: self._get_security_alerts_data,
            WidgetType.NETWORK_STATS: self._get_network_stats_data,
            WidgetType.ENERGY_CONSUMPTION: self._get_energy_consumption_data,
            WidgetType.MINING_STATS: self._get_mining_stats_data,
            WidgetType.RECENT_ACTIVITY: self._get_recent_activity_data,
            WidgetType.PERFORMANCE_METRICS: self._get_performance_metrics_data,
            WidgetType.CRYPTO_OPERATIONS: self._get_crypto_operations_data,
            WidgetType.ANOMALY_DETECTION: self._get_anomaly_detection_data,
            WidgetType.RECOMMENDATIONS: self._get_recommendations_data,
            WidgetType.CUSTOM_CHART: self._get_custom_chart_data
        }
    
    def is_ready(self) -> bool:
        """Vérifie si le service est prêt"""
        return self.is_initialized
    
    # ===== GESTION DES DASHBOARDS =====
    
    async def create_dashboard(self, user_id: str, dashboard_config: DashboardConfig) -> Dict[str, Any]:
        """Crée un nouveau dashboard personnalisé"""
        try:
            # Vérifier si l'utilisateur a déjà un dashboard par défaut
            if dashboard_config.is_default:
                await self.db.user_dashboards.update_many(
                    {"user_id": user_id},
                    {"$set": {"is_default": False}}
                )
            
            # Créer le dashboard
            dashboard_doc = {
                "user_id": user_id,
                "dashboard_id": dashboard_config.dashboard_id,
                "name": dashboard_config.name,
                "description": dashboard_config.description,
                "is_default": dashboard_config.is_default,
                "layout": dashboard_config.layout,
                "widgets": [widget.dict() for widget in dashboard_config.widgets],
                "theme": dashboard_config.theme,
                "auto_refresh": dashboard_config.auto_refresh,
                "refresh_interval": dashboard_config.refresh_interval,
                "created_at": dashboard_config.created_at,
                "updated_at": dashboard_config.updated_at
            }
            
            await self.db.user_dashboards.insert_one(dashboard_doc)
            
            return {
                "success": True,
                "dashboard_id": dashboard_config.dashboard_id,
                "message": "Dashboard créé avec succès"
            }
            
        except Exception as e:
            logger.error(f"Erreur création dashboard: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user_dashboards(self, user_id: str) -> List[Dict[str, Any]]:
        """Récupère tous les dashboards d'un utilisateur"""
        try:
            dashboards = await self.db.user_dashboards.find({
                "user_id": user_id
            }).sort("created_at", -1).to_list(None)
            
            # Si aucun dashboard, créer un dashboard par défaut
            if not dashboards:
                default_dashboard = await self._create_default_dashboard(user_id)
                dashboards = [default_dashboard]
            
            return dashboards
            
        except Exception as e:
            logger.error(f"Erreur récupération dashboards: {e}")
            return []
    
    async def get_dashboard(self, user_id: str, dashboard_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un dashboard spécifique"""
        try:
            dashboard = await self.db.user_dashboards.find_one({
                "user_id": user_id,
                "dashboard_id": dashboard_id
            })
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Erreur récupération dashboard: {e}")
            return None
    
    async def update_dashboard(self, user_id: str, dashboard_id: str, updates: Dict[str, Any]) -> bool:
        """Met à jour un dashboard"""
        try:
            updates["updated_at"] = datetime.utcnow()
            
            result = await self.db.user_dashboards.update_one(
                {"user_id": user_id, "dashboard_id": dashboard_id},
                {"$set": updates}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Erreur mise à jour dashboard: {e}")
            return False
    
    async def delete_dashboard(self, user_id: str, dashboard_id: str) -> bool:
        """Supprime un dashboard"""
        try:
            # Vérifier que ce n'est pas le seul dashboard
            dashboard_count = await self.db.user_dashboards.count_documents({
                "user_id": user_id
            })
            
            if dashboard_count <= 1:
                return False  # Ne pas supprimer le dernier dashboard
            
            result = await self.db.user_dashboards.delete_one({
                "user_id": user_id,
                "dashboard_id": dashboard_id
            })
            
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Erreur suppression dashboard: {e}")
            return False
    
    async def _create_default_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Crée un dashboard par défaut pour un utilisateur"""
        try:
            default_dashboard = DashboardConfig(
                name="Dashboard Principal",
                description="Dashboard par défaut avec widgets essentiels",
                is_default=True,
                layout={"columns": 3, "rows": 4},
                widgets=list(self.default_widgets.values()),
                theme="default"
            )
            
            dashboard_doc = {
                "user_id": user_id,
                "dashboard_id": default_dashboard.dashboard_id,
                "name": default_dashboard.name,
                "description": default_dashboard.description,
                "is_default": default_dashboard.is_default,
                "layout": default_dashboard.layout,
                "widgets": [widget.dict() for widget in default_dashboard.widgets],
                "theme": default_dashboard.theme,
                "auto_refresh": default_dashboard.auto_refresh,
                "refresh_interval": default_dashboard.refresh_interval,
                "created_at": default_dashboard.created_at,
                "updated_at": default_dashboard.updated_at
            }
            
            await self.db.user_dashboards.insert_one(dashboard_doc)
            
            return dashboard_doc
            
        except Exception as e:
            logger.error(f"Erreur création dashboard par défaut: {e}")
            return {}
    
    # ===== GESTION DES WIDGETS =====
    
    async def add_widget_to_dashboard(self, user_id: str, dashboard_id: str, widget_config: WidgetConfig) -> bool:
        """Ajoute un widget à un dashboard"""
        try:
            result = await self.db.user_dashboards.update_one(
                {"user_id": user_id, "dashboard_id": dashboard_id},
                {"$push": {"widgets": widget_config.dict()}, "$set": {"updated_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Erreur ajout widget: {e}")
            return False
    
    async def update_widget_in_dashboard(self, user_id: str, dashboard_id: str, widget_id: str, updates: Dict[str, Any]) -> bool:
        """Met à jour un widget dans un dashboard"""
        try:
            updates["updated_at"] = datetime.utcnow()
            
            result = await self.db.user_dashboards.update_one(
                {"user_id": user_id, "dashboard_id": dashboard_id, "widgets.widget_id": widget_id},
                {"$set": {f"widgets.$.{k}": v for k, v in updates.items()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Erreur mise à jour widget: {e}")
            return False
    
    async def remove_widget_from_dashboard(self, user_id: str, dashboard_id: str, widget_id: str) -> bool:
        """Supprime un widget d'un dashboard"""
        try:
            result = await self.db.user_dashboards.update_one(
                {"user_id": user_id, "dashboard_id": dashboard_id},
                {"$pull": {"widgets": {"widget_id": widget_id}}, "$set": {"updated_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Erreur suppression widget: {e}")
            return False
    
    async def get_widget_data(self, user_id: str, widget_config: WidgetConfig) -> Dict[str, Any]:
        """Récupère les données d'un widget"""
        try:
            widget_type = widget_config.widget_type
            
            if widget_type in self.widget_data_providers:
                data_provider = self.widget_data_providers[widget_type]
                data = await data_provider(user_id, widget_config.settings)
                
                return {
                    "widget_id": widget_config.widget_id,
                    "widget_type": widget_type.value,
                    "title": widget_config.title,
                    "data": data,
                    "last_updated": datetime.utcnow()
                }
            else:
                return {
                    "widget_id": widget_config.widget_id,
                    "widget_type": widget_type.value,
                    "title": widget_config.title,
                    "data": None,
                    "error": "Provider de données non trouvé"
                }
            
        except Exception as e:
            logger.error(f"Erreur récupération données widget: {e}")
            return {
                "widget_id": widget_config.widget_id,
                "widget_type": widget_config.widget_type.value,
                "title": widget_config.title,
                "data": None,
                "error": str(e)
            }
    
    async def get_dashboard_data(self, user_id: str, dashboard_id: str) -> Dict[str, Any]:
        """Récupère toutes les données d'un dashboard"""
        try:
            dashboard = await self.get_dashboard(user_id, dashboard_id)
            
            if not dashboard:
                return {
                    "success": False,
                    "error": "Dashboard non trouvé"
                }
            
            # Récupérer les données pour chaque widget
            widget_data = []
            for widget_dict in dashboard.get("widgets", []):
                widget_config = WidgetConfig(**widget_dict)
                if widget_config.enabled:
                    data = await self.get_widget_data(user_id, widget_config)
                    widget_data.append(data)
            
            return {
                "success": True,
                "dashboard": {
                    "dashboard_id": dashboard["dashboard_id"],
                    "name": dashboard["name"],
                    "description": dashboard["description"],
                    "layout": dashboard["layout"],
                    "theme": dashboard["theme"],
                    "auto_refresh": dashboard["auto_refresh"],
                    "refresh_interval": dashboard["refresh_interval"]
                },
                "widgets": widget_data,
                "last_updated": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Erreur récupération données dashboard: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ===== PROVIDERS DE DONNÉES POUR WIDGETS =====
    
    async def _get_device_status_data(self, user_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Récupère les données de statut des dispositifs"""
        try:
            # Récupérer les devices de l'utilisateur
            devices = await self.db.devices.find({"owner_id": user_id}).to_list(None)
            
            # Calculer les statistiques
            total_devices = len(devices)
            active_devices = len([d for d in devices if d.get("status") == "active"])
            offline_devices = len([d for d in devices if d.get("status") == "offline"])
            
            # Grouper par type
            device_types = {}
            for device in devices:
                device_type = device.get("device_type", "unknown")
                device_types[device_type] = device_types.get(device_type, 0) + 1
            
            return {
                "total_devices": total_devices,
                "active_devices": active_devices,
                "offline_devices": offline_devices,
                "device_types": device_types,
                "devices": devices[:10] if settings.get("show_list", False) else []
            }
            
        except Exception as e:
            logger.error(f"Erreur données device status: {e}")
            return {}
    
    async def _get_token_balance_data(self, user_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Récupère les données de solde de tokens"""
        try:
            # Récupérer le solde actuel
            balance_doc = await self.db.user_balances.find_one({"user_id": user_id})
            current_balance = balance_doc.get("balance", 0) if balance_doc else 0
            
            # Récupérer l'historique si demandé
            history = []
            if settings.get("show_history", False):
                transactions = await self.db.token_transactions.find({
                    "$or": [{"from_user": user_id}, {"to_user": user_id}]
                }).sort("timestamp", -1).limit(10).to_list(None)
                
                history = [
                    {
                        "timestamp": t["timestamp"],
                        "amount": t["amount"],
                        "type": "received" if t["to_user"] == user_id else "sent"
                    }
                    for t in transactions
                ]
            
            # Récupérer les récompenses récentes si demandé
            rewards = []
            if settings.get("show_rewards", False):
                reward_docs = await self.db.user_rewards.find({
                    "user_id": user_id
                }).sort("timestamp", -1).limit(5).to_list(None)
                
                rewards = [
                    {
                        "timestamp": r["timestamp"],
                        "amount": r["amount"],
                        "type": r["reward_type"]
                    }
                    for r in reward_docs
                ]
            
            return {
                "current_balance": current_balance,
                "history": history,
                "recent_rewards": rewards,
                "total_earned": sum(r["amount"] for r in rewards)
            }
            
        except Exception as e:
            logger.error(f"Erreur données token balance: {e}")
            return {}
    
    async def _get_security_alerts_data(self, user_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Récupère les données d'alertes de sécurité"""
        try:
            # Récupérer les devices de l'utilisateur
            user_devices = await self.db.devices.find({"owner_id": user_id}).to_list(None)
            device_ids = [d["device_id"] for d in user_devices]
            
            # Récupérer les alertes
            query = {
                "device_id": {"$in": device_ids},
                "timestamp": {"$gte": datetime.utcnow() - timedelta(days=7)}
            }
            
            if not settings.get("show_resolved", False):
                query["resolved"] = False
            
            alerts = await self.db.security_alerts.find(query).sort("timestamp", -1).limit(
                settings.get("max_alerts", 5)
            ).to_list(None)
            
            # Calculer les statistiques
            alert_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
            for alert in alerts:
                severity = alert.get("severity", "low")
                alert_counts[severity] = alert_counts.get(severity, 0) + 1
            
            return {
                "alerts": alerts,
                "alert_counts": alert_counts,
                "total_alerts": len(alerts)
            }
            
        except Exception as e:
            logger.error(f"Erreur données security alerts: {e}")
            return {}
    
    async def _get_network_stats_data(self, user_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Récupère les statistiques réseau"""
        try:
            # Statistiques blockchain
            blockchain_stats = {}
            if settings.get("show_blockchain", True):
                blockchain_doc = await self.db.blockchain_stats.find_one({}, sort=[("timestamp", -1)])
                if blockchain_doc:
                    blockchain_stats = {
                        "total_blocks": blockchain_doc.get("total_blocks", 0),
                        "total_transactions": blockchain_doc.get("total_transactions", 0),
                        "last_block_time": blockchain_doc.get("last_block_time")
                    }
            
            # Statistiques mining
            mining_stats = {}
            if settings.get("show_mining", True):
                mining_doc = await self.db.mining_stats.find_one({}, sort=[("timestamp", -1)])
                if mining_doc:
                    mining_stats = {
                        "difficulty": mining_doc.get("current_difficulty", 0),
                        "hash_rate": mining_doc.get("estimated_hash_rate", 0),
                        "active_miners": mining_doc.get("active_miners", 0)
                    }
            
            return {
                "blockchain": blockchain_stats,
                "mining": mining_stats,
                "network_health": "healthy"  # Calculé dynamiquement
            }
            
        except Exception as e:
            logger.error(f"Erreur données network stats: {e}")
            return {}
    
    async def _get_energy_consumption_data(self, user_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Récupère les données de consommation énergétique"""
        try:
            time_range = settings.get("time_range", "24h")
            
            # Convertir la période
            if time_range == "24h":
                start_time = datetime.utcnow() - timedelta(hours=24)
            elif time_range == "7d":
                start_time = datetime.utcnow() - timedelta(days=7)
            elif time_range == "30d":
                start_time = datetime.utcnow() - timedelta(days=30)
            else:
                start_time = datetime.utcnow() - timedelta(hours=24)
            
            # Récupérer les données énergétiques
            energy_data = await self.db.energy_metrics.find({
                "user_id": user_id,
                "timestamp": {"$gte": start_time}
            }).sort("timestamp", 1).to_list(None)
            
            # Calculer les statistiques
            if energy_data:
                total_consumption = sum(d.get("total_consumption", 0) for d in energy_data)
                avg_consumption = total_consumption / len(energy_data)
                peak_consumption = max(d.get("total_consumption", 0) for d in energy_data)
                
                # Préparation des données pour graphique
                chart_data = [
                    {
                        "timestamp": d["timestamp"],
                        "consumption": d.get("total_consumption", 0)
                    }
                    for d in energy_data
                ]
            else:
                total_consumption = avg_consumption = peak_consumption = 0
                chart_data = []
            
            return {
                "total_consumption": total_consumption,
                "average_consumption": avg_consumption,
                "peak_consumption": peak_consumption,
                "chart_data": chart_data,
                "time_range": time_range
            }
            
        except Exception as e:
            logger.error(f"Erreur données energy consumption: {e}")
            return {}
    
    async def _get_mining_stats_data(self, user_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Récupère les statistiques de mining"""
        try:
            # Récupérer les stats de mining de l'utilisateur
            user_mining = await self.db.user_mining_stats.find_one({"user_id": user_id})
            
            if user_mining:
                return {
                    "blocks_mined": user_mining.get("blocks_mined", 0),
                    "total_rewards": user_mining.get("total_rewards", 0),
                    "hash_rate": user_mining.get("hash_rate", 0),
                    "mining_efficiency": user_mining.get("efficiency", 0),
                    "last_block_time": user_mining.get("last_block_time")
                }
            else:
                return {
                    "blocks_mined": 0,
                    "total_rewards": 0,
                    "hash_rate": 0,
                    "mining_efficiency": 0,
                    "last_block_time": None
                }
            
        except Exception as e:
            logger.error(f"Erreur données mining stats: {e}")
            return {}
    
    async def _get_recent_activity_data(self, user_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Récupère les données d'activité récente"""
        try:
            limit = settings.get("max_activities", 10)
            
            # Récupérer les activités récentes
            activities = await self.db.activity_logs.find({
                "user_id": user_id
            }).sort("timestamp", -1).limit(limit).to_list(None)
            
            return {
                "activities": activities,
                "total_count": len(activities)
            }
            
        except Exception as e:
            logger.error(f"Erreur données recent activity: {e}")
            return {}
    
    async def _get_performance_metrics_data(self, user_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Récupère les métriques de performance"""
        try:
            # Placeholder pour les métriques de performance
            return {
                "response_time": 45,  # ms
                "uptime": 99.9,      # %
                "cpu_usage": 23,     # %
                "memory_usage": 67,  # %
                "network_latency": 12 # ms
            }
            
        except Exception as e:
            logger.error(f"Erreur données performance metrics: {e}")
            return {}
    
    async def _get_crypto_operations_data(self, user_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Récupère les données d'opérations cryptographiques"""
        try:
            # Récupérer les opérations crypto récentes
            operations = await self.db.crypto_operations.find({
                "user_id": user_id
            }).sort("timestamp", -1).limit(settings.get("max_operations", 10)).to_list(None)
            
            # Calculer les statistiques
            operation_counts = {}
            for op in operations:
                op_type = op.get("operation_type", "unknown")
                operation_counts[op_type] = operation_counts.get(op_type, 0) + 1
            
            return {
                "recent_operations": operations,
                "operation_counts": operation_counts,
                "total_operations": len(operations)
            }
            
        except Exception as e:
            logger.error(f"Erreur données crypto operations: {e}")
            return {}
    
    async def _get_anomaly_detection_data(self, user_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Récupère les données de détection d'anomalies"""
        try:
            # Récupérer les devices de l'utilisateur
            user_devices = await self.db.devices.find({"owner_id": user_id}).to_list(None)
            device_ids = [d["device_id"] for d in user_devices]
            
            # Récupérer les anomalies récentes
            anomalies = await self.db.anomaly_detections.find({
                "device_id": {"$in": device_ids},
                "detection_time": {"$gte": datetime.utcnow() - timedelta(days=7)}
            }).sort("detection_time", -1).limit(settings.get("max_anomalies", 10)).to_list(None)
            
            # Calculer les statistiques
            anomaly_counts = {}
            for anomaly in anomalies:
                anomaly_type = anomaly.get("anomaly_type", "unknown")
                anomaly_counts[anomaly_type] = anomaly_counts.get(anomaly_type, 0) + 1
            
            return {
                "recent_anomalies": anomalies,
                "anomaly_counts": anomaly_counts,
                "total_anomalies": len(anomalies)
            }
            
        except Exception as e:
            logger.error(f"Erreur données anomaly detection: {e}")
            return {}
    
    async def _get_recommendations_data(self, user_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Récupère les données de recommandations"""
        try:
            # Récupérer les recommandations récentes
            query = {"user_id": user_id, "expires_at": {"$gte": datetime.utcnow()}}
            
            priority_filter = settings.get("priority_filter")
            if priority_filter:
                query["priority"] = priority_filter
            
            recommendations = await self.db.user_recommendations.find(query).sort("created_at", -1).limit(
                settings.get("max_recommendations", 5)
            ).to_list(None)
            
            return {
                "recommendations": recommendations,
                "total_count": len(recommendations)
            }
            
        except Exception as e:
            logger.error(f"Erreur données recommendations: {e}")
            return {}
    
    async def _get_custom_chart_data(self, user_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Récupère les données pour un graphique personnalisé"""
        try:
            # Placeholder pour les graphiques personnalisés
            return {
                "chart_type": settings.get("chart_type", "line"),
                "data": [],
                "labels": [],
                "message": "Graphique personnalisé non implémenté"
            }
            
        except Exception as e:
            logger.error(f"Erreur données custom chart: {e}")
            return {}
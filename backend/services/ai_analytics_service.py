"""
Service d'Analytics et IA pour QuantumShield
Inclut: ML pour détection d'anomalies, prédiction de pannes, optimisation énergétique
"""

import json
import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import uuid
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.linear_model import LinearRegression
import joblib
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class AnomalyType(str, Enum):
    DEVICE_BEHAVIOR = "device_behavior"
    NETWORK_TRAFFIC = "network_traffic"
    ENERGY_CONSUMPTION = "energy_consumption"
    SECURITY_PATTERN = "security_pattern"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    CRYPTO_TIMING = "crypto_timing"

class PredictionType(str, Enum):
    DEVICE_FAILURE = "device_failure"
    ENERGY_USAGE = "energy_usage"
    NETWORK_LOAD = "network_load"
    SECURITY_THREAT = "security_threat"
    MAINTENANCE_NEED = "maintenance_need"

class ModelType(str, Enum):
    ISOLATION_FOREST = "isolation_forest"
    DBSCAN = "dbscan"
    LINEAR_REGRESSION = "linear_regression"
    NEURAL_NETWORK = "neural_network"

class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AIAnalyticsService:
    """Service d'Analytics et IA avancée"""
    
    def __init__(self, db):
        self.db = db
        self.is_initialized = False
        self.models = {}
        self.scalers = {}
        self.model_path = Path(__file__).parent / "ml_models"
        self.model_path.mkdir(exist_ok=True)
        self._initialize()
    
    def _initialize(self):
        """Initialise le service IA"""
        try:
            # Initialiser les modèles ML
            self._init_anomaly_detection_models()
            self._init_prediction_models()
            self.is_initialized = True
            logger.info("Service AI Analytics initialisé")
        except Exception as e:
            logger.error(f"Erreur initialisation AI Analytics: {e}")
            self.is_initialized = False
    
    def _init_anomaly_detection_models(self):
        """Initialise les modèles de détection d'anomalies"""
        try:
            # Modèle pour anomalies de dispositifs
            self.models["device_anomaly"] = IsolationForest(
                contamination=0.1,
                random_state=42,
                n_estimators=100
            )
            
            # Modèle pour anomalies réseau
            self.models["network_anomaly"] = IsolationForest(
                contamination=0.05,
                random_state=42,
                n_estimators=150
            )
            
            # Modèle pour anomalies énergétiques
            self.models["energy_anomaly"] = IsolationForest(
                contamination=0.08,
                random_state=42,
                n_estimators=120
            )
            
            # Modèle de clustering pour patterns
            self.models["behavior_clustering"] = DBSCAN(
                eps=0.5,
                min_samples=5
            )
            
            logger.info("Modèles de détection d'anomalies initialisés")
            
        except Exception as e:
            logger.error(f"Erreur initialisation modèles anomalies: {e}")
    
    def _init_prediction_models(self):
        """Initialise les modèles de prédiction"""
        try:
            # Modèle de prédiction de pannes
            self.models["failure_prediction"] = LinearRegression()
            
            # Modèle de prédiction énergétique
            self.models["energy_prediction"] = LinearRegression()
            
            # Modèle de prédiction de charge réseau
            self.models["network_load_prediction"] = LinearRegression()
            
            # Scalers pour normalisation
            self.scalers["device_features"] = StandardScaler()
            self.scalers["network_features"] = StandardScaler()
            self.scalers["energy_features"] = StandardScaler()
            
            logger.info("Modèles de prédiction initialisés")
            
        except Exception as e:
            logger.error(f"Erreur initialisation modèles prédiction: {e}")
    
    def is_ready(self) -> bool:
        """Vérifie si le service est prêt"""
        return self.is_initialized
    
    # ===== DÉTECTION D'ANOMALIES =====
    
    async def detect_device_anomalies(self, device_id: str, 
                                    time_window: timedelta = timedelta(hours=24)) -> Dict[str, Any]:
        """Détecte les anomalies comportementales des dispositifs"""
        try:
            # Récupérer les données historiques du dispositif
            end_time = datetime.utcnow()
            start_time = end_time - time_window
            
            device_data = await self.db.device_metrics.find({
                "device_id": device_id,
                "timestamp": {"$gte": start_time, "$lte": end_time}
            }).to_list(None)
            
            if len(device_data) < 10:
                return {
                    "anomalies_detected": False,
                    "reason": "Données insuffisantes pour l'analyse",
                    "data_points": len(device_data)
                }
            
            # Préparer les features
            features = []
            timestamps = []
            
            for data in device_data:
                feature_vector = [
                    data.get("cpu_usage", 0),
                    data.get("memory_usage", 0),
                    data.get("network_io", 0),
                    data.get("disk_io", 0),
                    data.get("temperature", 0),
                    data.get("battery_level", 100),
                    data.get("signal_strength", 0)
                ]
                features.append(feature_vector)
                timestamps.append(data["timestamp"])
            
            features_array = np.array(features)
            
            # Détecter les anomalies
            anomaly_scores = self.models["device_anomaly"].decision_function(features_array)
            anomaly_predictions = self.models["device_anomaly"].predict(features_array)
            
            # Analyser les résultats
            anomaly_indices = np.where(anomaly_predictions == -1)[0]
            anomalies = []
            
            for idx in anomaly_indices:
                anomaly = {
                    "timestamp": timestamps[idx],
                    "anomaly_score": float(anomaly_scores[idx]),
                    "features": {
                        "cpu_usage": features[idx][0],
                        "memory_usage": features[idx][1],
                        "network_io": features[idx][2],
                        "disk_io": features[idx][3],
                        "temperature": features[idx][4],
                        "battery_level": features[idx][5],
                        "signal_strength": features[idx][6]
                    },
                    "severity": self._calculate_anomaly_severity(anomaly_scores[idx])
                }
                anomalies.append(anomaly)
            
            # Enregistrer les anomalies détectées
            if anomalies:
                await self._save_anomaly_detection_result(
                    device_id=device_id,
                    anomaly_type=AnomalyType.DEVICE_BEHAVIOR,
                    anomalies=anomalies
                )
            
            return {
                "device_id": device_id,
                "anomalies_detected": len(anomalies) > 0,
                "anomaly_count": len(anomalies),
                "anomalies": anomalies,
                "analysis_period": {
                    "start": start_time,
                    "end": end_time
                },
                "total_data_points": len(device_data)
            }
            
        except Exception as e:
            logger.error(f"Erreur détection anomalies dispositif: {e}")
            return {
                "anomalies_detected": False,
                "error": str(e)
            }
    
    async def detect_network_anomalies(self, time_window: timedelta = timedelta(hours=6)) -> Dict[str, Any]:
        """Détecte les anomalies du trafic réseau"""
        try:
            # Récupérer les métriques réseau
            end_time = datetime.utcnow()
            start_time = end_time - time_window
            
            network_data = await self.db.network_metrics.find({
                "timestamp": {"$gte": start_time, "$lte": end_time}
            }).to_list(None)
            
            if len(network_data) < 20:
                return {
                    "anomalies_detected": False,
                    "reason": "Données réseau insuffisantes"
                }
            
            # Préparer les features réseau
            features = []
            timestamps = []
            
            for data in network_data:
                feature_vector = [
                    data.get("bytes_sent", 0),
                    data.get("bytes_received", 0),
                    data.get("packets_sent", 0),
                    data.get("packets_received", 0),
                    data.get("connections_active", 0),
                    data.get("latency", 0),
                    data.get("packet_loss", 0)
                ]
                features.append(feature_vector)
                timestamps.append(data["timestamp"])
            
            features_array = np.array(features)
            
            # Normaliser les features
            if "network_features" not in self.scalers:
                self.scalers["network_features"] = StandardScaler()
                features_scaled = self.scalers["network_features"].fit_transform(features_array)
            else:
                features_scaled = self.scalers["network_features"].transform(features_array)
            
            # Détecter les anomalies
            anomaly_scores = self.models["network_anomaly"].decision_function(features_scaled)
            anomaly_predictions = self.models["network_anomaly"].predict(features_scaled)
            
            # Analyser les résultats
            anomaly_indices = np.where(anomaly_predictions == -1)[0]
            anomalies = []
            
            for idx in anomaly_indices:
                anomaly = {
                    "timestamp": timestamps[idx],
                    "anomaly_score": float(anomaly_scores[idx]),
                    "network_metrics": {
                        "bytes_sent": features[idx][0],
                        "bytes_received": features[idx][1],
                        "packets_sent": features[idx][2],
                        "packets_received": features[idx][3],
                        "connections_active": features[idx][4],
                        "latency": features[idx][5],
                        "packet_loss": features[idx][6]
                    },
                    "severity": self._calculate_anomaly_severity(anomaly_scores[idx])
                }
                anomalies.append(anomaly)
            
            return {
                "anomalies_detected": len(anomalies) > 0,
                "anomaly_count": len(anomalies),
                "anomalies": anomalies,
                "analysis_period": {
                    "start": start_time,
                    "end": end_time
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur détection anomalies réseau: {e}")
            return {
                "anomalies_detected": False,
                "error": str(e)
            }
    
    async def detect_energy_anomalies(self, time_window: timedelta = timedelta(hours=12)) -> Dict[str, Any]:
        """Détecte les anomalies de consommation énergétique"""
        try:
            # Récupérer les données énergétiques
            end_time = datetime.utcnow()
            start_time = end_time - time_window
            
            energy_data = await self.db.energy_metrics.find({
                "timestamp": {"$gte": start_time, "$lte": end_time}
            }).to_list(None)
            
            if len(energy_data) < 15:
                return {
                    "anomalies_detected": False,
                    "reason": "Données énergétiques insuffisantes"
                }
            
            # Préparer les features énergétiques
            features = []
            timestamps = []
            
            for data in energy_data:
                feature_vector = [
                    data.get("total_consumption", 0),
                    data.get("device_consumption", 0),
                    data.get("network_consumption", 0),
                    data.get("crypto_consumption", 0),
                    data.get("idle_consumption", 0),
                    data.get("peak_usage", 0),
                    data.get("efficiency_ratio", 1.0)
                ]
                features.append(feature_vector)
                timestamps.append(data["timestamp"])
            
            features_array = np.array(features)
            
            # Détecter les anomalies
            anomaly_scores = self.models["energy_anomaly"].decision_function(features_array)
            anomaly_predictions = self.models["energy_anomaly"].predict(features_array)
            
            # Analyser les résultats
            anomaly_indices = np.where(anomaly_predictions == -1)[0]
            anomalies = []
            
            for idx in anomaly_indices:
                anomaly = {
                    "timestamp": timestamps[idx],
                    "anomaly_score": float(anomaly_scores[idx]),
                    "energy_metrics": {
                        "total_consumption": features[idx][0],
                        "device_consumption": features[idx][1],
                        "network_consumption": features[idx][2],
                        "crypto_consumption": features[idx][3],
                        "idle_consumption": features[idx][4],
                        "peak_usage": features[idx][5],
                        "efficiency_ratio": features[idx][6]
                    },
                    "severity": self._calculate_anomaly_severity(anomaly_scores[idx]),
                    "recommendations": self._generate_energy_recommendations(features[idx])
                }
                anomalies.append(anomaly)
            
            return {
                "anomalies_detected": len(anomalies) > 0,
                "anomaly_count": len(anomalies),
                "anomalies": anomalies,
                "analysis_period": {
                    "start": start_time,
                    "end": end_time
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur détection anomalies énergétiques: {e}")
            return {
                "anomalies_detected": False,
                "error": str(e)
            }
    
    # ===== PRÉDICTION DE PANNES =====
    
    async def predict_device_failure(self, device_id: str, 
                                   prediction_horizon: timedelta = timedelta(days=7)) -> Dict[str, Any]:
        """Prédit la probabilité de panne d'un dispositif"""
        try:
            # Récupérer l'historique du dispositif
            historical_data = await self.db.device_metrics.find({
                "device_id": device_id
            }).sort("timestamp", -1).limit(100).to_list(None)
            
            if len(historical_data) < 20:
                return {
                    "prediction_available": False,
                    "reason": "Historique insuffisant"
                }
            
            # Préparer les features pour la prédiction
            features = []
            failure_indicators = []
            
            for data in historical_data:
                # Features techniques
                feature_vector = [
                    data.get("cpu_usage", 0),
                    data.get("memory_usage", 0),
                    data.get("temperature", 0),
                    data.get("battery_level", 100),
                    data.get("error_count", 0),
                    data.get("restart_count", 0),
                    data.get("network_errors", 0)
                ]
                features.append(feature_vector)
                
                # Indicateurs de défaillance
                failure_score = 0
                if data.get("temperature", 0) > 80:
                    failure_score += 0.3
                if data.get("error_count", 0) > 5:
                    failure_score += 0.4
                if data.get("battery_level", 100) < 20:
                    failure_score += 0.2
                if data.get("restart_count", 0) > 2:
                    failure_score += 0.1
                
                failure_indicators.append(failure_score)
            
            # Entraîner le modèle de prédiction
            features_array = np.array(features)
            failure_array = np.array(failure_indicators)
            
            # Créer des séquences temporelles
            X, y = self._create_time_series_data(features_array, failure_array)
            
            if len(X) < 10:
                return {
                    "prediction_available": False,
                    "reason": "Données temporelles insuffisantes"
                }
            
            # Entraîner le modèle
            self.models["failure_prediction"].fit(X, y)
            
            # Faire la prédiction
            last_features = features_array[-1].reshape(1, -1)
            failure_probability = self.models["failure_prediction"].predict(last_features)[0]
            
            # Calculer la confiance
            confidence = self._calculate_prediction_confidence(features_array, failure_array)
            
            # Générer des recommandations
            recommendations = self._generate_failure_recommendations(
                features_array[-1], failure_probability
            )
            
            return {
                "device_id": device_id,
                "prediction_available": True,
                "failure_probability": max(0, min(1, failure_probability)),
                "confidence": confidence,
                "prediction_horizon": prediction_horizon,
                "risk_level": self._calculate_risk_level(failure_probability),
                "recommendations": recommendations,
                "predicted_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Erreur prédiction panne: {e}")
            return {
                "prediction_available": False,
                "error": str(e)
            }
    
    async def predict_energy_usage(self, prediction_horizon: timedelta = timedelta(days=1)) -> Dict[str, Any]:
        """Prédit la consommation énergétique future"""
        try:
            # Récupérer les données énergétiques historiques
            historical_data = await self.db.energy_metrics.find({}).sort("timestamp", -1).limit(200).to_list(None)
            
            if len(historical_data) < 50:
                return {
                    "prediction_available": False,
                    "reason": "Historique énergétique insuffisant"
                }
            
            # Préparer les séries temporelles
            timestamps = []
            consumption_values = []
            
            for data in reversed(historical_data):  # Chronologique
                timestamps.append(data["timestamp"])
                consumption_values.append(data.get("total_consumption", 0))
            
            # Créer les features temporelles
            features = []
            targets = []
            
            for i in range(len(consumption_values) - 24):  # Fenêtre de 24h
                feature_window = consumption_values[i:i+24]
                target = consumption_values[i+24]
                
                # Calculer des statistiques sur la fenêtre
                feature_vector = [
                    np.mean(feature_window),
                    np.std(feature_window),
                    np.min(feature_window),
                    np.max(feature_window),
                    feature_window[-1],  # Dernière valeur
                    np.mean(feature_window[-6:]),  # Moyenne des 6 dernières
                    timestamps[i+23].hour,  # Heure du jour
                    timestamps[i+23].weekday()  # Jour de la semaine
                ]
                
                features.append(feature_vector)
                targets.append(target)
            
            if len(features) < 20:
                return {
                    "prediction_available": False,
                    "reason": "Séries temporelles insuffisantes"
                }
            
            # Entraîner le modèle
            features_array = np.array(features)
            targets_array = np.array(targets)
            
            self.models["energy_prediction"].fit(features_array, targets_array)
            
            # Faire des prédictions
            predictions = []
            current_window = consumption_values[-24:]
            current_time = timestamps[-1]
            
            for hour in range(int(prediction_horizon.total_seconds() // 3600)):
                # Préparer les features pour cette heure
                prediction_time = current_time + timedelta(hours=hour+1)
                
                feature_vector = [
                    np.mean(current_window),
                    np.std(current_window),
                    np.min(current_window),
                    np.max(current_window),
                    current_window[-1],
                    np.mean(current_window[-6:]),
                    prediction_time.hour,
                    prediction_time.weekday()
                ]
                
                predicted_consumption = self.models["energy_prediction"].predict([feature_vector])[0]
                
                predictions.append({
                    "timestamp": prediction_time,
                    "predicted_consumption": max(0, predicted_consumption),
                    "confidence": self._calculate_prediction_confidence(features_array, targets_array)
                })
                
                # Mettre à jour la fenêtre
                current_window = current_window[1:] + [predicted_consumption]
            
            # Calculer les statistiques de prédiction
            total_predicted = sum(p["predicted_consumption"] for p in predictions)
            avg_consumption = total_predicted / len(predictions)
            
            return {
                "prediction_available": True,
                "prediction_horizon": prediction_horizon,
                "predictions": predictions,
                "summary": {
                    "total_predicted_consumption": total_predicted,
                    "average_hourly_consumption": avg_consumption,
                    "peak_consumption": max(p["predicted_consumption"] for p in predictions),
                    "low_consumption": min(p["predicted_consumption"] for p in predictions)
                },
                "recommendations": self._generate_energy_optimization_recommendations(predictions)
            }
            
        except Exception as e:
            logger.error(f"Erreur prédiction énergétique: {e}")
            return {
                "prediction_available": False,
                "error": str(e)
            }
    
    # ===== OPTIMISATION ÉNERGÉTIQUE =====
    
    async def optimize_energy_usage(self, target_reduction: float = 0.15) -> Dict[str, Any]:
        """Optimise la consommation énergétique du système"""
        try:
            # Analyser la consommation actuelle
            current_metrics = await self.db.energy_metrics.find({}).sort("timestamp", -1).limit(1).to_list(None)
            
            if not current_metrics:
                return {
                    "optimization_available": False,
                    "reason": "Aucune métrique énergétique disponible"
                }
            
            current_consumption = current_metrics[0].get("total_consumption", 0)
            
            # Récupérer les données détaillées
            detailed_metrics = await self.db.energy_metrics.find({}).sort("timestamp", -1).limit(50).to_list(None)
            
            # Analyser les composants consommateurs
            device_consumption = np.mean([m.get("device_consumption", 0) for m in detailed_metrics])
            network_consumption = np.mean([m.get("network_consumption", 0) for m in detailed_metrics])
            crypto_consumption = np.mean([m.get("crypto_consumption", 0) for m in detailed_metrics])
            idle_consumption = np.mean([m.get("idle_consumption", 0) for m in detailed_metrics])
            
            # Calculer les optimisations possibles
            optimizations = []
            
            # Optimisation des dispositifs
            if device_consumption > current_consumption * 0.4:
                device_savings = device_consumption * 0.2
                optimizations.append({
                    "component": "devices",
                    "current_consumption": device_consumption,
                    "potential_savings": device_savings,
                    "optimization_actions": [
                        "Réduire la fréquence des capteurs non critiques",
                        "Optimiser les cycles de veille",
                        "Implémenter l'adaptive sampling"
                    ]
                })
            
            # Optimisation réseau
            if network_consumption > current_consumption * 0.25:
                network_savings = network_consumption * 0.15
                optimizations.append({
                    "component": "network",
                    "current_consumption": network_consumption,
                    "potential_savings": network_savings,
                    "optimization_actions": [
                        "Compression des données",
                        "Agrégation des transmissions",
                        "Optimisation des protocoles"
                    ]
                })
            
            # Optimisation cryptographique
            if crypto_consumption > current_consumption * 0.3:
                crypto_savings = crypto_consumption * 0.25
                optimizations.append({
                    "component": "cryptography",
                    "current_consumption": crypto_consumption,
                    "potential_savings": crypto_savings,
                    "optimization_actions": [
                        "Utiliser des algorithmes plus efficaces",
                        "Batch processing des opérations crypto",
                        "Hardware acceleration"
                    ]
                })
            
            # Calculer les économies totales
            total_savings = sum(opt["potential_savings"] for opt in optimizations)
            
            # Générer un plan d'optimisation
            optimization_plan = {
                "priority_actions": [],
                "implementation_timeline": []
            }
            
            # Trier par potentiel d'économie
            optimizations.sort(key=lambda x: x["potential_savings"], reverse=True)
            
            for i, opt in enumerate(optimizations):
                optimization_plan["priority_actions"].append({
                    "rank": i + 1,
                    "component": opt["component"],
                    "actions": opt["optimization_actions"][:2],  # Top 2 actions
                    "expected_savings": opt["potential_savings"]
                })
                
                optimization_plan["implementation_timeline"].append({
                    "week": i + 1,
                    "component": opt["component"],
                    "milestone": f"Implémenter optimisations {opt['component']}"
                })
            
            return {
                "optimization_available": True,
                "current_consumption": current_consumption,
                "target_reduction": target_reduction,
                "potential_savings": total_savings,
                "savings_percentage": (total_savings / current_consumption) * 100,
                "meets_target": (total_savings / current_consumption) >= target_reduction,
                "optimizations": optimizations,
                "optimization_plan": optimization_plan,
                "estimated_implementation_time": f"{len(optimizations)} semaines"
            }
            
        except Exception as e:
            logger.error(f"Erreur optimisation énergétique: {e}")
            return {
                "optimization_available": False,
                "error": str(e)
            }
    
    # ===== MÉTHODES UTILITAIRES =====
    
    def _calculate_anomaly_severity(self, anomaly_score: float) -> str:
        """Calcule la sévérité d'une anomalie"""
        if anomaly_score < -0.8:
            return AlertSeverity.CRITICAL.value
        elif anomaly_score < -0.6:
            return AlertSeverity.HIGH.value
        elif anomaly_score < -0.4:
            return AlertSeverity.MEDIUM.value
        else:
            return AlertSeverity.LOW.value
    
    def _calculate_prediction_confidence(self, features: np.ndarray, targets: np.ndarray) -> float:
        """Calcule la confiance d'une prédiction"""
        try:
            # Calculer la variance des erreurs
            if len(features) < 5:
                return 0.5
            
            # Simple heuristique basée sur la variance
            variance = np.var(targets)
            confidence = max(0.1, min(0.9, 1.0 - (variance / (np.mean(targets) + 1e-8))))
            
            return confidence
            
        except Exception:
            return 0.5
    
    def _calculate_risk_level(self, failure_probability: float) -> str:
        """Calcule le niveau de risque"""
        if failure_probability >= 0.8:
            return AlertSeverity.CRITICAL.value
        elif failure_probability >= 0.6:
            return AlertSeverity.HIGH.value
        elif failure_probability >= 0.4:
            return AlertSeverity.MEDIUM.value
        else:
            return AlertSeverity.LOW.value
    
    def _create_time_series_data(self, features: np.ndarray, targets: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Crée des données de séries temporelles"""
        window_size = 5
        X, y = [], []
        
        for i in range(len(features) - window_size):
            X.append(features[i:i+window_size].flatten())
            y.append(targets[i+window_size])
        
        return np.array(X), np.array(y)
    
    def _generate_failure_recommendations(self, features: np.ndarray, failure_prob: float) -> List[str]:
        """Génère des recommandations pour prévenir les pannes"""
        recommendations = []
        
        if failure_prob > 0.7:
            recommendations.append("Planifier une maintenance préventive immédiate")
        
        if features[2] > 75:  # Température
            recommendations.append("Vérifier le système de refroidissement")
        
        if features[3] < 30:  # Batterie
            recommendations.append("Remplacer ou recharger la batterie")
        
        if features[4] > 3:  # Erreurs
            recommendations.append("Investiguer les erreurs système")
        
        return recommendations
    
    def _generate_energy_recommendations(self, energy_features: np.ndarray) -> List[str]:
        """Génère des recommandations d'optimisation énergétique"""
        recommendations = []
        
        if energy_features[0] > 100:  # Consommation totale élevée
            recommendations.append("Optimiser la consommation générale")
        
        if energy_features[3] > energy_features[0] * 0.4:  # Crypto consommation élevée
            recommendations.append("Optimiser les opérations cryptographiques")
        
        if energy_features[6] < 0.7:  # Efficacité faible
            recommendations.append("Améliorer l'efficacité énergétique")
        
        return recommendations
    
    def _generate_energy_optimization_recommendations(self, predictions: List[Dict]) -> List[str]:
        """Génère des recommandations d'optimisation basées sur les prédictions"""
        recommendations = []
        
        # Analyser les patterns de consommation
        consumptions = [p["predicted_consumption"] for p in predictions]
        peak_hours = [p["timestamp"].hour for p in predictions if p["predicted_consumption"] > np.mean(consumptions)]
        
        if peak_hours:
            recommendations.append(f"Éviter les opérations intensives entre {min(peak_hours)}h et {max(peak_hours)}h")
        
        recommendations.append("Programmer les tâches non critiques pendant les heures creuses")
        recommendations.append("Implémenter l'adaptive scaling basé sur les prédictions")
        
        return recommendations
    
    async def _save_anomaly_detection_result(self, device_id: str, 
                                           anomaly_type: AnomalyType, 
                                           anomalies: List[Dict]) -> None:
        """Sauvegarde les résultats de détection d'anomalies"""
        try:
            result = {
                "id": str(uuid.uuid4()),
                "device_id": device_id,
                "anomaly_type": anomaly_type.value,
                "anomalies": anomalies,
                "detection_time": datetime.utcnow(),
                "resolved": False
            }
            
            await self.db.anomaly_detections.insert_one(result)
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde anomalies: {e}")
    
    async def get_ai_analytics_dashboard(self) -> Dict[str, Any]:
        """Récupère les données du tableau de bord AI Analytics"""
        try:
            # Statistiques générales
            anomaly_count = await self.db.anomaly_detections.count_documents({"resolved": False})
            prediction_count = await self.db.ml_predictions.count_documents({})
            
            # Anomalies récentes
            recent_anomalies = await self.db.anomaly_detections.find({
                "detection_time": {"$gte": datetime.utcnow() - timedelta(days=1)}
            }).sort("detection_time", -1).limit(10).to_list(None)
            
            # Prédictions récentes
            recent_predictions = await self.db.ml_predictions.find({}).sort("created_at", -1).limit(5).to_list(None)
            
            return {
                "overview": {
                    "active_anomalies": anomaly_count,
                    "total_predictions": prediction_count,
                    "models_active": len(self.models),
                    "service_health": "healthy" if self.is_ready() else "degraded"
                },
                "recent_anomalies": recent_anomalies,
                "recent_predictions": recent_predictions,
                "model_status": {
                    "anomaly_detection": "active",
                    "failure_prediction": "active",
                    "energy_optimization": "active"
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur dashboard AI Analytics: {e}")
            return {
                "overview": {
                    "active_anomalies": 0,
                    "total_predictions": 0,
                    "models_active": 0,
                    "service_health": "error"
                }
            }
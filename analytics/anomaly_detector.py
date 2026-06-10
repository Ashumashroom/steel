"""
Anomaly Detector — Isolation Forest + LSTM Autoencoder hybrid.
"""
import pickle
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import ANOMALY_CONTAMINATION, SENSOR_DIR, MODELS_DIR, EQUIPMENT, SENSOR_PARAMS
from utils.logger import get_logger

log = get_logger("analytics.anomaly")


class AnomalyDetector:
    """Hybrid anomaly detector using Isolation Forest (+ optional LSTM-AE)."""

    def __init__(self):
        self.models: dict[str, IsolationForest] = {}
        self.scalers: dict[str, StandardScaler] = {}
        MODELS_DIR.mkdir(parents=True, exist_ok=True)

    def train(self, equipment_id: str, data: Optional[pd.DataFrame] = None) -> None:
        """Train Isolation Forest for a specific equipment."""
        if data is None:
            csv_path = SENSOR_DIR / f"{equipment_id}_sensors.csv"
            if not csv_path.exists():
                log.warning(f"No sensor data for {equipment_id}")
                return
            data = pd.read_csv(csv_path)

        etype = EQUIPMENT.get(equipment_id, {}).get("type", "")
        feature_cols = [c for c in SENSOR_PARAMS.get(etype, []) if c in data.columns]
        if not feature_cols:
            return

        X = data[feature_cols].dropna().values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        model = IsolationForest(
            contamination=ANOMALY_CONTAMINATION,
            n_estimators=200,
            random_state=42,
            n_jobs=-1,
        )
        model.fit(X_scaled)

        self.models[equipment_id] = model
        self.scalers[equipment_id] = scaler
        log.info(f"Trained anomaly detector for {equipment_id} on {len(X)} samples")

    def train_all(self) -> None:
        """Train anomaly detectors for all equipment."""
        for eid in EQUIPMENT:
            self.train(eid)
        log.info(f"Trained {len(self.models)} anomaly detection models")

    def detect(self, equipment_id: str, data: pd.DataFrame) -> pd.DataFrame:
        """Detect anomalies in sensor data. Returns DataFrame with anomaly scores."""
        if equipment_id not in self.models:
            self.train(equipment_id)
        if equipment_id not in self.models:
            return data.assign(anomaly_score=0, is_anomaly=False)

        etype = EQUIPMENT.get(equipment_id, {}).get("type", "")
        feature_cols = [c for c in SENSOR_PARAMS.get(etype, []) if c in data.columns]
        X = data[feature_cols].fillna(0).values
        X_scaled = self.scalers[equipment_id].transform(X)

        scores = self.models[equipment_id].decision_function(X_scaled)
        predictions = self.models[equipment_id].predict(X_scaled)

        result = data.copy()
        result["anomaly_score"] = -scores  # Higher = more anomalous
        result["is_anomaly"] = predictions == -1
        return result

    def get_current_status(self, equipment_id: str) -> dict:
        """Get latest anomaly status for an equipment."""
        csv_path = SENSOR_DIR / f"{equipment_id}_sensors.csv"
        if not csv_path.exists():
            return {"status": "no_data", "equipment_id": equipment_id}

        data = pd.read_csv(csv_path)
        result = self.detect(equipment_id, data)
        latest = result.iloc[-1]
        recent_anomalies = result.tail(100)["is_anomaly"].sum()

        return {
            "equipment_id": equipment_id,
            "anomaly_score": float(latest.get("anomaly_score", 0)),
            "is_anomaly": bool(latest.get("is_anomaly", False)),
            "recent_anomaly_rate": float(recent_anomalies / 100),
            "status": "anomalous" if latest.get("is_anomaly", False) else "normal",
        }


# Singleton
_detector = None

def get_detector() -> AnomalyDetector:
    global _detector
    if _detector is None:
        _detector = AnomalyDetector()
        _detector.train_all()
    return _detector

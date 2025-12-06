"""Anomaly detection service."""

from __future__ import annotations

import numpy as np
import pandas as pd

from app.modules.analytics.models import AnomalyResult


class AnomalyService:
    """Service for anomaly detection."""

    def detect_zscore(
        self,
        series: pd.Series,
        threshold: float = 3.0,
    ) -> AnomalyResult:
        """Detect anomalies using Z-score method."""
        clean = series.dropna()
        mean = clean.mean()
        std = clean.std()

        if std == 0:
            return AnomalyResult(
                method="z-score",
                total_points=len(clean),
                anomaly_count=0,
                anomaly_percentage=0.0,
                anomalies=[],
                threshold=threshold,
                interpretation="No variance in data - cannot detect anomalies.",
            )

        z_scores = (clean - mean) / std
        anomaly_mask = np.abs(z_scores) > threshold

        anomalies = []
        for idx in clean[anomaly_mask].index:
            anomalies.append(
                {
                    "index": (
                        int(idx) if isinstance(idx, (int, np.integer)) else str(idx)
                    ),
                    "value": float(clean.loc[idx]),
                    "z_score": float(z_scores.loc[idx]),
                }
            )

        count = len(anomalies)
        pct = (count / len(clean)) * 100

        interpretation = (
            f"Z-score analysis (threshold: {threshold}): Found {count} anomalies "
            f"({pct:.1f}% of data). Mean: {mean:.2f}, Std: {std:.2f}."
        )

        return AnomalyResult(
            method="z-score",
            total_points=len(clean),
            anomaly_count=count,
            anomaly_percentage=round(pct, 2),
            anomalies=anomalies,
            threshold=threshold,
            interpretation=interpretation,
        )

    def detect_iqr(
        self,
        series: pd.Series,
        multiplier: float = 1.5,
    ) -> AnomalyResult:
        """Detect anomalies using IQR method."""
        clean = series.dropna()
        q1 = clean.quantile(0.25)
        q3 = clean.quantile(0.75)
        iqr = q3 - q1

        lower_bound = q1 - multiplier * iqr
        upper_bound = q3 + multiplier * iqr

        anomaly_mask = (clean < lower_bound) | (clean > upper_bound)

        anomalies = []
        for idx in clean[anomaly_mask].index:
            val = clean.loc[idx]
            anomalies.append(
                {
                    "index": (
                        int(idx) if isinstance(idx, (int, np.integer)) else str(idx)
                    ),
                    "value": float(val),
                    "direction": "high" if val > upper_bound else "low",
                }
            )

        count = len(anomalies)
        pct = (count / len(clean)) * 100

        interpretation = (
            f"IQR analysis (multiplier: {multiplier}x): Found {count} anomalies "
            f"({pct:.1f}% of data). Normal range: [{lower_bound:.2f}, {upper_bound:.2f}]."
        )

        return AnomalyResult(
            method="iqr",
            total_points=len(clean),
            anomaly_count=count,
            anomaly_percentage=round(pct, 2),
            anomalies=anomalies,
            threshold=multiplier,
            interpretation=interpretation,
        )

    def detect_isolation_forest(
        self,
        df: pd.DataFrame,
        columns: list[str],
        contamination: float = 0.1,
    ) -> AnomalyResult:
        """Detect anomalies using Isolation Forest."""
        try:
            from sklearn.ensemble import IsolationForest
        except ImportError:
            raise ImportError("scikit-learn required for Isolation Forest")

        data = df[columns].dropna()

        model = IsolationForest(contamination=contamination, random_state=42)
        predictions = model.fit_predict(data)
        scores = model.decision_function(data)

        anomaly_mask = predictions == -1
        anomalies = []

        for idx in data[anomaly_mask].index:
            row = data.loc[idx]
            anomalies.append(
                {
                    "index": (
                        int(idx) if isinstance(idx, (int, np.integer)) else str(idx)
                    ),
                    "values": row.to_dict(),
                    "anomaly_score": float(scores[data.index.get_loc(idx)]),
                }
            )

        count = len(anomalies)
        pct = (count / len(data)) * 100

        interpretation = (
            f"Isolation Forest (contamination: {contamination}): Found {count} anomalies "
            f"({pct:.1f}% of data) using columns: {', '.join(columns)}."
        )

        return AnomalyResult(
            method="isolation_forest",
            total_points=len(data),
            anomaly_count=count,
            anomaly_percentage=round(pct, 2),
            anomalies=anomalies,
            threshold=contamination,
            interpretation=interpretation,
        )

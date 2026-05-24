"""XGBoost ranking model wrapper."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_squared_error


@dataclass
class RankingTrainResult:
    model: xgb.XGBRegressor
    train_rmse: float


def build_ranker() -> xgb.XGBRegressor:
    return xgb.XGBRegressor(
        objective="reg:squarederror",
        n_estimators=120,
        max_depth=4,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42,
    )


def train_ranker(
    features: np.ndarray,
    labels: np.ndarray,
) -> RankingTrainResult:
    model = build_ranker()
    model.fit(features, labels)
    preds = model.predict(features)
    rmse = float(np.sqrt(mean_squared_error(labels, preds)))
    return RankingTrainResult(model=model, train_rmse=rmse)


def predict_ranking_scores(model: xgb.XGBRegressor, features: np.ndarray) -> np.ndarray:
    return model.predict(features)

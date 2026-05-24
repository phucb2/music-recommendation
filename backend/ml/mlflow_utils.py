"""Shared MLflow helpers for model registration and production loading."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

import mlflow
from mlflow.tracking import MlflowClient

logger = logging.getLogger(__name__)

ITEM_MODEL_NAME = "TwoTowerItemEncoder"
USER_MODEL_NAME = "TwoTowerUserEncoder"
RANKING_MODEL_NAME = "XGBoostRanker"
TWO_TOWER_EXPERIMENT = "two-tower"
RANKING_EXPERIMENT = "xgboost-ranking"
ARTIFACTS_SUBDIR = "feature_artifacts"


def configure_mlflow(tracking_uri: str | None = None) -> None:
    uri = tracking_uri or os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5555")
    mlflow.set_tracking_uri(uri)


def transition_to_production(model_name: str, version: str) -> None:
    client = MlflowClient()
    client.set_registered_model_alias(model_name, "Production", version)


def _latest_production_version(model_name: str) -> str | None:
    client = MlflowClient()
    try:
        alias = client.get_model_version_by_alias(model_name, "Production")
        return alias.version
    except Exception as exc:
        logger.warning("get_model_version_by_alias failed for %s: %s", model_name, exc)
    # Fallback: pick the highest version number registered
    try:
        versions = client.search_model_versions(
            f"name='{model_name}'", order_by=["version_number DESC"], max_results=1
        )
        if versions:
            logger.warning(
                "No 'Production' alias for %s; using latest version %s as fallback",
                model_name,
                versions[0].version,
            )
            return versions[0].version
    except Exception as exc:
        logger.warning("search_model_versions failed for %s: %s", model_name, exc)
    return None


def load_production_pytorch_model(model_name: str) -> Any | None:
    version = _latest_production_version(model_name)
    if version is None:
        logger.warning("No Production version found for %s", model_name)
        return None
    model_uri = f"models:/{model_name}/{version}"
    try:
        import mlflow.pytorch

        return mlflow.pytorch.load_model(model_uri)
    except Exception as exc:
        logger.warning("Failed to load %s from MLflow: %s", model_name, exc)
        return None


def load_production_xgboost_model(model_name: str) -> Any | None:
    version = _latest_production_version(model_name)
    if version is None:
        logger.warning("No Production version found for %s", model_name)
        return None
    model_uri = f"models:/{model_name}/{version}"
    try:
        import mlflow.xgboost

        return mlflow.xgboost.load_model(model_uri)
    except Exception as exc:
        logger.warning("Failed to load %s from MLflow: %s", model_name, exc)
        return None


def save_feature_artifacts(run_id: str, artifacts: dict[str, Any]) -> None:
    client = MlflowClient()
    path = Path("feature_artifacts.json")
    path.write_text(json.dumps(artifacts, indent=2), encoding="utf-8")
    client.log_artifact(run_id, str(path), artifact_path=ARTIFACTS_SUBDIR)
    path.unlink(missing_ok=True)


def load_latest_feature_artifacts(model_name: str) -> dict[str, Any] | None:
    version = _latest_production_version(model_name)
    if version is None:
        return None
    client = MlflowClient()
    run_id = client.get_model_version(model_name, version).run_id
    logger.info("Downloading feature_artifacts for %s version=%s run_id=%s", model_name, version, run_id)
    try:
        local_dir = mlflow.artifacts.download_artifacts(
            run_id=run_id,
            artifact_path=ARTIFACTS_SUBDIR,
        )
    except Exception as exc:
        logger.error("download_artifacts failed for %s run_id=%s path=%s: %s", model_name, run_id, ARTIFACTS_SUBDIR, exc)
        raise
    artifact_path = Path(local_dir) / "feature_artifacts.json"
    if not artifact_path.is_file():
        logger.error("feature_artifacts.json not found in %s", local_dir)
        return None
    return json.loads(artifact_path.read_text(encoding="utf-8"))

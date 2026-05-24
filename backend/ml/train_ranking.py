"""Train the XGBoost ranking model and register it in MLflow."""

from __future__ import annotations

import asyncio
import logging
import random
from dataclasses import dataclass

import mlflow
import numpy as np
from mlflow.tracking import MlflowClient
from prisma import Prisma

from app.env_bootstrap import load_repo_environment
from ml.features import (
    FeatureArtifacts,
    build_feature_artifacts,
    ranking_feature_vector,
)
from ml.features import artifacts_to_dict
from ml.mlflow_utils import (
    RANKING_EXPERIMENT,
    RANKING_MODEL_NAME,
    configure_mlflow,
    save_feature_artifacts,
    transition_to_production,
)
from ml.ranking_model import train_ranker

load_repo_environment()
logger = logging.getLogger(__name__)


@dataclass
class RankingExample:
    user_id: str
    song_id: str
    label: float


def _play_ratio(event) -> float:
    if event.play_duration_seconds is None or event.song_duration_seconds is None:
        return 0.0
    if event.song_duration_seconds <= 0:
        return 0.0
    return max(0.0, min(1.0, event.play_duration_seconds / event.song_duration_seconds))


def build_ranking_examples(events, songs_by_id: dict) -> list[RankingExample]:
    examples: list[RankingExample] = []
    for event in events:
        if event.song_id not in songs_by_id:
            continue
        label = _play_ratio(event)
        if label <= 0:
            continue
        examples.append(RankingExample(event.user_id, event.song_id, label))
    return examples


def build_synthetic_ranking_examples(songs, min_examples: int = 32) -> list[RankingExample]:
    rng = random.Random(42)
    examples: list[RankingExample] = []
    user_idx = 0
    for song in songs:
        genre = (song.genre or "others").strip().lower()
        for other in songs:
            same_genre = (other.genre or "others").strip().lower() == genre
            base = 0.75 if same_genre else 0.25
            label = max(0.05, min(0.95, base + rng.uniform(-0.1, 0.1)))
            examples.append(RankingExample(f"synthetic_user_{user_idx}", other.song_id, label))
            user_idx += 1
            if len(examples) >= min_examples:
                return examples
    return examples


async def _load_training_data(prisma: Prisma):
    songs = list(await prisma.song.find_many())
    events = list(await prisma.analyticsevent.find_many())
    songs_by_id = {song.song_id: song for song in songs}
    return songs, events, songs_by_id


async def main_async() -> None:
    configure_mlflow()
    mlflow.set_experiment(RANKING_EXPERIMENT)

    prisma = Prisma()
    await prisma.connect()
    try:
        songs, events, songs_by_id = await _load_training_data(prisma)
        if not songs:
            raise RuntimeError("No songs found. Run seed before training.")

        artifacts = build_feature_artifacts(songs)
        examples = build_ranking_examples(events, songs_by_id)
        if len(examples) < 16:
            logger.warning("Insufficient analytics events; using synthetic ranking examples.")
            examples = build_synthetic_ranking_examples(songs, min_examples=max(32, len(songs) * 4))

        features = []
        labels = []
        for example in examples:
            song = songs_by_id[example.song_id]
            features.append(
                ranking_feature_vector(
                    example.user_id,
                    song,
                    events,
                    songs_by_id,
                    artifacts.genre_vocab,
                    two_tower_score=0.5,
                )
            )
            labels.append(example.label)

        x = np.stack(features)
        y = np.asarray(labels, dtype=np.float32)
        result = train_ranker(x, y)

        with mlflow.start_run(run_name="xgboost-ranking-training") as run:
            mlflow.log_param("num_examples", len(examples))
            mlflow.log_metric("train_rmse", result.train_rmse)
            save_feature_artifacts(run.info.run_id, artifacts_to_dict(artifacts))
            mlflow.xgboost.log_model(
                result.model,
                name="model",
                registered_model_name=RANKING_MODEL_NAME,
            )
            client = MlflowClient()
            versions = client.search_model_versions(
                f"name='{RANKING_MODEL_NAME}'", order_by=["version_number DESC"], max_results=1
            )
            if not versions:
                raise RuntimeError(f"No versions found for model '{RANKING_MODEL_NAME}' after registration")
            version = versions[0].version
            transition_to_production(RANKING_MODEL_NAME, version)
            logger.info("Registered XGBoost ranker. Train RMSE=%.4f", result.train_rmse)
    finally:
        await prisma.disconnect()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main_async())


if __name__ == "__main__":
    main()

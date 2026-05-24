"""Train the two-tower retrieval model and register encoders in MLflow."""

from __future__ import annotations

import asyncio
import logging
import random
from dataclasses import dataclass

import mlflow
import numpy as np
import torch
from mlflow.tracking import MlflowClient
from prisma import Prisma

from app.env_bootstrap import load_repo_environment
from ml.features import (
    FeatureArtifacts,
    artifacts_to_dict,
    build_feature_artifacts,
    item_feature_vector,
    user_feature_vector,
)
from ml.mlflow_utils import (
    ITEM_MODEL_NAME,
    TWO_TOWER_EXPERIMENT,
    USER_MODEL_NAME,
    configure_mlflow,
    save_feature_artifacts,
    transition_to_production,
)
from ml.two_tower_model import TwoTowerModel, infonce_loss

load_repo_environment()
logger = logging.getLogger(__name__)


@dataclass
class TrainingPair:
    user_id: str
    song_id: str


def _play_ratio(event) -> float:
    if event.play_duration_seconds is None or event.song_duration_seconds is None:
        return 0.0
    if event.song_duration_seconds <= 0:
        return 0.0
    return max(0.0, min(1.0, event.play_duration_seconds / event.song_duration_seconds))


def build_training_pairs(events, songs_by_id: dict) -> list[TrainingPair]:
    pairs: list[TrainingPair] = []
    seen: set[tuple[str, str]] = set()
    for event in events:
        if event.song_id not in songs_by_id:
            continue
        if _play_ratio(event) < 0.5:
            continue
        key = (event.user_id, event.song_id)
        if key in seen:
            continue
        seen.add(key)
        pairs.append(TrainingPair(user_id=event.user_id, song_id=event.song_id))
    return pairs


def build_synthetic_pairs(songs, min_pairs: int = 32) -> list[TrainingPair]:
    pairs: list[TrainingPair] = []
    by_genre: dict[str, list] = {}
    for song in songs:
        genre = (song.genre or "others").strip().lower()
        by_genre.setdefault(genre, []).append(song)

    user_idx = 0
    for genre, genre_songs in by_genre.items():
        for song in genre_songs:
            pairs.append(TrainingPair(user_id=f"synthetic_user_{user_idx}", song_id=song.song_id))
            user_idx += 1
            for other in genre_songs:
                if other.song_id != song.song_id:
                    pairs.append(
                        TrainingPair(user_id=f"synthetic_user_{user_idx}", song_id=other.song_id)
                    )
                    user_idx += 1
                if len(pairs) >= min_pairs:
                    return pairs
    return pairs


def train_two_tower(
    pairs: list[TrainingPair],
    songs_by_id: dict,
    events,
    artifacts: FeatureArtifacts,
    epochs: int = 40,
    batch_size: int = 16,
    learning_rate: float = 1e-3,
) -> tuple[TwoTowerModel, float]:
    model = TwoTowerModel(artifacts.item_input_dim, artifacts.user_input_dim)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    rng = random.Random(42)
    final_loss = 0.0

    for _ in range(epochs):
        rng.shuffle(pairs)
        batch_losses: list[float] = []
        for start in range(0, len(pairs), batch_size):
            batch = pairs[start : start + batch_size]
            if len(batch) < 2:
                continue

            user_feats = []
            item_feats = []
            for pair in batch:
                song = songs_by_id[pair.song_id]
                user_feats.append(
                    user_feature_vector(pair.user_id, events, songs_by_id, artifacts.genre_vocab)
                )
                item_feats.append(item_feature_vector(song, artifacts.genre_vocab))

            user_tensor = torch.tensor(np.stack(user_feats), dtype=torch.float32)
            item_tensor = torch.tensor(np.stack(item_feats), dtype=torch.float32)
            user_emb, item_emb = model(user_tensor, item_tensor)
            loss = infonce_loss(user_emb, item_emb)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            batch_losses.append(float(loss.item()))

        if batch_losses:
            final_loss = float(np.mean(batch_losses))

    return model, final_loss


async def _load_training_data(prisma: Prisma):
    songs = list(await prisma.song.find_many())
    events = list(await prisma.analyticsevent.find_many())
    songs_by_id = {song.song_id: song for song in songs}
    return songs, events, songs_by_id


def _latest_version(client: MlflowClient, model_name: str) -> str:
    versions = client.search_model_versions(f"name='{model_name}'", order_by=["version_number DESC"], max_results=1)
    if not versions:
        raise RuntimeError(f"No versions found for model '{model_name}' after registration")
    return versions[0].version


def _register_models(model: TwoTowerModel, run_id: str) -> None:
    import mlflow.pytorch

    mlflow.pytorch.log_model(
        model.item_tower,
        name="item_tower",
        registered_model_name=ITEM_MODEL_NAME,
    )
    mlflow.pytorch.log_model(
        model.user_tower,
        name="user_tower",
        registered_model_name=USER_MODEL_NAME,
    )
    client = MlflowClient()
    item_version = _latest_version(client, ITEM_MODEL_NAME)
    user_version = _latest_version(client, USER_MODEL_NAME)
    transition_to_production(ITEM_MODEL_NAME, item_version)
    transition_to_production(USER_MODEL_NAME, user_version)
    _ = run_id


async def main_async() -> None:
    configure_mlflow()
    mlflow.set_experiment(TWO_TOWER_EXPERIMENT)

    prisma = Prisma()
    await prisma.connect()
    try:
        songs, events, songs_by_id = await _load_training_data(prisma)
        if not songs:
            raise RuntimeError("No songs found. Run seed before training.")

        artifacts = build_feature_artifacts(songs)
        pairs = build_training_pairs(events, songs_by_id)
        if len(pairs) < 8:
            logger.warning("Insufficient analytics events; using synthetic genre pairs.")
            pairs = build_synthetic_pairs(songs, min_pairs=max(16, len(songs) * 2))

        model, final_loss = train_two_tower(pairs, songs_by_id, events, artifacts)
        with mlflow.start_run(run_name="two-tower-training") as run:
            mlflow.log_param("epochs", 40)
            mlflow.log_param("batch_size", 16)
            mlflow.log_param("num_pairs", len(pairs))
            mlflow.log_param("item_input_dim", artifacts.item_input_dim)
            mlflow.log_param("user_input_dim", artifacts.user_input_dim)
            mlflow.log_metric("final_infonce_loss", final_loss)
            save_feature_artifacts(run.info.run_id, artifacts_to_dict(artifacts))
            _register_models(model, run.info.run_id)
            logger.info("Registered two-tower models. Final loss=%.4f", final_loss)
    finally:
        await prisma.disconnect()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main_async())


if __name__ == "__main__":
    main()

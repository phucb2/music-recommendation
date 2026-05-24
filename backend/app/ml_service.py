"""Online ML recommendation service: two-tower retrieval + XGBoost re-ranking."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
import torch
from prisma import Prisma
from prisma.models import Song

from app.config import settings
from ml.features import (
    FeatureArtifacts,
    artifacts_from_dict,
    item_feature_vector,
    ranking_feature_vector,
    user_feature_vector,
)
from ml.mlflow_utils import (
    ITEM_MODEL_NAME,
    RANKING_MODEL_NAME,
    USER_MODEL_NAME,
    configure_mlflow,
    load_latest_feature_artifacts,
    load_production_pytorch_model,
    load_production_xgboost_model,
)
from ml.ranking_model import predict_ranking_scores

logger = logging.getLogger(__name__)


@dataclass
class MLRuntime:
    ready: bool = False
    item_tower: torch.nn.Module | None = None
    user_tower: torch.nn.Module | None = None
    ranker: object | None = None
    artifacts: FeatureArtifacts | None = None

    def load_models_sync(self) -> None:
        configure_mlflow(settings.mlflow_tracking_uri)
        artifact_payload = load_latest_feature_artifacts(ITEM_MODEL_NAME)
        item_tower = load_production_pytorch_model(ITEM_MODEL_NAME)
        user_tower = load_production_pytorch_model(USER_MODEL_NAME)
        ranker = load_production_xgboost_model(RANKING_MODEL_NAME)

        if artifact_payload is None or item_tower is None or user_tower is None or ranker is None:
            logger.warning("ML models not fully available; falling back to deterministic recommendations.")
            self.ready = False
            return

        self.artifacts = artifacts_from_dict(artifact_payload)
        self.item_tower = item_tower.eval()
        self.user_tower = user_tower.eval()
        self.ranker = ranker
        self.ready = True
        logger.info("Loaded ML recommendation models from MLflow.")

    async def load_models(self) -> None:
        import asyncio

        await asyncio.to_thread(self.load_models_sync)

    def _encode_user(self, user_features: np.ndarray) -> np.ndarray:
        assert self.user_tower is not None
        with torch.no_grad():
            tensor = torch.tensor(user_features, dtype=torch.float32).unsqueeze(0)
            return self.user_tower(tensor).squeeze(0).cpu().numpy()

    async def _vector_search(
        self,
        prisma: Prisma,
        user_embedding: np.ndarray,
        limit: int = 100,
        exclude_song_id: str | None = None,
    ) -> list[tuple[str, float]]:
        vector_literal = "[" + ",".join(f"{float(v):.8f}" for v in user_embedding.tolist()) + "]"
        if exclude_song_id:
            rows = await prisma.query_raw(
                """
                SELECT song_id, 1 - (embedding <=> $1::vector) AS score
                FROM songs
                WHERE embedding IS NOT NULL AND song_id <> $2
                ORDER BY embedding <=> $1::vector
                LIMIT $3
                """,
                vector_literal,
                exclude_song_id,
                limit,
            )
        else:
            rows = await prisma.query_raw(
                """
                SELECT song_id, 1 - (embedding <=> $1::vector) AS score
                FROM songs
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> $1::vector
                LIMIT $2
                """,
                vector_literal,
                limit,
            )

        return [(row["song_id"], float(row["score"])) for row in rows]

    async def recommend_home(
        self,
        prisma: Prisma,
        user_id: str,
        limit: int = 10,
    ) -> list[Song]:
        if not self.ready or self.artifacts is None:
            return []

        songs = list(await prisma.song.find_many())
        events = list(
            await prisma.analyticsevent.find_many(where={"user_id": user_id})
        )
        songs_by_id = {song.song_id: song for song in songs}
        user_features = user_feature_vector(user_id, events, songs_by_id, self.artifacts.genre_vocab)
        user_embedding = self._encode_user(user_features)
        candidates = await self._vector_search(prisma, user_embedding, limit=100)
        if not candidates:
            return []

        ranked = self._rerank(user_id, candidates, songs_by_id, events)
        top_ids = [song_id for song_id, _ in ranked[:limit]]
        ordered = [songs_by_id[song_id] for song_id in top_ids if song_id in songs_by_id]
        return ordered

    async def recommend_next(
        self,
        prisma: Prisma,
        user_id: str,
        current_song_id: str,
        limit: int = 6,
    ) -> list[Song]:
        if not self.ready or self.artifacts is None:
            return []

        songs = list(await prisma.song.find_many())
        events = list(
            await prisma.analyticsevent.find_many(where={"user_id": user_id})
        )
        songs_by_id = {song.song_id: song for song in songs}
        current = songs_by_id.get(current_song_id)
        if current is None:
            return []

        item_features = item_feature_vector(current, self.artifacts.genre_vocab)
        assert self.item_tower is not None
        with torch.no_grad():
            tensor = torch.tensor(item_features, dtype=torch.float32).unsqueeze(0)
            seed_embedding = self.item_tower(tensor).squeeze(0).cpu().numpy()

        candidates = await self._vector_search(
            prisma,
            seed_embedding,
            limit=100,
            exclude_song_id=current_song_id,
        )
        if not candidates:
            return []

        ranked = self._rerank(user_id, candidates, songs_by_id, events)
        top_ids = [song_id for song_id, _ in ranked[:limit]]
        return [songs_by_id[song_id] for song_id in top_ids if song_id in songs_by_id]

    def _rerank(
        self,
        user_id: str,
        candidates: list[tuple[str, float]],
        songs_by_id: dict[str, Song],
        events,
    ) -> list[tuple[str, float]]:
        assert self.ranker is not None
        assert self.artifacts is not None

        features = []
        song_ids = []
        for song_id, two_tower_score in candidates:
            song = songs_by_id.get(song_id)
            if song is None:
                continue
            features.append(
                ranking_feature_vector(
                    user_id,
                    song,
                    events,
                    songs_by_id,
                    self.artifacts.genre_vocab,
                    two_tower_score=two_tower_score,
                )
            )
            song_ids.append(song_id)

        if not features:
            return []

        scores = predict_ranking_scores(self.ranker, np.stack(features))
        ranked = sorted(zip(song_ids, scores.tolist()), key=lambda item: item[1], reverse=True)
        return ranked


ml_runtime = MLRuntime()

"""Generate song embeddings with the item tower and store them in pgvector."""

from __future__ import annotations

import asyncio
import logging

import asyncpg
import numpy as np
import torch
from prisma import Prisma

from app.config import settings
from app.env_bootstrap import load_repo_environment
from ml.features import artifacts_from_dict, item_feature_vector
from ml.mlflow_utils import ITEM_MODEL_NAME, configure_mlflow, load_latest_feature_artifacts, load_production_pytorch_model

load_repo_environment()
logger = logging.getLogger(__name__)


def _vector_literal(values: np.ndarray) -> str:
    return "[" + ",".join(f"{float(v):.8f}" for v in values.tolist()) + "]"


async def upsert_embeddings(rows: list[tuple[str, str]]) -> None:
    db_url = settings.direct_url or settings.database_url
    conn = await asyncpg.connect(dsn=db_url)
    try:
        async with conn.transaction():
            for song_id, embedding in rows:
                await conn.execute(
                    "UPDATE songs SET embedding = $1::vector WHERE song_id = $2",
                    embedding,
                    song_id,
                )
    finally:
        await conn.close()


async def main_async() -> None:
    configure_mlflow()
    artifact_payload = load_latest_feature_artifacts(ITEM_MODEL_NAME)
    if artifact_payload is None:
        raise RuntimeError("Feature artifacts not found. Train the two-tower model first.")

    item_tower = load_production_pytorch_model(ITEM_MODEL_NAME)
    if item_tower is None:
        raise RuntimeError("TwoTowerItemEncoder Production model not found.")

    artifacts = artifacts_from_dict(artifact_payload)
    item_tower.eval()

    prisma = Prisma()
    await prisma.connect()
    try:
        songs = list(await prisma.song.find_many())
        if not songs:
            raise RuntimeError("No songs found.")

        rows: list[tuple[str, str]] = []
        with torch.no_grad():
            for song in songs:
                features = item_feature_vector(song, artifacts.genre_vocab)
                tensor = torch.tensor(features, dtype=torch.float32).unsqueeze(0)
                embedding = item_tower(tensor).squeeze(0).cpu().numpy()
                rows.append((song.song_id, _vector_literal(embedding)))

        await upsert_embeddings(rows)
        logger.info("Updated embeddings for %d songs.", len(rows))
    finally:
        await prisma.disconnect()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main_async())


if __name__ == "__main__":
    main()

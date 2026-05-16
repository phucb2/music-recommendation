"""Content-based KNN music recommendation using MinMaxScaler + cosine similarity."""

from __future__ import annotations

import logging
from functools import lru_cache

import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Song

logger = logging.getLogger(__name__)

# Audio features used by the KNN model
AUDIO_FEATURES = [
    "danceability",
    "energy",
    "tempo",
    "valence",
    "acousticness",
]


class KNNRecommender:
    """Builds and caches a KNN model from all songs in the database."""

    def __init__(self) -> None:
        self._song_ids: list[str] = []
        self._scaler = MinMaxScaler()
        self._knn = NearestNeighbors(metric="cosine")
        self._X_scaled: np.ndarray | None = None
        self._fitted = False

    def fit(self, songs: list[Song]) -> None:
        """Fit the model on all songs that have audio features."""
        valid_songs = [
            s for s in songs
            if all(getattr(s, f) is not None for f in AUDIO_FEATURES)
        ]
        if not valid_songs:
            logger.warning("No songs with audio features found – KNN not fitted.")
            self._fitted = False
            return

        self._song_ids = [s.song_id for s in valid_songs]
        X = np.array([[getattr(s, f) for f in AUDIO_FEATURES] for s in valid_songs])

        self._X_scaled = self._scaler.fit_transform(X)
        n = len(valid_songs)
        self._knn.set_params(n_neighbors=min(n, 10))
        self._knn.fit(self._X_scaled)
        self._fitted = True
        logger.info("KNN recommender fitted on %d songs.", n)

    def similar(self, song_id: str, top_n: int = 6) -> list[tuple[str, float]]:
        """Return (song_id, similarity_score) for the top_n most similar songs."""
        if not self._fitted or self._X_scaled is None:
            return []
        if song_id not in self._song_ids:
            return []

        idx = self._song_ids.index(song_id)
        k = min(top_n + 1, len(self._song_ids))
        distances, indices = self._knn.kneighbors([self._X_scaled[idx]], n_neighbors=k)

        results: list[tuple[str, float]] = []
        for i, dist in zip(indices[0], distances[0]):
            if self._song_ids[i] == song_id:
                continue
            results.append((self._song_ids[i], round(1 - dist, 4)))
        return results[:top_n]


# Module-level singleton
_recommender = KNNRecommender()


def _ensure_fitted(db: Session) -> KNNRecommender:
    """Lazy-fit the KNN model on first call (or if not yet fitted)."""
    if not _recommender._fitted:
        rows = list(db.scalars(select(Song)).all())
        _recommender.fit(rows)
    return _recommender


def rebuild_model(db: Session) -> None:
    """Force re-fit (call after seeding or adding songs)."""
    rows = list(db.scalars(select(Song)).all())
    _recommender.fit(rows)


# ── Public API used by the router ────────────────────────────────────────


def home_recommendations(db: Session, user_id: str) -> list[Song]:
    """Return personalised-ish homepage list.

    Strategy: pick a deterministic seed song per user, then return its KNN
    neighbours so the homepage feels personalised.  Falls back to all songs
    sorted by id when audio features are missing.
    """
    all_songs = list(db.scalars(select(Song).order_by(Song.song_id)).all())
    if not all_songs:
        return []

    rec = _ensure_fitted(db)

    # Deterministic seed: hash user_id to pick a "liked" song
    seed_idx = abs(hash(user_id)) % len(all_songs)
    seed_song = all_songs[seed_idx]

    similar = rec.similar(seed_song.song_id, top_n=10)
    if not similar:
        # Fallback: return all songs
        return [all_songs[seed_idx], *all_songs[:10]]

    id_to_song = {s.song_id: s for s in all_songs}
    result = [seed_song]
    for sid, _score in similar:
        if sid in id_to_song:
            result.append(id_to_song[sid])

    return result


def next_songs(db: Session, current_song_id: str, limit: int = 6) -> list[Song]:
    """Return KNN-based 'up next' songs for the player."""
    rec = _ensure_fitted(db)
    similar = rec.similar(current_song_id, top_n=limit)

    if similar:
        all_songs = {
            s.song_id: s
            for s in db.scalars(select(Song)).all()
        }
        return [all_songs[sid] for sid, _ in similar if sid in all_songs]

    # Fallback: ordered list excluding current
    rows = list(
        db.scalars(
            select(Song).where(Song.song_id != current_song_id).order_by(Song.song_id)
        ).all()
    )
    return rows[:limit]


def similar_songs(
    db: Session, song_id: str, top_n: int = 6,
) -> list[dict]:
    """Return similar songs with similarity scores (for the /similar endpoint)."""
    rec = _ensure_fitted(db)
    pairs = rec.similar(song_id, top_n=top_n)

    all_songs = {s.song_id: s for s in db.scalars(select(Song)).all()}
    results = []
    for sid, score in pairs:
        song = all_songs.get(sid)
        if song:
            results.append({
                "song": song,
                "similarity_score": score,
            })
    return results

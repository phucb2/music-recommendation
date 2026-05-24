"""Feature extraction for two-tower retrieval and XGBoost ranking."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from prisma.models import AnalyticsEvent, Song

AUDIO_FEATURE_NAMES: tuple[str, ...] = (
    "popularity",
    "danceability",
    "energy",
    "loudness",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
)

DEFAULT_AUDIO_FEATURES: dict[str, float] = {
    "popularity": 50.0,
    "danceability": 0.5,
    "energy": 0.5,
    "loudness": -10.0,
    "speechiness": 0.05,
    "acousticness": 0.5,
    "instrumentalness": 0.0,
    "liveness": 0.1,
    "valence": 0.5,
    "tempo": 120.0,
}


@dataclass(frozen=True)
class FeatureArtifacts:
    genre_vocab: list[str]
    item_input_dim: int
    user_input_dim: int


def _audio_vector(song: Song, normalized: bool = True) -> np.ndarray:
    values: list[float] = []
    for name in AUDIO_FEATURE_NAMES:
        raw = getattr(song, name, None)
        if raw is None:
            raw = DEFAULT_AUDIO_FEATURES[name]
        values.append(float(raw))

    arr = np.asarray(values, dtype=np.float32)
    if not normalized:
        return arr

    # Scale popularity and tempo to roughly [0, 1] for neural towers.
    arr[0] = arr[0] / 100.0
    arr[9] = arr[9] / 200.0
    return arr


def build_genre_vocab(songs: list[Song]) -> list[str]:
    genres = sorted({song.genre.strip().lower() for song in songs if song.genre})
    return genres or ["others"]


def genre_one_hot(genre: str, genre_vocab: list[str]) -> np.ndarray:
    vec = np.zeros(len(genre_vocab), dtype=np.float32)
    key = (genre or "others").strip().lower()
    if key in genre_vocab:
        vec[genre_vocab.index(key)] = 1.0
    elif "others" in genre_vocab:
        vec[genre_vocab.index("others")] = 1.0
    return vec


def build_feature_artifacts(songs: list[Song]) -> FeatureArtifacts:
    genre_vocab = build_genre_vocab(songs)
    item_input_dim = len(AUDIO_FEATURE_NAMES) + len(genre_vocab)
    user_input_dim = item_input_dim + 2
    return FeatureArtifacts(
        genre_vocab=genre_vocab,
        item_input_dim=item_input_dim,
        user_input_dim=user_input_dim,
    )


def item_feature_vector(song: Song, genre_vocab: list[str]) -> np.ndarray:
    audio = _audio_vector(song, normalized=True)
    genre = genre_one_hot(song.genre, genre_vocab)
    return np.concatenate([audio, genre]).astype(np.float32)


def _play_ratio(event: AnalyticsEvent) -> float:
    if event.play_duration_seconds is None or event.song_duration_seconds is None:
        return 0.0
    if event.song_duration_seconds <= 0:
        return 0.0
    return float(max(0.0, min(1.0, event.play_duration_seconds / event.song_duration_seconds)))


def user_history_stats(
    user_id: str,
    events: list[AnalyticsEvent],
    songs_by_id: dict[str, Song],
    genre_vocab: list[str],
) -> tuple[np.ndarray, float, float, str | None]:
    user_events = [event for event in events if event.user_id == user_id]
    if not user_events:
        zeros = np.zeros(len(AUDIO_FEATURE_NAMES) + len(genre_vocab) + 2, dtype=np.float32)
        return zeros, 0.0, 0.0, None

    weighted_audio = np.zeros(len(AUDIO_FEATURE_NAMES), dtype=np.float64)
    genre_counts = np.zeros(len(genre_vocab), dtype=np.float64)
    total_weight = 0.0
    play_ratios: list[float] = []

    for event in user_events:
        song = songs_by_id.get(event.song_id)
        if song is None:
            continue
        ratio = _play_ratio(event)
        weight = max(ratio, 0.05)
        weighted_audio += _audio_vector(song, normalized=True) * weight
        genre = (song.genre or "others").strip().lower()
        if genre in genre_vocab:
            genre_counts[genre_vocab.index(genre)] += weight
        total_weight += weight
        play_ratios.append(ratio)

    if total_weight <= 0:
        zeros = np.zeros(len(AUDIO_FEATURE_NAMES) + len(genre_vocab) + 2, dtype=np.float32)
        return zeros, 0.0, float(len(user_events)), None

    audio_avg = (weighted_audio / total_weight).astype(np.float32)
    genre_pref = (genre_counts / total_weight).astype(np.float32)
    avg_play_ratio = float(np.mean(play_ratios)) if play_ratios else 0.0
    total_plays = float(len(user_events))
    top_genre_idx = int(np.argmax(genre_pref)) if genre_pref.sum() > 0 else -1
    top_genre = genre_vocab[top_genre_idx] if top_genre_idx >= 0 else None

    stats = np.asarray([avg_play_ratio, min(total_plays / 100.0, 1.0)], dtype=np.float32)
    vector = np.concatenate([audio_avg, genre_pref, stats]).astype(np.float32)
    return vector, avg_play_ratio, total_plays, top_genre


def user_feature_vector(
    user_id: str,
    events: list[AnalyticsEvent],
    songs_by_id: dict[str, Song],
    genre_vocab: list[str],
) -> np.ndarray:
    vector, _, _, _ = user_history_stats(user_id, events, songs_by_id, genre_vocab)
    return vector


def ranking_feature_vector(
    user_id: str,
    song: Song,
    events: list[AnalyticsEvent],
    songs_by_id: dict[str, Song],
    genre_vocab: list[str],
    two_tower_score: float = 0.0,
) -> np.ndarray:
    _, avg_play_ratio, total_plays, top_genre = user_history_stats(
        user_id, events, songs_by_id, genre_vocab
    )
    audio = _audio_vector(song, normalized=False)
    popularity = float(song.popularity if song.popularity is not None else DEFAULT_AUDIO_FEATURES["popularity"])
    song_genre = (song.genre or "others").strip().lower()
    genre_match = 1.0 if top_genre is not None and song_genre == top_genre else 0.0
    return np.asarray(
        [
            avg_play_ratio,
            min(total_plays / 100.0, 1.0),
            genre_match,
            popularity / 100.0,
            *audio.tolist(),
            two_tower_score,
        ],
        dtype=np.float32,
    )


def ranking_feature_names() -> list[str]:
    return [
        "avg_play_ratio",
        "total_plays_norm",
        "genre_match",
        "popularity_norm",
        *AUDIO_FEATURE_NAMES,
        "two_tower_score",
    ]


def artifacts_to_dict(artifacts: FeatureArtifacts) -> dict[str, Any]:
    return {
        "genre_vocab": artifacts.genre_vocab,
        "item_input_dim": artifacts.item_input_dim,
        "user_input_dim": artifacts.user_input_dim,
    }


def artifacts_from_dict(payload: dict[str, Any]) -> FeatureArtifacts:
    return FeatureArtifacts(
        genre_vocab=list(payload["genre_vocab"]),
        item_input_dim=int(payload["item_input_dim"]),
        user_input_dim=int(payload["user_input_dim"]),
    )

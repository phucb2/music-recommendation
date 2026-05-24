"""Idempotent seed: demo user and catalog tracks (run after migrations)."""

from __future__ import annotations

import asyncio

from app.env_bootstrap import load_repo_environment
from prisma import Prisma

load_repo_environment()

GENRE_SENTINEL = "others"

CATALOG_ROWS: list[dict] = [
    {
        "song_id": "s1",
        "title": "Midnight Hall",
        "author": "Maya Ortiz",
        "singer": "The Amber Keys",
        "genre": "Indie rock",
        "artwork_url": "https://picsum.photos/seed/midnight/400/400",
        "duration_seconds": 372,
        "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
        "popularity": 68.0,
        "danceability": 0.58,
        "energy": 0.79,
        "loudness": -7.2,
        "speechiness": 0.04,
        "acousticness": 0.22,
        "instrumentalness": 0.01,
        "liveness": 0.14,
        "valence": 0.46,
        "tempo": 128.0,
    },
    {
        "song_id": "s2",
        "title": "Velvet Stage",
        "author": "Jonah Reeves & Lina Cho",
        "singer": "Luna Quartet",
        "genre": "Contemporary jazz",
        "artwork_url": "https://picsum.photos/seed/velvet/400/400",
        "duration_seconds": 398,
        "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
        "popularity": 61.0,
        "danceability": 0.52,
        "energy": 0.41,
        "loudness": -11.8,
        "speechiness": 0.06,
        "acousticness": 0.63,
        "instrumentalness": 0.42,
        "liveness": 0.18,
        "valence": 0.55,
        "tempo": 96.0,
    },
    {
        "song_id": "s3",
        "title": "Slow Spotlight",
        "author": "Elena Voss",
        "singer": "Nora Grey",
        "genre": "Soul",
        "artwork_url": "https://picsum.photos/seed/spotlight/400/400",
        "duration_seconds": 421,
        "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
        "popularity": 74.0,
        "danceability": 0.67,
        "energy": 0.48,
        "loudness": -8.9,
        "speechiness": 0.05,
        "acousticness": 0.35,
        "instrumentalness": 0.0,
        "liveness": 0.11,
        "valence": 0.62,
        "tempo": 88.0,
    },
    {
        "song_id": "s4",
        "title": "Brass Echo",
        "author": "Marcus Bell",
        "singer": "Harbor Brass",
        "genre": "Brass band",
        "artwork_url": "https://picsum.photos/seed/brass/400/400",
        "duration_seconds": 350,
        "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
        "popularity": 55.0,
        "danceability": 0.49,
        "energy": 0.72,
        "loudness": -6.5,
        "speechiness": 0.07,
        "acousticness": 0.18,
        "instrumentalness": 0.55,
        "liveness": 0.24,
        "valence": 0.71,
        "tempo": 112.0,
    },
    {
        "song_id": "s5",
        "title": "Side Door",
        "author": "Priya Nair",
        "singer": "Metro Fiction",
        "genre": "Alternative",
        "artwork_url": "https://picsum.photos/seed/sidedoor/400/400",
        "duration_seconds": 405,
        "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3",
        "popularity": 63.0,
        "danceability": 0.61,
        "energy": 0.76,
        "loudness": -7.8,
        "speechiness": 0.03,
        "acousticness": 0.12,
        "instrumentalness": 0.02,
        "liveness": 0.16,
        "valence": 0.44,
        "tempo": 132.0,
    },
    {
        "song_id": "s6",
        "title": "Encore Whisper",
        "author": "Chris Yamamoto",
        "singer": "Soft Voltage",
        "genre": "Electronic",
        "artwork_url": "https://picsum.photos/seed/encore/400/400",
        "duration_seconds": 388,
        "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3",
        "popularity": 71.0,
        "danceability": 0.74,
        "energy": 0.83,
        "loudness": -5.9,
        "speechiness": 0.05,
        "acousticness": 0.08,
        "instrumentalness": 0.67,
        "liveness": 0.09,
        "valence": 0.58,
        "tempo": 124.0,
    },
    {
        "song_id": "s7",
        "title": "Crowd Fade",
        "author": "Sam Okonkwo",
        "singer": "Analog Tides",
        "genre": "Ambient rock",
        "artwork_url": "https://picsum.photos/seed/crowd/400/400",
        "duration_seconds": 410,
        "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-7.mp3",
        "popularity": 59.0,
        "danceability": 0.43,
        "energy": 0.57,
        "loudness": -10.4,
        "speechiness": 0.04,
        "acousticness": 0.48,
        "instrumentalness": 0.21,
        "liveness": 0.13,
        "valence": 0.37,
        "tempo": 102.0,
    },
    {
        "song_id": "s8",
        "title": "House Lights",
        "author": "Dana Frost",
        "singer": "Circuit Choir",
        "genre": "others",
        "artwork_url": "https://picsum.photos/seed/houselights/400/400",
        "duration_seconds": 365,
        "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3",
        "popularity": 52.0,
        "danceability": 0.55,
        "energy": 0.64,
        "loudness": -9.1,
        "speechiness": 0.08,
        "acousticness": 0.27,
        "instrumentalness": 0.04,
        "liveness": 0.2,
        "valence": 0.49,
        "tempo": 118.0,
    },
]

_OPTIONAL_SONG_KEYS = (
    "subgenre",
    "language",
    "release_year",
    "album_id",
    "artist_id",
    "featured_artists",
    "region",
    "explicit_content",
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


def _normalize_genre(row: dict) -> str:
    g = row.get("genre")
    if g is None:
        return GENRE_SENTINEL
    s = str(g).strip()
    return s if s else GENRE_SENTINEL


def _song_row_to_values(row: dict) -> dict:
    required = (
        "song_id",
        "title",
        "author",
        "singer",
        "artwork_url",
        "duration_seconds",
        "audio_url",
    )
    out = {k: row[k] for k in required}
    out["genre"] = _normalize_genre(row)
    for k in _OPTIONAL_SONG_KEYS:
        out[k] = row.get(k)
    return out


async def _run_async() -> None:
    prisma = Prisma()
    await prisma.connect()
    try:
        await prisma.user.upsert(
            where={"user_id": "user_demo"},
            data={
                "create": {
                    "user_id": "user_demo",
                    "username": "demo",
                    "password_hash": None,
                },
                "update": {"username": "demo"},
            },
        )
        for row in CATALOG_ROWS:
            v = _song_row_to_values(row)
            sid = v["song_id"]
            update = {k: val for k, val in v.items() if k != "song_id"}
            await prisma.song.upsert(
                where={"song_id": sid},
                data={
                    "create": v,
                    "update": update,
                },
            )
    finally:
        await prisma.disconnect()


def run() -> None:
    asyncio.run(_run_async())


if __name__ == "__main__":
    run()

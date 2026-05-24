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
    },
    {
        "song_id": "s8",
        "title": "House Lights",
        "author": "Dana Frost",
        "singer": "Circuit Choir",
        "artwork_url": "https://picsum.photos/seed/houselights/400/400",
        "duration_seconds": 365,
        "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3",
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

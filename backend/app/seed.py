"""Idempotent seed: demo user and catalog tracks (run after migrations)."""

from __future__ import annotations

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models import Song, User

GENRE_SENTINEL = "others"

# Canonical catalog: optional keys may be absent → NULL in DB; missing `genre` → GENRE_SENTINEL.
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
        "danceability": 0.55,
        "energy": 0.72,
        "tempo": 128.0,
        "valence": 0.45,
        "acousticness": 0.12,
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
        "danceability": 0.42,
        "energy": 0.35,
        "tempo": 95.0,
        "valence": 0.68,
        "acousticness": 0.78,
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
        "danceability": 0.60,
        "energy": 0.45,
        "tempo": 88.0,
        "valence": 0.72,
        "acousticness": 0.65,
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
        "danceability": 0.70,
        "energy": 0.80,
        "tempo": 140.0,
        "valence": 0.82,
        "acousticness": 0.30,
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
        "danceability": 0.48,
        "energy": 0.65,
        "tempo": 120.0,
        "valence": 0.38,
        "acousticness": 0.20,
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
        "danceability": 0.78,
        "energy": 0.85,
        "tempo": 135.0,
        "valence": 0.55,
        "acousticness": 0.05,
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
        "danceability": 0.35,
        "energy": 0.50,
        "tempo": 105.0,
        "valence": 0.30,
        "acousticness": 0.45,
    },
    {
        "song_id": "s8",
        "title": "House Lights",
        "author": "Dana Frost",
        "singer": "Circuit Choir",
        "artwork_url": "https://picsum.photos/seed/houselights/400/400",
        "duration_seconds": 365,
        "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3",
        "genre": "Electronic",
        "danceability": 0.82,
        "energy": 0.90,
        "tempo": 130.0,
        "valence": 0.60,
        "acousticness": 0.03,
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


def _is_postgres() -> bool:
    u = settings.database_url.lower()
    return u.startswith("postgresql") or "+psycopg2" in u or "+asyncpg" in u


def _normalize_genre(row: dict) -> str:
    g = row.get("genre")
    if g is None:
        return GENRE_SENTINEL
    s = str(g).strip()
    return s if s else GENRE_SENTINEL


def _song_row_to_values(row: dict) -> dict:
    """Full row for Song: missing optional keys become None; genre never NULL (see GENRE_SENTINEL)."""
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


def _seed_users(session: Session) -> None:
    if _is_postgres():
        stmt = (
            pg_insert(User)
            .values(user_id="user_demo", username="demo", password_hash=None)
            .on_conflict_do_nothing(index_elements=["user_id"])
        )
        session.execute(stmt)
        return
    if session.get(User, "user_demo") is None:
        session.add(User(user_id="user_demo", username="demo", password_hash=None))


def _seed_songs_postgres(session: Session) -> None:
    for row in CATALOG_ROWS:
        v = _song_row_to_values(row)
        insert_stmt = pg_insert(Song).values(**v)
        set_ = {k: getattr(insert_stmt.excluded, k) for k in v if k != "song_id"}
        stmt = insert_stmt.on_conflict_do_update(index_elements=["song_id"], set_=set_)
        session.execute(stmt)


def _seed_songs_generic(session: Session) -> None:
    for row in CATALOG_ROWS:
        v = _song_row_to_values(row)
        sid = v["song_id"]
        existing = session.get(Song, sid)
        if existing is None:
            session.add(Song(**v))
        else:
            for key, val in v.items():
                setattr(existing, key, val)


def _seed_songs(session: Session) -> None:
    if _is_postgres():
        _seed_songs_postgres(session)
    else:
        _seed_songs_generic(session)


def run() -> None:
    with SessionLocal() as session:
        _seed_users(session)
        _seed_songs(session)
        session.commit()


if __name__ == "__main__":
    run()

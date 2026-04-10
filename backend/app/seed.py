"""Idempotent seed: demo user and catalog tracks (run after migrations)."""

from __future__ import annotations

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models import Song, User

# Canonical catalog: keys must match Song columns (optional keys may be absent → stored as NULL).
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
        "genre": "Choral",
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
)


def _is_postgres() -> bool:
    u = settings.database_url.lower()
    return u.startswith("postgresql") or "+psycopg2" in u or "+asyncpg" in u


def _song_row_to_values(row: dict) -> dict:
    """Full row for Song: missing optional keys become None so DB stays aligned with catalog."""
    required = (
        "song_id",
        "title",
        "author",
        "singer",
        "genre",
        "artwork_url",
        "duration_seconds",
        "audio_url",
    )
    out = {k: row[k] for k in required}
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

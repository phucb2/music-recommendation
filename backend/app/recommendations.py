"""Deterministic homepage / next-song logic matching frontend/lib/mock/catalog.ts."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Song


def js_hash(s: str) -> int:
    """32-bit signed hash matching TypeScript: (Math.imul(31, h) + code) | 0."""
    h = 0
    for ch in s:
        h = (31 * h + ord(ch)) & 0xFFFFFFFF
    if h >= 0x80000000:
        h -= 0x100000000
    return h


def home_recommendations(db: Session, user_id: str) -> list[Song]:
    rows = list(db.scalars(select(Song)).all())
    rows.sort(key=lambda s: js_hash(user_id + s.song_id))
    out = rows[:10]
    if out:
        return [out[0], *out]
    return out


def next_songs(db: Session, current_song_id: str, limit: int = 6) -> list[Song]:
    rows = list(
        db.scalars(
            select(Song).where(Song.song_id != current_song_id).order_by(Song.song_id)
        ).all()
    )
    return rows[:limit]

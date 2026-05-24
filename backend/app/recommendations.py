"""Deterministic homepage / next-song logic matching frontend/lib/mock/catalog.ts."""

from prisma import Prisma
from prisma.models import Song


def js_hash(s: str) -> int:
    """32-bit signed hash matching TypeScript: (Math.imul(31, h) + code) | 0."""
    h = 0
    for ch in s:
        h = (31 * h + ord(ch)) & 0xFFFFFFFF
    if h >= 0x80000000:
        h -= 0x100000000
    return h


async def home_recommendations(prisma: Prisma, user_id: str) -> list[Song]:
    rows = list(await prisma.song.find_many())
    rows.sort(key=lambda s: js_hash(user_id + s.song_id))
    out = rows[:10]
    if out:
        return [out[0], *out]
    return out


async def next_songs(prisma: Prisma, current_song_id: str, limit: int = 6) -> list[Song]:
    return await prisma.song.find_many(
        where={"song_id": {"not": current_song_id}},
        order={"song_id": "asc"},
        take=limit,
    )

"""Deterministic homepage / next-song logic matching frontend/lib/mock/catalog.ts."""

import logging
import time
from dataclasses import dataclass
from typing import Any

from prisma import Prisma
from prisma.models import Song

from app.ml_service import ml_runtime

logger = logging.getLogger(__name__)

# Cache TTL in seconds (5 minutes by default)
_CACHE_TTL: int = 300


@dataclass
class _CacheEntry:
    value: Any
    expires_at: float


class RecommendationCache:
    """Thread-safe in-memory TTL cache for ML recommendation results."""

    def __init__(self, ttl: int = _CACHE_TTL) -> None:
        self._ttl = ttl
        self._store: dict[tuple, _CacheEntry] = {}

    def get(self, key: tuple) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        if time.monotonic() > entry.expires_at:
            del self._store[key]
            return None
        return entry.value

    def set(self, key: tuple, value: Any) -> None:
        self._store[key] = _CacheEntry(value=value, expires_at=time.monotonic() + self._ttl)

    def invalidate(self, user_id: str | None = None) -> None:
        """Remove all entries, or only those matching a user_id prefix."""
        if user_id is None:
            self._store.clear()
        else:
            to_delete = [k for k in self._store if k and k[0] == user_id]
            for k in to_delete:
                del self._store[k]

    @property
    def size(self) -> int:
        now = time.monotonic()
        return sum(1 for e in self._store.values() if e.expires_at > now)


_cache = RecommendationCache()


def js_hash(s: str) -> int:
    """32-bit signed hash matching TypeScript: (Math.imul(31, h) + code) | 0."""
    h = 0
    for ch in s:
        h = (31 * h + ord(ch)) & 0xFFFFFFFF
    if h >= 0x80000000:
        h -= 0x100000000
    return h


async def home_recommendations(prisma: Prisma, user_id: str) -> list[Song]:
    logger.info("home_recommendations called: user_id=%s ml_ready=%s", user_id, ml_runtime.ready)

    cache_key = ("home", user_id)
    cached = _cache.get(cache_key)
    if cached is not None:
        logger.debug("home_recommendations: cache hit for user_id=%s", user_id)
        return cached

    if ml_runtime.ready:
        ml_rows = await ml_runtime.recommend_home(prisma, user_id)
        if ml_rows:
            logger.info("home_recommendations: ML returned %d songs for user_id=%s", len(ml_rows), user_id)
            _cache.set(cache_key, ml_rows)
            return ml_rows
        logger.warning("home_recommendations: ML returned no results for user_id=%s, falling back to hash sort", user_id)

    rows = list(await prisma.song.find_many())
    rows.sort(key=lambda s: js_hash(user_id + s.song_id))
    out = rows[:10]
    logger.info("home_recommendations: fallback returned %d songs for user_id=%s", len(out), user_id)
    result = [out[0], *out] if out else out
    _cache.set(cache_key, result)
    return result


async def next_songs(
    prisma: Prisma,
    current_song_id: str,
    user_id: str | None = None,
    limit: int = 6,
) -> list[Song]:
    cache_key = ("next", user_id, current_song_id, limit)
    cached = _cache.get(cache_key)
    if cached is not None:
        logger.debug("next_songs: cache hit for user_id=%s song=%s", user_id, current_song_id)
        return cached

    if ml_runtime.ready and user_id:
        ml_rows = await ml_runtime.recommend_next(prisma, user_id, current_song_id, limit=limit)
        if ml_rows:
            _cache.set(cache_key, ml_rows)
            return ml_rows

    result = await prisma.song.find_many(
        where={"song_id": {"not": current_song_id}},
        order={"song_id": "asc"},
        take=limit,
    )
    _cache.set(cache_key, result)
    return result


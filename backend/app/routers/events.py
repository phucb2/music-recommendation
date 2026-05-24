from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import TypeAdapter
from prisma import Prisma

from app.database import get_prisma
from app.schemas import AnalyticsEventIn, EventsAccepted

router = APIRouter(tags=["events"])

_event_adapter = TypeAdapter(AnalyticsEventIn)


def _parse_iso_ts(ts: str) -> datetime:
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid timestamp: {ts}") from e
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


@router.post("/v1/events", response_model=EventsAccepted)
async def ingest_events(request: Request, prisma: Prisma = Depends(get_prisma)) -> EventsAccepted:
    try:
        body = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON") from e

    items: list[dict]
    if isinstance(body, list):
        items = body
    elif isinstance(body, dict) and "events" in body:
        raw = body["events"]
        if not isinstance(raw, list):
            raise HTTPException(status_code=400, detail="events must be an array")
        items = raw
    elif isinstance(body, dict):
        items = [body]
    else:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    if not items:
        raise HTTPException(status_code=400, detail="No valid events")

    events_in: list[AnalyticsEventIn] = []
    for item in items:
        if not isinstance(item, dict):
            raise HTTPException(status_code=400, detail="Each event must be an object")
        try:
            events_in.append(_event_adapter.validate_python(item))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid event: {e}") from e

    user_ids = {e.user_id for e in events_in}
    song_ids = {e.song_id for e in events_in}

    found_users = await prisma.user.find_many(
        where={"user_id": {"in": list(user_ids)}},
    )
    users_found = {u.user_id for u in found_users}
    missing_u = user_ids - users_found
    if missing_u:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown user_id(s): {sorted(missing_u)}",
        )

    found_songs = await prisma.song.find_many(
        where={"song_id": {"in": list(song_ids)}},
    )
    songs_found = {s.song_id for s in found_songs}
    missing_s = song_ids - songs_found
    if missing_s:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown song_id(s): {sorted(missing_s)}",
        )

    data = [
        {
            "user_id": e.user_id,
            "song_id": e.song_id,
            "occurred_at": _parse_iso_ts(e.timestamp),
            "surface": e.surface,
            "event_type": e.event_type,
            "session_id": e.session_id,
            "play_duration_seconds": e.play_duration_seconds,
            "song_duration_seconds": e.song_duration_seconds,
            "position": e.position,
            "request_id": e.request_id,
            "recommendation_id": e.recommendation_id,
            "completed": e.completed,
        }
        for e in events_in
    ]

    received = await prisma.analyticsevent.create_many(data=data)

    return EventsAccepted(received=received)

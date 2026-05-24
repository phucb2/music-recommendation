from fastapi import APIRouter, Depends, HTTPException, Query
from prisma import Prisma
from prisma.models import Song

from app.database import get_prisma
from app.schemas import SongOut

router = APIRouter(prefix="/v1/songs", tags=["songs"])


@router.get("", response_model=list[SongOut])
async def list_songs(
    prisma: Prisma = Depends(get_prisma),
    limit: int = Query(default=10_000, ge=1, le=10_000),
    offset: int = Query(default=0, ge=0),
) -> list[Song]:
    return await prisma.song.find_many(
        take=limit,
        skip=offset,
        order={"song_id": "asc"},
    )


@router.get("/{song_id}", response_model=SongOut)
async def get_song(song_id: str, prisma: Prisma = Depends(get_prisma)) -> Song:
    row = await prisma.song.find_unique(where={"song_id": song_id})
    if row is None:
        raise HTTPException(status_code=404, detail="Song not found")
    return row

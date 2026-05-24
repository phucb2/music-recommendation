from fastapi import APIRouter, Depends, HTTPException, Query
from prisma import Prisma
from prisma.models import Song

from app.database import get_prisma
from app.recommendations import home_recommendations, next_songs
from app.schemas import SongOut

router = APIRouter(prefix="/v1/recommendations", tags=["recommendations"])


@router.get("/home", response_model=list[SongOut])
async def rec_home(
    user_id: str = Query(..., min_length=1),
    prisma: Prisma = Depends(get_prisma),
) -> list[Song]:
    return await home_recommendations(prisma, user_id)


@router.get("/next", response_model=list[SongOut])
async def rec_next(
    current_song_id: str = Query(..., min_length=1),
    prisma: Prisma = Depends(get_prisma),
) -> list[Song]:
    if await prisma.song.find_unique(where={"song_id": current_song_id}) is None:
        raise HTTPException(status_code=404, detail="Current song not found")
    return await next_songs(prisma, current_song_id)

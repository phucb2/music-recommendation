from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Song
from app.recommendations import home_recommendations, next_songs
from app.schemas import SongOut

router = APIRouter(prefix="/v1/recommendations", tags=["recommendations"])


@router.get("/home", response_model=list[SongOut])
def rec_home(
    user_id: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
) -> list[Song]:
    return home_recommendations(db, user_id)


@router.get("/next", response_model=list[SongOut])
def rec_next(
    current_song_id: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
) -> list[Song]:
    if db.get(Song, current_song_id) is None:
        raise HTTPException(status_code=404, detail="Current song not found")
    return next_songs(db, current_song_id)

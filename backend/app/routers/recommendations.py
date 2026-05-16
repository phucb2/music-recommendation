from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Song
from app.recommendations import home_recommendations, next_songs, similar_songs, rebuild_model
from app.schemas import SongOut, SimilarSongOut

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


@router.get("/similar", response_model=list[SimilarSongOut])
def rec_similar(
    song_id: str = Query(..., min_length=1),
    top_n: int = Query(default=6, ge=1, le=20),
    db: Session = Depends(get_db),
) -> list[dict]:
    """Return songs similar to the given song using KNN content-based filtering."""
    if db.get(Song, song_id) is None:
        raise HTTPException(status_code=404, detail="Song not found")
    return similar_songs(db, song_id, top_n=top_n)


@router.post("/rebuild", status_code=204)
def rec_rebuild(db: Session = Depends(get_db)) -> None:
    """Force rebuild the KNN model (call after adding/updating songs)."""
    rebuild_model(db)

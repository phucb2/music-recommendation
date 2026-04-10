from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Song
from app.schemas import SongOut

router = APIRouter(prefix="/v1/songs", tags=["songs"])


@router.get("", response_model=list[SongOut])
def list_songs(
    db: Session = Depends(get_db),
    limit: int = Query(default=10_000, ge=1, le=10_000),
    offset: int = Query(default=0, ge=0),
) -> list[Song]:
    q = select(Song).order_by(Song.song_id).limit(limit).offset(offset)
    return list(db.scalars(q).all())


@router.get("/{song_id}", response_model=SongOut)
def get_song(song_id: str, db: Session = Depends(get_db)) -> Song:
    row = db.get(Song, song_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Song not found")
    return row

from pydantic import BaseModel


class SongOut(BaseModel):
    model_config = {"from_attributes": True}

    song_id: str
    title: str
    author: str
    singer: str
    genre: str
    artwork_url: str
    duration_seconds: int
    audio_url: str
    subgenre: str | None = None
    language: str | None = None
    release_year: int | None = None
    album_id: str | None = None
    artist_id: str | None = None
    featured_artists: str | None = None
    region: str | None = None
    explicit_content: bool | None = None
    popularity: float | None = None
    danceability: float | None = None
    energy: float | None = None
    loudness: float | None = None
    speechiness: float | None = None
    acousticness: float | None = None
    instrumentalness: float | None = None
    liveness: float | None = None
    valence: float | None = None
    tempo: float | None = None


class AnalyticsEventIn(BaseModel):
    user_id: str
    song_id: str
    timestamp: str
    surface: str
    event_type: str
    session_id: str
    play_duration_seconds: float | None = None
    song_duration_seconds: float | None = None
    position: int | None = None
    request_id: str | None = None
    recommendation_id: str | None = None
    completed: bool | None = None


class EventsAccepted(BaseModel):
    received: int


class SimilarSongOut(BaseModel):
    model_config = {"from_attributes": True}

    song: SongOut
    similarity_score: float

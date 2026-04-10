from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    events: Mapped[list["AnalyticsEvent"]] = relationship(back_populates="user")


class Song(Base):
    __tablename__ = "songs"

    song_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    author: Mapped[str] = mapped_column(String(512), nullable=False)
    singer: Mapped[str] = mapped_column(String(512), nullable=False)
    genre: Mapped[str] = mapped_column(String(255), nullable=False)
    artwork_url: Mapped[str] = mapped_column(Text, nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    audio_url: Mapped[str] = mapped_column(Text, nullable=False)

    subgenre: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language: Mapped[str | None] = mapped_column(String(64), nullable=True)
    release_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    album_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    artist_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    featured_artists: Mapped[str | None] = mapped_column(Text, nullable=True)
    region: Mapped[str | None] = mapped_column(String(64), nullable=True)
    explicit_content: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    popularity: Mapped[float | None] = mapped_column(Float, nullable=True)

    __table_args__ = (
        Index("ix_songs_genre", "genre"),
        Index("ix_songs_artist_id", "artist_id"),
    )

    events: Mapped[list["AnalyticsEvent"]] = relationship(back_populates="song")


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=False
    )
    song_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("songs.song_id", ondelete="RESTRICT"), nullable=False
    )
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    surface: Mapped[str] = mapped_column(String(64), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    session_id: Mapped[str] = mapped_column(String(128), nullable=False)

    play_duration_seconds: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    song_duration_seconds: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    recommendation_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    completed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="events")
    song: Mapped["Song"] = relationship(back_populates="events")

    __table_args__ = (
        Index("ix_analytics_events_user_occurred", "user_id", "occurred_at"),
        Index("ix_analytics_events_song_id", "song_id"),
        Index("ix_analytics_events_type_surface", "event_type", "surface"),
        Index("ix_analytics_events_session_id", "session_id"),
    )

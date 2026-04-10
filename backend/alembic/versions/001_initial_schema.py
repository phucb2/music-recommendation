"""Initial users, songs, analytics_events.

Revision ID: 001_initial
Revises:
Create Date: 2026-04-08

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("username"),
    )
    op.create_table(
        "songs",
        sa.Column("song_id", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("author", sa.String(length=512), nullable=False),
        sa.Column("singer", sa.String(length=512), nullable=False),
        sa.Column("genre", sa.String(length=255), nullable=False),
        sa.Column("artwork_url", sa.Text(), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=False),
        sa.Column("audio_url", sa.Text(), nullable=False),
        sa.Column("subgenre", sa.String(length=255), nullable=True),
        sa.Column("language", sa.String(length=64), nullable=True),
        sa.Column("release_year", sa.Integer(), nullable=True),
        sa.Column("album_id", sa.String(length=64), nullable=True),
        sa.Column("artist_id", sa.String(length=64), nullable=True),
        sa.Column("featured_artists", sa.Text(), nullable=True),
        sa.Column("region", sa.String(length=64), nullable=True),
        sa.Column("explicit_content", sa.Boolean(), nullable=True),
        sa.Column("popularity", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("song_id"),
    )
    op.create_index("ix_songs_artist_id", "songs", ["artist_id"], unique=False)
    op.create_index("ix_songs_genre", "songs", ["genre"], unique=False)
    op.create_table(
        "analytics_events",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("song_id", sa.String(length=64), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("surface", sa.String(length=64), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("session_id", sa.String(length=128), nullable=False),
        sa.Column("play_duration_seconds", sa.Numeric(12, 4), nullable=True),
        sa.Column("song_duration_seconds", sa.Numeric(12, 4), nullable=True),
        sa.Column("position", sa.Integer(), nullable=True),
        sa.Column("request_id", sa.String(length=128), nullable=True),
        sa.Column("recommendation_id", sa.String(length=128), nullable=True),
        sa.Column("completed", sa.Boolean(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["song_id"], ["songs.song_id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_analytics_events_user_occurred",
        "analytics_events",
        ["user_id", "occurred_at"],
        unique=False,
    )
    op.create_index("ix_analytics_events_song_id", "analytics_events", ["song_id"], unique=False)
    op.create_index(
        "ix_analytics_events_type_surface",
        "analytics_events",
        ["event_type", "surface"],
        unique=False,
    )
    op.create_index(
        "ix_analytics_events_session_id", "analytics_events", ["session_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_analytics_events_session_id", table_name="analytics_events")
    op.drop_index("ix_analytics_events_type_surface", table_name="analytics_events")
    op.drop_index("ix_analytics_events_song_id", table_name="analytics_events")
    op.drop_index("ix_analytics_events_user_occurred", table_name="analytics_events")
    op.drop_table("analytics_events")
    op.drop_index("ix_songs_genre", table_name="songs")
    op.drop_index("ix_songs_artist_id", table_name="songs")
    op.drop_table("songs")
    op.drop_table("users")

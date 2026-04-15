"""Add optional audio feature columns on songs.

Revision ID: 002_audio_features
Revises: 001_initial
Create Date: 2026-04-15

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_audio_features"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("songs", sa.Column("danceability", sa.Float(), nullable=True))
    op.add_column("songs", sa.Column("energy", sa.Float(), nullable=True))
    op.add_column("songs", sa.Column("loudness", sa.Float(), nullable=True))
    op.add_column("songs", sa.Column("speechiness", sa.Float(), nullable=True))
    op.add_column("songs", sa.Column("acousticness", sa.Float(), nullable=True))
    op.add_column("songs", sa.Column("instrumentalness", sa.Float(), nullable=True))
    op.add_column("songs", sa.Column("liveness", sa.Float(), nullable=True))
    op.add_column("songs", sa.Column("valence", sa.Float(), nullable=True))
    op.add_column("songs", sa.Column("tempo", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("songs", "tempo")
    op.drop_column("songs", "valence")
    op.drop_column("songs", "liveness")
    op.drop_column("songs", "instrumentalness")
    op.drop_column("songs", "acousticness")
    op.drop_column("songs", "speechiness")
    op.drop_column("songs", "loudness")
    op.drop_column("songs", "energy")
    op.drop_column("songs", "danceability")

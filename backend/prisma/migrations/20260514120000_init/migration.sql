-- CreateTable
CREATE TABLE "users" (
    "user_id" VARCHAR(64) NOT NULL,
    "username" VARCHAR(255) NOT NULL,
    "password_hash" TEXT,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "users_pkey" PRIMARY KEY ("user_id")
);

-- CreateTable
CREATE TABLE "songs" (
    "song_id" VARCHAR(64) NOT NULL,
    "title" VARCHAR(512) NOT NULL,
    "author" VARCHAR(512) NOT NULL,
    "singer" VARCHAR(512) NOT NULL,
    "genre" VARCHAR(255) NOT NULL,
    "artwork_url" TEXT NOT NULL,
    "duration_seconds" INTEGER NOT NULL,
    "audio_url" TEXT NOT NULL,
    "subgenre" VARCHAR(255),
    "language" VARCHAR(64),
    "release_year" INTEGER,
    "album_id" VARCHAR(64),
    "artist_id" VARCHAR(64),
    "featured_artists" TEXT,
    "region" VARCHAR(64),
    "explicit_content" BOOLEAN,
    "popularity" DOUBLE PRECISION,
    "danceability" DOUBLE PRECISION,
    "energy" DOUBLE PRECISION,
    "loudness" DOUBLE PRECISION,
    "speechiness" DOUBLE PRECISION,
    "acousticness" DOUBLE PRECISION,
    "instrumentalness" DOUBLE PRECISION,
    "liveness" DOUBLE PRECISION,
    "valence" DOUBLE PRECISION,
    "tempo" DOUBLE PRECISION,

    CONSTRAINT "songs_pkey" PRIMARY KEY ("song_id")
);

-- CreateTable
CREATE TABLE "analytics_events" (
    "id" BIGSERIAL NOT NULL,
    "user_id" VARCHAR(64) NOT NULL,
    "song_id" VARCHAR(64) NOT NULL,
    "occurred_at" TIMESTAMPTZ(6) NOT NULL,
    "surface" VARCHAR(64) NOT NULL,
    "event_type" VARCHAR(64) NOT NULL,
    "session_id" VARCHAR(128) NOT NULL,
    "play_duration_seconds" DOUBLE PRECISION,
    "song_duration_seconds" DOUBLE PRECISION,
    "position" INTEGER,
    "request_id" VARCHAR(128),
    "recommendation_id" VARCHAR(128),
    "completed" BOOLEAN,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "analytics_events_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "users_username_key" ON "users"("username");

-- CreateIndex
CREATE INDEX "ix_songs_genre" ON "songs"("genre");

-- CreateIndex
CREATE INDEX "ix_songs_artist_id" ON "songs"("artist_id");

-- CreateIndex
CREATE INDEX "ix_analytics_events_user_occurred" ON "analytics_events"("user_id", "occurred_at");

-- CreateIndex
CREATE INDEX "ix_analytics_events_song_id" ON "analytics_events"("song_id");

-- CreateIndex
CREATE INDEX "ix_analytics_events_type_surface" ON "analytics_events"("event_type", "surface");

-- CreateIndex
CREATE INDEX "ix_analytics_events_session_id" ON "analytics_events"("session_id");

-- AddForeignKey
ALTER TABLE "analytics_events" ADD CONSTRAINT "analytics_events_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("user_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "analytics_events" ADD CONSTRAINT "analytics_events_song_id_fkey" FOREIGN KEY ("song_id") REFERENCES "songs"("song_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- Enable pgvector extension and add song embedding column for ANN retrieval.
CREATE EXTENSION IF NOT EXISTS vector;

ALTER TABLE "songs" ADD COLUMN IF NOT EXISTS "embedding" vector(64);

CREATE INDEX IF NOT EXISTS "ix_songs_embedding_hnsw"
  ON "songs" USING hnsw ("embedding" vector_cosine_ops);

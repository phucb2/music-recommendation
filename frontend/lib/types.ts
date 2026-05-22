import { EVENT_TYPE, SURFACE } from "./constants";

export type Song = {
  song_id: string;
  title: string;
  /** Songwriter / composer credit. */
  author: string;
  /** Vocalist or lead performer credit. */
  singer: string;
  /** Musical genre (e.g. jazz, indie rock). */
  genre: string;
  /** Remote URL for artwork (use with next/image remotePatterns). */
  artwork_url: string;
  duration_seconds: number;
  /** Stream URL for HTML audio. */
  audio_url: string;
  /** Precomputed audio features (optional; same semantics as PRD §8.4.1). */
  danceability?: number;
  energy?: number;
  loudness?: number;
  speechiness?: number;
  acousticness?: number;
  instrumentalness?: number;
  liveness?: number;
  valence?: number;
  /** Tempo in BPM. */
  tempo?: number;
};

export type Surface = (typeof SURFACE)[keyof typeof SURFACE];
export type EventType = (typeof EVENT_TYPE)[keyof typeof EVENT_TYPE];

/** Origin surface for plays (homepage vs next_song). */
export type PlaySurface = "homepage" | "next_song";

export type AnalyticsEvent = {
  user_id: string;
  song_id: string;
  timestamp: string;
  surface: Surface | PlaySurface;
  event_type: EventType;
  session_id: string;
  play_duration_seconds?: number;
  song_duration_seconds?: number;
  /** 0-based index in list for impression/click. */
  position?: number;
  request_id?: string;
  recommendation_id?: string;
  /** True when playback reached natural end. */
  completed?: boolean;
};

export type SimilarSong = {
  song: Song;
  similarity_score: number;
};

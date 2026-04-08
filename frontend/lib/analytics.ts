"use client";

import { EVENT_TYPE, SURFACE } from "@/lib/constants";
import type { AnalyticsEvent, PlaySurface } from "@/lib/types";

const SESSION_KEY = "analytics_session_id";

export function getOrCreateAnalyticsSessionId(): string {
  if (typeof window === "undefined") return "ssr";
  let id = sessionStorage.getItem(SESSION_KEY);
  if (!id) {
    id =
      typeof crypto !== "undefined" && crypto.randomUUID
        ? crypto.randomUUID()
        : `sess_${Math.random().toString(36).slice(2)}`;
    sessionStorage.setItem(SESSION_KEY, id);
  }
  return id;
}

export async function emitEvent(
  partial: Omit<AnalyticsEvent, "timestamp" | "session_id"> & {
    session_id?: string;
  },
): Promise<void> {
  const session_id = partial.session_id ?? getOrCreateAnalyticsSessionId();
  const body: AnalyticsEvent = {
    ...partial,
    session_id,
    timestamp: new Date().toISOString(),
  };
  try {
    await fetch("/api/events", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      keepalive: true,
    });
  } catch {
    /* best-effort */
  }
}

export async function emitPlayEnd(args: {
  userId: string;
  songId: string;
  playSurface: PlaySurface;
  playDurationSeconds: number;
  songDurationSeconds: number;
  completed: boolean;
}): Promise<void> {
  await emitEvent({
    user_id: args.userId,
    song_id: args.songId,
    surface: args.playSurface,
    event_type: EVENT_TYPE.play_end,
    play_duration_seconds: Math.round(args.playDurationSeconds),
    song_duration_seconds: args.songDurationSeconds,
    completed: args.completed,
  });
}

export async function emitSkip(args: {
  userId: string;
  songId: string;
  playSurface: PlaySurface;
  playDurationSeconds: number;
  songDurationSeconds: number;
}): Promise<void> {
  await emitEvent({
    user_id: args.userId,
    song_id: args.songId,
    surface: args.playSurface,
    event_type: EVENT_TYPE.skip,
    play_duration_seconds: Math.round(args.playDurationSeconds),
    song_duration_seconds: args.songDurationSeconds,
  });
}

export async function emitLikeDislike(args: {
  userId: string;
  songId: string;
  kind: "like" | "dislike";
}): Promise<void> {
  await emitEvent({
    user_id: args.userId,
    song_id: args.songId,
    surface: SURFACE.player,
    event_type: args.kind === "like" ? EVENT_TYPE.like : EVENT_TYPE.dislike,
  });
}

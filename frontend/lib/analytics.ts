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

type EmitOptions = {
  /** Use only for unload / tab hide / in-flight navigations — not for normal clicks (keepalive can break some browsers’ POST handling). */
  keepalive?: boolean;
};

export async function emitEvent(
  partial: Omit<AnalyticsEvent, "timestamp" | "session_id"> & {
    session_id?: string;
  },
  options?: EmitOptions,
): Promise<void> {
  const session_id = partial.session_id ?? getOrCreateAnalyticsSessionId();
  const body: AnalyticsEvent = {
    ...partial,
    session_id,
    timestamp: new Date().toISOString(),
  };
  try {
    const res = await fetch("/api/events", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      ...(options?.keepalive ? { keepalive: true as const } : {}),
    });
    if (!res.ok) {
      const detail = await res.text().catch(() => "");
      if (process.env.NODE_ENV === "development") {
        console.warn("[analytics] POST /api/events failed", res.status, detail);
      }
    }
  } catch (e) {
    if (process.env.NODE_ENV === "development") {
      console.warn("[analytics] POST /api/events error", e);
    }
  }
}

export async function emitPlayEnd(args: {
  userId: string;
  songId: string;
  playSurface: PlaySurface;
  playDurationSeconds: number;
  songDurationSeconds: number;
  completed: boolean;
  /** Tab close / hide — request may outlive the page. */
  keepalive?: boolean;
}): Promise<void> {
  await emitEvent(
    {
      user_id: args.userId,
      song_id: args.songId,
      surface: args.playSurface,
      event_type: EVENT_TYPE.play_end,
      play_duration_seconds: Math.round(args.playDurationSeconds),
      song_duration_seconds: args.songDurationSeconds,
      completed: args.completed,
    },
    { keepalive: args.keepalive },
  );
}

export async function emitSkip(args: {
  userId: string;
  songId: string;
  playSurface: PlaySurface;
  playDurationSeconds: number;
  songDurationSeconds: number;
}): Promise<void> {
  await emitEvent(
    {
      user_id: args.userId,
      song_id: args.songId,
      surface: args.playSurface,
      event_type: EVENT_TYPE.skip,
      play_duration_seconds: Math.round(args.playDurationSeconds),
      song_duration_seconds: args.songDurationSeconds,
    },
    { keepalive: true },
  );
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

/** Surfaces for analytics (mockup + PRD alignment). */
export const SURFACE = {
  homepage: "homepage",
  next_song: "next_song",
  player: "player",
} as const;

/** Event types sent to /api/events. */
export const EVENT_TYPE = {
  impression: "impression",
  click: "click",
  play_start: "play_start",
  play_progress: "play_progress",
  play_end: "play_end",
  skip: "skip",
  like: "like",
  dislike: "dislike",
} as const;

export const SESSION_COOKIE = "demo_session";

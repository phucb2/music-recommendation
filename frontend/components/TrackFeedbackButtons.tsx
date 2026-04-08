"use client";

import { emitLikeDislike } from "@/lib/analytics";

/** Heroicons 24 outline — heart */
function HeartIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden
    >
      <path
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.5}
        d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12Z"
      />
    </svg>
  );
}

/** Heroicons 24 outline — hand thumb down */
function ThumbDownIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden
    >
      <path
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.5}
        d="M7.498 15.25H4.372c-1.026 0-1.945-.694-2.054-1.715a12.137 12.137 0 0 1-.068-1.285c0-2.848.992-5.464 2.649-7.521C5.287 4.247 5.886 4 6.504 4h4.016a4.5 4.5 0 0 1 1.423.23l3.114 1.04a4.5 4.5 0 0 0 1.423.23h1.294M7.498 15.25c.618 0 .991.724.725 1.282A7.471 7.471 0 0 0 7.5 19.75 2.25 2.25 0 0 0 9.75 22a.75.75 0 0 0 .75-.75v-.633c0-.573.11-1.14.322-1.672.304-.76.93-1.33 1.653-1.715a9.04 9.04 0 0 0 2.86-2.4c.498-.634 1.226-1.08 2.032-1.08h.384m-10.253 1.5H9.7m8.075-9.75c.01.05.027.1.05.148.593 1.2.925 2.55.925 3.977 0 1.487-.36 2.89-.999 4.125m.023-8.25c-.076-.365.183-.75.575-.75h.908c.889 0 1.713.518 1.972 1.368.339 1.11.521 2.287.521 3.507 0 1.553-.295 3.036-.831 4.398-.306.774-1.086 1.227-1.918 1.227h-1.053c-.472 0-.745-.556-.5-.96a8.95 8.95 0 0 0 .303-.54"
      />
    </svg>
  );
}

export function TrackFeedbackButtons({
  userId,
  songId,
}: {
  userId: string;
  songId: string;
}) {
  return (
    <div className="flex shrink-0 items-center gap-2 sm:gap-2.5">
      <button
        type="button"
        onClick={() => void emitLikeDislike({ userId, songId, kind: "like" })}
        className="group inline-flex items-center gap-2 rounded-full border border-white/12 bg-gradient-to-b from-white/[0.09] to-white/[0.02] px-3.5 py-2 text-sm font-medium text-muted shadow-sm shadow-black/25 ring-1 ring-white/[0.06] transition-all duration-200 hover:border-accent/50 hover:bg-accent/[0.12] hover:text-accent hover:shadow-md hover:shadow-accent/15 hover:ring-accent/25 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/50 focus-visible:ring-offset-2 focus-visible:ring-offset-venue active:scale-[0.98]"
      >
        <HeartIcon className="h-[1.125rem] w-[1.125rem] text-accent/75 transition-transform duration-200 group-hover:scale-110 group-hover:text-accent" />
        <span>Like</span>
      </button>
      <button
        type="button"
        onClick={() => void emitLikeDislike({ userId, songId, kind: "dislike" })}
        className="group inline-flex items-center gap-2 rounded-full border border-white/12 bg-gradient-to-b from-white/[0.06] to-white/[0.02] px-3.5 py-2 text-sm font-medium text-muted shadow-sm shadow-black/25 ring-1 ring-white/[0.06] transition-all duration-200 hover:border-rose-400/40 hover:bg-rose-500/[0.1] hover:text-rose-100 hover:shadow-md hover:shadow-rose-950/30 hover:ring-rose-400/20 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-rose-400/45 focus-visible:ring-offset-2 focus-visible:ring-offset-venue active:scale-[0.98]"
      >
        <ThumbDownIcon className="h-[1.125rem] w-[1.125rem] text-rose-300/65 transition-transform duration-200 group-hover:-translate-y-px group-hover:text-rose-200" />
        <span>Dislike</span>
      </button>
    </div>
  );
}

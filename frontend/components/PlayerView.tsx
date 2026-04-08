"use client";

import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { EVENT_TYPE, SURFACE } from "@/lib/constants";
import { emitEvent, emitPlayEnd, emitSkip } from "@/lib/analytics";
import { TrackList } from "@/components/TrackList";
import { LogoutButton } from "@/components/LogoutButton";
import { SessionUser } from "@/components/SessionUser";
import { TrackFeedbackButtons } from "@/components/TrackFeedbackButtons";
import { PlaybackTimeline } from "@/components/PlaybackTimeline";
import { SongCreditsPlayer } from "@/components/SongCredits";
import { SiteFooter } from "@/components/SiteFooter";
import type { PlaySurface, Song } from "@/lib/types";

/** Show this many “Up next” rows so the player fits one viewport without scrolling. */
const UP_NEXT_VISIBLE = 3;

export function PlayerView({
  song,
  userId,
  username,
  playSurface,
  nextSongs,
}: {
  song: Song;
  userId: string;
  username: string;
  playSurface: PlaySurface;
  nextSongs: Song[];
}) {
  const router = useRouter();
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const playStartSent = useRef(false);
  const lastProgressEmit = useRef(0);
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);

  const queueVisible = nextSongs.slice(0, UP_NEXT_VISIBLE);
  const queueOverflow = nextSongs.length - queueVisible.length;

  const sendPlayEnd = useCallback(
    async (completed: boolean) => {
      const a = audioRef.current;
      if (!a) return;
      await emitPlayEnd({
        userId,
        songId: song.song_id,
        playSurface,
        playDurationSeconds: a.currentTime,
        songDurationSeconds: song.duration_seconds,
        completed,
      });
    },
    [playSurface, song.duration_seconds, song.song_id, userId],
  );

  useEffect(() => {
    playStartSent.current = false;
    lastProgressEmit.current = 0;
    const a = audioRef.current;
    if (a) {
      void a.load();
    }
  }, [song.song_id]);

  useEffect(() => {
    const a = audioRef.current;
    if (!a) return;

    const onPlaying = () => {
      setPlaying(true);
      if (playStartSent.current) return;
      playStartSent.current = true;
      void emitEvent({
        user_id: userId,
        song_id: song.song_id,
        surface: playSurface,
        event_type: EVENT_TYPE.play_start,
      });
    };

    const onPause = () => {
      setPlaying(false);
    };

    const onTimeUpdate = () => {
      setCurrentTime(a.currentTime);
      const now = Date.now();
      if (now - lastProgressEmit.current < 10_000) return;
      if (a.paused) return;
      lastProgressEmit.current = now;
      void emitEvent({
        user_id: userId,
        song_id: song.song_id,
        surface: playSurface,
        event_type: EVENT_TYPE.play_progress,
        play_duration_seconds: Math.floor(a.currentTime),
        song_duration_seconds: song.duration_seconds,
      });
    };

    const onEnded = () => {
      setPlaying(false);
      void sendPlayEnd(true);
    };

    a.addEventListener("playing", onPlaying);
    a.addEventListener("pause", onPause);
    a.addEventListener("timeupdate", onTimeUpdate);
    a.addEventListener("ended", onEnded);

    return () => {
      a.removeEventListener("playing", onPlaying);
      a.removeEventListener("pause", onPause);
      a.removeEventListener("timeupdate", onTimeUpdate);
      a.removeEventListener("ended", onEnded);
    };
  }, [playSurface, sendPlayEnd, song.duration_seconds, song.song_id, userId]);

  useEffect(() => {
    function onHide() {
      if (document.visibilityState !== "hidden") return;
      const a = audioRef.current;
      if (!a) return;
      void emitPlayEnd({
        userId,
        songId: song.song_id,
        playSurface,
        playDurationSeconds: a.currentTime,
        songDurationSeconds: song.duration_seconds,
        completed: false,
      });
    }

    function onBeforeUnload() {
      const a = audioRef.current;
      if (!a) return;
      void emitPlayEnd({
        userId,
        songId: song.song_id,
        playSurface,
        playDurationSeconds: a.currentTime,
        songDurationSeconds: song.duration_seconds,
        completed: false,
      });
    }

    document.addEventListener("visibilitychange", onHide);
    window.addEventListener("beforeunload", onBeforeUnload);
    return () => {
      document.removeEventListener("visibilitychange", onHide);
      window.removeEventListener("beforeunload", onBeforeUnload);
    };
  }, [playSurface, song.duration_seconds, song.song_id, userId]);

  async function togglePlay() {
    const a = audioRef.current;
    if (!a) return;
    if (a.paused) {
      await a.play();
    } else {
      await sendPlayEnd(false);
      a.pause();
    }
  }

  async function handleSkip() {
    const a = audioRef.current;
    const next = nextSongs[0];
    if (a) {
      await emitSkip({
        userId,
        songId: song.song_id,
        playSurface,
        playDurationSeconds: a.currentTime,
        songDurationSeconds: song.duration_seconds,
      });
      await emitPlayEnd({
        userId,
        songId: song.song_id,
        playSurface,
        playDurationSeconds: a.currentTime,
        songDurationSeconds: song.duration_seconds,
        completed: false,
      });
    }
    if (next) {
      router.push(`/play/${next.song_id}?from=next_song`);
    }
  }

  return (
    <div className="flex h-[100dvh] max-h-[100dvh] flex-col overflow-hidden bg-venue">
      <header className="flex shrink-0 items-center justify-between gap-3 border-b border-white/5 px-4 py-3 sm:px-6 lg:px-8">
        <Link
          href="/"
          className="text-sm font-medium text-accent transition-colors hover:text-accent-dim"
        >
          ← Home
        </Link>
        <div className="flex min-w-0 flex-wrap items-center justify-end gap-3 sm:gap-4">
          <SessionUser username={username} />
          <LogoutButton />
        </div>
      </header>

      <div className="mx-auto grid min-h-0 w-full max-w-7xl flex-1 grid-cols-1 gap-4 overflow-hidden p-4 sm:gap-5 sm:p-5 lg:grid-cols-12 lg:gap-6 lg:p-6">
        <div className="flex min-h-0 flex-col overflow-hidden lg:col-span-7 lg:pr-1 xl:col-span-6">
          <div className="flex min-h-0 flex-1 flex-col justify-center gap-3 sm:gap-4">
            <div className="relative mx-auto aspect-square h-[min(20vh,176px)] w-[min(20vh,176px)] shrink-0 overflow-hidden rounded-2xl border border-white/10 bg-black/30 shadow-lg shadow-black/40 sm:h-[min(22vh,200px)] sm:w-[min(22vh,200px)] lg:mx-0 lg:h-[min(26vh,228px)] lg:w-[min(26vh,228px)]">
              <Image
                src={song.artwork_url}
                alt=""
                fill
                priority
                sizes="240px"
                className="object-cover"
              />
            </div>

            <div className="min-h-0 w-full max-w-xl shrink text-center lg:max-w-none lg:text-left">
              <div className="flex w-full min-w-0 flex-wrap items-center justify-center gap-2 sm:gap-3 lg:justify-between">
                <h1 className="min-w-0 flex-1 basis-[min(100%,14rem)] font-display text-xl font-semibold leading-tight text-foreground sm:basis-auto sm:text-2xl lg:text-left">
                  {song.title}
                </h1>
                <TrackFeedbackButtons userId={userId} songId={song.song_id} />
              </div>
              <div className="mx-auto mt-2 max-w-xl text-left lg:mx-0">
                <SongCreditsPlayer song={song} compact />
              </div>
            </div>

            {/* No native controls — playback is not seekable from the UI. */}
            <audio
              ref={audioRef}
              src={song.audio_url}
              preload="metadata"
              className="hidden"
              tabIndex={-1}
            />

            <div className="w-full max-w-xl shrink-0 lg:max-w-none">
              <PlaybackTimeline
                currentSeconds={currentTime}
                totalSeconds={song.duration_seconds}
              />
              <p className="sr-only">
                The timeline shows elapsed time and time remaining. Seeking or scrubbing is not
                supported.
              </p>
            </div>

            <div className="flex shrink-0 flex-wrap items-center justify-center gap-2 lg:justify-start">
              <button
                type="button"
                onClick={() => void togglePlay()}
                className="rounded-full bg-accent px-5 py-2 text-sm font-medium text-venue hover:opacity-90"
              >
                {playing ? "Pause" : "Play"}
              </button>
              <button
                type="button"
                onClick={() => void handleSkip()}
                className="rounded-full border border-white/20 px-4 py-2 text-sm text-foreground hover:border-accent/50"
              >
                Skip
              </button>
            </div>

          </div>
        </div>

        <section
          className="flex min-h-0 flex-col overflow-hidden border-t border-white/10 pt-4 lg:col-span-5 lg:border-l lg:border-t-0 lg:pl-6 lg:pt-0 xl:col-span-6 xl:pl-8"
          aria-labelledby="up-next"
        >
          <div className="mb-2 flex shrink-0 items-baseline justify-between gap-2">
            <h2 id="up-next" className="text-xs font-medium uppercase tracking-wider text-muted">
              Up next
            </h2>
            {queueOverflow > 0 ? (
              <span className="text-[10px] text-muted/80">+{queueOverflow} more in queue</span>
            ) : null}
          </div>
          <div className="min-h-0 flex-1 overflow-hidden">
            <TrackList
              songs={queueVisible}
              userId={userId}
              surface={SURFACE.next_song}
              layout="stack"
              compact
            />
          </div>
        </section>
      </div>

      <SiteFooter compact />
    </div>
  );
}

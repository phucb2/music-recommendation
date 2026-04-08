"use client";

import { SearchBarDecor } from "@/components/SearchBarDecor";
import { TrackList } from "@/components/TrackList";
import { SURFACE } from "@/lib/constants";
import type { Song } from "@/lib/types";
import { LogoutButton } from "@/components/LogoutButton";
import { SessionUser } from "@/components/SessionUser";
import { SiteFooter } from "@/components/SiteFooter";

export function HomeContent({
  songs,
  userId,
  username,
}: {
  songs: Song[];
  userId: string;
  username: string;
}) {
  return (
    <div className="mx-auto flex min-h-full w-full max-w-7xl flex-col px-4 pb-16 pt-8 sm:px-6 lg:px-10 lg:pt-12">
      <header className="mb-8 flex flex-col gap-6 sm:flex-row sm:items-start sm:justify-between lg:mb-10">
        <div>
          <p className="font-display text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
            Nhạc của tôi
          </p>
          <p className="mt-1 text-sm text-muted">For you</p>
        </div>
        <div className="flex w-full flex-col gap-3 sm:max-w-md sm:shrink-0 sm:items-end">
          <div className="w-full sm:w-full">
            <SearchBarDecor />
          </div>
          <div className="flex w-full flex-wrap items-center justify-end gap-3 sm:gap-4">
            <SessionUser username={username} />
            <LogoutButton />
          </div>
        </div>
      </header>

      <section aria-labelledby="recs-heading" className="min-w-0 flex-1">
        <h2 id="recs-heading" className="mb-4 text-sm font-medium uppercase tracking-wider text-muted">
          Recommended
        </h2>
        <TrackList
          songs={songs}
          userId={userId}
          surface={SURFACE.homepage}
          layout="grid"
        />
      </section>

      <SiteFooter className="mt-6 lg:mt-8" />
    </div>
  );
}

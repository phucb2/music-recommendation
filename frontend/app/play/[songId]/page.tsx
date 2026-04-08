import { notFound, redirect } from "next/navigation";
import { PlayerView } from "@/components/PlayerView";
import { getSession } from "@/lib/auth";
import { getNextSongs, getSongById } from "@/lib/mock/catalog";
import type { PlaySurface } from "@/lib/types";

export default async function PlayPage({
  params,
  searchParams,
}: {
  params: Promise<{ songId: string }>;
  searchParams: Promise<{ from?: string }>;
}) {
  const session = await getSession();
  if (!session) redirect("/login");

  const { songId } = await params;
  const { from } = await searchParams;

  const song = getSongById(songId);
  if (!song) notFound();

  const nextSongs = getNextSongs(songId);
  const playSurface: PlaySurface = from === "next_song" ? "next_song" : "homepage";

  return (
    <PlayerView
      song={song}
      userId={session.userId}
      username={session.username}
      playSurface={playSurface}
      nextSongs={nextSongs}
    />
  );
}

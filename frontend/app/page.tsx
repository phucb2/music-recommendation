import { redirect } from "next/navigation";
import { HomeContent } from "@/components/HomeContent";
import { getSession } from "@/lib/auth";
import { dedupeBySongId, getHomeRecommendations } from "@/lib/mock/catalog";

export default async function Home() {
  const session = await getSession();
  if (!session) redirect("/login");

  const raw = getHomeRecommendations(session.userId);
  const songs = dedupeBySongId(raw);

  return (
    <HomeContent songs={songs} userId={session.userId} username={session.username} />
  );
}

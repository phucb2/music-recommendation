import { redirect } from "next/navigation";
import { HomeContent } from "@/components/HomeContent";
import { getSession } from "@/lib/auth";
import { resolveHomeRecommendations } from "@/lib/server/catalog-api";

export default async function Home() {
  const session = await getSession();
  if (!session) redirect("/login");

  const songs = await resolveHomeRecommendations(session.userId);

  return (
    <HomeContent songs={songs} userId={session.userId} username={session.username} />
  );
}

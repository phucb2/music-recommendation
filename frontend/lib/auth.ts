import { cookies } from "next/headers";
import { SESSION_COOKIE } from "@/lib/constants";

export type Session = {
  userId: string;
  /** Username from sign-in (shown in the header). */
  username: string;
};

export async function getSession(): Promise<Session | null> {
  const jar = await cookies();
  const raw = jar.get(SESSION_COOKIE)?.value;
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw) as Partial<Session>;
    if (!parsed?.userId || typeof parsed.userId !== "string") return null;
    const username =
      typeof parsed.username === "string" && parsed.username.length > 0
        ? parsed.username
        : parsed.userId;
    return { userId: parsed.userId, username };
  } catch {
    /* ignore */
  }
  return null;
}

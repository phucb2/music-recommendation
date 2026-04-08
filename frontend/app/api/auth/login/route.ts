import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { SESSION_COOKIE } from "@/lib/constants";

const DEMO_USER = "demo";
const DEMO_PASS = "demo";

export async function POST(request: Request) {
  let body: { username?: string; password?: string };
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid body" }, { status: 400 });
  }

  if (body.username !== DEMO_USER || body.password !== DEMO_PASS) {
    return NextResponse.json({ error: "Invalid credentials" }, { status: 401 });
  }

  const jar = await cookies();
  jar.set(
    SESSION_COOKIE,
    JSON.stringify({
      userId: "user_demo",
      username: body.username ?? DEMO_USER,
    }),
    {
      httpOnly: true,
      sameSite: "lax",
      path: "/",
      maxAge: 60 * 60 * 24 * 7,
    },
  );

  return NextResponse.json({ ok: true });
}

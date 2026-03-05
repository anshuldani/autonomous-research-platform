import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET() {
  const backendUrl = process.env.BACKEND_URL ?? "(not set — using localhost:8000)";
  let reachable = false;
  try {
    const res = await fetch(`${process.env.BACKEND_URL ?? "http://localhost:8000"}/health`, {
      signal: AbortSignal.timeout(5000),
    });
    reachable = res.ok;
  } catch {}
  return NextResponse.json({ backendUrl, reachable });
}

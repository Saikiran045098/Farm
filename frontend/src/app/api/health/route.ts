import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const DJANGO_API_URL = process.env.DJANGO_API_URL || "http://127.0.0.1:8000";

export async function GET() {
  let backendOk = false;
  try {
    const res = await fetch(`${DJANGO_API_URL}/api/health`, { cache: "no-store" });
    backendOk = res.ok;
  } catch {
    backendOk = false;
  }

  return NextResponse.json({
    frontend: "Next.js 16 (App Router)",
    backend: backendOk ? "Django REST API (Healthy)" : "Django backend offline",
    djangoUrl: DJANGO_API_URL,
    ok: true,
  });
}

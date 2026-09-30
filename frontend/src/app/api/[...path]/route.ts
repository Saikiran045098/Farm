import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const DJANGO_API_URL = process.env.DJANGO_API_URL || "http://127.0.0.1:8000";

async function proxy(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  const { path } = await ctx.params;
  const pathStr = path.join("/");
  const targetUrl = `${DJANGO_API_URL}/api/${pathStr}${req.nextUrl.search}`;

  const headers = new Headers();
  req.headers.forEach((val, key) => {
    if (key.toLowerCase() !== "host") {
      headers.set(key, val);
    }
  });

  const init: RequestInit = {
    method: req.method,
    headers,
    redirect: "manual",
  };

  if (req.method !== "GET" && req.method !== "HEAD") {
    try {
      init.body = await req.arrayBuffer();
    } catch {
      // body empty or stream
    }
  }

  try {
    const res = await fetch(targetUrl, init);
    const resHeaders = new Headers();

    res.headers.forEach((val, key) => {
      if (key.toLowerCase() !== "content-encoding") {
        resHeaders.set(key, val);
      }
    });

    return new NextResponse(res.body, {
      status: res.status,
      statusText: res.statusText,
      headers: resHeaders,
    });
  } catch {
    return NextResponse.json(
      {
        error: `Django backend is not running at ${DJANGO_API_URL}. Please start Django: 'cd backend && python manage.py runserver'`,
      },
      { status: 503 }
    );
  }
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const DELETE = proxy;
export const PATCH = proxy;

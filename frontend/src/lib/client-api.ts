const catalogCache = new Map<string, { data: unknown; expires: number }>();
const inFlight = new Map<string, Promise<unknown>>();
let cacheVersion = 0;
export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
 const method = options.method || "GET";
 const cacheable = method === "GET" && /^(products(?:[/?]|$)|categories(?:\?|$))/.test(path);
 if (method !== "GET") { catalogCache.clear(); inFlight.clear(); cacheVersion++; }
 const saved = catalogCache.get(path);
 if (cacheable && saved && saved.expires > Date.now()) return saved.data as T;
 if (cacheable && inFlight.has(path)) return await inFlight.get(path) as T;
 const version = cacheVersion;
 const request = (async () => {
  const response = await fetch(`/api/${path}`, { ...options, headers: { "Content-Type": "application/json", ...options.headers }, cache: "no-store" });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Something went wrong. Please try again.");
  if (cacheable && version === cacheVersion) catalogCache.set(path, { data, expires: Date.now() + 15000 });
  return data as T;
 })();
 if (cacheable) inFlight.set(path, request);
 try { return await request; } finally { if (cacheable && inFlight.get(path) === request) inFlight.delete(path); }
}
export const json = (data: unknown) => JSON.stringify(data);
export const delay = (ms: number) => new Promise<void>(resolve => setTimeout(resolve, ms));

import { cookies, headers } from "next/headers";
import { SignJWT, jwtVerify } from "jose";
import { createHash, randomUUID } from "crypto";
import { db } from "@/db";
import { users, cartItems, wishlists } from "@/db/schema";
import { and, eq, sql } from "drizzle-orm";
import type { User } from "@/lib/types";
const key = () => new TextEncoder().encode(createHash("sha256").update(process.env.JWT_SECRET || `${process.env.DATABASE_URL}:farmbuddy-session`).digest("hex"));
export function safeUser(u: typeof users.$inferSelect): User { return { id: u.id, name: u.name, email: u.email, phone: u.phone, role: u.role, addresses: u.addresses }; }
export async function currentUser(): Promise<User | null> {
 const token = (await cookies()).get("fb_session")?.value;
 if (!token) return null;
 try {
  const { payload } = await jwtVerify(token, key(), { algorithms: ["HS256"] });
  if (!payload.sub) return null;
  const [u] = await db.select().from(users).where(eq(users.id, payload.sub));
  return u ? safeUser(u) : null;
 } catch { return null; }
}
export async function signIn(u: typeof users.$inferSelect) {
 const jar = await cookies();
 const guest = jar.get("fb_guest")?.value;
 if (guest) {
  const guestItems = await db.select().from(cartItems).where(eq(cartItems.owner, guest));
  for (const item of guestItems) {
   await db.insert(cartItems).values({ id: randomUUID(), owner: u.id, productId: item.productId, weight: item.weight, quantity: item.quantity })
    .onConflictDoUpdate({ target: [cartItems.owner, cartItems.productId, cartItems.weight], set: { quantity: sql`least(${cartItems.quantity} + ${item.quantity}, 20)` } });
  }
  await db.delete(cartItems).where(eq(cartItems.owner, guest));
  const saved = await db.select().from(wishlists).where(eq(wishlists.owner, guest));
  for (const item of saved) await db.insert(wishlists).values({ id: randomUUID(), owner: u.id, productId: item.productId }).onConflictDoNothing();
  await db.delete(wishlists).where(eq(wishlists.owner, guest));
 }
 const token = await new SignJWT({ role: u.role }).setProtectedHeader({ alg: "HS256" }).setSubject(u.id).setIssuedAt().setExpirationTime("7d").sign(key());
 jar.set("fb_session", token, { httpOnly: true, sameSite: "lax", secure: (await headers()).get("x-forwarded-proto") === "https", path: "/", maxAge: 604800 });
 return safeUser(u);
}
export async function ownerFor(user: User | null) {
 if (user) return user.id;
 const jar = await cookies();
 let owner = jar.get("fb_guest")?.value;
 if (!owner || !/^[a-f0-9-]{36}$/.test(owner)) {
  owner = randomUUID(); jar.set("fb_guest", owner, { httpOnly: true, sameSite: "lax", path: "/", maxAge: 2592000, secure: (await headers()).get("x-forwarded-proto") === "https" });
 }
 return owner;
}
export async function signOut() { (await cookies()).delete("fb_session"); }
export const ownerItem = (owner: string, id: string) => and(eq(cartItems.owner, owner), eq(cartItems.id, id));
const attempts = new Map<string, { count: number; expires: number }>();
export function rateLimit(ip: string) {
 const item = attempts.get(ip);
 if (!item || item.expires < Date.now()) { attempts.set(ip, { count: 1, expires: Date.now() + 60000 }); return false; }
 item.count++; return item.count > 12;
}

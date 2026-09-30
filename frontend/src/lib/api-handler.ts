import { NextRequest, NextResponse } from "next/server";
import { db } from "@/db";
import { products, categories, users, cartItems, orders, subscriptions, newsletters, messages, wishlists } from "@/db/schema";
import { eq, and, or, ilike, desc, asc, sql, count, gte, lte } from "drizzle-orm";
import { z } from "zod";
import { hash, compare } from "bcryptjs";
import { randomUUID } from "crypto";
import { currentUser, signIn, signOut, safeUser, ownerFor, ownerItem, rateLimit } from "@/lib/auth";
import { ensureSeed } from "@/lib/seed";
import { weightedPrice } from "@/lib/types";
const productSchema = z.object({ name: z.string().min(2).max(150), teluguName: z.string().min(1).max(200), slug: z.string().regex(/^[a-z0-9-]+$/), description: z.string().min(10).max(4000), teluguDescription: z.string().max(4000).default(""), category: z.string().min(1), price: z.number().int().min(1).max(10000), originalPrice: z.number().int().positive().nullable().default(null), weight: z.string().regex(/^\d+(?:\.\d+)?(?:g|kg|ml|L)$/).refine(v => parseFloat(v) > 0, "Pack size must be positive"), weights: z.array(z.string().regex(/^\d+(?:\.\d+)?(?:g|kg|ml|L)$/).refine(v => parseFloat(v) > 0, "Pack size must be positive")).min(1), image: z.string().min(1).max(4000000).refine(v => v.startsWith("/images/") || v.startsWith("https://") || /^data:image\/(jpeg|png|webp);base64,/.test(v), "Use an image URL or supported image upload"), stock: z.number().int().min(0).max(10000), farmer: z.string().min(1).max(150), village: z.string().min(1).max(150), ingredients: z.array(z.string().max(100)), rating: z.string().default("4.8"), reviews: z.number().int().min(0).default(0), badge: z.string().max(60).nullable().default(null), isFeatured: z.boolean().default(false), isOrganic: z.boolean().default(true) });
const orderSchema = z.object({ name: z.string().min(2).max(120), phone: z.string().regex(/^[6-9]\d{9}$/, "Enter a valid 10-digit Indian mobile number"), email: z.string().email(), address: z.object({ house: z.string().min(1), street: z.string().min(2), area: z.string().min(2), city: z.string().min(2), district: z.string().min(2), state: z.string().min(2), pincode: z.string().regex(/^\d{6}$/) }), paymentMethod: z.enum(["Cash on Delivery", "UPI", "Card", "Net Banking"]), coupon: z.string().optional() });
const statuses = ["Pending", "Confirmed", "Processing", "Packed", "Out for Delivery", "Delivered", "Cancelled"];
type Context = { params: Promise<{ path: string[] }> };
function response(data: unknown, status = 200) { return NextResponse.json(data, { status }); }
class ApiError extends Error { constructor(message: string, public status = 400) { super(message); } }
async function handler(req: NextRequest, ctx: Context) {
 try {
  if (req.method !== "GET") {
   const origin = req.headers.get("origin"); const host = req.headers.get("x-forwarded-host") || req.headers.get("host");
   if (origin && new URL(origin).host !== host && new URL(origin).host !== req.nextUrl.host) throw new ApiError("Request origin is not allowed", 403);
  }
  await ensureSeed();
  const { path } = await ctx.params; const [resource, id, action] = path;
  const method = req.method; const query = req.nextUrl.searchParams;
  const user = await currentUser();
  const admin = () => { if (!user || user.role !== "admin") throw new ApiError("Administrator access required", 403); };
  const authenticated = () => { if (!user) throw new ApiError("Please sign in to continue", 401); return user; };
  const body = async () => { try { return await req.json(); } catch { throw new ApiError("Invalid request body"); } };
  if (resource === "auth") {
   if (id === "me" && method === "GET") return response({ user });
   if (id === "logout" && method === "POST") { await signOut(); return response({ ok: true }); }
   if ((id === "login" || id === "register") && method === "POST") {
    if (rateLimit(req.headers.get("x-forwarded-for") || "local")) throw new ApiError("Too many attempts. Please try again in a minute.", 429);
    const raw = await body();
    const data = z.object({ email: z.string().email().transform(v => v.toLowerCase().trim()), password: z.string().min(8).max(100), name: z.string().min(2).max(120).optional(), phone: z.string().regex(/^[6-9]\d{9}$/).optional() }).parse(raw);
    const [existing] = await db.select().from(users).where(eq(users.email, data.email));
    if (id === "register") {
     if (!data.name) throw new ApiError("Please enter your name");
     if (existing) throw new ApiError("An account with this email already exists", 409);
     const [created] = await db.insert(users).values({ id: randomUUID(), name: data.name, email: data.email, phone: data.phone || "", password: await hash(data.password, 12), role: "customer" }).returning();
     return response({ user: await signIn(created) }, 201);
    }
    if (!existing || !(await compare(data.password, existing.password))) throw new ApiError("Email or password is incorrect", 401);
    return response({ user: await signIn(existing) });
   }
  }
  if (resource === "products") {
   if (method === "GET") {
    if (id) { const [product] = await db.select().from(products).where(or(eq(products.id, id), eq(products.slug, id))); if (!product) throw new ApiError("This product is no longer available", 404); return response({ product }); }
    const filters = [];
    if (query.get("category")) filters.push(eq(products.category, query.get("category")!));
    const q = query.get("q")?.trim().slice(0, 100);
    if (q) for (const token of q.toLowerCase().split(/\s+/).filter(Boolean)) {
     const pattern = `%${token.replace(/[\\%_]/g, v => `\\${v}`)}%`;
     const aliases: Record<string, string> = { snacks: "telangana-foods", foods: "telangana-foods", dairy: "dairy", flour: "grains", flours: "grains", nuts: "dry-fruits", pickles: "pickles", seeds: "seeds", vegetables: "farm-produce", produce: "farm-produce" };
     const choices = [ilike(products.name, pattern), ilike(products.teluguName, pattern), ilike(products.category, pattern), ilike(products.farmer, pattern), ilike(products.village, pattern), sql`${products.ingredients}::text ilike ${pattern}`];
     if (aliases[token]) choices.push(eq(products.category, aliases[token]));
     if (/^\d+(?:\.\d+)?(?:g|kg|ml|l)$/i.test(token)) choices.push(sql`${products.weights} @> ${JSON.stringify([/\d+l$/i.test(token) && !token.endsWith("ml") ? token.toUpperCase() : token])}::jsonb`);
     filters.push(or(...choices)!);
    }
    if (query.get("featured") === "true") filters.push(eq(products.isFeatured, true));
    if (query.get("minPrice")) filters.push(gte(products.price, Math.max(0, Number(query.get("minPrice")) || 0)));
    if (query.has("maxPrice")) { const value = Number(query.get("maxPrice")); filters.push(lte(products.price, Number.isFinite(value) ? Math.max(0, value) : 2000)); }
    if (query.get("availability") === "in") filters.push(gte(products.stock, 1));
    if (query.get("availability") === "out") filters.push(eq(products.stock, 0));
    if (query.get("weight")) filters.push(sql`${products.weights} @> ${JSON.stringify([query.get("weight")])}::jsonb`);
    const sort = query.get("sort"); const ordering = sort === "price-low" ? asc(products.price) : sort === "price-high" ? desc(products.price) : sort === "newest" ? desc(products.createdAt) : asc(products.id);
    const limit = Math.min(100, Math.max(1, Number(query.get("limit")) || 12)); const page = Math.max(1, Number(query.get("page")) || 1);
    const where = and(...filters);
    const [rows, [total]] = await Promise.all([db.select().from(products).where(where).orderBy(ordering).limit(limit).offset((page - 1) * limit), db.select({ count: count() }).from(products).where(where)]);
    return response({ products: rows, total: total.count, page, pages: Math.ceil(total.count / limit) });
   }
   admin();
   if (method === "POST") { const data = productSchema.parse(await body()); if (!data.weights.includes(data.weight)) throw new ApiError("Available pack sizes must include the base pack size"); const [category] = await db.select().from(categories).where(eq(categories.slug, data.category)); if (!category) throw new ApiError("Select a valid category"); const [product] = await db.insert(products).values({ ...data, id: randomUUID() }).returning(); return response({ product }, 201); }
   if (method === "PUT" && id) { const data = productSchema.partial().parse(await body()); const [existing] = await db.select().from(products).where(eq(products.id, id)); if (!existing) throw new ApiError("Product not found", 404); if (!(data.weights || existing.weights).includes(data.weight || existing.weight)) throw new ApiError("Available pack sizes must include the base pack size"); const [product] = await db.update(products).set(data).where(eq(products.id, id)).returning(); return response({ product }); }
   if (method === "DELETE" && id) { const removed = await db.delete(products).where(eq(products.id, id)).returning(); if (!removed.length) throw new ApiError("Product not found", 404); return response({ ok: true }); }
  }
  if (resource === "categories") {
   if (method === "GET") return response({ categories: await db.select().from(categories) });
   admin();
   if (method === "POST") { const data = z.object({ slug: z.string().regex(/^[a-z0-9-]+$/), name: z.string().min(2), teluguName: z.string().min(1), description: z.string().default(""), image: z.string().default("/images/grains.jpg"), icon: z.string().default("Wheat") }).parse(await body()); const [category] = await db.insert(categories).values(data).returning(); return response({ category }, 201); }
   if (method === "PUT" && id) { const data = z.object({ name: z.string().min(2).max(100), teluguName: z.string().min(1).max(150), description: z.string().max(2000), image: z.string().min(1), icon: z.string().min(1) }).partial().parse(await body()); const [category] = await db.update(categories).set(data).where(eq(categories.slug, id)).returning(); if (!category) throw new ApiError("Category not found", 404); return response({ category }); }
   if (method === "DELETE" && id) { const [existing] = await db.select({ count: count() }).from(products).where(eq(products.category, id)); if (existing.count) throw new ApiError("Move all products to another category before removing this category."); const removed = await db.delete(categories).where(eq(categories.slug, id)).returning(); if (!removed.length) throw new ApiError("Category not found", 404); return response({ ok: true }); }
  }
  if (resource === "cart") {
   const owner = await ownerFor(user);
   if (method === "GET") { const rows = await db.select({ item: cartItems, product: products }).from(cartItems).innerJoin(products, eq(cartItems.productId, products.id)).where(eq(cartItems.owner, owner)); return response({ items: rows.map(({ item, product }) => ({ ...item, product, price: weightedPrice(product, item.weight) })) }); }
   if (method === "POST") {
    const data = z.object({ productId: z.string(), weight: z.string(), quantity: z.number().int().min(1).max(20).default(1) }).parse(await body());
    const item = await db.transaction(async tx => {
     const [product] = await tx.select().from(products).where(eq(products.id, data.productId)).for("update"); if (!product) throw new ApiError("Product unavailable", 404);
     if (!product.weights.includes(data.weight)) throw new ApiError("Please choose an available weight");
     const [existing] = await tx.select().from(cartItems).where(and(eq(cartItems.owner, owner), eq(cartItems.productId, product.id), eq(cartItems.weight, data.weight)));
     const amount = (existing?.quantity || 0) + data.quantity;
     if (amount > product.stock) throw new ApiError(`Only ${product.stock} packs are available`); if (amount > 20) throw new ApiError("You can add up to 20 packs of each product");
     const [saved] = await tx.insert(cartItems).values({ id: randomUUID(), owner, productId: product.id, weight: data.weight, quantity: data.quantity }).onConflictDoUpdate({ target: [cartItems.owner, cartItems.productId, cartItems.weight], set: { quantity: amount } }).returning(); return saved;
    }); return response({ item }, 201);
   }
   if (method === "PUT" && id) {
    const data = z.object({ quantity: z.number().int().min(1).max(20) }).parse(await body()); const [entry] = await db.select({ item: cartItems, product: products }).from(cartItems).innerJoin(products, eq(cartItems.productId, products.id)).where(ownerItem(owner, id));
    if (!entry) throw new ApiError("Basket item not found", 404); if (data.quantity > entry.product.stock) throw new ApiError(`Only ${entry.product.stock} packs are available`);
    const [item] = await db.update(cartItems).set(data).where(ownerItem(owner, id)).returning(); return response({ item });
   }
   if (method === "DELETE" && id) { await db.delete(cartItems).where(ownerItem(owner, id)); return response({ ok: true }); }
  }
  if (resource === "wishlist") {
   const owner = await ownerFor(user);
   if (method === "GET") { const rows = await db.select({ product: products }).from(wishlists).innerJoin(products, eq(wishlists.productId, products.id)).where(eq(wishlists.owner, owner)); return response({ products: rows.map(r => r.product) }); }
   if (method === "POST") { const data = z.object({ productId: z.string() }).parse(await body()); await db.insert(wishlists).values({ id: randomUUID(), owner, productId: data.productId }).onConflictDoNothing(); return response({ ok: true }); }
   if (method === "DELETE" && id) { await db.delete(wishlists).where(and(eq(wishlists.owner, owner), eq(wishlists.productId, id))); return response({ ok: true }); }
  }
  if (resource === "orders") {
   const owner = await ownerFor(user);
   if (method === "GET") {
    const condition = user?.role === "admin" ? undefined : eq(orders.owner, owner);
    if (id) { const [order] = await db.select().from(orders).where(and(eq(orders.id, id), condition)); if (!order) throw new ApiError("Order not found", 404); return response({ order }); }
    return response({ orders: await db.select().from(orders).where(condition).orderBy(desc(orders.createdAt)).limit(200) });
   }
   if (method === "POST") {
    const data = orderSchema.parse(await body());
    const order = await db.transaction(async tx => {
     const basket = await tx.select().from(cartItems).where(eq(cartItems.owner, owner)).orderBy(asc(cartItems.productId)).for("update");
     if (!basket.length) throw new ApiError("Your basket is empty. Add some village goodness first.");
     const items = [];
     for (const item of basket) {
      const [product] = await tx.select().from(products).where(eq(products.id, item.productId)).for("update");
      if (!product || product.stock < item.quantity) throw new ApiError(`${product?.name || "A product"} is no longer available in this quantity`);
      if (!product.weights.includes(item.weight)) throw new ApiError(`${product.name}: please select an available weight`);
      items.push({ productId: product.id, name: product.name, teluguName: product.teluguName, image: product.image, weight: item.weight, quantity: item.quantity, price: weightedPrice(product, item.weight) });
      await tx.update(products).set({ stock: product.stock - item.quantity }).where(eq(products.id, product.id));
     }
     const subtotal = items.reduce((s, i) => s + i.price * i.quantity, 0); const deliveryFee = subtotal >= 499 ? 0 : 40;
     const discount = data.coupon?.toUpperCase() === "VILLAGE10" && subtotal >= 499 ? Math.min(100, Math.round(subtotal * .1)) : 0;
     const [created] = await tx.insert(orders).values({ id: `FB-${Date.now().toString(36).toUpperCase()}-${randomUUID().slice(0, 4).toUpperCase()}`, owner, userId: user?.id || null, customerName: data.name, email: data.email, phone: data.phone, shippingAddress: data.address, items, subtotal, deliveryFee, discount, total: subtotal + deliveryFee - discount, paymentMethod: data.paymentMethod, paymentStatus: "pending", orderStatus: data.paymentMethod === "Cash on Delivery" ? "Confirmed" : "Pending" }).returning();
     await tx.delete(cartItems).where(eq(cartItems.owner, owner));
     if (user) await tx.update(users).set({ phone: data.phone, addresses: [data.address] }).where(eq(users.id, user.id));
     return created;
    }); return response({ order }, 201);
   }
   if (method === "PUT" && id && action === "status") {
    admin(); const { status } = z.object({ status: z.enum(["Pending", "Confirmed", "Processing", "Packed", "Out for Delivery", "Delivered", "Cancelled"]) }).parse(await body());
    const order = await db.transaction(async tx => {
     const [existing] = await tx.select().from(orders).where(eq(orders.id, id)).for("update"); if (!existing) throw new ApiError("Order not found", 404);
     if (existing.orderStatus === "Cancelled" && status !== "Cancelled") throw new ApiError("Cancelled orders cannot be reopened");
     if (existing.orderStatus === "Delivered" && status !== "Delivered") throw new ApiError("Delivered orders cannot be changed");
     if (status === "Cancelled" && existing.orderStatus !== "Cancelled") for (const item of existing.items) await tx.update(products).set({ stock: sql`${products.stock} + ${item.quantity}` }).where(eq(products.id, item.productId));
     const [updated] = await tx.update(orders).set({ orderStatus: status, ...(status === "Delivered" && existing.paymentMethod === "Cash on Delivery" ? { paymentStatus: "paid" } : {}) }).where(eq(orders.id, id)).returning(); return updated;
    }); return response({ order });
   }
  }
  if (resource === "users") {
   if (method === "GET") {
    admin(); const list = await db.select().from(users).where(id ? eq(users.id, id) : undefined); const allOrders = await db.select().from(orders);
    const customers = list.map(u => { const own = allOrders.filter(o => o.userId === u.id); return { ...safeUser(u), createdAt: u.createdAt, orders: own.length, spent: own.filter(o => o.orderStatus !== "Cancelled").reduce((s, o) => s + o.total, 0) }; });
    if (id && !customers.length) throw new ApiError("Customer not found", 404); return response(id ? { user: customers[0] } : { users: customers });
   }
   if (method === "PUT" && id) { const me = authenticated(); if (me.id !== id && me.role !== "admin") throw new ApiError("Not authorized", 403); const data = z.object({ name: z.string().min(2), phone: z.string().regex(/^[6-9]\d{9}$/), addresses: z.array(z.record(z.string(), z.string())).optional() }).parse(await body()); const [updated] = await db.update(users).set(data).where(eq(users.id, id)).returning(); if (!updated) throw new ApiError("Customer not found", 404); return response({ user: safeUser(updated) }); }
  }
  if (resource === "subscriptions") {
   const me = authenticated();
   if (method === "GET") return response({ subscriptions: await db.select().from(subscriptions).where(eq(subscriptions.userId, me.id)) });
   if (method === "POST") { const data = z.object({ quantity: z.enum(["500ml", "1L", "2L"]), frequency: z.enum(["Daily", "Alternate Days", "Weekly"]), address: z.string().min(10).max(1000) }).parse(await body()); const [subscription] = await db.insert(subscriptions).values({ ...data, id: randomUUID(), userId: me.id }).returning(); return response({ subscription }, 201); }
   if (method === "PUT" && id) { const data = z.object({ status: z.enum(["Active", "Paused", "Cancelled"]) }).parse(await body()); const [subscription] = await db.update(subscriptions).set(data).where(and(eq(subscriptions.id, id), eq(subscriptions.userId, me.id))).returning(); if (!subscription) throw new ApiError("Subscription not found", 404); return response({ subscription }); }
  }
  if (resource === "newsletter" && method === "POST") { const data = z.object({ email: z.string().email().transform(v => v.toLowerCase()) }).parse(await body()); await db.insert(newsletters).values(data).onConflictDoNothing(); return response({ ok: true }); }
  if (resource === "contact" && method === "POST") { const data = z.object({ name: z.string().min(2).max(100), email: z.string().email(), message: z.string().min(10).max(3000) }).parse(await body()); await db.insert(messages).values({ ...data, id: randomUUID() }); return response({ ok: true }, 201); }
  if (resource === "admin" && id === "stats" && method === "GET") {
   admin(); const [allOrders, allProducts, allUsers] = await Promise.all([db.select().from(orders).orderBy(desc(orders.createdAt)), db.select().from(products), db.select().from(users)]);
   const active = allOrders.filter(o => o.orderStatus !== "Cancelled");
   const sales = Array.from({ length: 7 }, (_, i) => { const d = new Date(); d.setDate(d.getDate() - 6 + i); const date = d.toISOString().slice(0, 10); const dayOrders = active.filter(o => o.createdAt.toISOString().slice(0, 10) === date); return { day: d.toLocaleDateString("en-IN", { weekday: "short" }), sales: dayOrders.reduce((s, o) => s + o.total, 0), orders: dayOrders.length }; });
   const performance = allProducts.map(p => ({ name: p.name, units: active.reduce((s, o) => s + o.items.filter(i => i.productId === p.id).reduce((a, i) => a + i.quantity, 0), 0) })).sort((a, b) => b.units - a.units).slice(0, 5);
   return response({ totalOrders: allOrders.length, revenue: active.reduce((s, o) => s + o.total, 0), customers: allUsers.filter(u => u.role === "customer").length, products: allProducts.length, lowStock: allProducts.filter(p => p.stock < 10), todayOrders: allOrders.filter(o => o.createdAt.toDateString() === new Date().toDateString()).length, sales, performance, recentOrders: allOrders.slice(0, 6), statuses });
  }
  throw new ApiError("Endpoint not found", 404);
 } catch (error) {
  if (error instanceof z.ZodError) return response({ error: error.issues.map(i => `${i.path.join(".")}: ${i.message}`).join(". ") }, 400);
  if (error instanceof ApiError) return response({ error: error.message }, error.status);
  const pgCode = (error as { cause?: { code?: string }; code?: string }).cause?.code || (error as { code?: string }).code;
  if (pgCode === "23505") return response({ error: "This email, slug, or entry already exists. Please use a unique value." }, 409);
  if (pgCode === "23503") return response({ error: "The selected related item no longer exists." }, 400);
  console.error("FarmBuddy API:", error); return response({ error: "Something went wrong. Please try again in a moment." }, 500);
 }
}
export const GET = handler; export const POST = handler; export const PUT = handler; export const DELETE = handler;

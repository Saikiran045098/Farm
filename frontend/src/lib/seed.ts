import { db } from "@/db";
import { categories, products, users, orders } from "@/db/schema";
import { demoCategories, demoProducts } from "@/data/catalog";
import { hash } from "bcryptjs";
import { count } from "drizzle-orm";
const globalSeed = globalThis as typeof globalThis & { fbSeed?: Promise<void> };
export async function ensureSeed() {
 if (!globalSeed.fbSeed) globalSeed.fbSeed = seed().catch((error) => { globalSeed.fbSeed = undefined; throw error; });
 await globalSeed.fbSeed;
}
async function seed() {
 const [existing] = await db.select({ count: count() }).from(products);
 if (existing.count > 0) return;
 await db.insert(categories).values(demoCategories).onConflictDoNothing();
 await db.insert(products).values(demoProducts.map(({ createdAt, ...product }) => ({ ...product, ...(createdAt instanceof Date ? { createdAt } : {}) }))).onConflictDoNothing();
 const password = await hash(process.env.DEMO_PASSWORD || "Village@2026", 12);
 const adminPassword = await hash(process.env.ADMIN_PASSWORD || "FarmBuddy@2026", 12);
 await db.insert(users).values([
  { id: "demo-admin", name: "FarmBuddy Admin", email: process.env.ADMIN_EMAIL || "admin@farmbuddy.in", phone: "9000010001", password: adminPassword, role: "admin" },
  { id: "demo-customer", name: "Ananya Reddy", email: "customer@farmbuddy.in", phone: "9876543210", password, role: "customer", addresses: [{ house: "12-4", street: "Green Park Road", area: "Kondapur", city: "Hyderabad", district: "Rangareddy", state: "Telangana", pincode: "500084" }] },
  { id: "demo-customer-2", name: "Praveen Kumar", email: "praveen@example.com", phone: "9849012345", password, role: "customer" },
  { id: "demo-customer-3", name: "Sowmya Rao", email: "sowmya@example.com", phone: "9700012345", password, role: "customer" },
 ]).onConflictDoNothing();
 const statuses = ["Delivered", "Delivered", "Delivered", "Delivered", "Packed", "Out for Delivery", "Processing", "Confirmed"];
 for (let i = 0; i < 16; i++) {
  const selected = [demoProducts[i % 4], demoProducts[10 + i % 8]];
  const items = selected.map((p) => ({ productId: p.id, name: p.name, teluguName: p.teluguName, image: p.image, weight: p.weight, quantity: 1 + i % 2, price: p.price }));
  const subtotal = items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const uid = i % 3 === 0 ? "demo-customer-2" : i % 3 === 1 ? "demo-customer-3" : "demo-customer";
  await db.insert(orders).values({ id: `FB-DEMO-${String(i + 1).padStart(4, "0")}`, owner: uid, userId: uid,
   customerName: uid === "demo-customer" ? "Ananya Reddy" : uid === "demo-customer-2" ? "Praveen Kumar" : "Sowmya Rao", email: uid === "demo-customer" ? "customer@farmbuddy.in" : uid === "demo-customer-2" ? "praveen@example.com" : "sowmya@example.com", phone: "9876543210",
   items, shippingAddress: { house: "12-4", street: "Green Park Road", area: "Kondapur", city: "Hyderabad", district: "Rangareddy", state: "Telangana", pincode: "500084" }, subtotal, deliveryFee: subtotal >= 499 ? 0 : 40, discount: 0, total: subtotal + (subtotal >= 499 ? 0 : 40), paymentMethod: "Cash on Delivery", paymentStatus: i < 10 ? "paid" : "pending", orderStatus: statuses[i % statuses.length], createdAt: new Date(Date.now() - (15 - i) * 24 * 60 * 60 * 1000) }).onConflictDoNothing();
 }
}

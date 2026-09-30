import { pgTable, text, integer, boolean, timestamp, jsonb, uniqueIndex } from "drizzle-orm/pg-core";

export const categories = pgTable("fb_categories", {
  slug: text("slug").primaryKey(), name: text("name").notNull(), teluguName: text("telugu_name").notNull(),
  description: text("description").notNull().default(""), image: text("image").notNull(), icon: text("icon").notNull(),
});
export const products = pgTable("fb_products", {
  id: text("id").primaryKey(), slug: text("slug").notNull().unique(), name: text("name").notNull(),
  teluguName: text("telugu_name").notNull(), description: text("description").notNull(),
  teluguDescription: text("telugu_description").notNull().default(""),
  category: text("category").notNull().references(() => categories.slug),
  price: integer("price").notNull(), originalPrice: integer("original_price"), weight: text("weight").notNull(),
  weights: jsonb("weights").$type<string[]>().notNull().default(["250g", "500g", "1kg"]),
  image: text("image").notNull(), stock: integer("stock").notNull().default(50),
  farmer: text("farmer").notNull().default("FarmBuddy Collective"), village: text("village").notNull().default("Siddipet, Telangana"),
  ingredients: jsonb("ingredients").$type<string[]>().notNull().default([]),
  rating: text("rating").notNull().default("4.8"), reviews: integer("reviews").notNull().default(24),
  badge: text("badge"), isFeatured: boolean("is_featured").notNull().default(false),
  isOrganic: boolean("is_organic").notNull().default(true), createdAt: timestamp("created_at").notNull().defaultNow(),
});
export const users = pgTable("fb_users", {
  id: text("id").primaryKey(), name: text("name").notNull(), email: text("email").notNull().unique(),
  phone: text("phone").notNull().default(""), password: text("password").notNull(), role: text("role").notNull().default("customer"),
  addresses: jsonb("addresses").$type<Record<string, string>[]>().notNull().default([]), createdAt: timestamp("created_at").notNull().defaultNow(),
});
export const cartItems = pgTable("fb_cart_items", {
  id: text("id").primaryKey(), owner: text("owner").notNull(), productId: text("product_id").notNull().references(() => products.id, { onDelete: "cascade" }),
  weight: text("weight").notNull(), quantity: integer("quantity").notNull().default(1),
}, (table) => [uniqueIndex("fb_cart_owner_product_weight").on(table.owner, table.productId, table.weight)]);
export type StoredOrderItem = { productId: string; name: string; teluguName: string; image: string; weight: string; quantity: number; price: number };
export const orders = pgTable("fb_orders", {
  id: text("id").primaryKey(), owner: text("owner").notNull(), userId: text("user_id").references(() => users.id, { onDelete: "set null" }),
  customerName: text("customer_name").notNull(), email: text("email").notNull(), phone: text("phone").notNull(),
  items: jsonb("items").$type<StoredOrderItem[]>().notNull(), shippingAddress: jsonb("shipping_address").$type<Record<string, string>>().notNull(),
  subtotal: integer("subtotal").notNull(), deliveryFee: integer("delivery_fee").notNull(), discount: integer("discount").notNull().default(0),
  total: integer("total").notNull(), paymentMethod: text("payment_method").notNull(), paymentStatus: text("payment_status").notNull().default("pending"),
  orderStatus: text("order_status").notNull().default("Confirmed"), createdAt: timestamp("created_at").notNull().defaultNow(),
});
export const subscriptions = pgTable("fb_subscriptions", {
  id: text("id").primaryKey(), userId: text("user_id").notNull().references(() => users.id),
  quantity: text("quantity").notNull(), frequency: text("frequency").notNull(), address: text("address").notNull(),
  status: text("status").notNull().default("Active"), createdAt: timestamp("created_at").notNull().defaultNow(),
});
export const newsletters = pgTable("fb_newsletters", { email: text("email").primaryKey(), createdAt: timestamp("created_at").notNull().defaultNow() });
export const messages = pgTable("fb_messages", { id: text("id").primaryKey(), name: text("name").notNull(), email: text("email").notNull(), message: text("message").notNull(), createdAt: timestamp("created_at").notNull().defaultNow() });
export const wishlists = pgTable("fb_wishlists", {
  id: text("id").primaryKey(), owner: text("owner").notNull(), productId: text("product_id").notNull().references(() => products.id, { onDelete: "cascade" }),
}, (table) => [uniqueIndex("fb_wishlist_owner_product").on(table.owner, table.productId)]);

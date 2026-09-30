export type Category = { slug: string; name: string; teluguName: string; description: string; image: string; icon: string };
export type Product = {
  id: string; slug: string; name: string; teluguName: string; description: string; teluguDescription: string;
  category: string; price: number; originalPrice: number | null; weight: string; weights: string[]; image: string;
  stock: number; farmer: string; village: string; ingredients: string[]; rating: string; reviews: number;
  badge: string | null; isFeatured: boolean; isOrganic: boolean; createdAt?: string | Date;
};
export type User = { id: string; name: string; email: string; phone: string; role: string; addresses?: Record<string, string>[] };
export type CartItem = { id: string; productId: string; weight: string; quantity: number; price: number; product: Product };
export type OrderItem = { productId: string; name: string; teluguName: string; image: string; weight: string; quantity: number; price: number };
export type Order = { id: string; customerName: string; email: string; phone: string; items: OrderItem[]; shippingAddress: Record<string, string>; subtotal: number; deliveryFee: number; discount: number; total: number; paymentMethod: string; paymentStatus: string; orderStatus: string; createdAt: string | Date };
export type Subscription = { id: string; quantity: string; frequency: string; address: string; status: string };
export const money = (value: number) => `₹${value.toLocaleString("en-IN")}`;
export function weightNumber(weight: string) { const n = parseFloat(weight); return /kg|^\d+L$/i.test(weight) ? n * 1000 : n; }
export function weightedPrice(product: Pick<Product, "price" | "weight">, weight: string) { return Math.round(product.price * weightNumber(weight) / weightNumber(product.weight)); }

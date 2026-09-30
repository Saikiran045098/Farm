import { demoCategories, demoProducts } from "@/data/catalog";
import type { Category, Product } from "@/lib/types";

const DJANGO_API_URL = process.env.DJANGO_API_URL || "http://127.0.0.1:8000";

export async function getProducts(params?: Record<string, string>): Promise<{ products: Product[]; total: number }> {
  try {
    const searchParams = new URLSearchParams(params);
    const res = await fetch(`${DJANGO_API_URL}/api/products?${searchParams.toString()}`, {
      cache: "no-store",
    });
    if (res.ok) {
      const data = await res.json();
      return { products: data.products || [], total: data.total || 0 };
    }
  } catch {
    // Graceful fallback during startup / build
  }
  return { products: demoProducts, total: demoProducts.length };
}

export async function getCategories(): Promise<Category[]> {
  try {
    const res = await fetch(`${DJANGO_API_URL}/api/categories`, {
      cache: "no-store",
    });
    if (res.ok) {
      const data = await res.json();
      return data.categories || [];
    }
  } catch {
    // Graceful fallback during startup / build
  }
  return demoCategories;
}

export async function getProductBySlug(slug: string): Promise<Product | null> {
  try {
    const res = await fetch(`${DJANGO_API_URL}/api/products/${slug}`, {
      cache: "no-store",
    });
    if (res.ok) {
      const data = await res.json();
      return data.product || null;
    }
  } catch {
    // Graceful fallback during startup / build
  }
  return demoProducts.find((p) => p.slug === slug || p.id === slug) || null;
}

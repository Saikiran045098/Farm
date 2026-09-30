import { getCategories } from "@/lib/server-api";
import { ShopContent } from "@/components/shop-content";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Our Village Market",
  description: "Explore fresh milk, authentic Telangana foods, wholesome grains, seeds and village products.",
};

export const dynamic = "force-dynamic";

export default async function ShopPage({
  searchParams,
}: {
  searchParams: Promise<{ category?: string; q?: string }>;
}) {
  const [groups, params] = await Promise.all([
    getCategories(),
    searchParams,
  ]);

  return (
    <ShopContent
      categories={groups}
      initialCategory={params.category}
      initialQuery={params.q}
    />
  );
}

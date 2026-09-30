import { getProducts, getCategories } from "@/lib/server-api";
import { HomePageContent } from "@/components/homepage";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const [{ products: catalog }, groups] = await Promise.all([
    getProducts({ limit: "100" }),
    getCategories(),
  ]);

  return <HomePageContent products={catalog} categories={groups} />;
}

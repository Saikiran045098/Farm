import { getProductBySlug, getProducts } from "@/lib/server-api";
import { notFound } from "next/navigation";
import Link from "next/link";
import { ChevronRight } from "lucide-react";
import { ProductDetail } from "@/components/product-detail";
import { ProductGrid } from "@/components/product-card";
import { SectionHeading } from "@/components/ui";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const product = await getProductBySlug(slug);
  return {
    title: product?.name || "Product not found",
    description: product?.description,
    openGraph: product
      ? { title: product.name, description: product.description, images: [product.image] }
      : undefined,
  };
}

export default async function ProductPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const product = await getProductBySlug(slug);
  if (!product) notFound();

  const { products: allInCategory } = await getProducts({ category: product.category, limit: "5" });
  const related = allInCategory.filter((p) => p.id !== product.id).slice(0, 4);

  const structuredData = {
    "@context": "https://schema.org",
    "@type": "Product",
    name: product.name,
    description: product.description,
    image: product.image,
    sku: product.id,
    brand: { "@type": "Brand", name: "FarmBuddy" },
    offers: {
      "@type": "Offer",
      price: product.price,
      priceCurrency: "INR",
      availability: product.stock > 0 ? "https://schema.org/InStock" : "https://schema.org/OutOfStock",
    },
  };

  return (
    <main className="container">
      <div className="breadcrumbs" style={{ paddingTop: 29 }}>
        <Link href="/">Home</Link>
        <ChevronRight size={11} />
        <Link href="/shop">Village market</Link>
        <ChevronRight size={11} />
        <Link href={`/shop?category=${product.category}`}>
          {product.category.replaceAll("-", " ")}
        </Link>
        <ChevronRight size={11} />
        <span>{product.name}</span>
      </div>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData).replace(/</g, "\\u003c") }}
      />
      <ProductDetail product={product} full />
      {related.length > 0 && (
        <section className="section">
          <SectionHeading
            eyebrow="A LITTLE MORE FROM OUR VILLAGE"
            title="Good company for your basket."
            href={`/shop?category=${product.category}`}
          />
          <ProductGrid products={related} />
        </section>
      )}
    </main>
  );
}

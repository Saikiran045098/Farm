import { CheckoutContent } from "@/components/checkout-content";
import type { Metadata } from "next";
export const metadata: Metadata = { title: "Bring Your Basket Home", robots: { index: false, follow: false } };
export default function CheckoutPage() { return <CheckoutContent />; }

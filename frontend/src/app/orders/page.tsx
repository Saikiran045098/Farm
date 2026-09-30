import { OrdersPanel } from "@/components/orders-content";
import Link from "next/link";
export const metadata = { title: "Your Farm Baskets", robots: { index: false, follow: false } };
export default function OrdersPage() { return <main className="container info-page"><div className="page-heading"><span className="eyebrow">YOUR LITTLE VILLAGE JOURNEYS</span><h1>Your baskets of goodness.</h1><p>From our fields and kitchens, to your family. <Link className="text-link" href="/account">Manage your account</Link></p></div><OrdersPanel /></main>; }

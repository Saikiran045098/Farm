import { OrderTrackingContent } from "@/components/orders-content";
export const metadata = { title: "Your Basket’s Journey", robots: { index: false, follow: false } };
export default async function OrderPage({ params }: { params: Promise<{ id: string }> }) { const { id } = await params; return <OrderTrackingContent id={id} />; }

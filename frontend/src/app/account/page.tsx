import { AccountContent } from "@/components/account-content";
import type { Metadata } from "next";
export const metadata: Metadata = { title: "Your Village Account", robots: { index: false, follow: false } };
export default async function AccountPage({ searchParams }: { searchParams: Promise<{ tab?: string }> }) { const params = await searchParams; return <AccountContent initialTab={params.tab} />; }

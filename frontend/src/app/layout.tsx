import type { Metadata } from "next";
import type { ReactNode } from "react";
import { FarmProvider } from "@/components/farm-provider";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000"),
  title: { default: "FarmBuddy | Fresh Farm Products & Telangana Traditional Foods", template: "%s | FarmBuddy" },
  description: "Shop fresh milk, dairy products, Telangana traditional foods, grains, seeds, dry fruits and authentic village products with FarmBuddy.",
  applicationName: "FarmBuddy",
  keywords: ["Telangana", "Sarvapindi", "fresh milk", "village market", "farm fresh", "Sakinalu"],
  openGraph: {
    title: "FarmBuddy — From our village, with love.",
    description: "Fresh from the Farm. Authentic from Our Village.",
    images: [{ url: "/images/village-hero.jpg", width: 1536, height: 1024 }],
    type: "website",
  },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400..700;1,9..40,400..700&family=Lora:ital,wght@0,400..700;1,400..700&family=Noto+Sans+Telugu:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <FarmProvider>{children}</FarmProvider>
      </body>
    </html>
  );
}

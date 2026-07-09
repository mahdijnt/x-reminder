import type { Metadata } from "next";
import type { ReactNode } from "react";

import "./globals.css";

import { AppProviders } from "@/providers/app-providers";
import { appConfig } from "@/config/app.config";

export const metadata: Metadata = {
  title: { default: appConfig.name, template: `%s | ${appConfig.name}` },
  description: appConfig.description,
  metadataBase: new URL(appConfig.url),
  openGraph: { title: appConfig.name, description: appConfig.description, url: appConfig.url, siteName: appConfig.name, type: "website" },
  twitter: { card: "summary_large_image", title: appConfig.name, description: appConfig.description },
  robots: { index: true, follow: true },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-background text-foreground antialiased">
        <a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:bg-background focus:px-3 focus:py-2 focus:text-sm">Skip to main content</a>
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}

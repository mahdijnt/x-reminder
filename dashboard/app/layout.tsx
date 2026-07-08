import type { ReactNode } from "react";

import "./globals.css";

export const metadata = {
  title: "X Engagement Intelligence Manager",
  description: "Dashboard skeleton (no product features yet).",
};

export default function RootLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-background text-foreground antialiased">
        {children}
      </body>
    </html>
  );
}

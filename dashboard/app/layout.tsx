import type { ReactNode } from "react";

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
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

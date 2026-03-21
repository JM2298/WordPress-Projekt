import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "WordPress Projekt Frontend",
  description: "Next.js frontend for authentication and ecommerce views.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pl">
      <body>{children}</body>
    </html>
  );
}

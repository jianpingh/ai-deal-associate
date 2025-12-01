import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Deal Associate",
  description: "AI Agent for Deal Processing",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

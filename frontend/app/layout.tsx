import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BuildWise AI - AI CTO Platform",
  description: "Enterprise-grade multi-agent AI CTO translating software ideas into technical specs.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen flex flex-col justify-between">
        <main className="flex-grow">{children}</main>
      </body>
    </html>
  );
}

import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";
import { Providers } from "./providers";
import { HeaderConnectionStatus } from "@/components/HeaderConnectionStatus";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "EstimateIQ - AI-Powered Marine Service Estimates",
  description: "Transform your service department's collective experience into instant, accurate estimates with AI-powered recommendations.",
};

function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-marine-200 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <Link href="/" className="flex items-center space-x-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-marine-600">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="h-5 w-5 text-white"
            >
              <path d="M2 12h6" />
              <path d="M22 12h-6" />
              <path d="M12 2v6" />
              <path d="M12 22v-6" />
              <circle cx="12" cy="12" r="4" />
            </svg>
          </div>
          <span className="text-xl font-bold text-marine-800">EstimateIQ</span>
        </Link>
        <nav className="flex items-center space-x-6">
          <HeaderConnectionStatus />
          <Link
            href="/estimate/new"
            className="text-sm font-medium text-marine-600 hover:text-marine-800 transition-colors"
          >
            New Estimate
          </Link>
          <Link
            href="/estimate/new"
            className="inline-flex h-9 items-center justify-center rounded-md bg-marine-600 px-4 text-sm font-medium text-white shadow transition-colors hover:bg-marine-700 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-marine-700"
          >
            Get Started
          </Link>
        </nav>
      </div>
    </header>
  );
}

function Footer() {
  return (
    <footer className="border-t border-marine-200 bg-marine-50">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <p className="text-sm text-marine-500">
          &copy; {new Date().getFullYear()} EstimateIQ by DockMaster. A Valsoft Company.
        </p>
        <p className="text-sm text-marine-400">
          AI-Powered Marine Service Estimates
        </p>
      </div>
    </footer>
  );
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen flex flex-col`}
      >
        <Providers>
          <Header />
          <main className="flex-1">
            {children}
          </main>
          <Footer />
        </Providers>
      </body>
    </html>
  );
}

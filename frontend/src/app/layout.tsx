// src/app/layout.tsx
//
// PURPOSE: Root layout — wraps EVERY page in the app.
//
// WHY layout.tsx?
// Next.js App Router requires a layout.tsx at each directory level.
// The root layout defines the <html> and <body> tags. You can only have
// one root layout. Nested layouts can exist inside route folders.
//
// Server Component (no "use client"):
// layout.tsx runs on the server. It never needs useState or browser APIs.
// Keeping it as a Server Component means Next.js can pre-render the shell
// HTML before sending it to the browser.
//
// METADATA:
// The `metadata` export tells Next.js what to put in <title> and <meta>
// without needing a separate HTML file.

import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Task Platform — Distributed Task Processing",
  description:
    "Frontend for the Distributed Task Processing Platform. Manage tasks and trigger Celery background jobs via FastAPI.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

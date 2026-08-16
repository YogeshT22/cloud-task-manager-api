"use client";
// src/app/page.tsx
//
// PURPOSE: Root route ("/"). Acts as an auth-aware redirect.
//
// WHY "use client"?
// We need localStorage (browser API) to check if the user is logged in.
// localStorage does not exist on the server. "use client" tells Next.js:
// "Run this component in the browser, not during server rendering."
//
// INTERVIEW QUESTION: "Why can't a Server Component access localStorage?"
// Answer: Server Components run in Node.js at request time. Node.js has no
// browser APIs — localStorage, window, document don't exist there.
// Only Client Components (with "use client") run in the browser.
//
// PATTERN: useEffect + useRouter = the standard way to do a client-side
// redirect based on browser state (auth token, cookies, etc.)

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { isAuthenticated } from "./lib/auth";

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    // Check auth token in localStorage and redirect accordingly.
    // This runs only after the component mounts in the browser.
    if (isAuthenticated()) {
      router.replace("/dashboard");
    } else {
      router.replace("/login");
    }
  }, [router]);

  // Show nothing while the redirect happens.
  // In production you'd render a branded loading screen.
  return null;
}

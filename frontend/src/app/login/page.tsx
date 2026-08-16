"use client";
// src/app/login/page.tsx
//
// PURPOSE: Login and Register form. Handles user authentication.
//
// WHY "use client":
// This component uses useState (for form fields, loading, error messages)
// and event handlers (onSubmit). These require the browser.
// A Server Component can't hold mutable state or respond to user input.
//
// FLOW (Login):
//   1. User submits form
//   2. We call POST /login via api.ts
//   3. FastAPI validates credentials, returns { access_token, token_type }
//   4. We store the token in localStorage via auth.ts
//   5. We redirect to /dashboard using Next.js router
//
// FLOW (Register):
//   1. User submits form
//   2. We call POST /users/ to create the account
//   3. On success, we auto-switch to login tab
//
// INTERVIEW POINT:
// FastAPI's /login endpoint uses OAuth2PasswordRequestForm which requires
// application/x-www-form-urlencoded encoding (NOT JSON). This is why
// api.ts uses URLSearchParams for that specific call.

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { login, registerUser } from "../lib/api";
import { saveToken } from "../lib/auth";

type Tab = "login" | "register";

export default function LoginPage() {
  const router = useRouter();

  // Tab state to switch between Login and Register views
  const [activeTab, setActiveTab] = useState<Tab>("login");

  // Controlled form inputs — React manages the value of each input
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  // UI feedback state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Reset messages when switching tabs
  function switchTab(tab: Tab) {
    setActiveTab(tab);
    setError(null);
    setSuccessMsg(null);
  }

  async function handleLogin(e: FormEvent) {
    e.preventDefault(); // Prevent browser's default form submission (page reload)
    setLoading(true);
    setError(null);
    try {
      const response = await login(email, password);
      saveToken(response.access_token);       // Store JWT in localStorage
      router.push("/dashboard");              // Navigate to protected dashboard
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleRegister(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccessMsg(null);
    try {
      await registerUser(email, password);
      setSuccessMsg("Account created! You can now log in.");
      setActiveTab("login");
      setPassword(""); // Clear password after registration
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-box">
        {/* Logo / Brand */}
        <div className="login-logo">
          <div className="login-logo-mark">⚡</div>
          <h1 className="login-title">Task Platform</h1>
          <p className="login-subtitle">Distributed background processing</p>
        </div>

        {/* Tab switcher */}
        <div className="login-tabs">
          <button
            id="tab-login"
            className={`login-tab ${activeTab === "login" ? "active" : ""}`}
            onClick={() => switchTab("login")}
            type="button"
          >
            Sign In
          </button>
          <button
            id="tab-register"
            className={`login-tab ${activeTab === "register" ? "active" : ""}`}
            onClick={() => switchTab("register")}
            type="button"
          >
            Register
          </button>
        </div>

        {/* Card */}
        <div className="card">
          {/* Error / success alerts */}
          {error && <div className="alert alert-error" role="alert">{error}</div>}
          {successMsg && <div className="alert alert-success" role="status">{successMsg}</div>}

          {/* Form — same structure for both tabs; only the submit handler differs */}
          <form
            onSubmit={activeTab === "login" ? handleLogin : handleRegister}
            id="auth-form"
          >
            <div className="form-group">
              <label htmlFor="email">Email Address</label>
              <input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete={activeTab === "login" ? "current-password" : "new-password"}
              />
            </div>

            <button
              id="submit-btn"
              type="submit"
              className="btn btn-primary btn-full"
              disabled={loading}
            >
              {loading ? (
                <><span className="spinner" /> Processing…</>
              ) : activeTab === "login" ? (
                "Sign In"
              ) : (
                "Create Account"
              )}
            </button>
          </form>
        </div>

        {/* Footer note */}
        <p style={{
          textAlign: "center",
          marginTop: "16px",
          fontSize: "0.75rem",
          color: "var(--text-muted)",
          fontFamily: "var(--font-mono)"
        }}>
          Backend: {process.env.NEXT_PUBLIC_API_URL}
        </p>
      </div>
    </div>
  );
}

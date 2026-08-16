"use client";
// src/app/dashboard/page.tsx
//
// PURPOSE: Main task management dashboard. Full CRUD + reminder dispatch.
//
// WHY "use client":
// - useState for task list, form fields, loading/error states
// - useEffect to load tasks on mount
// - Event handlers for every button (create, delete, complete, remind)
// All of these require the browser runtime.
//
// DATA FLOW:
//   On mount (useEffect) → GET /tasks/ → render task list
//   Create form submit   → POST /tasks/ → prepend to task list
//   Toggle completed     → PUT /tasks/{id} → update item in list
//   Delete               → DELETE /tasks/{id} → remove from list
//   Send reminder        → POST /tasks/{id}/remind → show toast with Celery task ID
//
// INTERVIEW POINT — Why useEffect for data fetching here?
// In a real production app with Next.js App Router, you'd prefer server-side
// data fetching in a Server Component (faster first render, no loading flash).
// Here we use useEffect because the request needs the JWT token from localStorage,
// which is only available in the browser. This is the correct pattern when auth
// state lives client-side.

import { useState, useEffect, FormEvent } from "react";
import { useRouter } from "next/navigation";
import {
  getTasks,
  createTask,
  updateTask,
  deleteTask,
  sendReminder,
  Task,
} from "../lib/api";
import { isAuthenticated, clearToken } from "../lib/auth";

// Small typed state for the "reminder queued" toast
interface ToastState {
  taskTitle: string;
  celeryId: string;
}

export default function DashboardPage() {
  const router = useRouter();

  // ── State ──────────────────────────────────────────────────────────────────
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Create-task form
  const [newTitle, setNewTitle] = useState("");
  const [newContent, setNewContent] = useState("");
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  // Reminder toast
  const [toast, setToast] = useState<ToastState | null>(null);

  // ── Auth guard ─────────────────────────────────────────────────────────────
  // Check on mount. If no token, redirect to login.
  // This is a client-side guard — it runs after initial render.
  // For a production app, a middleware.ts route guard is more robust.
  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login");
    }
  }, [router]);

  // ── Fetch tasks on mount ───────────────────────────────────────────────────
  useEffect(() => {
    fetchTasks();
  }, []);

  async function fetchTasks() {
    setLoading(true);
    setError(null);
    try {
      const data = await getTasks();
      setTasks(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load tasks");
    } finally {
      setLoading(false);
    }
  }

  // ── Create task ────────────────────────────────────────────────────────────
  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    if (!newTitle.trim() || !newContent.trim()) return;
    setCreating(true);
    setCreateError(null);
    try {
      const created = await createTask({ title: newTitle.trim(), content: newContent.trim() });
      // Prepend the new task so it appears at the top of the list
      setTasks((prev) => [created, ...prev]);
      setNewTitle("");
      setNewContent("");
    } catch (err: unknown) {
      setCreateError(err instanceof Error ? err.message : "Create failed");
    } finally {
      setCreating(false);
    }
  }

  // ── Toggle completed ───────────────────────────────────────────────────────
  async function handleToggle(task: Task) {
    try {
      const updated = await updateTask(task.id, {
        title: task.title,
        content: task.content,
        completed: !task.completed,
      });
      // Replace just the updated task in the list (immutable state update pattern)
      setTasks((prev) => prev.map((t) => (t.id === task.id ? updated : t)));
    } catch {
      setError("Failed to update task");
    }
  }

  // ── Delete task ────────────────────────────────────────────────────────────
  async function handleDelete(id: number) {
    try {
      await deleteTask(id);
      // Filter the deleted task out of local state
      setTasks((prev) => prev.filter((t) => t.id !== id));
    } catch {
      setError("Failed to delete task");
    }
  }

  // ── Send reminder (Celery background job) ──────────────────────────────────
  async function handleRemind(task: Task) {
    try {
      const result = await sendReminder(task.id);
      // Show a toast notification with the Celery task ID
      setToast({ taskTitle: task.title, celeryId: result.task_id });
      // Auto-dismiss after 6 seconds
      setTimeout(() => setToast(null), 6000);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Reminder dispatch failed");
    }
  }

  // ── Logout ─────────────────────────────────────────────────────────────────
  function handleLogout() {
    clearToken();
    router.replace("/login");
  }

  // ── Derived stats ──────────────────────────────────────────────────────────
  const totalTasks = tasks.length;
  const completedTasks = tasks.filter((t) => t.completed).length;
  const pendingTasks = totalTasks - completedTasks;

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <>
      {/* Sticky Navbar */}
      <nav className="navbar">
        <div className="container">
          <div className="navbar-inner">
            <div className="navbar-brand">
              <div className="navbar-logo">⚡ Task <span>Platform</span></div>
              <div className="navbar-meta">FastAPI + Celery + RabbitMQ</div>
            </div>
            <button
              id="logout-btn"
              onClick={handleLogout}
              className="btn btn-ghost"
              style={{ fontSize: "0.8125rem" }}
            >
              Sign Out
            </button>
          </div>
        </div>
      </nav>

      <main className="container">
        {/* Page Header */}
        <div className="page-header">
          <h1 className="page-title">Task Dashboard</h1>
          <p className="page-subtitle">
            Manage tasks and dispatch background reminders via Celery workers
          </p>
        </div>

        {/* Stats Row */}
        <div className="stats-row">
          <div className="stat-card">
            <div className="stat-number">{totalTasks}</div>
            <div className="stat-label">Total Tasks</div>
          </div>
          <div className="stat-card">
            <div className="stat-number" style={{ color: "var(--accent-green)" }}>{completedTasks}</div>
            <div className="stat-label">Completed</div>
          </div>
          <div className="stat-card">
            <div className="stat-number" style={{ color: "var(--accent-yellow)" }}>{pendingTasks}</div>
            <div className="stat-label">Pending</div>
          </div>
        </div>

        {/* Create Task Form */}
        <div className="create-form">
          <div className="section-header">
            <h2 className="section-title">➕ New Task</h2>
          </div>
          {createError && <div className="alert alert-error">{createError}</div>}
          <form onSubmit={handleCreate} id="create-task-form">
            <div className="create-form-grid">
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label htmlFor="task-title">Title</label>
                <input
                  id="task-title"
                  type="text"
                  placeholder="e.g. Review pull request"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  required
                />
              </div>
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label htmlFor="task-content">Description</label>
                <input
                  id="task-content"
                  type="text"
                  placeholder="e.g. Check the feature/auth branch"
                  value={newContent}
                  onChange={(e) => setNewContent(e.target.value)}
                  required
                />
              </div>
            </div>
            <div style={{ marginTop: "16px" }}>
              <button
                id="create-task-btn"
                type="submit"
                className="btn btn-primary"
                disabled={creating}
              >
                {creating ? <><span className="spinner" /> Creating…</> : "Create Task"}
              </button>
            </div>
          </form>
        </div>

        {/* Task List */}
        <div className="section-header">
          <h2 className="section-title">📋 Your Tasks</h2>
          <button
            id="refresh-btn"
            onClick={fetchTasks}
            className="btn btn-ghost"
            disabled={loading}
            style={{ fontSize: "0.8125rem" }}
          >
            {loading ? <><span className="spinner" /></> : "↻ Refresh"}
          </button>
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        {loading ? (
          <div className="empty-state">
            <div className="spinner" style={{ width: 32, height: 32, borderWidth: 3 }} />
          </div>
        ) : tasks.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">📭</div>
            <p className="empty-state-text">No tasks yet. Create one above!</p>
          </div>
        ) : (
          <div className="task-list">
            {tasks.map((task) => (
              <div
                key={task.id}
                className={`task-item ${task.completed ? "completed" : ""}`}
                id={`task-${task.id}`}
              >
                {/* Left: task content */}
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                    <span className="task-title">{task.title}</span>
                    <span className={`badge ${task.completed ? "badge-done" : "badge-pending"}`}>
                      {task.completed ? "Done" : "Pending"}
                    </span>
                  </div>
                  <p className="task-content">{task.content}</p>
                  <div className="task-meta">
                    <span>ID: {task.id}</span>
                    <span>Created: {new Date(task.created_at).toLocaleString()}</span>
                  </div>
                </div>

                {/* Right: action buttons */}
                <div className="task-actions">
                  <button
                    id={`toggle-${task.id}`}
                    onClick={() => handleToggle(task)}
                    className="btn btn-success"
                    title={task.completed ? "Mark as pending" : "Mark as done"}
                  >
                    {task.completed ? "↩ Reopen" : "✓ Done"}
                  </button>

                  <button
                    id={`remind-${task.id}`}
                    onClick={() => handleRemind(task)}
                    className="btn btn-ghost"
                    title="Queue a Celery reminder for this task"
                    disabled={task.completed}
                  >
                    🔔 Remind
                  </button>

                  <button
                    id={`delete-${task.id}`}
                    onClick={() => handleDelete(task.id)}
                    className="btn btn-danger"
                    title="Delete this task"
                  >
                    🗑
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        <div style={{ height: "48px" }} />
      </main>

      {/* Reminder Toast
          Appears bottom-right when POST /tasks/{id}/remind returns 202.
          Shows the Celery task ID so you can cross-reference with worker logs. */}
      {toast && (
        <div className="reminder-toast" role="status" id="reminder-toast">
          <div className="reminder-toast-title">✅ Reminder queued via Celery</div>
          <div style={{ fontSize: "0.8125rem", color: "var(--text-secondary)", marginBottom: "4px" }}>
            Task: &ldquo;{toast.taskTitle}&rdquo;
          </div>
          <div className="reminder-toast-id">Celery ID: {toast.celeryId}</div>
          <button
            onClick={() => setToast(null)}
            style={{ marginTop: "8px", fontSize: "0.75rem" }}
            className="btn btn-ghost"
          >
            Dismiss
          </button>
        </div>
      )}
    </>
  );
}

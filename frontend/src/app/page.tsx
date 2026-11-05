
"use client";

import { useEffect, useState } from "react";
import { createClient, SupabaseClient } from "@supabase/supabase-js";

type Task = {
  id: string;
  title: string;
  description?: string;
  status: "pending" | "in_progress" | "completed";
  priority: "low" | "medium" | "high";
  created_at: string;
};

type AppUser = {
  id: string;
  full_name: string | null;
  email: string;
};

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

const API =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "http://127.0.0.1:5000";

let supabase: SupabaseClient | null = null;

if (supabaseUrl && supabaseKey) {
  supabase = createClient(supabaseUrl, supabaseKey);
}

export default function Home() {
  const [user, setUser] = useState<any>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [users, setUsers] = useState<AppUser[]>([]);
  const [selectedUsers, setSelectedUsers] =
    useState<Record<string, string>>({});
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState("medium");
  const [message, setMessage] = useState(
    "Welcome to your workspace."
  );
  const [loading, setLoading] = useState(false);
  const [assigningTask, setAssigningTask] =
    useState<string | null>(null);

  useEffect(() => {
    if (!supabase) {
      setMessage(
        "Supabase configuration missing. Check Vercel environment variables."
      );
      return;
    }

    supabase.auth.getSession().then(({ data, error }) => {
      if (error) setMessage(error.message);
      setUser(data.session?.user ?? null);
    });

    const { data: listener } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setUser(session?.user ?? null);
      }
    );

    return () => listener.subscription.unsubscribe();
  }, []);

  useEffect(() => {
    if (user) {
      loadTasks();
      loadUsers();
    } else {
      setTasks([]);
      setUsers([]);
    }
  }, [user]);

  async function login() {
    if (!supabase) {
      setMessage("Supabase configuration is missing.");
      return;
    }

    setLoading(true);
    setMessage("Connecting to Google...");

    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
        },
      });

      if (error) {
        setMessage(error.message);
        setLoading(false);
      }
    } catch (error: any) {
      setMessage(error.message || "Google login failed.");
      setLoading(false);
    }
  }

  async function logout() {
    if (!supabase) return;

    await supabase.auth.signOut();
    setTasks([]);
    setUsers([]);
    setUser(null);
    setMessage("You have signed out.");
  }

  async function apiRequest(
    path: string,
    options: RequestInit = {}
  ) {
    if (!supabase) throw new Error("Supabase is not configured.");

    const { data } = await supabase.auth.getSession();
    const token = data.session?.access_token;

    if (!token) throw new Error("Please sign in first.");

    const response = await fetch(`${API}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
        ...options.headers,
      },
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error || "Something went wrong.");
    }

    return result;
  }

  async function loadTasks() {
    try {
      const result = await apiRequest("/api/tasks");
      setTasks(result.tasks || []);
    } catch (error: any) {
      setMessage(error.message);
    }
  }

  async function loadUsers() {
    try {
      const result = await apiRequest("/api/tasks/users");
      setUsers(result.users || []);
    } catch (error: any) {
      setMessage("Could not load users: " + error.message);
    }
  }

  async function createTask(e: React.FormEvent) {
    e.preventDefault();

    if (!title.trim()) {
      setMessage("Please enter a task title.");
      return;
    }

    setLoading(true);

    try {
      await apiRequest("/api/tasks", {
        method: "POST",
        body: JSON.stringify({
          title,
          description,
          priority,
        }),
      });

      setTitle("");
      setDescription("");
      setPriority("medium");
      setMessage("Task created successfully!");
      await loadTasks();
    } catch (error: any) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function updateStatus(id: string, status: string) {
    try {
      await apiRequest(`/api/tasks/${id}`, {
        method: "PATCH",
        body: JSON.stringify({ status }),
      });

      setMessage("Task status updated.");
      await loadTasks();
    } catch (error: any) {
      setMessage(error.message);
    }
  }

  async function assignTask(taskId: string) {
    const selectedUserId = selectedUsers[taskId];

    if (!selectedUserId) {
      setMessage("Please select a user first.");
      return;
    }

    setAssigningTask(taskId);

    try {
      await apiRequest(`/api/tasks/${taskId}/assign`, {
        method: "POST",
        body: JSON.stringify({
          user_id: selectedUserId,
        }),
      });

      const assignedUser = users.find(
        (item) => item.id === selectedUserId
      );

      setMessage(
        `Task assigned successfully to ${assignedUser?.email || "user"}!`
      );

      setSelectedUsers((previous) => ({
        ...previous,
        [taskId]: "",
      }));
    } catch (error: any) {
      setMessage("Assignment failed: " + error.message);
    } finally {
      setAssigningTask(null);
    }
  }

  const completed = tasks.filter(
    (task) => task.status === "completed"
  ).length;

  const progress = tasks.filter(
    (task) => task.status === "in_progress"
  ).length;

  const pending = tasks.filter(
    (task) => task.status === "pending"
  ).length;

  return (
    <main className="shell">
      <section className="hero">
        <span className="eyebrow">HAIRDRAMA TASK MANAGER</span>

        <h1>
          Make teamwork
          <br />
          <em>feel effortless.</em>
        </h1>

        <p className="intro">
          Create tasks, manage your work and track your team's progress
          in one simple workspace.
        </p>

        {!user ? (
          <div className="actions">
            <button onClick={login} disabled={loading}>
              {loading ? "Connecting..." : "Continue with Google"}
            </button>
          </div>
        ) : (
          <div className="actions">
            <span>Signed in as {user.email}</span>
            <button className="secondary" onClick={logout}>
              Logout
            </button>
          </div>
        )}

        <p className="status" role="status">
          {message}
        </p>
      </section>

      <section className="preview">
        <div className="preview-top">
          <span>MY WORKSPACE</span>
          <span className="dot">● LIVE</span>
        </div>

        <div className="stats">
          <div>
            <small>PENDING</small>
            <strong>{pending}</strong>
          </div>
          <div>
            <small>IN PROGRESS</small>
            <strong>{progress}</strong>
          </div>
          <div>
            <small>COMPLETED</small>
            <strong>{completed}</strong>
          </div>
        </div>

        {user && (
          <>
            <h2>Create a new task</h2>

            <form onSubmit={createTask} className="task-form">
              <input
                placeholder="Task title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                maxLength={160}
                required
              />

              <textarea
                placeholder="Task description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />

              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
              >
                <option value="low">Low priority</option>
                <option value="medium">Medium priority</option>
                <option value="high">High priority</option>
              </select>

              <button type="submit" disabled={loading}>
                {loading ? "Saving..." : "Create Task"}
              </button>
            </form>

            <h2>Registered team members ({users.length})</h2>

            {users.length === 0 ? (
              <p className="note">
                No other registered users found. Sign in with another
                account to add a team member.
              </p>
            ) : (
              users.map((item) => (
                <p className="team-member" key={item.id}>
                  <b>{item.full_name || "Team member"}</b>
                  <small>{item.email}</small>
                </p>
              ))
            )}

            <h2>Your tasks ({tasks.length})</h2>

            {tasks.length === 0 && (
              <p>No tasks yet. Create your first task!</p>
            )}

            {tasks.map((task) => (
              <div className="task-card" key={task.id}>
                <div className="task">
                  <div>
                    <b>{task.title}</b>
                    <small>
                      {task.description || "No description"} ·{" "}
                      {task.priority} priority
                    </small>
                  </div>

                  <select
                    value={task.status}
                    onChange={(e) =>
                      updateStatus(task.id, e.target.value)
                    }
                  >
                    <option value="pending">Pending</option>
                    <option value="in_progress">In progress</option>
                    <option value="completed">Completed</option>
                  </select>
                </div>

                <div className="assign-row">
                  <select
                    value={selectedUsers[task.id] || ""}
                    onChange={(e) =>
                      setSelectedUsers((previous) => ({
                        ...previous,
                        [task.id]: e.target.value,
                      }))
                    }
                  >
                    <option value="">Select team member</option>

                    {users.map((item) => (
                      <option key={item.id} value={item.id}>
                        {item.full_name || item.email}
                      </option>
                    ))}
                  </select>

                  <button
                    type="button"
                    disabled={
                      !selectedUsers[task.id] ||
                      assigningTask === task.id
                    }
                    onClick={() => assignTask(task.id)}
                  >
                    {assigningTask === task.id
                      ? "Assigning..."
                      : "Assign Task"}
                  </button>
                </div>
              </div>
            ))}
          </>
        )}

        {!user && (
          <p className="note">
            Sign in with Google to create and manage your real tasks.
          </p>
        )}
      </section>
    </main>
  );
}

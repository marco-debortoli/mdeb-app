import type {
  Category,
  Project,
  Task,
  TaskCreate,
  TaskFilters,
  TaskNote,
  TaskSummary,
  TaskUpdate,
} from "@/types/tasks";

const BASE = "/api";

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// ── Categories ────────────────────────────────────────────────────────────────

export const categoryApi = {
  list: () => request<Category[]>(`${BASE}/categories`),

  create: (name: string, color: string) =>
    request<Category>(`${BASE}/categories`, {
      method: "POST",
      body: JSON.stringify({ name, color }),
    }),

  update: (id: number, data: Partial<{ name: string; color: string }>) =>
    request<Category>(`${BASE}/categories/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  delete: (id: number) => request<void>(`${BASE}/categories/${id}`, { method: "DELETE" }),
};

// ── Projects ──────────────────────────────────────────────────────────────────

export const projectApi = {
  list: () => request<Project[]>(`${BASE}/projects`),

  create: (name: string, description?: string) =>
    request<Project>(`${BASE}/projects`, {
      method: "POST",
      body: JSON.stringify({ name, description: description ?? null }),
    }),

  update: (id: number, data: Partial<{ name: string; description: string | null }>) =>
    request<Project>(`${BASE}/projects/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  delete: (id: number) => request<void>(`${BASE}/projects/${id}`, { method: "DELETE" }),
};

// ── Tasks ─────────────────────────────────────────────────────────────────────

export const taskApi = {
  list: (filters: Partial<TaskFilters> = {}) => {
    const params = new URLSearchParams();
    if (filters.status) params.set("status", filters.status);
    if (filters.category_id) params.set("category_id", String(filters.category_id));
    if (filters.project_id) params.set("project_id", String(filters.project_id));
    const qs = params.toString();
    return request<TaskSummary[]>(`${BASE}/tasks${qs ? `?${qs}` : ""}`);
  },

  get: (id: number) => request<Task>(`${BASE}/tasks/${id}`),

  create: (data: TaskCreate) =>
    request<Task>(`${BASE}/tasks`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  update: (id: number, data: TaskUpdate) =>
    request<Task>(`${BASE}/tasks/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  delete: (id: number) => request<void>(`${BASE}/tasks/${id}`, { method: "DELETE" }),

  addNote: (taskId: number, content: string) =>
    request<TaskNote>(`${BASE}/tasks/${taskId}/notes`, {
      method: "POST",
      body: JSON.stringify({ content }),
    }),

  deleteNote: (taskId: number, noteId: number) =>
    request<void>(`${BASE}/tasks/${taskId}/notes/${noteId}`, { method: "DELETE" }),
};

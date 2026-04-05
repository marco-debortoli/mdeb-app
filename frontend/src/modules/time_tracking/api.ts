import type {
  MonthEntriesResponse,
  MonthSummaryResponse,
  TimeCategory,
  TimeCategoryCreate,
  TimeCategoryUpdate,
  TimeEntryCreate,
  TimeEntryResponse,
  TimeEntryUpdate,
  TimeSubcategory,
  TimeSubcategoryCreate,
  TimeSubcategoryUpdate,
} from "@/modules/time_tracking/types";

const BASE = "/api/time";

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

export const timeCategoryApi = {
  list: () => request<TimeCategory[]>(`${BASE}/categories`),

  create: (data: TimeCategoryCreate) =>
    request<TimeCategory>(`${BASE}/categories`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  update: (id: number, data: TimeCategoryUpdate) =>
    request<TimeCategory>(`${BASE}/categories/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  delete: (id: number) => request<void>(`${BASE}/categories/${id}`, { method: "DELETE" }),
};

// ── Subcategories ─────────────────────────────────────────────────────────────

export const timeSubcategoryApi = {
  create: (data: TimeSubcategoryCreate) =>
    request<TimeSubcategory>(`${BASE}/subcategories`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  update: (id: number, data: TimeSubcategoryUpdate) =>
    request<TimeSubcategory>(`${BASE}/subcategories/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  delete: (id: number) => request<void>(`${BASE}/subcategories/${id}`, { method: "DELETE" }),
};

// ── Entries ───────────────────────────────────────────────────────────────────

export const timeEntryApi = {
  list: (month: string) => request<MonthEntriesResponse>(`${BASE}/entries?month=${encodeURIComponent(month)}`),

  create: (data: TimeEntryCreate) =>
    request<TimeEntryResponse>(`${BASE}/entries`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  update: (id: number, data: TimeEntryUpdate) =>
    request<TimeEntryResponse>(`${BASE}/entries/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  delete: (id: number) => request<void>(`${BASE}/entries/${id}`, { method: "DELETE" }),
};

// ── Summary ───────────────────────────────────────────────────────────────────

export const timeSummaryApi = {
  get: (month: string) => request<MonthSummaryResponse>(`${BASE}/summary?month=${encodeURIComponent(month)}`),
};

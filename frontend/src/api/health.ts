import type { HealthLog, HealthLogUpsert, SyncResponse } from "@/types/health";

const BASE = "/api/health";

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, { headers: { "Content-Type": "application/json" }, ...options });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const healthApi = {
  getLog: (date: string) => request<HealthLog>(`${BASE}/logs/${date}`),

  listLogs: (start?: string, end?: string) => {
    const params = new URLSearchParams();
    if (start) params.set("start", start);
    if (end) params.set("end", end);
    const qs = params.toString();
    return request<HealthLog[]>(`${BASE}/logs${qs ? `?${qs}` : ""}`);
  },

  upsertLog: (date: string, body: HealthLogUpsert) =>
    request<HealthLog>(`${BASE}/logs/${date}`, {
      method: "PUT",
      body: JSON.stringify(body),
    }),

  triggerSync: (startDate?: string, endDate?: string) =>
    request<SyncResponse>(`${BASE}/sync`, {
      method: "POST",
      body: JSON.stringify({ start_date: startDate ?? null, end_date: endDate ?? null }),
    }),
};

import type { DayProfile, MonthOverview } from "@/modules/timeline/types";

const BASE = "/api/timeline";

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  return res.json();
}

export const timelineApi = {
  getMonthOverview: (year: number, month: number) =>
    request<MonthOverview>(`${BASE}/month-overview?year=${year}&month=${month}`),

  getDayProfile: (date: string) => request<DayProfile>(`${BASE}/day/${date}`),
};

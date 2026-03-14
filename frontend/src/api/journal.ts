import type { DayRating, JournalEntry } from "@/types/journal";

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

// ── Journal Entries ───────────────────────────────────────────────────────────

export const journalApi = {
  /** Fetch a single entry for a date. Throws on 404 if no entry exists. */
  get: (date: string) => request<JournalEntry>(`${BASE}/journal/${date}`),

  /** Create or update the entry for a date. */
  upsert: (date: string, content: string) =>
    request<JournalEntry>(`${BASE}/journal/${date}`, {
      method: "PUT",
      body: JSON.stringify({ content }),
    }),

  /** Return all ISO date strings that have an existing entry. */
  listDates: () => request<string[]>(`${BASE}/journal/dates`),

  /** Return past entries from the same month/day in previous years. */
  onThisDay: (month: number, day: number, excludeYear: number) =>
    request<JournalEntry[]>(`${BASE}/journal/on-this-day?month=${month}&day=${day}&exclude_year=${excludeYear}`),
};

// ── Day Ratings ───────────────────────────────────────────────────────────────

export const dayRatingApi = {
  /** Fetch rating for a date. Throws on 404 if no rating exists. */
  get: (date: string) => request<DayRating>(`${BASE}/day-ratings/${date}`),

  /** Create or update the rating for a date. */
  upsert: (date: string, rating: number) =>
    request<DayRating>(`${BASE}/day-ratings/${date}`, {
      method: "PUT",
      body: JSON.stringify({ rating }),
    }),
};

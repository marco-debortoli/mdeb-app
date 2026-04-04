export interface JournalEntry {
  id: number;
  date: string; // ISO date string, e.g. "2026-03-08"
  content: string;
  created_at: string;
  updated_at: string;
}

export interface DayRating {
  id: number;
  date: string; // ISO date string, e.g. "2026-03-08"
  rating: number; // 1–5
  created_at: string;
  updated_at: string;
}

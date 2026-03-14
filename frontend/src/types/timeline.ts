import type { JournalEntry, DayRating } from "./journal";
import type { Transaction } from "./finance";
import type { TimeEntry } from "./time_tracking";
import type { TaskSummary } from "./tasks";

export interface DaySignals {
  has_journal: boolean;
  has_transactions: boolean;
  has_completed_tasks: boolean;
  has_time_entries: boolean;
}

export interface MonthOverview {
  year: number;
  month: number;
  days: Record<string, DaySignals>;
}

export interface DayProfile {
  date: string;
  journal: JournalEntry | null;
  rating: DayRating | null;
  transactions: Transaction[];
  completed_tasks: TaskSummary[];
  time_entries: TimeEntry[];
}

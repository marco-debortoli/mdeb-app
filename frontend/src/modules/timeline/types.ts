import type { JournalEntry, DayRating } from "@/modules/journal/types";
import type { Transaction } from "@/modules/finance/types";
import type { TimeEntry } from "@/modules/time_tracking/types";
import type { TaskSummary } from "@/modules/tasks/types";
import type { HealthLog } from "@/modules/health/types";

export interface DaySignals {
  has_journal: boolean;
  has_transactions: boolean;
  has_completed_tasks: boolean;
  has_time_entries: boolean;
  has_health_log: boolean;
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
  health_log: HealthLog | null;
}

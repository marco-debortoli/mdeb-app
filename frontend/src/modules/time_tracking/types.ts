// ── Subcategory ───────────────────────────────────────────────────────────────

export interface TimeSubcategory {
  id: number;
  time_category_id: number;
  name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// ── Category ──────────────────────────────────────────────────────────────────

export interface TimeCategory {
  id: number;
  name: string;
  color: string;
  icon: string | null;
  is_active: boolean;
  subcategories: TimeSubcategory[];
  created_at: string;
  updated_at: string;
}

// ── Entry ─────────────────────────────────────────────────────────────────────

export interface TimeEntry {
  id: number;
  date: string; // YYYY-MM-DD
  start_time: string; // ISO datetime
  end_time: string; // ISO datetime (may be next day for overnight)
  duration_minutes: number;
  time_category_id: number;
  time_subcategory_id: number | null;
  notes: string | null;
  category: TimeCategory;
  subcategory: TimeSubcategory | null;
  created_at: string;
  updated_at: string;
}

export interface TimeEntryResponse extends TimeEntry {
  has_overlap: boolean;
  conflicting_entry_ids: number[];
}

// ── Day/Month aggregates ───────────────────────────────────────────────────────

export interface DayEntries {
  date: string; // YYYY-MM-DD
  entries: TimeEntry[];
  total_minutes: number;
  has_overlap: boolean;
}

export interface MonthEntriesResponse {
  days: DayEntries[];
}

export interface CategorySummary {
  category_id: number;
  category_name: string;
  color: string;
  total_minutes: number;
}

export interface MonthSummaryResponse {
  categories: CategorySummary[];
  grand_total_minutes: number;
}

// ── Create/Update payloads ────────────────────────────────────────────────────

export interface TimeEntryCreate {
  date: string;
  start_time: string; // ISO datetime
  end_time: string; // ISO datetime
  time_category_id: number;
  time_subcategory_id?: number | null;
  notes?: string | null;
}

export interface TimeEntryUpdate {
  date?: string;
  start_time?: string;
  end_time?: string;
  time_category_id?: number;
  time_subcategory_id?: number | null;
  notes?: string | null;
}

export interface TimeCategoryCreate {
  name: string;
  color: string;
  icon?: string | null;
}

export interface TimeCategoryUpdate {
  name?: string;
  color?: string;
  icon?: string | null;
  is_active?: boolean;
}

export interface TimeSubcategoryCreate {
  time_category_id: number;
  name: string;
}

export interface TimeSubcategoryUpdate {
  name?: string;
  is_active?: boolean;
}

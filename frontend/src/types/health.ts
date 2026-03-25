export interface HealthLog {
  date: string;
  steps: number | null;
  sleep_score: number | null;
  sleep_rating: number | null;
  energy_rating: number | null;
  weight_kg: number | null;
  garmin_body_battery_low: number | null;
  garmin_body_battery_high: number | null;
  resting_hr: number | null;
  synced_at: string | null;
  intensity_minutes_moderate: number | null;
  intensity_minutes_vigorous: number | null;
  stress_score: number | null;
}

export interface HealthLogUpsert {
  energy_rating?: number | null;
  weight_kg?: number | null;
  steps?: number | null;
  sleep_score?: number | null;
  garmin_body_battery_low?: number | null;
  garmin_body_battery_high?: number | null;
  resting_hr?: number | null;
  intensity_minutes_moderate?: number | null;
  intensity_minutes_vigorous?: number | null;
  stress_score?: number | null;
}

export interface SyncResponse {
  upserted: number;
  dates: string[];
}

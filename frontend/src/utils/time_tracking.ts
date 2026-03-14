// ── Duration formatting ───────────────────────────────────────────────────────

export function formatDuration(minutes: number): string {
  if (minutes <= 0) return "0m";
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  if (h === 0) return `${m}m`;
  if (m === 0) return `${h}h`;
  return `${h}h ${m}m`;
}

// ── Time formatting ───────────────────────────────────────────────────────────

/** Format an ISO datetime string to 12-hour time (e.g. "9:00am", "11:30pm") */
export function formatTime(isoDatetime: string): string {
  // Parse the time portion directly from the ISO string for display
  const [, timePart] = isoDatetime.split("T");
  if (!timePart) return isoDatetime;
  const [hStr, mStr] = timePart.split(":");
  const h = parseInt(hStr, 10);
  const m = parseInt(mStr, 10);
  const period = h < 12 ? "am" : "pm";
  const h12 = h === 0 ? 12 : h > 12 ? h - 12 : h;
  return `${h12}:${String(m).padStart(2, "0")}${period}`;
}

/** True if end_time is on a later date than start_time */
export function isNextDay(startIso: string, endIso: string): boolean {
  return startIso.split("T")[0] !== endIso.split("T")[0];
}

// ── 15-minute time option generation ─────────────────────────────────────────

export interface TimeOption {
  label: string;
  value: string; // ISO datetime string (naive, no 'Z')
}

function pad2(n: number): string {
  return String(n).padStart(2, "0");
}

function formatHM12(h: number, m: number): string {
  const period = h < 12 ? "am" : "pm";
  const h12 = h === 0 ? 12 : h > 12 ? h - 12 : h;
  return `${h12}:${pad2(m)}${period}`;
}

function addDays(dateStr: string, days: number): string {
  const [y, mo, d] = dateStr.split("-").map(Number);
  const dt = new Date(y, mo - 1, d + days);
  return `${dt.getFullYear()}-${pad2(dt.getMonth() + 1)}-${pad2(dt.getDate())}`;
}

/**
 * Generate 15-minute time options for start-time picker:
 * 96 options covering baseDate 00:00 → 23:45.
 */
export function generateStartOptions(baseDate: string): TimeOption[] {
  const options: TimeOption[] = [];
  for (let h = 0; h < 24; h++) {
    for (const m of [0, 15, 30, 45]) {
      options.push({
        label: formatHM12(h, m),
        value: `${baseDate}T${pad2(h)}:${pad2(m)}:00`,
      });
    }
  }
  return options;
}

/**
 * Generate 15-minute time options for end-time picker:
 * 192 options covering baseDate 00:00 → next day 23:45.
 * Next-day options are labelled with "+1d".
 */
export function generateEndOptions(baseDate: string): TimeOption[] {
  const options: TimeOption[] = [];
  const nextDate = addDays(baseDate, 1);
  for (let dayOffset = 0; dayOffset <= 1; dayOffset++) {
    const d = dayOffset === 0 ? baseDate : nextDate;
    const suffix = dayOffset === 1 ? " +1d" : "";
    for (let h = 0; h < 24; h++) {
      for (const m of [0, 15, 30, 45]) {
        options.push({
          label: formatHM12(h, m) + suffix,
          value: `${d}T${pad2(h)}:${pad2(m)}:00`,
        });
      }
    }
  }
  return options;
}

// ── Month string helpers ──────────────────────────────────────────────────────

export function currentMonthISO(): string {
  const d = new Date();
  return `${d.getFullYear()}-${pad2(d.getMonth() + 1)}`;
}

export function shiftMonth(monthISO: string, delta: number): string {
  const [y, m] = monthISO.split("-").map(Number);
  const dt = new Date(y, m - 1 + delta, 1);
  return `${dt.getFullYear()}-${pad2(dt.getMonth() + 1)}`;
}

const MONTH_NAMES = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];

export function formatMonthLabel(monthISO: string): string {
  const [y, m] = monthISO.split("-").map(Number);
  return `${MONTH_NAMES[m - 1]} ${y}`;
}

const DAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

export function formatDayHeader(dateISO: string): string {
  const [y, m, d] = dateISO.split("-").map(Number);
  const dt = new Date(y, m - 1, d);
  return `${DAY_NAMES[dt.getDay()]}, ${MONTH_NAMES[m - 1]} ${d}`;
}

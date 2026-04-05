import { computed, isRef, type Ref } from "vue";
import { useTimeStore } from "@/modules/time_tracking/store";
import { clippedMinutesForDate } from "@/modules/time_tracking/utils";
import type { DayEntries } from "@/modules/time_tracking/types";

function prevDateISO(iso: string): string {
  const [y, m, d] = iso.split("-").map(Number);
  const dt = new Date(y, m - 1, d - 1);
  return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, "0")}-${String(dt.getDate()).padStart(2, "0")}`;
}

/**
 * Returns a computed DayEntries for the given date, including:
 * - Entries filed under the previous day whose end_time falls on this date (overnight entries)
 * - total_minutes clipped to only the portion within this calendar day
 */
export function useDayEntries(date: Ref<string> | string) {
  const store = useTimeStore();

  return computed((): DayEntries | undefined => {
    const d = isRef(date) ? date.value : date;
    const dayData = store.days.find((day) => day.date === d);
    const prevISO = prevDateISO(d);
    const prevDayData =
      store.days.find((day) => day.date === prevISO) ??
      (store.prevMonthLastDay?.date === prevISO ? store.prevMonthLastDay : undefined);

    const overnight = (prevDayData?.entries ?? []).filter(
      (e) => e.end_time.split("T")[0] === d,
    );

    if (!overnight.length) {
      if (!dayData) return undefined;
      return {
        ...dayData,
        total_minutes: dayData.entries.reduce(
          (sum, e) => sum + clippedMinutesForDate(e, d),
          0,
        ),
      };
    }

    const entries = [...overnight, ...(dayData?.entries ?? [])].sort((a, b) =>
      a.start_time.localeCompare(b.start_time),
    );
    return {
      date: d,
      entries,
      total_minutes: entries.reduce((sum, e) => sum + clippedMinutesForDate(e, d), 0),
      has_overlap: dayData?.has_overlap ?? false,
    };
  });
}

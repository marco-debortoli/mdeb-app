import { ref } from "vue";
import { defineStore } from "pinia";
import { timelineApi } from "@/modules/timeline/api";
import type { DayProfile, MonthOverview } from "@/modules/timeline/types";

export const useTimelineStore = defineStore("timeline", () => {
  // ── State ──────────────────────────────────────────────────────────────────
  const today = new Date();
  const currentYear = ref(today.getFullYear());
  const currentMonth = ref(today.getMonth() + 1); // 1-indexed

  const monthOverview = ref<MonthOverview | null>(null);
  const selectedDate = ref<string | null>(null);
  const dayProfile = ref<DayProfile | null>(null);

  const loadingOverview = ref(false);
  const loadingProfile = ref(false);
  const error = ref<string | null>(null);

  // ── Month navigation ───────────────────────────────────────────────────────

  async function prevMonth() {
    if (currentMonth.value === 1) {
      currentMonth.value = 12;
      currentYear.value -= 1;
    } else {
      currentMonth.value -= 1;
    }
    await fetchMonthOverview();
  }

  async function nextMonth() {
    if (currentMonth.value === 12) {
      currentMonth.value = 1;
      currentYear.value += 1;
    } else {
      currentMonth.value += 1;
    }
    await fetchMonthOverview();
  }

  // ── Fetchers ───────────────────────────────────────────────────────────────

  async function fetchMonthOverview() {
    loadingOverview.value = true;
    error.value = null;
    try {
      monthOverview.value = await timelineApi.getMonthOverview(currentYear.value, currentMonth.value);
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : "Failed to load timeline";
    } finally {
      loadingOverview.value = false;
    }
  }

  async function selectDay(date: string) {
    selectedDate.value = date;
    dayProfile.value = null;
    loadingProfile.value = true;
    error.value = null;
    try {
      dayProfile.value = await timelineApi.getDayProfile(date);
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : "Failed to load day profile";
    } finally {
      loadingProfile.value = false;
    }
  }

  function clearSelectedDay() {
    selectedDate.value = null;
    dayProfile.value = null;
  }

  return {
    currentYear,
    currentMonth,
    monthOverview,
    selectedDate,
    dayProfile,
    loadingOverview,
    loadingProfile,
    error,
    fetchMonthOverview,
    selectDay,
    clearSelectedDay,
    prevMonth,
    nextMonth,
  };
});

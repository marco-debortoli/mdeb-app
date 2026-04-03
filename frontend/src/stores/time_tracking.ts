import { ref } from "vue";
import { defineStore } from "pinia";
import { timeCategoryApi, timeSubcategoryApi, timeEntryApi, timeSummaryApi } from "@/api/time_tracking";
import { currentMonthISO, shiftMonth } from "@/utils/time_tracking";
import type {
  DayEntries,
  TimeCategory,
  TimeCategoryCreate,
  TimeCategoryUpdate,
  TimeEntryCreate,
  TimeEntryResponse,
  TimeEntryUpdate,
  CategorySummary,
  TimeSubcategoryCreate,
  TimeSubcategoryUpdate,
} from "@/types/time_tracking";

export const useTimeStore = defineStore("time", () => {
  // ── State ───────────────────────────────────────────────────────────────────
  const days = ref<DayEntries[]>([]);
  const prevMonthLastDay = ref<DayEntries | null>(null);
  const categories = ref<TimeCategory[]>([]);
  const summary = ref<CategorySummary[]>([]);
  const grandTotalMinutes = ref(0);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const currentMonth = ref(currentMonthISO()); // 'YYYY-MM'

  // ── Fetchers ────────────────────────────────────────────────────────────────

  async function fetchCategories() {
    categories.value = await timeCategoryApi.list();
  }

  async function fetchEntries() {
    const [res, prevRes] = await Promise.all([
      timeEntryApi.list(currentMonth.value),
      timeEntryApi.list(shiftMonth(currentMonth.value, -1)),
    ]);
    days.value = res.days;
    // Cache the last calendar day of the previous month so useDayEntries can
    // detect overnight entries that cross the month boundary (e.g. Mar 31 → Apr 1).
    prevMonthLastDay.value = prevRes.days[prevRes.days.length - 1] ?? null;
  }

  async function fetchSummary() {
    const res = await timeSummaryApi.get(currentMonth.value);
    summary.value = res.categories;
    grandTotalMinutes.value = res.grand_total_minutes;
  }

  async function fetchAll() {
    loading.value = true;
    error.value = null;
    try {
      await Promise.all([fetchCategories(), fetchEntries(), fetchSummary()]);
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : "Failed to load time tracking data";
    } finally {
      loading.value = false;
    }
  }

  // ── Month navigation ────────────────────────────────────────────────────────

  async function prevMonth() {
    currentMonth.value = shiftMonth(currentMonth.value, -1);
    await Promise.all([fetchEntries(), fetchSummary()]);
  }

  async function nextMonth() {
    currentMonth.value = shiftMonth(currentMonth.value, 1);
    await Promise.all([fetchEntries(), fetchSummary()]);
  }

  // ── Entry actions ───────────────────────────────────────────────────────────

  async function createEntry(data: TimeEntryCreate): Promise<TimeEntryResponse> {
    const res = await timeEntryApi.create(data);
    await Promise.all([fetchEntries(), fetchSummary()]);
    return res;
  }

  async function updateEntry(id: number, data: TimeEntryUpdate): Promise<TimeEntryResponse> {
    const res = await timeEntryApi.update(id, data);
    await Promise.all([fetchEntries(), fetchSummary()]);
    return res;
  }

  async function deleteEntry(id: number): Promise<void> {
    await timeEntryApi.delete(id);
    await Promise.all([fetchEntries(), fetchSummary()]);
  }

  // ── Category actions ────────────────────────────────────────────────────────

  async function createCategory(data: TimeCategoryCreate): Promise<TimeCategory> {
    const cat = await timeCategoryApi.create(data);
    await fetchCategories();
    return cat;
  }

  async function updateCategory(id: number, data: TimeCategoryUpdate): Promise<void> {
    await timeCategoryApi.update(id, data);
    await fetchCategories();
  }

  async function deleteCategory(id: number): Promise<void> {
    await timeCategoryApi.delete(id);
    await fetchCategories();
  }

  // ── Subcategory actions ─────────────────────────────────────────────────────

  async function createSubcategory(data: TimeSubcategoryCreate): Promise<void> {
    await timeSubcategoryApi.create(data);
    await fetchCategories();
  }

  async function updateSubcategory(id: number, data: TimeSubcategoryUpdate): Promise<void> {
    await timeSubcategoryApi.update(id, data);
    await fetchCategories();
  }

  async function deleteSubcategory(id: number): Promise<void> {
    await timeSubcategoryApi.delete(id);
    await fetchCategories();
  }

  return {
    days,
    prevMonthLastDay,
    categories,
    summary,
    grandTotalMinutes,
    loading,
    error,
    currentMonth,
    fetchAll,
    prevMonth,
    nextMonth,
    createEntry,
    updateEntry,
    deleteEntry,
    createCategory,
    updateCategory,
    deleteCategory,
    createSubcategory,
    updateSubcategory,
    deleteSubcategory,
  };
});

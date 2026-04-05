import { ref } from "vue";
import { defineStore } from "pinia";
import { dayRatingApi, journalApi } from "@/modules/journal/api";
import type { DayRating, JournalEntry } from "@/modules/journal/types";

export const useJournalStore = defineStore("journal", () => {
  const entry = ref<JournalEntry | null>(null);
  const rating = ref<DayRating | null>(null);
  const datesWithEntries = ref<string[]>([]);
  const onThisDayEntries = ref<JournalEntry[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // ── Fetch ───────────────────────────────────────────────────────────────────

  async function fetchEntry(date: string) {
    try {
      entry.value = await journalApi.get(date);
    } catch (e: unknown) {
      // 404 means no entry yet — that's normal
      if (e instanceof Error && e.message.startsWith("404")) {
        entry.value = null;
      } else {
        throw e;
      }
    }
  }

  async function fetchRating(date: string) {
    try {
      rating.value = await dayRatingApi.get(date);
    } catch (e: unknown) {
      if (e instanceof Error && e.message.startsWith("404")) {
        rating.value = null;
      } else {
        throw e;
      }
    }
  }

  async function fetchDatesWithEntries() {
    datesWithEntries.value = await journalApi.listDates();
  }

  async function fetchOnThisDay(month: number, day: number, excludeYear: number) {
    onThisDayEntries.value = await journalApi.onThisDay(month, day, excludeYear);
  }

  async function fetchAll(date: string) {
    loading.value = true;
    error.value = null;
    const [month, day, year] = [
      parseInt(date.slice(5, 7), 10),
      parseInt(date.slice(8, 10), 10),
      parseInt(date.slice(0, 4), 10),
    ];
    try {
      await Promise.all([
        fetchEntry(date),
        fetchRating(date),
        fetchDatesWithEntries(),
        fetchOnThisDay(month, day, year),
      ]);
    } catch (e) {
      error.value = String(e);
    } finally {
      loading.value = false;
    }
  }

  // ── Save ────────────────────────────────────────────────────────────────────

  async function saveEntry(date: string, content: string): Promise<void> {
    const saved = await journalApi.upsert(date, content);
    entry.value = saved;
    // Refresh the dates list so the mini-calendar dot appears
    if (!datesWithEntries.value.includes(date)) {
      datesWithEntries.value = [...datesWithEntries.value, date].sort();
    }
  }

  async function saveRating(date: string, ratingValue: number): Promise<void> {
    rating.value = await dayRatingApi.upsert(date, ratingValue);
  }

  return {
    entry,
    rating,
    datesWithEntries,
    onThisDayEntries,
    loading,
    error,
    fetchAll,
    fetchEntry,
    fetchRating,
    fetchDatesWithEntries,
    fetchOnThisDay,
    saveEntry,
    saveRating,
  };
});

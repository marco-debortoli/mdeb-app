<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import { useTimeStore } from "@/stores/time_tracking";
import type { TimeEntry, DayEntries } from "@/types/time_tracking";
import { formatMonthLabel, formatDuration, formatDayHeader, clippedMinutesForDate } from "@/utils/time_tracking";
import { timeEntryApi } from "@/api/time_tracking";
import { useDayEntries } from "@/composables/useDayEntries";
import TimeEntryTable from "@/components/time/TimeEntryTable.vue";
import TimeEntryModal from "@/components/time/TimeEntryModal.vue";
import TimeCategoryModal from "@/components/time/TimeCategoryModal.vue";
import MiniDatePicker from "@/components/layout/MiniDatePicker.vue";

const store = useTimeStore();

// ── View mode ─────────────────────────────────────────────────────────────────

const viewMode = ref<"day" | "week" | "month">("day");

// ── Date helpers ──────────────────────────────────────────────────────────────

function todayISO(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function parseDate(iso: string): Date {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(y, m - 1, d);
}

function shiftDate(iso: string, days: number): string {
  const d = parseDate(iso);
  d.setDate(d.getDate() + days);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

// ── Day view state ────────────────────────────────────────────────────────────

const currentDate = ref<string>(todayISO());
const showDatePicker = ref(false);
const isToday = computed(() => currentDate.value === todayISO());

// ── Week view state ───────────────────────────────────────────────────────────

function getWeekMonday(dateISO: string): string {
  const [y, m, d] = dateISO.split("-").map(Number);
  const dt = new Date(y, m - 1, d);
  const dow = dt.getDay(); // 0 = Sun
  dt.setDate(dt.getDate() + (dow === 0 ? -6 : 1 - dow));
  return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, "0")}-${String(dt.getDate()).padStart(2, "0")}`;
}

const currentWeekMonday = ref<string>(getWeekMonday(todayISO()));
const weekExtraDays = ref<DayEntries[]>([]);
const weekLoading = ref(false);

const weekDates = computed((): string[] =>
  Array.from({ length: 7 }, (_, i) => shiftDate(currentWeekMonday.value, i)),
);

const isThisWeek = computed(() => currentWeekMonday.value === getWeekMonday(todayISO()));

function formatWeekLabel(monday: string): string {
  const sunday = shiftDate(monday, 6);
  const [my, mm, md] = monday.split("-").map(Number);
  const [sy, sm, sd] = sunday.split("-").map(Number);
  const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  if (my === sy && mm === sm) return `${MONTHS[mm - 1]} ${md}–${sd}, ${my}`;
  if (my === sy) return `${MONTHS[mm - 1]} ${md} – ${MONTHS[sm - 1]} ${sd}, ${my}`;
  return `${MONTHS[mm - 1]} ${md}, ${my} – ${MONTHS[sm - 1]} ${sd}, ${sy}`;
}

async function loadWeekExtraDays(monday: string) {
  const sunday = shiftDate(monday, 6);
  const monMonth = monday.slice(0, 7);
  const sunMonth = sunday.slice(0, 7);
  if (monMonth !== sunMonth) {
    const res = await timeEntryApi.list(sunMonth);
    weekExtraDays.value = res.days;
  } else {
    weekExtraDays.value = [];
  }
}

async function navigateToWeek(monday: string) {
  currentWeekMonday.value = monday;
  const primaryMonth = monday.slice(0, 7);
  weekLoading.value = true;
  try {
    if (primaryMonth !== store.currentMonth) {
      store.currentMonth = primaryMonth;
      await store.fetchAll();
    }
    await loadWeekExtraDays(monday);
  } finally {
    weekLoading.value = false;
  }
}

function prevWeek() {
  navigateToWeek(shiftDate(currentWeekMonday.value, -7));
}
function nextWeek() {
  navigateToWeek(shiftDate(currentWeekMonday.value, 7));
}

// When switching to week view, sync to the week containing the current day view date
watch(viewMode, async (newMode) => {
  if (newMode === "week") {
    const monday = getWeekMonday(currentDate.value);
    currentWeekMonday.value = monday;
    const primaryMonth = monday.slice(0, 7);
    if (primaryMonth !== store.currentMonth) {
      store.currentMonth = primaryMonth;
      await store.fetchAll();
    }
    await loadWeekExtraDays(monday);
  }
});

function getWeekDayEntries(date: string): DayEntries | undefined {
  const allDays = [...store.days, ...weekExtraDays.value];
  const prevDate = shiftDate(date, -1);
  const dayData = allDays.find((day) => day.date === date);
  const prevDayData = allDays.find((day) => day.date === prevDate);
  const overnight = (prevDayData?.entries ?? []).filter((e) => e.end_time.split("T")[0] === date);
  if (!overnight.length) {
    if (!dayData) return undefined;
    return {
      ...dayData,
      total_minutes: dayData.entries.reduce((sum, e) => sum + clippedMinutesForDate(e, date), 0),
    };
  }
  const entries = [...overnight, ...(dayData?.entries ?? [])].sort((a, b) =>
    a.start_time.localeCompare(b.start_time),
  );
  return {
    date,
    entries,
    total_minutes: entries.reduce((sum, e) => sum + clippedMinutesForDate(e, date), 0),
    has_overlap: dayData?.has_overlap ?? false,
  };
}

const weekDaysData = computed(() =>
  weekDates.value.map((date) => ({ date, data: getWeekDayEntries(date) })),
);

const weeklySummary = computed(() => {
  const map = new Map<number, { category_id: number; category_name: string; color: string; total_minutes: number }>();
  for (const { date, data } of weekDaysData.value) {
    if (!data) continue;
    for (const entry of data.entries) {
      const key = entry.category.id;
      if (!map.has(key)) {
        map.set(key, { category_id: key, category_name: entry.category.name, color: entry.category.color, total_minutes: 0 });
      }
      map.get(key)!.total_minutes += clippedMinutesForDate(entry, date);
    }
  }
  return [...map.values()];
});

const weeklyGrandTotal = computed(() =>
  weekDaysData.value.reduce((sum, { data }) => sum + (data?.total_minutes ?? 0), 0),
);

async function navigateTo(date: string) {
  currentDate.value = date;
  showDatePicker.value = false;
  const newMonth = date.slice(0, 7);
  if (newMonth !== store.currentMonth) {
    store.currentMonth = newMonth;
    await store.fetchAll();
  }
}

function prevDay() {
  navigateTo(shiftDate(currentDate.value, -1));
}
function nextDay() {
  navigateTo(shiftDate(currentDate.value, 1));
}

const currentDayData = useDayEntries(currentDate);

const dailySummary = computed(() => {
  if (!currentDayData.value) return [];
  const map = new Map<number, { category_id: number; category_name: string; color: string; total_minutes: number }>();
  for (const entry of currentDayData.value.entries) {
    const key = entry.category.id;
    if (!map.has(key)) {
      map.set(key, {
        category_id: key,
        category_name: entry.category.name,
        color: entry.category.color,
        total_minutes: 0,
      });
    }
    map.get(key)!.total_minutes += clippedMinutesForDate(entry, currentDate.value);
  }
  return [...map.values()];
});

const dailyGrandTotal = computed(() => currentDayData.value?.total_minutes ?? 0);

const datesWithEntries = computed(() => store.days.filter((d) => d.entries.length > 0).map((d) => d.date));

// ── Entry modal state ─────────────────────────────────────────────────────────

const entryModalOpen = ref(false);
const entryModalMode = ref<"create" | "edit">("create");
const editingEntry = ref<TimeEntry | null>(null);
const entryDefaultDate = ref<string | undefined>(undefined);

function openCreateEntry(date?: string) {
  entryModalMode.value = "create";
  editingEntry.value = null;
  entryDefaultDate.value = date;
  entryModalOpen.value = true;
}

function openEditEntry(entry: TimeEntry) {
  entryModalMode.value = "edit";
  editingEntry.value = entry;
  entryDefaultDate.value = undefined;
  entryModalOpen.value = true;
}

// ── Category modal ────────────────────────────────────────────────────────────

const catModalOpen = ref(false);

// ── Init ──────────────────────────────────────────────────────────────────────

onMounted(() => store.fetchAll());
</script>

<template>
  <div class="max-w-7xl mx-auto" @click.self="showDatePicker = false">
    <!-- Page header -->
    <div class="flex flex-wrap items-center justify-between gap-4 mb-4">
      <!-- Left: navigation -->
      <div class="flex items-center gap-3">
        <!-- Day view: day navigation + date picker -->
        <template v-if="viewMode === 'day'">
          <button
            class="p-1.5 rounded-lg text-slate-500 hover:bg-parchment-200 hover:text-slate-700 transition-colors"
            title="Previous day"
            @click="prevDay"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
            </svg>
          </button>

          <div class="relative">
            <button
              class="px-3 py-1.5 rounded-lg text-lg font-semibold text-slate-800 hover:bg-parchment-200 transition-colors"
              @click.stop="showDatePicker = !showDatePicker"
            >
              {{ formatDayHeader(currentDate) }}
            </button>
            <MiniDatePicker
              :show="showDatePicker"
              :current-date="currentDate"
              :dates-with-entries="datesWithEntries"
              @select="navigateTo"
            />
          </div>

          <button
            :disabled="isToday"
            class="p-1.5 rounded-lg text-slate-500 hover:bg-parchment-200 hover:text-slate-700 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            title="Next day"
            @click="nextDay"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
            </svg>
          </button>
        </template>

        <!-- Week view: week navigation -->
        <template v-else-if="viewMode === 'week'">
          <button
            class="p-1.5 rounded-lg text-slate-500 hover:bg-parchment-200 hover:text-slate-700 transition-colors"
            title="Previous week"
            @click="prevWeek"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
            </svg>
          </button>
          <span class="text-lg font-semibold text-slate-800 min-w-[200px] text-center font-mono tracking-wide">
            {{ formatWeekLabel(currentWeekMonday) }}
          </span>
          <button
            :disabled="isThisWeek"
            class="p-1.5 rounded-lg text-slate-500 hover:bg-parchment-200 hover:text-slate-700 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            title="Next week"
            @click="nextWeek"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
            </svg>
          </button>
        </template>

        <!-- Month view: month navigation -->
        <template v-else>
          <button
            class="p-1.5 rounded-lg text-slate-500 hover:bg-parchment-200 hover:text-slate-700 transition-colors"
            title="Previous month"
            @click="store.prevMonth()"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
            </svg>
          </button>
          <span class="text-lg font-semibold text-slate-800 min-w-[160px] text-center font-mono tracking-wide">
            {{ formatMonthLabel(store.currentMonth) }}
          </span>
          <button
            class="p-1.5 rounded-lg text-slate-500 hover:bg-parchment-200 hover:text-slate-700 transition-colors"
            title="Next month"
            @click="store.nextMonth()"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
            </svg>
          </button>
        </template>
      </div>

      <!-- Right: view toggle + categories -->
      <div class="flex items-center gap-2">
        <div class="flex rounded-lg border border-parchment-300 overflow-hidden text-xs font-medium">
          <button
            :class="
              viewMode === 'day'
                ? 'bg-forest-600 text-white px-3 py-1.5'
                : 'bg-parchment-50 text-slate-500 hover:bg-parchment-100 px-3 py-1.5 transition-colors'
            "
            @click="viewMode = 'day'"
          >
            Day
          </button>
          <button
            :class="
              viewMode === 'week'
                ? 'bg-forest-600 text-white px-3 py-1.5'
                : 'bg-parchment-50 text-slate-500 hover:bg-parchment-100 px-3 py-1.5 transition-colors'
            "
            @click="viewMode = 'week'"
          >
            Week
          </button>
          <button
            :class="
              viewMode === 'month'
                ? 'bg-forest-600 text-white px-3 py-1.5'
                : 'bg-parchment-50 text-slate-500 hover:bg-parchment-100 px-3 py-1.5 transition-colors'
            "
            @click="viewMode = 'month'"
          >
            Month
          </button>
        </div>

        <button
          class="text-xs font-medium text-slate-500 hover:text-slate-700 px-2 py-1 rounded hover:bg-parchment-200 transition-colors"
          @click="catModalOpen = true"
        >
          Categories
        </button>
      </div>
    </div>

    <!-- Loading / error -->
    <div v-if="store.loading" class="text-sm text-slate-400 py-8 text-center">Loading…</div>
    <div v-else-if="store.error" class="text-sm text-red-600 bg-red-50 rounded-xl px-4 py-3 mb-4">
      {{ store.error }}
    </div>

    <template v-else>
      <!-- ── Day View ──────────────────────────────────────────────────────── -->
      <div v-if="viewMode === 'day'" class="grid gap-4 items-start grid-cols-1 md:grid-cols-[1fr_240px]">
        <!-- Single day entry table -->
        <div>
          <TimeEntryTable v-if="currentDayData" :day="currentDayData" @create="openCreateEntry" @edit="openEditEntry" />
          <div v-else class="bg-parchment-50 border border-parchment-300 rounded-xl px-4 py-10 text-center">
            <p class="text-sm text-slate-400 italic mb-3">No entries for this day.</p>
            <button
              class="text-xs font-medium text-forest-600 hover:text-forest-700 transition-colors"
              @click="openCreateEntry(currentDate)"
            >
              + Add Entry
            </button>
          </div>
        </div>

        <!-- Day summary sidebar -->
        <aside class="bg-parchment-50 border border-parchment-300 rounded-xl overflow-hidden">
          <div class="px-4 py-3 border-b border-parchment-200">
            <h3 class="text-xs font-semibold uppercase tracking-widest text-slate-400">Day Summary</h3>
          </div>
          <div v-if="dailySummary.length" class="divide-y divide-parchment-200">
            <div
              v-for="cat in dailySummary"
              :key="cat.category_id"
              class="flex items-center justify-between px-4 py-2.5"
            >
              <div class="flex items-center gap-2 min-w-0">
                <span class="w-2.5 h-2.5 rounded-full shrink-0" :style="{ backgroundColor: cat.color }" />
                <span class="text-sm text-slate-700 truncate">{{ cat.category_name }}</span>
              </div>
              <span class="text-sm font-mono text-slate-600 shrink-0 ml-2">{{
                formatDuration(cat.total_minutes)
              }}</span>
            </div>
            <div class="flex items-center justify-between px-4 py-2.5 bg-parchment-100">
              <span class="text-xs font-semibold uppercase tracking-wider text-slate-500">Total</span>
              <span class="text-sm font-mono font-semibold text-slate-700">{{ formatDuration(dailyGrandTotal) }}</span>
            </div>
          </div>
          <div v-else class="px-4 py-6 text-sm text-slate-400 text-center italic">No entries this day.</div>
        </aside>
      </div>

      <!-- ── Week View ──────────────────────────────────────────────────────── -->
      <div v-else-if="viewMode === 'week'" class="grid gap-4 items-start grid-cols-1 md:grid-cols-[1fr_240px]">
        <!-- Day blocks Mon–Sun -->
        <div class="space-y-3">
          <div v-if="weekLoading" class="text-sm text-slate-400 py-8 text-center">Loading…</div>
          <template v-else>
            <template v-for="{ date, data } in weekDaysData" :key="date">
              <TimeEntryTable v-if="data" :day="data" @create="openCreateEntry" @edit="openEditEntry" />
              <div v-else class="bg-parchment-50 border border-parchment-300 rounded-xl px-4 py-5 flex items-center justify-between">
                <span class="text-sm text-slate-400 italic">{{ formatDayHeader(date) }} — no entries</span>
                <button
                  class="text-xs font-medium text-forest-600 hover:text-forest-700 transition-colors"
                  @click="openCreateEntry(date)"
                >
                  + Add
                </button>
              </div>
            </template>
          </template>
        </div>

        <!-- Weekly category totals -->
        <aside class="bg-parchment-50 border border-parchment-300 rounded-xl overflow-hidden">
          <div class="px-4 py-3 border-b border-parchment-200">
            <h3 class="text-xs font-semibold uppercase tracking-widest text-slate-400">Week Summary</h3>
          </div>
          <div v-if="weeklySummary.length" class="divide-y divide-parchment-200">
            <div
              v-for="cat in weeklySummary"
              :key="cat.category_id"
              class="flex items-center justify-between px-4 py-2.5"
            >
              <div class="flex items-center gap-2 min-w-0">
                <span class="w-2.5 h-2.5 rounded-full shrink-0" :style="{ backgroundColor: cat.color }" />
                <span class="text-sm text-slate-700 truncate">{{ cat.category_name }}</span>
              </div>
              <span class="text-sm font-mono text-slate-600 shrink-0 ml-2">{{ formatDuration(cat.total_minutes) }}</span>
            </div>
            <div class="flex items-center justify-between px-4 py-2.5 bg-parchment-100">
              <span class="text-xs font-semibold uppercase tracking-wider text-slate-500">Total</span>
              <span class="text-sm font-mono font-semibold text-slate-700">{{ formatDuration(weeklyGrandTotal) }}</span>
            </div>
          </div>
          <div v-else class="px-4 py-6 text-sm text-slate-400 text-center italic">No entries this week.</div>
        </aside>
      </div>

      <!-- ── Month View ─────────────────────────────────────────────────────── -->
      <div v-else class="grid gap-4 items-start grid-cols-1 md:grid-cols-[1fr_240px]">
        <!-- Day blocks -->
        <div class="space-y-3">
          <TimeEntryTable
            v-for="day in store.days"
            :key="day.date"
            :day="day"
            @create="openCreateEntry"
            @edit="openEditEntry"
          />
        </div>

        <!-- Monthly category totals -->
        <aside class="bg-parchment-50 border border-parchment-300 rounded-xl overflow-hidden">
          <div class="px-4 py-3 border-b border-parchment-200">
            <h3 class="text-xs font-semibold uppercase tracking-widest text-slate-400">Categories</h3>
          </div>
          <div v-if="store.summary.length" class="divide-y divide-parchment-200">
            <div
              v-for="cat in store.summary"
              :key="cat.category_id"
              class="flex items-center justify-between px-4 py-2.5"
            >
              <div class="flex items-center gap-2 min-w-0">
                <span class="w-2.5 h-2.5 rounded-full shrink-0" :style="{ backgroundColor: cat.color }" />
                <span class="text-sm text-slate-700 truncate">{{ cat.category_name }}</span>
              </div>
              <span class="text-sm font-mono text-slate-600 shrink-0 ml-2">{{
                formatDuration(cat.total_minutes)
              }}</span>
            </div>
            <div class="flex items-center justify-between px-4 py-2.5 bg-parchment-100">
              <span class="text-xs font-semibold uppercase tracking-wider text-slate-500">Total</span>
              <span class="text-sm font-mono font-semibold text-slate-700">{{
                formatDuration(store.grandTotalMinutes)
              }}</span>
            </div>
          </div>
          <div v-else class="px-4 py-6 text-sm text-slate-400 text-center italic">No entries this month.</div>
        </aside>
      </div>
    </template>
  </div>

  <!-- Modals -->
  <TimeEntryModal
    :open="entryModalOpen"
    :mode="entryModalMode"
    :entry="editingEntry"
    :default-date="entryDefaultDate"
    @close="entryModalOpen = false"
  />
  <TimeCategoryModal :open="catModalOpen" @close="catModalOpen = false" />
</template>

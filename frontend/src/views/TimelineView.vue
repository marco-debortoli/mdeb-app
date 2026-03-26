<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useTimelineStore } from "@/stores/timeline";
import DayProfilePanel from "@/components/timeline/DayProfilePanel.vue";
import type { DaySignals } from "@/types/timeline";
import { MONTH_NAMES } from "@/utils/date";

const store = useTimelineStore();

onMounted(() => store.fetchMonthOverview());

// ── Calendar helpers ──────────────────────────────────────────────────────────

const DAY_HEADERS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

const todayISO = (() => {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
})();

function pad2(n: number) {
  return String(n).padStart(2, "0");
}

// Returns an array of 42 cells (6 weeks × 7 days) for the calendar grid.
// Each cell has { dateISO: string, currentMonth: boolean }
const calendarCells = computed(() => {
  const y = store.currentYear;
  const m = store.currentMonth;
  const firstDay = new Date(y, m - 1, 1).getDay(); // 0=Sun
  const daysInMonth = new Date(y, m, 0).getDate();
  const daysInPrevMonth = new Date(y, m - 1, 0).getDate();

  const cells: { dateISO: string; currentMonth: boolean }[] = [];

  // Leading days from previous month
  for (let i = firstDay - 1; i >= 0; i--) {
    const d = daysInPrevMonth - i;
    const prevM = m === 1 ? 12 : m - 1;
    const prevY = m === 1 ? y - 1 : y;
    cells.push({ dateISO: `${prevY}-${pad2(prevM)}-${pad2(d)}`, currentMonth: false });
  }

  // Days in current month
  for (let d = 1; d <= daysInMonth; d++) {
    cells.push({ dateISO: `${y}-${pad2(m)}-${pad2(d)}`, currentMonth: true });
  }

  // Trailing days to fill 6 rows
  const nextM = m === 12 ? 1 : m + 1;
  const nextY = m === 12 ? y + 1 : y;
  let nextD = 1;
  while (cells.length < 42) {
    cells.push({ dateISO: `${nextY}-${pad2(nextM)}-${pad2(nextD++)}`, currentMonth: false });
  }

  return cells;
});

function signalsFor(dateISO: string): DaySignals | null {
  return store.monthOverview?.days[dateISO] ?? null;
}

function hasAnySignal(s: DaySignals | null): boolean {
  if (!s) return false;
  return s.has_journal || s.has_transactions || s.has_completed_tasks || s.has_time_entries || s.has_health_log;
}
</script>

<template>
  <div class="max-w-3xl mx-auto space-y-4">
    <!-- Page header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-bold text-slate-800">Timeline</h1>
        <p class="text-sm text-parchment-500">Monthly overview of your days</p>
      </div>
    </div>

    <!-- Calendar card -->
    <div class="bg-white rounded-xl border border-parchment-200 shadow-sm overflow-hidden">
      <!-- Month navigation -->
      <div class="flex items-center justify-between px-5 py-3 bg-forest-800 text-parchment-100">
        <button
          class="p-1.5 rounded-lg hover:bg-forest-700 transition-colors"
          :disabled="store.loadingOverview"
          aria-label="Previous month"
          @click="store.prevMonth()"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
          </svg>
        </button>

        <div class="text-center">
          <h2 class="text-base font-semibold tracking-wide">
            {{ MONTH_NAMES[store.currentMonth - 1] }} {{ store.currentYear }}
          </h2>
        </div>

        <button
          class="p-1.5 rounded-lg hover:bg-forest-700 transition-colors"
          :disabled="store.loadingOverview"
          aria-label="Next month"
          @click="store.nextMonth()"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
          </svg>
        </button>
      </div>

      <!-- Day-of-week headers -->
      <div class="grid grid-cols-7 border-b border-parchment-200">
        <div
          v-for="day in DAY_HEADERS"
          :key="day"
          class="py-2 text-center text-xs font-semibold text-parchment-500 uppercase tracking-wider"
        >
          {{ day }}
        </div>
      </div>

      <!-- Calendar grid -->
      <div class="grid grid-cols-7" :class="{ 'opacity-50 pointer-events-none': store.loadingOverview }">
        <button
          v-for="cell in calendarCells"
          :key="cell.dateISO"
          :disabled="!cell.currentMonth"
          :class="[
            'relative flex flex-col items-center pt-2 pb-1.5 min-h-[4rem] border-b border-r border-parchment-100 transition-colors',
            cell.currentMonth ? 'hover:bg-parchment-50 cursor-pointer' : 'cursor-default',
            cell.dateISO === todayISO ? 'bg-forest-50' : '',
          ]"
          @click="cell.currentMonth && store.selectDay(cell.dateISO)"
        >
          <!-- Day number -->
          <span
            :class="[
              'flex items-center justify-center w-7 h-7 rounded-full text-sm font-medium mb-1 transition-colors',
              cell.dateISO === todayISO
                ? 'bg-forest-700 text-parchment-50'
                : cell.currentMonth
                  ? 'text-slate-800'
                  : 'text-parchment-300',
            ]"
          >
            {{ cell.dateISO.split("-")[2].replace(/^0/, "") }}
          </span>

          <!-- Signal dots -->
          <div
            v-if="cell.currentMonth && hasAnySignal(signalsFor(cell.dateISO))"
            class="flex gap-0.5 flex-wrap justify-center max-w-[2.5rem]"
          >
            <span
              v-if="signalsFor(cell.dateISO)?.has_journal"
              class="w-1.5 h-1.5 rounded-full bg-forest-500"
              title="Journal entry"
            />
            <span
              v-if="signalsFor(cell.dateISO)?.has_transactions"
              class="w-1.5 h-1.5 rounded-full bg-earth-500"
              title="Transactions"
            />
            <span
              v-if="signalsFor(cell.dateISO)?.has_completed_tasks"
              class="w-1.5 h-1.5 rounded-full bg-slate-500"
              title="Completed tasks"
            />
            <span
              v-if="signalsFor(cell.dateISO)?.has_time_entries"
              class="w-1.5 h-1.5 rounded-full bg-blue-500"
              title="Time entries"
            />
            <span
              v-if="signalsFor(cell.dateISO)?.has_health_log"
              class="w-1.5 h-1.5 rounded-full bg-green-500"
              title="Health data"
            />
          </div>
        </button>
      </div>
    </div>

    <!-- Legend -->
    <div class="flex flex-wrap gap-x-5 gap-y-2 px-1">
      <div class="flex items-center gap-1.5 text-xs text-parchment-600">
        <span class="w-2.5 h-2.5 rounded-full bg-forest-500 shrink-0"></span>
        Journal
      </div>
      <div class="flex items-center gap-1.5 text-xs text-parchment-600">
        <span class="w-2.5 h-2.5 rounded-full bg-earth-500 shrink-0"></span>
        Finance
      </div>
      <div class="flex items-center gap-1.5 text-xs text-parchment-600">
        <span class="w-2.5 h-2.5 rounded-full bg-slate-500 shrink-0"></span>
        Tasks
      </div>
      <div class="flex items-center gap-1.5 text-xs text-parchment-600">
        <span class="w-2.5 h-2.5 rounded-full bg-blue-500 shrink-0"></span>
        Time
      </div>
      <div class="flex items-center gap-1.5 text-xs text-parchment-600">
        <span class="w-2.5 h-2.5 rounded-full bg-green-500 shrink-0"></span>
        Health
      </div>
    </div>

    <!-- Error state -->
    <div v-if="store.error" class="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
      {{ store.error }}
    </div>

    <!-- Day profile panel -->
    <Teleport to="body">
      <DayProfilePanel
        v-if="store.selectedDate"
        :date="store.selectedDate"
        :profile="store.dayProfile"
        :loading="store.loadingProfile"
        @close="store.clearSelectedDay()"
      />
    </Teleport>
  </div>
</template>

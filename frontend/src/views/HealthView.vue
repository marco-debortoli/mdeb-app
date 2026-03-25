<script setup lang="ts">
import { computed, ref } from "vue";
import HealthDaily from "@/components/health/HealthDaily.vue";
import HealthOverview from "@/components/health/HealthOverview.vue";
import MiniDatePicker from "@/components/layout/MiniDatePicker.vue";
import { MONTH_NAMES } from "@/utils/date";

// ── View state ─────────────────────────────────────────────────────────────────

const activeView = ref<"daily" | "overview">("daily");
const dailyRef = ref<InstanceType<typeof HealthDaily> | null>(null);

async function switchView(view: "daily" | "overview") {
  if (view === "overview" && dailyRef.value) await dailyRef.value.flush();
  activeView.value = view;
}

// ── Date helpers ───────────────────────────────────────────────────────────────

function toISODate(d: Date): string {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function todayISO(): string {
  return toISODate(new Date());
}

function parseDate(iso: string): Date {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(y, m - 1, d);
}

function shiftDate(iso: string, days: number): string {
  const d = parseDate(iso);
  d.setDate(d.getDate() + days);
  return toISODate(d);
}

function formatDateHeader(iso: string): string {
  const d = parseDate(iso);
  const dayName = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][d.getDay()];
  return `${dayName}, ${d.getDate()} ${MONTH_NAMES[d.getMonth()]} ${d.getFullYear()}`;
}

// ── Daily navigation ───────────────────────────────────────────────────────────

const currentDate = ref<string>(todayISO());
const showDatePicker = ref(false);
const isToday = computed(() => currentDate.value === todayISO());

async function navigateTo(date: string) {
  if (dailyRef.value) await dailyRef.value.flush();
  currentDate.value = date;
  showDatePicker.value = false;
}

function prevDay() { navigateTo(shiftDate(currentDate.value, -1)); }
function nextDay() { navigateTo(shiftDate(currentDate.value, 1)); }

// ── Overview range ─────────────────────────────────────────────────────────────

const RANGES = [
  { label: "30d", days: 30 },
  { label: "90d", days: 90 },
  { label: "6m", days: 180 },
  { label: "1y", days: 365 },
] as const;

type RangeLabel = (typeof RANGES)[number]["label"];

const selectedRange = ref<RangeLabel>("30d");
</script>

<template>
  <div class="max-w-3xl mx-auto" @click.self="showDatePicker = false">
    <!-- ── Unified header ──────────────────────────────────────────────────── -->
    <div class="flex items-center gap-2 mb-6">

      <!-- Daily: prev / date picker / next -->
      <template v-if="activeView === 'daily'">
        <div class="flex items-center gap-1">
          <button
            class="p-1.5 rounded-lg text-slate-400 hover:bg-parchment-200 hover:text-slate-700 transition-colors"
            title="Previous day"
            @click="prevDay"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
          </button>

          <div class="relative">
            <button
              class="px-3 py-1.5 rounded-lg text-xl font-semibold text-slate-800 hover:bg-parchment-200 transition-colors leading-tight"
              @click.stop="showDatePicker = !showDatePicker"
            >
              {{ formatDateHeader(currentDate) }}
            </button>
            <MiniDatePicker
              :show="showDatePicker"
              :current-date="currentDate"
              :dates-with-entries="[]"
              @select="navigateTo"
            />
          </div>

          <button
            :disabled="isToday"
            class="p-1.5 rounded-lg text-slate-400 hover:bg-parchment-200 hover:text-slate-700 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            title="Next day"
            @click="nextDay"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </template>

      <!-- Overview: back arrow + title -->
      <template v-else>
        <button
          class="p-1.5 rounded-lg text-slate-400 hover:bg-parchment-200 hover:text-slate-700 transition-colors"
          title="Back to daily view"
          @click="switchView('daily')"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <h1 class="text-xl font-semibold text-slate-800">Overview</h1>
      </template>

      <!-- Spacer -->
      <div class="flex-1" />

      <!-- Daily: overview button + sync -->
      <template v-if="activeView === 'daily'">
        <button
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium border border-parchment-300 bg-parchment-50 text-slate-600 hover:bg-parchment-100 transition-colors"
          @click="switchView('overview')"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
          </svg>
          Overview
        </button>

        <button
          disabled
          title="Garmin sync is currently unavailable"
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium border border-parchment-200 bg-parchment-50 text-parchment-400 cursor-not-allowed opacity-50"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
          </svg>
          Sync
        </button>
      </template>

      <!-- Overview: range buttons -->
      <template v-else>
        <div class="flex gap-1">
          <button
            v-for="r in RANGES"
            :key="r.label"
            class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
            :class="
              selectedRange === r.label
                ? 'bg-forest-700 text-parchment-50'
                : 'bg-parchment-100 text-slate-600 hover:bg-parchment-200'
            "
            @click="selectedRange = r.label"
          >
            {{ r.label }}
          </button>
        </div>
      </template>
    </div>

    <HealthDaily v-if="activeView === 'daily'" ref="dailyRef" :current-date="currentDate" />
    <HealthOverview v-else :selected-range="selectedRange" />
  </div>
</template>

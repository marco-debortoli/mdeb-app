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
    <!-- ── Header ──────────────────────────────────────────────────────────── -->
    <div class="flex items-center gap-2 mb-6">

      <!-- Left: date nav (daily) or range selector (overview) -->
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

      <!-- Spacer -->
      <div class="flex-1" />

      <!-- Right: always-visible Daily / Overview tabs -->
      <div class="flex rounded-lg border border-parchment-300 overflow-hidden">
        <button
          class="px-3 py-1.5 text-sm font-medium transition-colors"
          :class="
            activeView === 'daily'
              ? 'bg-forest-700 text-parchment-50'
              : 'bg-parchment-50 text-slate-600 hover:bg-parchment-100'
          "
          @click="switchView('daily')"
        >
          Daily
        </button>
        <button
          class="px-3 py-1.5 text-sm font-medium border-l border-parchment-300 transition-colors"
          :class="
            activeView === 'overview'
              ? 'bg-forest-700 text-parchment-50'
              : 'bg-parchment-50 text-slate-600 hover:bg-parchment-100'
          "
          @click="switchView('overview')"
        >
          Overview
        </button>
      </div>
    </div>

    <HealthDaily v-if="activeView === 'daily'" ref="dailyRef" :current-date="currentDate" />
    <HealthOverview v-else :selected-range="selectedRange" />
  </div>
</template>

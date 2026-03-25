<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import {
  Chart,
  CategoryScale,
  LinearScale,
  BarElement,
  BarController,
  LineElement,
  LineController,
  PointElement,
  Title,
  Tooltip,
  Legend,
  type ChartData,
  type ChartOptions,
} from "chart.js";
import { useHealthStore } from "@/stores/health";
import type { HealthLog } from "@/types/health";

Chart.register(
  CategoryScale,
  LinearScale,
  BarElement,
  BarController,
  LineElement,
  LineController,
  PointElement,
  Title,
  Tooltip,
  Legend,
);

// ── Date helpers ───────────────────────────────────────────────────────────────

function toISODate(d: Date): string {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function todayISO(): string {
  return toISODate(new Date());
}

function addDays(iso: string, days: number): string {
  const [y, m, d] = iso.split("-").map(Number);
  const dt = new Date(y, m - 1, d);
  dt.setDate(dt.getDate() + days);
  return toISODate(dt);
}

function formatDateLabel(iso: string): string {
  const [, m, d] = iso.split("-").map(Number);
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  return `${months[m - 1]} ${d}`;
}

// ── Range config ───────────────────────────────────────────────────────────────

const RANGES = [
  { label: "30d", days: 30 },
  { label: "90d", days: 90 },
  { label: "6m", days: 180 },
  { label: "1y", days: 365 },
] as const;

type RangeLabel = (typeof RANGES)[number]["label"];

const selectedRange = ref<RangeLabel>("30d");

function getRangeDays(label: RangeLabel): number {
  return RANGES.find((r) => r.label === label)!.days;
}

function getDateRange(label: RangeLabel): { start: string; end: string } {
  const end = todayISO();
  const start = addDays(end, -(getRangeDays(label) - 1));
  return { start, end };
}

// Build ordered list of all dates in range
function buildDateList(start: string, end: string): string[] {
  const dates: string[] = [];
  let cur = start;
  while (cur <= end) {
    dates.push(cur);
    cur = addDays(cur, 1);
  }
  return dates;
}

// ── Store & data ───────────────────────────────────────────────────────────────

const store = useHealthStore();

async function loadRange(label: RangeLabel) {
  const { start, end } = getDateRange(label);
  await store.fetchLogs(start, end);
}

// ── Summary stats ──────────────────────────────────────────────────────────────

function avg(values: (number | null)[]): number | null {
  const valid = values.filter((v) => v != null) as number[];
  if (!valid.length) return null;
  return Math.round(valid.reduce((a, b) => a + b, 0) / valid.length);
}

const summaryStats = computed(() => {
  const logs = store.logs;
  return {
    avgSteps: avg(logs.map((l) => l.steps)),
    avgSleep: avg(logs.map((l) => l.sleep_score)),
    avgEnergy: avg(logs.map((l) => l.energy_rating)),
    avgStress: avg(logs.map((l) => l.stress_score)),
  };
});

// ── Chart data builders ────────────────────────────────────────────────────────

const SLEEP_COLORS: Record<number, string> = {
  1: "rgba(239, 68, 68, 0.75)",
  2: "rgba(249, 115, 22, 0.75)",
  3: "rgba(234, 179, 8, 0.75)",
  4: "rgba(132, 204, 16, 0.75)",
  5: "rgba(34, 197, 94, 0.75)",
};

function buildChartArrays() {
  const { start, end } = getDateRange(selectedRange.value);
  const allDates = buildDateList(start, end);
  const byDate = new Map<string, HealthLog>(store.logs.map((l) => [l.date, l]));

  const labels = allDates.map(formatDateLabel);
  const weightData: (number | null)[] = allDates.map((d) => byDate.get(d)?.weight_kg ?? null);
  const sleepData: (number | null)[] = allDates.map((d) => byDate.get(d)?.sleep_score ?? null);
  const sleepColors: string[] = allDates.map((d) => {
    const rating = byDate.get(d)?.sleep_rating;
    return rating != null ? SLEEP_COLORS[rating] : "transparent";
  });
  const stepsData: (number | null)[] = allDates.map((d) => byDate.get(d)?.steps ?? null);

  return { labels, weightData, sleepData, sleepColors, stepsData };
}

function computeWeightYAxis(weightData: (number | null)[]): { min: number; max: number } | undefined {
  const vals = weightData.filter((v) => v != null) as number[];
  if (vals.length < 2) return undefined;
  const min = Math.min(...vals);
  const max = Math.max(...vals);
  const pad = Math.max((max - min) * 0.15, 1);
  return { min: Math.floor(min - pad), max: Math.ceil(max + pad) };
}

// ── Chart instances ────────────────────────────────────────────────────────────

const weightCanvas = ref<HTMLCanvasElement | null>(null);
const sleepCanvas = ref<HTMLCanvasElement | null>(null);
const stepsCanvas = ref<HTMLCanvasElement | null>(null);

let weightChart: Chart | null = null;
let sleepChart: Chart | null = null;
let stepsChart: Chart | null = null;

const commonXOptions = {
  grid: { display: false },
  ticks: {
    maxTicksLimit: 10,
    maxRotation: 0,
    color: "#6b7280",
    font: { size: 11 },
  },
};

const commonYOptions = {
  grid: { color: "rgba(0,0,0,0.06)" },
  ticks: { color: "#6b7280", font: { size: 11 } },
};

function destroyCharts() {
  weightChart?.destroy();
  sleepChart?.destroy();
  stepsChart?.destroy();
  weightChart = sleepChart = stepsChart = null;
}

function initCharts() {
  destroyCharts();
  const { labels, weightData, sleepData, sleepColors, stepsData } = buildChartArrays();
  const yBounds = computeWeightYAxis(weightData);

  if (weightCanvas.value) {
    weightChart = new Chart(weightCanvas.value, {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: "Weight (kg)",
            data: weightData,
            borderColor: "rgba(180, 83, 9, 0.85)",
            backgroundColor: "rgba(180, 83, 9, 0.15)",
            pointBackgroundColor: "rgba(180, 83, 9, 0.9)",
            pointRadius: 4,
            pointHoverRadius: 6,
            borderWidth: 2,
            spanGaps: false,
            tension: 0,
          },
        ],
      } as ChartData<"line">,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: commonXOptions,
          y: {
            ...commonYOptions,
            ...(yBounds ?? {}),
          },
        },
      } as ChartOptions<"line">,
    });
  }

  if (sleepCanvas.value) {
    sleepChart = new Chart(sleepCanvas.value, {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            label: "Sleep Score",
            data: sleepData,
            backgroundColor: sleepColors,
            borderRadius: 3,
            borderSkipped: false,
          },
        ],
      } as ChartData<"bar">,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: commonXOptions,
          y: { ...commonYOptions, min: 0, max: 100 },
        },
      } as ChartOptions<"bar">,
    });
  }

  if (stepsCanvas.value) {
    stepsChart = new Chart(stepsCanvas.value, {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            type: "bar" as const,
            label: "Steps",
            data: stepsData,
            backgroundColor: "rgba(79, 119, 79, 0.7)",
            borderRadius: 3,
            borderSkipped: false,
          },
          {
            type: "line" as const,
            label: "10,000 steps",
            data: labels.map(() => 10000),
            borderColor: "rgba(100, 116, 139, 0.4)",
            borderWidth: 1.5,
            borderDash: [4, 4],
            pointRadius: 0,
            fill: false,
            tension: 0,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
        },
        scales: {
          x: commonXOptions,
          y: { ...commonYOptions, min: 0 },
        },
      },
    });
  }
}

// ── Range change ───────────────────────────────────────────────────────────────

async function changeRange(label: RangeLabel) {
  selectedRange.value = label;
  await loadRange(label);
}

watch(
  () => store.logs,
  async () => {
    await nextTick();
    initCharts();
  },
);

onMounted(async () => {
  await loadRange(selectedRange.value);
});

onBeforeUnmount(() => {
  destroyCharts();
});
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <!-- ── Header ──────────────────────────────────────────────────────────── -->
    <div class="flex items-center gap-3 mb-6">
      <RouterLink
        to="/health"
        class="p-1.5 rounded-lg text-slate-400 hover:bg-parchment-200 hover:text-slate-700 transition-colors"
        title="Back to daily view"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
      </RouterLink>

      <h1 class="text-xl font-semibold text-slate-800 flex-1">Health Overview</h1>

      <!-- Range buttons -->
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
          @click="changeRange(r.label)"
        >
          {{ r.label }}
        </button>
      </div>
    </div>

    <!-- Loading / error -->
    <div v-if="store.loading" class="text-sm text-slate-400 py-16 text-center">Loading…</div>
    <div v-else-if="store.error" class="text-sm text-red-600 bg-red-50 rounded-xl px-4 py-3 mb-4">
      {{ store.error }}
    </div>

    <template v-else>
      <!-- ── Summary strip ───────────────────────────────────────────────── -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
        <div class="bg-parchment-50 border border-parchment-300 rounded-xl px-4 py-3 text-center">
          <p class="text-xs text-slate-500 mb-1">Avg Steps</p>
          <p class="text-lg font-semibold" :class="summaryStats.avgSteps != null ? 'text-slate-800' : 'text-parchment-300'">
            {{ summaryStats.avgSteps != null ? summaryStats.avgSteps.toLocaleString() : "—" }}
          </p>
        </div>
        <div class="bg-parchment-50 border border-parchment-300 rounded-xl px-4 py-3 text-center">
          <p class="text-xs text-slate-500 mb-1">Avg Sleep</p>
          <p class="text-lg font-semibold" :class="summaryStats.avgSleep != null ? 'text-slate-800' : 'text-parchment-300'">
            {{ summaryStats.avgSleep != null ? summaryStats.avgSleep : "—" }}
          </p>
        </div>
        <div class="bg-parchment-50 border border-parchment-300 rounded-xl px-4 py-3 text-center">
          <p class="text-xs text-slate-500 mb-1">Avg Energy</p>
          <p class="text-lg font-semibold" :class="summaryStats.avgEnergy != null ? 'text-slate-800' : 'text-parchment-300'">
            {{ summaryStats.avgEnergy != null ? summaryStats.avgEnergy : "—" }}
          </p>
        </div>
        <div class="bg-parchment-50 border border-parchment-300 rounded-xl px-4 py-3 text-center">
          <p class="text-xs text-slate-500 mb-1">Avg Stress</p>
          <p class="text-lg font-semibold" :class="summaryStats.avgStress != null ? 'text-slate-800' : 'text-parchment-300'">
            {{ summaryStats.avgStress != null ? summaryStats.avgStress : "—" }}
          </p>
        </div>
      </div>

      <!-- ── Charts ──────────────────────────────────────────────────────── -->

      <!-- Weight -->
      <div class="bg-parchment-50 border border-parchment-300 rounded-xl px-5 py-4 mb-4">
        <h3 class="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-4">Weight (kg)</h3>
        <div class="h-48">
          <canvas ref="weightCanvas" />
        </div>
      </div>

      <!-- Sleep -->
      <div class="bg-parchment-50 border border-parchment-300 rounded-xl px-5 py-4 mb-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xs font-semibold uppercase tracking-widest text-slate-400">Sleep Score</h3>
          <div class="flex items-center gap-3 text-xs text-slate-400">
            <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-2.5 rounded-sm" style="background: rgba(239,68,68,0.75)" /> Poor</span>
            <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-2.5 rounded-sm" style="background: rgba(249,115,22,0.75)" /> Fair</span>
            <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-2.5 rounded-sm" style="background: rgba(234,179,8,0.75)" /> Good</span>
            <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-2.5 rounded-sm" style="background: rgba(132,204,16,0.75)" /> V.Good</span>
            <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-2.5 rounded-sm" style="background: rgba(34,197,94,0.75)" /> Exc.</span>
          </div>
        </div>
        <div class="h-48">
          <canvas ref="sleepCanvas" />
        </div>
      </div>

      <!-- Steps -->
      <div class="bg-parchment-50 border border-parchment-300 rounded-xl px-5 py-4">
        <h3 class="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-4">Steps</h3>
        <div class="h-48">
          <canvas ref="stepsCanvas" />
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { useHealthStore } from "@/stores/health";
import { healthApi } from "@/api/health";

const KG_PER_LB = 0.45359237;

function kgToLbs(kg: number): number {
  return Math.round((kg / KG_PER_LB) * 10) / 10;
}

function lbsToKg(lbs: number): number {
  return Math.round(lbs * KG_PER_LB * 100) / 100;
}

const props = defineProps<{ currentDate: string }>();

// ── Store & state ──────────────────────────────────────────────────────────────

const store = useHealthStore();

const localSteps = ref<string>("");
const localSleepScore = ref<string>("");
const localRestingHr = ref<string>("");
const localBatteryLow = ref<string>("");
const localBatteryHigh = ref<string>("");
const localStressScore = ref<string>("");
const localIntensityMod = ref<string>("");
const localIntensityVig = ref<string>("");
const localEnergyRating = ref<number>(0);
const localWeightLbs = ref<string>("");
const lastWeightLbs = ref<number | null>(null);

const localSleepRating = computed(() => {
  const n = parseInt(localSleepScore.value);
  if (isNaN(n)) return null;
  if (n <= 39) return 1;
  if (n <= 59) return 2;
  if (n <= 74) return 3;
  if (n <= 84) return 4;
  return 5;
});

const saveStatus = ref<"idle" | "saving" | "saved" | "error">("idle");
let saveTimer: ReturnType<typeof setTimeout> | null = null;
let idleTimer: ReturnType<typeof setTimeout> | null = null;

const uploadStatus = ref<"idle" | "uploading" | "success" | "error">("idle");
const uploadError = ref<string>("");

async function handleFitUpload(event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) return;
  input.value = "";

  uploadStatus.value = "uploading";
  uploadError.value = "";
  try {
    const updated = await healthApi.uploadFit(props.currentDate, file);
    store.log = updated;
    syncLocalFromStore();
    uploadStatus.value = "success";
    setTimeout(() => (uploadStatus.value = "idle"), 3000);
  } catch (e: any) {
    uploadStatus.value = "error";
    uploadError.value = e.message ?? "Upload failed";
  }
}

const hoverRating = ref(0);

// ── Data loading ───────────────────────────────────────────────────────────────

function numToStr(v: number | null | undefined): string {
  return v != null ? String(v) : "";
}

function syncLocalFromStore() {
  const l = store.log;
  localSteps.value = numToStr(l?.steps);
  localSleepScore.value = numToStr(l?.sleep_score);
  localRestingHr.value = numToStr(l?.resting_hr);
  localBatteryLow.value = numToStr(l?.garmin_body_battery_low);
  localBatteryHigh.value = numToStr(l?.garmin_body_battery_high);
  localStressScore.value = numToStr(l?.stress_score);
  localIntensityMod.value = numToStr(l?.intensity_minutes_moderate);
  localIntensityVig.value = numToStr(l?.intensity_minutes_vigorous);
  localEnergyRating.value = l?.energy_rating ?? 0;
  localWeightLbs.value = l?.weight_kg != null ? String(kgToLbs(l.weight_kg)) : "";
}

async function loadDate(date: string) {
  await store.fetchLog(date);
  syncLocalFromStore();
  lastWeightLbs.value = await fetchLastWeight(date);
}

async function fetchLastWeight(date: string): Promise<number | null> {
  const d = new Date(date + "T00:00:00");
  d.setDate(d.getDate() - 1);
  const end = d.toISOString().slice(0, 10);
  d.setDate(d.getDate() - 89);
  const start = d.toISOString().slice(0, 10);
  try {
    const logs = await healthApi.listLogs(start, end);
    for (let i = logs.length - 1; i >= 0; i--) {
      if (logs[i].weight_kg != null) return kgToLbs(logs[i].weight_kg!);
    }
  } catch { /* ignore */ }
  return null;
}

watch(() => props.currentDate, loadDate, { immediate: true });

// ── Save helpers ───────────────────────────────────────────────────────────────

function parseIntField(val: string): number | null {
  const n = parseInt(val);
  return isNaN(n) ? null : n;
}

function parseFloatField(val: string): number | null {
  const n = parseFloat(val);
  return isNaN(n) ? null : n;
}

function currentPayload() {
  return {
    steps: parseIntField(localSteps.value),
    sleep_score: parseIntField(localSleepScore.value),
    resting_hr: parseIntField(localRestingHr.value),
    garmin_body_battery_low: parseIntField(localBatteryLow.value),
    garmin_body_battery_high: parseIntField(localBatteryHigh.value),
    stress_score: parseIntField(localStressScore.value),
    intensity_minutes_moderate: parseIntField(localIntensityMod.value),
    intensity_minutes_vigorous: parseIntField(localIntensityVig.value),
    energy_rating: localEnergyRating.value > 0 ? localEnergyRating.value : null,
    weight_kg: (() => { const lbs = parseFloatField(localWeightLbs.value); return lbs != null ? lbsToKg(lbs) : null; })(),
  };
}

// ── Auto-save ──────────────────────────────────────────────────────────────────

function scheduleSave() {
  if (saveTimer) clearTimeout(saveTimer);
  if (idleTimer) clearTimeout(idleTimer);
  saveStatus.value = "saving";
  saveTimer = setTimeout(async () => {
    try {
      await store.saveManual(props.currentDate, currentPayload());
      saveStatus.value = "saved";
      idleTimer = setTimeout(() => (saveStatus.value = "idle"), 2500);
    } catch {
      saveStatus.value = "error";
    }
  }, 800);
}

function setEnergyRating(value: number) {
  localEnergyRating.value = value;
  scheduleSave();
}

// ── Flush pending save (called by parent before navigating) ────────────────────

async function flush() {
  if (saveTimer) {
    clearTimeout(saveTimer);
    saveTimer = null;
    try {
      await store.saveManual(props.currentDate, currentPayload());
    } catch {
      /* ignore on navigate */
    }
  }
}

defineExpose({ flush });

// ── Lifecycle ──────────────────────────────────────────────────────────────────

onBeforeUnmount(() => {
  if (saveTimer) clearTimeout(saveTimer);
  if (idleTimer) clearTimeout(idleTimer);
});
</script>

<template>
  <!-- Loading / error -->
  <div v-if="store.loading" class="text-sm text-slate-400 py-16 text-center">Loading…</div>
  <div v-else-if="store.error" class="text-sm text-red-600 bg-red-50 rounded-xl px-4 py-3 mb-4">
    {{ store.error }}
  </div>

  <template v-else>
    <!-- ── Save status / upload row ────────────────────────────────────────── -->
    <div class="flex items-center justify-between mb-3 min-h-6">
      <!-- Left: FIT upload -->
      <label
        class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium cursor-pointer transition-colors border"
        :class="uploadStatus === 'uploading'
          ? 'bg-parchment-200 border-parchment-300 text-slate-400 cursor-not-allowed pointer-events-none'
          : uploadStatus === 'error'
            ? 'bg-red-50 border-red-200 text-red-500'
            : uploadStatus === 'success'
              ? 'bg-forest-50 border-forest-200 text-forest-700'
              : 'bg-parchment-100 border-parchment-300 text-slate-600 hover:bg-parchment-200'"
      >
        <svg class="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
        </svg>
        <span v-if="uploadStatus === 'uploading'">Uploading…</span>
        <span v-else-if="uploadStatus === 'success'">Imported</span>
        <span v-else-if="uploadStatus === 'error'">{{ uploadError }}</span>
        <span v-else>Import FIT ZIP</span>
        <input
          type="file"
          accept=".zip"
          class="sr-only"
          :disabled="uploadStatus === 'uploading'"
          @change="handleFitUpload"
        />
      </label>

      <!-- Right: auto-save status -->
      <span
        class="text-xs transition-opacity"
        :class="{
          'text-slate-400 opacity-100': saveStatus === 'saving',
          'text-forest-600 opacity-100': saveStatus === 'saved',
          'text-red-500 opacity-100': saveStatus === 'error',
          'opacity-0': saveStatus === 'idle',
        }"
      >
        <template v-if="saveStatus === 'saving'">Saving…</template>
        <template v-else-if="saveStatus === 'saved'">Saved</template>
        <template v-else-if="saveStatus === 'error'">Save failed</template>
      </span>
    </div>

    <!-- ── Unified metrics grid ───────────────────────────────────────────── -->
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">

      <!-- Steps -->
      <div class="bg-parchment-50 border border-parchment-300 rounded-xl px-4 py-3">
        <div class="flex items-center gap-2 mb-2">
          <svg class="w-4 h-4 text-slate-400 shrink-0" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 5.25a3 3 0 013 3m3 0a6 6 0 01-7.029 5.912c-.563-.097-1.159.026-1.563.43L10.5 17.25H8.25v2.25H6v2.25H2.25v-2.818c0-.597.237-1.17.659-1.591l6.499-6.499c.404-.404.527-1 .43-1.563A6 6 0 1121.75 8.25z" />
          </svg>
          <span class="text-xs text-slate-500">Steps</span>
        </div>
        <input
          v-model="localSteps"
          type="number"
          min="0"
          placeholder="—"
          class="w-full px-2 py-1 rounded-lg border border-parchment-300 bg-white text-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-forest-400 focus:border-transparent"
          @input="scheduleSave"
        />
      </div>

      <!-- Sleep Score -->
      <div class="bg-parchment-50 border border-parchment-300 rounded-xl px-4 py-3">
        <div class="flex items-center gap-2 mb-2">
          <svg class="w-4 h-4 text-slate-400 shrink-0" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z" />
          </svg>
          <span class="text-xs text-slate-500">Sleep Score</span>
        </div>
        <input
          v-model="localSleepScore"
          type="number"
          min="0"
          max="100"
          placeholder="—"
          class="w-full px-2 py-1 rounded-lg border border-parchment-300 bg-white text-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-forest-400 focus:border-transparent"
          @input="scheduleSave"
        />
        <div v-if="localSleepRating != null" class="flex gap-0.5 mt-1.5">
          <span
            v-for="star in 5"
            :key="star"
            class="text-xs leading-none"
            :class="star <= localSleepRating ? 'text-earth-400' : 'text-parchment-300'"
          >★</span>
        </div>
      </div>

      <!-- Resting HR -->
      <div class="bg-parchment-50 border border-parchment-300 rounded-xl px-4 py-3">
        <div class="flex items-center gap-2 mb-2">
          <svg class="w-4 h-4 text-slate-400 shrink-0" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
          </svg>
          <span class="text-xs text-slate-500">Resting HR</span>
        </div>
        <div class="flex items-center gap-1.5">
          <input
            v-model="localRestingHr"
            type="number"
            min="0"
            placeholder="—"
            class="w-full px-2 py-1 rounded-lg border border-parchment-300 bg-white text-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-forest-400 focus:border-transparent"
            @input="scheduleSave"
          />
          <span class="text-xs text-slate-400 shrink-0">bpm</span>
        </div>
      </div>

      <!-- Body Battery -->
      <div class="bg-parchment-50 border border-parchment-300 rounded-xl px-4 py-3">
        <div class="flex items-center gap-2 mb-2">
          <svg class="w-4 h-4 text-slate-400 shrink-0" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 10.5h.375c.621 0 1.125.504 1.125 1.125v2.25c0 .621-.504 1.125-1.125 1.125H21M3.75 18h15A2.25 2.25 0 0021 15.75v-6a2.25 2.25 0 00-2.25-2.25h-15A2.25 2.25 0 001.5 9.75v6A2.25 2.25 0 003.75 18z" />
          </svg>
          <span class="text-xs text-slate-500">Body Battery</span>
        </div>
        <div class="flex items-center gap-1">
          <input
            v-model="localBatteryLow"
            type="number"
            min="0"
            max="100"
            placeholder="—"
            class="w-full px-2 py-1 rounded-lg border border-parchment-300 bg-white text-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-forest-400 focus:border-transparent"
            @input="scheduleSave"
          />
          <span class="text-xs text-slate-400 shrink-0">→</span>
          <input
            v-model="localBatteryHigh"
            type="number"
            min="0"
            max="100"
            placeholder="—"
            class="w-full px-2 py-1 rounded-lg border border-parchment-300 bg-white text-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-forest-400 focus:border-transparent"
            @input="scheduleSave"
          />
        </div>
      </div>

      <!-- Stress -->
      <div class="bg-parchment-50 border border-parchment-300 rounded-xl px-4 py-3">
        <div class="flex items-center gap-2 mb-2">
          <svg class="w-4 h-4 text-slate-400 shrink-0" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
          </svg>
          <span class="text-xs text-slate-500">Stress</span>
        </div>
        <input
          v-model="localStressScore"
          type="number"
          min="0"
          max="100"
          placeholder="—"
          class="w-full px-2 py-1 rounded-lg border border-parchment-300 bg-white text-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-forest-400 focus:border-transparent"
          @input="scheduleSave"
        />
      </div>

      <!-- Intensity Minutes -->
      <div class="bg-parchment-50 border border-parchment-300 rounded-xl px-4 py-3">
        <div class="flex items-center gap-2 mb-2">
          <svg class="w-4 h-4 text-slate-400 shrink-0" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5M9 11.25v1.5M12 9v3.75m3-6v6" />
          </svg>
          <span class="text-xs text-slate-500">Intensity Min</span>
        </div>
        <div class="flex items-center gap-1">
          <input
            v-model="localIntensityMod"
            type="number"
            min="0"
            placeholder="—"
            class="w-full px-2 py-1 rounded-lg border border-parchment-300 bg-white text-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-forest-400 focus:border-transparent"
            @input="scheduleSave"
          />
          <span class="text-xs text-slate-400 shrink-0">/</span>
          <input
            v-model="localIntensityVig"
            type="number"
            min="0"
            placeholder="—"
            class="w-full px-2 py-1 rounded-lg border border-parchment-300 bg-white text-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-forest-400 focus:border-transparent"
            @input="scheduleSave"
          />
        </div>
        <p class="text-xs text-slate-400 mt-1">mod / vig</p>
      </div>

      <!-- Energy Rating -->
      <div class="bg-parchment-50 border border-parchment-300 rounded-xl px-4 py-3">
        <div class="flex items-center gap-2 mb-2">
          <svg class="w-4 h-4 text-slate-400 shrink-0" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" />
          </svg>
          <span class="text-xs text-slate-500">Energy</span>
        </div>
        <div class="flex items-center gap-0.5 mt-1" @mouseleave="hoverRating = 0">
          <button
            v-for="star in 5"
            :key="star"
            class="text-xl leading-none transition-colors p-0.5"
            :class="star <= (hoverRating || localEnergyRating) ? 'text-earth-400' : 'text-parchment-300'"
            :title="`Energy: ${star} star${star !== 1 ? 's' : ''}`"
            @mouseenter="hoverRating = star"
            @click="setEnergyRating(star)"
          >
            ★
          </button>
        </div>
      </div>

      <!-- Weight -->
      <div class="bg-parchment-50 border border-parchment-300 rounded-xl px-4 py-3">
        <div class="flex items-center gap-2 mb-2">
          <svg class="w-4 h-4 text-slate-400 shrink-0" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v17.25m0 0c-1.472 0-2.882.265-4.185.75M12 20.25c1.472 0 2.882.265 4.185.75M18.75 4.97A48.416 48.416 0 0012 4.5c-2.291 0-4.545.16-6.75.47m13.5 0c1.01.143 2.01.317 3 .52m-3-.52l2.62 10.726c.122.499-.106 1.028-.589 1.202a5.988 5.988 0 01-2.031.352 5.988 5.988 0 01-2.031-.352c-.483-.174-.711-.703-.59-1.202L18.75 4.97zm-16.5.52c.99-.203 1.99-.377 3-.52m0 0l2.62 10.726c.122.499-.106 1.028-.589 1.202a5.989 5.989 0 01-2.031.352 5.989 5.989 0 01-2.031-.352c-.483-.174-.711-.703-.59-1.202L5.25 4.97z" />
          </svg>
          <span class="text-xs text-slate-500">Weight</span>
        </div>
        <div class="flex items-center gap-1.5">
          <input
            v-model="localWeightLbs"
            type="number"
            step="0.1"
            min="0"
            placeholder="—"
            class="w-full px-2 py-1 rounded-lg border border-parchment-300 bg-white text-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-forest-400 focus:border-transparent"
            @input="scheduleSave"
          />
          <span class="text-xs text-slate-400 shrink-0">lbs</span>
        </div>
        <button
          v-if="lastWeightLbs !== null"
          class="mt-1.5 text-xs text-slate-400 hover:text-slate-600 transition-colors text-left"
          @click="localWeightLbs = String(lastWeightLbs); scheduleSave()"
        >
          Use last: {{ lastWeightLbs }} lbs
        </button>
      </div>

    </div>
  </template>
</template>

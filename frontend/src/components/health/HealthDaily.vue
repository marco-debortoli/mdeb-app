<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { useHealthStore } from "@/stores/health";

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
const localWeightKg = ref<string>("");

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
  localWeightKg.value = numToStr(l?.weight_kg);
}

async function loadDate(date: string) {
  await store.fetchLog(date);
  syncLocalFromStore();
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
    weight_kg: parseFloatField(localWeightKg.value),
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

// ── Synced-at formatting ───────────────────────────────────────────────────────

function formatSyncedAt(dt: string | null): string {
  if (!dt) return "Not yet synced";
  const d = new Date(dt);
  return `Last synced: ${d.toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })} at ${d.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" })}`;
}

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
    <!-- ── Save status ──────────────────────────────────────────────────────── -->
    <div class="flex justify-end mb-3 h-4">
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

    <!-- ── Health Metrics ────────────────────────────────────────────────────── -->
    <section class="mb-6">
      <h2 class="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-3">Health Metrics</h2>

      <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
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
      </div>

      <!-- Synced at -->
      <p class="mt-3 text-xs text-slate-400">
        {{ formatSyncedAt(store.log?.synced_at ?? null) }}
      </p>
    </section>

    <!-- ── Manual Entries ──────────────────────────────────────────────────── -->
    <section>
      <h2 class="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-3">Manual Entries</h2>

      <div class="bg-parchment-50 border border-parchment-300 rounded-xl px-5 py-4 space-y-5">
        <!-- Energy rating -->
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-2">Energy Rating</label>
          <div class="flex items-center gap-0.5" @mouseleave="hoverRating = 0">
            <button
              v-for="star in 5"
              :key="star"
              class="text-2xl leading-none transition-colors p-0.5"
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
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-2">Weight</label>
          <div class="flex items-center gap-2">
            <input
              v-model="localWeightKg"
              type="number"
              step="0.1"
              min="0"
              placeholder="—"
              class="w-28 px-3 py-1.5 rounded-lg border border-parchment-300 bg-white text-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-forest-400 focus:border-transparent"
              @input="scheduleSave"
            />
            <span class="text-sm text-slate-500">kg</span>
          </div>
        </div>
      </div>
    </section>
  </template>
</template>

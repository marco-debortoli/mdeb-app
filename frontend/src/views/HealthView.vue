<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import MiniDatePicker from "@/components/layout/MiniDatePicker.vue";
import { useHealthStore } from "@/stores/health";

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

const MONTH_NAMES = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

function formatDateHeader(iso: string): string {
  const d = parseDate(iso);
  const dayName = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][d.getDay()];
  return `${dayName}, ${d.getDate()} ${MONTH_NAMES[d.getMonth()]} ${d.getFullYear()}`;
}

function formatSyncedAt(dt: string | null): string {
  if (!dt) return "Not yet synced";
  const d = new Date(dt);
  return `Last synced: ${d.toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })} at ${d.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" })}`;
}

// ── Store & state ──────────────────────────────────────────────────────────────

const store = useHealthStore();

const currentDate = ref<string>(todayISO());
const showDatePicker = ref(false);

// Local state for manual fields (separate from store so we can debounce)
const localEnergyRating = ref<number>(0);
const localWeightKg = ref<string>("");

// Save status
const saveStatus = ref<"idle" | "saving" | "saved" | "error">("idle");
let saveTimer: ReturnType<typeof setTimeout> | null = null;
let idleTimer: ReturnType<typeof setTimeout> | null = null;

// Sync status
const syncStatus = ref<"idle" | "syncing" | "done" | "error">("idle");
const syncMessage = ref("");
let syncMsgTimer: ReturnType<typeof setTimeout> | null = null;

// Star hover
const hoverRating = ref(0);

// ── Data loading ───────────────────────────────────────────────────────────────

function syncLocalFromStore() {
  localEnergyRating.value = store.log?.energy_rating ?? 0;
  localWeightKg.value = store.log?.weight_kg != null ? String(store.log.weight_kg) : "";
}

async function loadDate(date: string) {
  await store.fetchLog(date);
  syncLocalFromStore();
}

// ── Auto-save ──────────────────────────────────────────────────────────────────

function scheduleSave() {
  if (saveTimer) clearTimeout(saveTimer);
  if (idleTimer) clearTimeout(idleTimer);
  saveStatus.value = "saving";
  saveTimer = setTimeout(async () => {
    try {
      const weight = localWeightKg.value.trim() ? parseFloat(localWeightKg.value) : null;
      const energy = localEnergyRating.value > 0 ? localEnergyRating.value : null;
      await store.saveManual(currentDate.value, energy, weight);
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

// ── Date navigation ────────────────────────────────────────────────────────────

async function navigateTo(date: string) {
  if (saveTimer) {
    clearTimeout(saveTimer);
    saveTimer = null;
    const weight = localWeightKg.value.trim() ? parseFloat(localWeightKg.value) : null;
    const energy = localEnergyRating.value > 0 ? localEnergyRating.value : null;
    try {
      await store.saveManual(currentDate.value, energy, weight);
    } catch {
      /* ignore on navigate */
    }
  }
  currentDate.value = date;
  showDatePicker.value = false;
  await loadDate(date);
}

function prevDay() {
  navigateTo(shiftDate(currentDate.value, -1));
}
function nextDay() {
  navigateTo(shiftDate(currentDate.value, 1));
}
const isToday = computed(() => currentDate.value === todayISO());

// ── Garmin sync ────────────────────────────────────────────────────────────────

async function triggerSync() {
  if (syncStatus.value === "syncing") return;
  syncStatus.value = "syncing";
  syncMessage.value = "";
  if (syncMsgTimer) clearTimeout(syncMsgTimer);
  try {
    const result = await store.sync(currentDate.value, currentDate.value);
    syncStatus.value = "done";
    syncMessage.value = `Synced ${result.upserted} record${result.upserted !== 1 ? "s" : ""}`;
    await loadDate(currentDate.value);
    syncMsgTimer = setTimeout(() => {
      syncStatus.value = "idle";
      syncMessage.value = "";
    }, 3000);
  } catch {
    syncStatus.value = "error";
    syncMessage.value = "Sync failed";
    syncMsgTimer = setTimeout(() => {
      syncStatus.value = "idle";
      syncMessage.value = "";
    }, 4000);
  }
}

// ── Lifecycle ──────────────────────────────────────────────────────────────────

onMounted(() => loadDate(currentDate.value));
onBeforeUnmount(() => {
  if (saveTimer) clearTimeout(saveTimer);
  if (idleTimer) clearTimeout(idleTimer);
  if (syncMsgTimer) clearTimeout(syncMsgTimer);
});
</script>

<template>
  <div class="max-w-3xl mx-auto" @click.self="showDatePicker = false">
    <!-- ── Header ──────────────────────────────────────────────────────────── -->
    <div class="flex items-center gap-2 mb-6">
      <!-- Prev/next + date -->
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

      <!-- Spacer -->
      <div class="flex-1" />

      <!-- Overview link -->
      <RouterLink
        to="/health/overview"
        class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium border border-parchment-300 bg-parchment-50 text-slate-600 hover:bg-parchment-100 transition-colors"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
        </svg>
        Overview
      </RouterLink>

      <!-- Sync button -->
      <button
        :disabled="syncStatus === 'syncing'"
        class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium border transition-colors"
        :class="
          syncStatus === 'done'
            ? 'border-forest-300 bg-forest-50 text-forest-700'
            : syncStatus === 'error'
              ? 'border-red-200 bg-red-50 text-red-600'
              : 'border-parchment-300 bg-parchment-50 text-slate-600 hover:bg-parchment-100'
        "
        @click="triggerSync"
      >
        <svg
          class="w-4 h-4"
          :class="{ 'animate-spin': syncStatus === 'syncing' }"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99"
          />
        </svg>
        <span>{{ syncStatus === "syncing" ? "Syncing…" : "Sync" }}</span>
      </button>
    </div>

    <!-- Sync status message -->
    <div
      v-if="syncMessage"
      class="mb-4 px-4 py-2 rounded-lg text-sm"
      :class="syncStatus === 'error' ? 'bg-red-50 text-red-600' : 'bg-forest-50 text-forest-700'"
    >
      {{ syncMessage }}
    </div>

    <!-- Loading / error -->
    <div v-if="store.loading" class="text-sm text-slate-400 py-16 text-center">Loading…</div>
    <div v-else-if="store.error" class="text-sm text-red-600 bg-red-50 rounded-xl px-4 py-3 mb-4">
      {{ store.error }}
    </div>

    <template v-else>
      <!-- ── Garmin Data ──────────────────────────────────────────────────── -->
      <section class="mb-6">
        <h2 class="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-3">Garmin Data</h2>

        <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
          <!-- Steps -->
          <div class="bg-parchment-50 border border-parchment-300 rounded-xl px-4 py-3">
            <div class="flex items-center gap-2 mb-1">
              <svg class="w-4 h-4 text-slate-400 shrink-0" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 5.25a3 3 0 013 3m3 0a6 6 0 01-7.029 5.912c-.563-.097-1.159.026-1.563.43L10.5 17.25H8.25v2.25H6v2.25H2.25v-2.818c0-.597.237-1.17.659-1.591l6.499-6.499c.404-.404.527-1 .43-1.563A6 6 0 1121.75 8.25z" />
              </svg>
              <span class="text-xs text-slate-500">Steps</span>
            </div>
            <p class="text-lg font-semibold" :class="store.log?.steps != null ? 'text-slate-800' : 'text-parchment-300'">
              {{ store.log?.steps != null ? store.log.steps.toLocaleString() : "—" }}
            </p>
          </div>

          <!-- Sleep -->
          <div class="bg-parchment-50 border border-parchment-300 rounded-xl px-4 py-3">
            <div class="flex items-center gap-2 mb-1">
              <svg class="w-4 h-4 text-slate-400 shrink-0" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z" />
              </svg>
              <span class="text-xs text-slate-500">Sleep</span>
            </div>
            <p class="text-lg font-semibold" :class="store.log?.sleep_score != null ? 'text-slate-800' : 'text-parchment-300'">
              {{ store.log?.sleep_score != null ? store.log.sleep_score : "—" }}
            </p>
            <div v-if="store.log?.sleep_rating != null" class="flex gap-0.5 mt-1">
              <span
                v-for="star in 5"
                :key="star"
                class="text-sm leading-none"
                :class="star <= store.log.sleep_rating ? 'text-earth-400' : 'text-parchment-300'"
              >★</span>
            </div>
          </div>

          <!-- Resting HR -->
          <div class="bg-parchment-50 border border-parchment-300 rounded-xl px-4 py-3">
            <div class="flex items-center gap-2 mb-1">
              <svg class="w-4 h-4 text-slate-400 shrink-0" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
              </svg>
              <span class="text-xs text-slate-500">Resting HR</span>
            </div>
            <p class="text-lg font-semibold" :class="store.log?.resting_hr != null ? 'text-slate-800' : 'text-parchment-300'">
              {{ store.log?.resting_hr != null ? `${store.log.resting_hr} bpm` : "—" }}
            </p>
          </div>

          <!-- Body Battery -->
          <div class="bg-parchment-50 border border-parchment-300 rounded-xl px-4 py-3">
            <div class="flex items-center gap-2 mb-1">
              <svg class="w-4 h-4 text-slate-400 shrink-0" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M21 10.5h.375c.621 0 1.125.504 1.125 1.125v2.25c0 .621-.504 1.125-1.125 1.125H21M3.75 18h15A2.25 2.25 0 0021 15.75v-6a2.25 2.25 0 00-2.25-2.25h-15A2.25 2.25 0 001.5 9.75v6A2.25 2.25 0 003.75 18z" />
              </svg>
              <span class="text-xs text-slate-500">Body Battery</span>
            </div>
            <p
              class="text-lg font-semibold"
              :class="store.log?.garmin_body_battery_low != null ? 'text-slate-800' : 'text-parchment-300'"
            >
              <template v-if="store.log?.garmin_body_battery_low != null">
                {{ store.log.garmin_body_battery_low }} → {{ store.log.garmin_body_battery_high }}
              </template>
              <template v-else>—</template>
            </p>
          </div>

          <!-- Stress -->
          <div class="bg-parchment-50 border border-parchment-300 rounded-xl px-4 py-3">
            <div class="flex items-center gap-2 mb-1">
              <svg class="w-4 h-4 text-slate-400 shrink-0" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
              </svg>
              <span class="text-xs text-slate-500">Stress</span>
            </div>
            <p class="text-lg font-semibold" :class="store.log?.stress_score != null ? 'text-slate-800' : 'text-parchment-300'">
              {{ store.log?.stress_score != null ? store.log.stress_score : "—" }}
            </p>
          </div>

          <!-- Intensity Minutes -->
          <div class="bg-parchment-50 border border-parchment-300 rounded-xl px-4 py-3">
            <div class="flex items-center gap-2 mb-1">
              <svg class="w-4 h-4 text-slate-400 shrink-0" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5M9 11.25v1.5M12 9v3.75m3-6v6" />
              </svg>
              <span class="text-xs text-slate-500">Intensity Min</span>
            </div>
            <p
              class="text-lg font-semibold"
              :class="store.log?.intensity_minutes_moderate != null ? 'text-slate-800' : 'text-parchment-300'"
            >
              <template v-if="store.log?.intensity_minutes_moderate != null">
                {{ store.log.intensity_minutes_moderate }} mod / {{ store.log.intensity_minutes_vigorous }} vig
              </template>
              <template v-else>—</template>
            </p>
          </div>
        </div>

        <!-- Synced at -->
        <p class="mt-3 text-xs text-slate-400">
          {{ formatSyncedAt(store.log?.synced_at ?? null) }}
        </p>
      </section>

      <!-- ── Manual Entries ──────────────────────────────────────────────── -->
      <section>
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-xs font-semibold uppercase tracking-widest text-slate-400">Manual Entries</h2>
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
  </div>
</template>

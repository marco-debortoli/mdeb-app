<script setup lang="ts">
import { onMounted } from "vue";
import { useHealthStore } from "@/stores/health";

const d = new Date();
const today = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;

const KG_PER_LB = 0.45359237;

function kgToLbs(kg: number): number {
  return Math.round((kg / KG_PER_LB) * 10) / 10;
}

const store = useHealthStore();

onMounted(() => store.fetchLog(today));
</script>

<template>
  <section class="bg-parchment-50 border border-parchment-300 rounded-xl overflow-hidden shadow-sm flex flex-col h-full">
    <!-- Header -->
    <div class="flex items-center justify-between px-4 py-3 border-b border-parchment-200 shrink-0">
      <div class="flex items-center gap-2">
        <div class="w-7 h-7 rounded-md bg-green-700 flex items-center justify-center shrink-0">
          <svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.5" class="w-4 h-4">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
          </svg>
        </div>
        <h2 class="font-semibold text-slate-800 text-sm">Health Today</h2>
      </div>
      <RouterLink to="/health" class="text-xs text-forest-600 hover:text-forest-700 transition-colors">View all →</RouterLink>
    </div>

    <!-- Content -->
    <div v-if="store.loading" class="flex-1 flex items-center justify-center text-sm text-slate-400">Loading…</div>
    <div v-else-if="!store.log" class="flex-1 flex items-center justify-center px-4 py-6">
      <p class="text-sm text-slate-400 italic">No health data for today.</p>
    </div>
    <div v-else class="flex-1 grid grid-cols-2 sm:grid-cols-3 gap-px bg-parchment-200">
      <!-- Steps -->
      <div v-if="store.log.steps != null" class="bg-parchment-50 px-4 py-3">
        <p class="text-xs text-parchment-500 mb-0.5">Steps</p>
        <p class="text-sm font-semibold text-slate-800">{{ store.log.steps.toLocaleString() }}</p>
      </div>
      <!-- Sleep -->
      <div v-if="store.log.sleep_score != null" class="bg-parchment-50 px-4 py-3">
        <p class="text-xs text-parchment-500 mb-0.5">Sleep Score</p>
        <div class="flex items-center gap-1.5">
          <p class="text-sm font-semibold text-slate-800">{{ store.log.sleep_score }}</p>
          <div v-if="store.log.sleep_rating" class="flex gap-0.5">
            <span
              v-for="n in 5"
              :key="n"
              class="text-xs leading-none"
              :class="n <= store.log.sleep_rating ? 'text-earth-400' : 'text-parchment-300'"
            >★</span>
          </div>
        </div>
      </div>
      <!-- Resting HR -->
      <div v-if="store.log.resting_hr != null" class="bg-parchment-50 px-4 py-3">
        <p class="text-xs text-parchment-500 mb-0.5">Resting HR</p>
        <p class="text-sm font-semibold text-slate-800">
          {{ store.log.resting_hr }} <span class="text-xs font-normal text-parchment-400">bpm</span>
        </p>
      </div>
      <!-- Body Battery -->
      <div
        v-if="store.log.garmin_body_battery_low != null || store.log.garmin_body_battery_high != null"
        class="bg-parchment-50 px-4 py-3"
      >
        <p class="text-xs text-parchment-500 mb-0.5">Body Battery</p>
        <p class="text-sm font-semibold text-slate-800">
          {{ store.log.garmin_body_battery_low ?? '—' }} → {{ store.log.garmin_body_battery_high ?? '—' }}
        </p>
      </div>
      <!-- Stress -->
      <div v-if="store.log.stress_score != null" class="bg-parchment-50 px-4 py-3">
        <p class="text-xs text-parchment-500 mb-0.5">Stress</p>
        <p class="text-sm font-semibold text-slate-800">{{ store.log.stress_score }}</p>
      </div>
      <!-- Energy -->
      <div v-if="store.log.energy_rating != null" class="bg-parchment-50 px-4 py-3">
        <p class="text-xs text-parchment-500 mb-0.5">Energy</p>
        <div class="flex gap-0.5 mt-0.5">
          <span
            v-for="n in 5"
            :key="n"
            class="text-sm leading-none"
            :class="n <= store.log.energy_rating! ? 'text-earth-400' : 'text-parchment-300'"
          >★</span>
        </div>
      </div>
      <!-- Weight -->
      <div v-if="store.log.weight_kg != null" class="bg-parchment-50 px-4 py-3">
        <p class="text-xs text-parchment-500 mb-0.5">Weight</p>
        <p class="text-sm font-semibold text-slate-800">
          {{ kgToLbs(store.log.weight_kg!) }} <span class="text-xs font-normal text-parchment-400">lbs</span>
        </p>
      </div>
      <!-- Intensity Minutes -->
      <div
        v-if="store.log.intensity_minutes_moderate != null || store.log.intensity_minutes_vigorous != null"
        class="bg-parchment-50 px-4 py-3"
      >
        <p class="text-xs text-parchment-500 mb-0.5">Intensity Min</p>
        <p class="text-sm font-semibold text-slate-800">
          {{ store.log.intensity_minutes_moderate ?? '—' }} / {{ store.log.intensity_minutes_vigorous ?? '—' }}
          <span class="text-xs font-normal text-parchment-400">mod/vig</span>
        </p>
      </div>
    </div>
  </section>
</template>

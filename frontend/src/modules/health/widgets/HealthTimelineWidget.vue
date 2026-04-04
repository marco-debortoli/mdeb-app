<script setup lang="ts">
import type { HealthLog } from "@/modules/health/types";

defineProps<{
  healthLog: HealthLog | null;
}>();
</script>

<template>
  <section class="bg-white rounded-lg border border-parchment-200 overflow-hidden">
    <div class="flex items-center gap-2 px-4 py-2.5 bg-green-50 border-b border-parchment-200">
      <span class="w-2.5 h-2.5 rounded-full bg-green-500 shrink-0"></span>
      <h3 class="text-sm font-semibold text-green-800 uppercase tracking-wider">Health</h3>
    </div>
    <div v-if="healthLog" class="grid grid-cols-2 sm:grid-cols-3 gap-px bg-parchment-100">
      <!-- Steps -->
      <div v-if="healthLog.steps != null" class="bg-white px-4 py-2.5">
        <p class="text-xs text-parchment-500">Steps</p>
        <p class="text-sm font-medium text-slate-800">{{ healthLog.steps.toLocaleString() }}</p>
      </div>
      <!-- Sleep -->
      <div v-if="healthLog.sleep_score != null" class="bg-white px-4 py-2.5">
        <p class="text-xs text-parchment-500">Sleep Score</p>
        <div class="flex items-center gap-1.5">
          <p class="text-sm font-medium text-slate-800">{{ healthLog.sleep_score }}</p>
          <div v-if="healthLog.sleep_rating" class="flex gap-0.5">
            <span
              v-for="n in 5"
              :key="n"
              class="text-xs leading-none"
              :class="n <= healthLog.sleep_rating! ? 'text-earth-400' : 'text-parchment-300'"
            >★</span>
          </div>
        </div>
      </div>
      <!-- Resting HR -->
      <div v-if="healthLog.resting_hr != null" class="bg-white px-4 py-2.5">
        <p class="text-xs text-parchment-500">Resting HR</p>
        <p class="text-sm font-medium text-slate-800">
          {{ healthLog.resting_hr }} <span class="text-xs font-normal text-parchment-400">bpm</span>
        </p>
      </div>
      <!-- Body Battery -->
      <div
        v-if="healthLog.garmin_body_battery_low != null || healthLog.garmin_body_battery_high != null"
        class="bg-white px-4 py-2.5"
      >
        <p class="text-xs text-parchment-500">Body Battery</p>
        <p class="text-sm font-medium text-slate-800">
          {{ healthLog.garmin_body_battery_low ?? '—' }} → {{ healthLog.garmin_body_battery_high ?? '—' }}
        </p>
      </div>
      <!-- Stress -->
      <div v-if="healthLog.stress_score != null" class="bg-white px-4 py-2.5">
        <p class="text-xs text-parchment-500">Stress</p>
        <p class="text-sm font-medium text-slate-800">{{ healthLog.stress_score }}</p>
      </div>
      <!-- Intensity Minutes -->
      <div
        v-if="healthLog.intensity_minutes_moderate != null || healthLog.intensity_minutes_vigorous != null"
        class="bg-white px-4 py-2.5"
      >
        <p class="text-xs text-parchment-500">Intensity Min</p>
        <p class="text-sm font-medium text-slate-800">
          {{ healthLog.intensity_minutes_moderate ?? '—' }} / {{ healthLog.intensity_minutes_vigorous ?? '—' }}
          <span class="text-xs font-normal text-parchment-400">mod/vig</span>
        </p>
      </div>
      <!-- Energy Rating -->
      <div v-if="healthLog.energy_rating != null" class="bg-white px-4 py-2.5">
        <p class="text-xs text-parchment-500">Energy</p>
        <div class="flex gap-0.5 mt-0.5">
          <span
            v-for="n in 5"
            :key="n"
            class="text-sm leading-none"
            :class="n <= healthLog.energy_rating! ? 'text-earth-400' : 'text-parchment-300'"
          >★</span>
        </div>
      </div>
      <!-- Weight -->
      <div v-if="healthLog.weight_kg != null" class="bg-white px-4 py-2.5">
        <p class="text-xs text-parchment-500">Weight</p>
        <p class="text-sm font-medium text-slate-800">
          {{ Math.round((healthLog.weight_kg! / 0.45359237) * 10) / 10 }}
          <span class="text-xs font-normal text-parchment-400">lbs</span>
        </p>
      </div>
    </div>
    <div v-else class="px-4 py-4 text-sm text-parchment-400 italic">No health data for this day.</div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";

const props = defineProps<{
  show: boolean;
  currentDate: string;
  datesWithEntries?: string[];
}>();

const emit = defineEmits<{
  select: [date: string];
}>();

// ── Constants ─────────────────────────────────────────────────────────────────

import { MONTH_NAMES } from "@/utils/date";

const DAY_NAMES = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"];

// ── Helpers ───────────────────────────────────────────────────────────────────

function todayISO(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function parseDate(iso: string): Date {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(y, m - 1, d);
}

// ── Picker navigation state ───────────────────────────────────────────────────

const pickerYear = ref(0);
const pickerMonth = ref(0);

// Sync to currentDate's month whenever the picker opens
watch(
  () => props.show,
  (val) => {
    if (val) {
      const d = parseDate(props.currentDate);
      pickerYear.value = d.getFullYear();
      pickerMonth.value = d.getMonth();
    }
  },
  { immediate: true },
);

function pickerPrevMonth() {
  if (pickerMonth.value === 0) {
    pickerMonth.value = 11;
    pickerYear.value--;
  } else pickerMonth.value--;
}

function pickerNextMonth() {
  if (pickerMonth.value === 11) {
    pickerMonth.value = 0;
    pickerYear.value++;
  } else pickerMonth.value++;
}

const pickerDays = computed(() => {
  const year = pickerYear.value;
  const month = pickerMonth.value;
  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const today = todayISO();
  const cells: Array<{
    day: number | null;
    iso: string | null;
    hasEntry: boolean;
    isToday: boolean;
    isCurrent: boolean;
  }> = [];

  for (let i = 0; i < firstDay; i++) {
    cells.push({ day: null, iso: null, hasEntry: false, isToday: false, isCurrent: false });
  }
  for (let d = 1; d <= daysInMonth; d++) {
    const iso = `${year}-${String(month + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
    cells.push({
      day: d,
      iso,
      hasEntry: (props.datesWithEntries ?? []).includes(iso),
      isToday: iso === today,
      isCurrent: iso === props.currentDate,
    });
  }
  return cells;
});
</script>

<template>
  <Transition name="picker">
    <div
      v-if="show"
      class="absolute left-0 top-full mt-2 z-30 bg-white border border-parchment-300 rounded-xl shadow-xl p-3 w-64"
      @click.stop
    >
      <!-- Month navigation -->
      <div class="flex items-center justify-between mb-2">
        <button
          class="p-1 rounded text-slate-400 hover:text-slate-700 hover:bg-parchment-100 transition-colors"
          @click="pickerPrevMonth"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <span class="text-sm font-medium text-slate-700">{{ MONTH_NAMES[pickerMonth] }} {{ pickerYear }}</span>
        <button
          class="p-1 rounded text-slate-400 hover:text-slate-700 hover:bg-parchment-100 transition-colors"
          @click="pickerNextMonth"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>

      <!-- Day-of-week headers -->
      <div class="grid grid-cols-7 mb-1">
        <span v-for="name in DAY_NAMES" :key="name" class="text-center text-xs text-slate-400 font-medium py-0.5">{{
          name
        }}</span>
      </div>

      <!-- Day cells -->
      <div class="grid grid-cols-7 gap-y-0.5">
        <div v-for="(cell, idx) in pickerDays" :key="idx" class="flex flex-col items-center">
          <button
            v-if="cell.day"
            :class="[
              'w-7 h-7 rounded-lg text-xs font-medium transition-colors flex items-center justify-center',
              cell.isCurrent
                ? 'bg-forest-600 text-white'
                : cell.isToday
                  ? 'bg-parchment-200 text-forest-700 font-semibold'
                  : 'text-slate-700 hover:bg-parchment-100',
            ]"
            @click="emit('select', cell.iso!)"
          >
            {{ cell.day }}
          </button>
          <span v-else class="w-7 h-7" />
          <span v-if="cell.day && cell.hasEntry" class="w-1 h-1 rounded-full bg-forest-400 mt-0.5" />
          <span v-else-if="cell.day" class="mt-0.5 h-1" />
        </div>
      </div>

      <!-- Jump to today -->
      <div class="mt-2 pt-2 border-t border-parchment-200 text-center">
        <button class="text-xs text-forest-600 hover:text-forest-800 font-medium" @click="emit('select', todayISO())">
          Go to today
        </button>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.picker-enter-active,
.picker-leave-active {
  transition:
    opacity 0.15s ease,
    transform 0.15s ease;
}
.picker-enter-from,
.picker-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>

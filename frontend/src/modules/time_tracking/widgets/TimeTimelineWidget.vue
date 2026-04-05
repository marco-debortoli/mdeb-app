<script setup lang="ts">
import type { TimeEntry } from "@/modules/time_tracking/types";
import { formatDuration, formatTime, isNextDay, clippedMinutesForDate } from "@/modules/time_tracking/utils";

defineProps<{
  entries: TimeEntry[];
  date: string;
}>();
</script>

<template>
  <section class="bg-white rounded-lg border border-parchment-200 overflow-hidden">
    <div class="flex items-center gap-2 px-4 py-2.5 bg-blue-50 border-b border-parchment-200">
      <span class="w-2.5 h-2.5 rounded-full bg-blue-500 shrink-0"></span>
      <h3 class="text-sm font-semibold text-blue-800 uppercase tracking-wider">Time Entries</h3>
      <span v-if="entries.length" class="ml-auto text-xs text-parchment-500">
        {{ formatDuration(entries.reduce((s, e) => s + clippedMinutesForDate(e, date), 0)) }} total
      </span>
    </div>
    <div v-if="entries.length">
      <div
        v-for="entry in entries"
        :key="entry.id"
        class="flex items-center gap-3 px-4 py-2.5 border-b border-parchment-100 last:border-b-0"
      >
        <span class="w-2.5 h-2.5 rounded-full shrink-0" :style="{ backgroundColor: entry.category.color }" />
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-slate-800">{{ entry.category.name }}</p>
          <p class="text-xs text-parchment-500">
            {{ entry.subcategory?.name }}
            <span v-if="entry.notes" class="italic"> — {{ entry.notes }}</span>
          </p>
        </div>
        <div class="text-right shrink-0">
          <p class="text-xs text-slate-600">
            {{ formatTime(entry.start_time) }} – {{ formatTime(entry.end_time) }}
            <span v-if="isNextDay(entry.start_time, entry.end_time)" class="text-parchment-400">+1d</span>
          </p>
          <p class="text-xs font-medium text-slate-700">{{ formatDuration(clippedMinutesForDate(entry, date)) }}</p>
        </div>
      </div>
    </div>
    <div v-else class="px-4 py-4 text-sm text-parchment-400 italic">No time entries for this day.</div>
  </section>
</template>

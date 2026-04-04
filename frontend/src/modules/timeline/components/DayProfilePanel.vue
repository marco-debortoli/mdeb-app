<script setup lang="ts">
import { computed } from "vue";
import type { DayProfile } from "@/modules/timeline/types";
import { MONTH_NAMES, DAY_NAMES } from "@/shared/utils/date";
import JournalTimelineWidget from "@/modules/journal/widgets/JournalTimelineWidget.vue";
import FinanceTimelineWidget from "@/modules/finance/widgets/FinanceTimelineWidget.vue";
import TasksTimelineWidget from "@/modules/tasks/widgets/TasksTimelineWidget.vue";
import TimeTimelineWidget from "@/modules/time_tracking/widgets/TimeTimelineWidget.vue";
import HealthTimelineWidget from "@/modules/health/widgets/HealthTimelineWidget.vue";

const props = defineProps<{
  date: string;
  profile: DayProfile | null;
  loading: boolean;
}>();

const emit = defineEmits<{
  close: [];
}>();

const formattedDate = computed(() => {
  const [y, m, d] = props.date.split("-").map(Number);
  const dt = new Date(y, m - 1, d);
  return `${DAY_NAMES[dt.getDay()]}, ${d} ${MONTH_NAMES[m - 1]} ${y}`;
});
</script>

<template>
  <!-- Backdrop -->
  <div class="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/40" @click.self="emit('close')">
    <!-- Panel -->
    <div
      class="relative w-full sm:max-w-2xl max-h-[92vh] sm:max-h-[88vh] bg-parchment-50 sm:rounded-xl rounded-t-xl flex flex-col overflow-hidden shadow-2xl"
    >
      <!-- Header -->
      <div
        class="flex items-center justify-between px-5 py-4 border-b border-parchment-200 bg-forest-800 text-parchment-100 shrink-0 rounded-t-xl"
      >
        <div>
          <p class="text-xs font-medium text-parchment-300 uppercase tracking-widest mb-0.5">Day Profile</p>
          <h2 class="text-lg font-semibold">{{ formattedDate }}</h2>
        </div>
        <button class="p-2 rounded-lg hover:bg-forest-700 transition-colors" aria-label="Close" @click="emit('close')">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Scrollable body -->
      <div class="flex-1 overflow-y-auto p-5 space-y-5">
        <!-- Loading skeleton -->
        <div v-if="loading" class="space-y-4">
          <div v-for="i in 4" :key="i" class="bg-parchment-100 rounded-lg h-24 animate-pulse" />
        </div>

        <template v-else-if="profile">
          <JournalTimelineWidget :journal="profile.journal" :rating="profile.rating" />
          <FinanceTimelineWidget :transactions="profile.transactions" />
          <TasksTimelineWidget :tasks="profile.completed_tasks" />
          <TimeTimelineWidget :entries="profile.time_entries" :date="date" />
          <HealthTimelineWidget :health-log="profile.health_log" />
        </template>

        <!-- Empty state if profile is null and not loading -->
        <div v-else class="flex flex-col items-center justify-center py-12 text-parchment-400">
          <svg class="w-12 h-12 mb-3 opacity-40" fill="none" stroke="currentColor" stroke-width="1" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 9v7.5"
            />
          </svg>
          <p class="text-sm">No data available for this day.</p>
        </div>
      </div>
    </div>
  </div>
</template>

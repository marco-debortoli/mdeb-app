<script setup lang="ts">
import type { TaskSummary } from "@/modules/tasks/types";

defineProps<{
  tasks: TaskSummary[];
}>();
</script>

<template>
  <section class="bg-white rounded-lg border border-parchment-200 overflow-hidden">
    <div class="flex items-center gap-2 px-4 py-2.5 bg-slate-50 border-b border-parchment-200">
      <span class="w-2.5 h-2.5 rounded-full bg-slate-500 shrink-0"></span>
      <h3 class="text-sm font-semibold text-slate-700 uppercase tracking-wider">Completed Tasks</h3>
      <span v-if="tasks.length" class="ml-auto text-xs text-parchment-500">
        {{ tasks.length }} task{{ tasks.length !== 1 ? "s" : "" }}
      </span>
    </div>
    <div v-if="tasks.length">
      <div
        v-for="task in tasks"
        :key="task.id"
        class="flex items-start gap-3 px-4 py-2.5 border-b border-parchment-100 last:border-b-0"
      >
        <!-- Checkmark -->
        <svg
          class="w-4 h-4 text-forest-500 mt-0.5 shrink-0"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <div class="flex-1 min-w-0">
          <p class="text-sm text-slate-800">{{ task.title }}</p>
          <div class="flex flex-wrap gap-1.5 mt-1">
            <span
              v-if="task.category"
              class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium text-white"
              :style="{ backgroundColor: task.category.color }"
            >
              {{ task.category.name }}
            </span>
            <span v-if="task.project" class="text-xs text-parchment-500">{{ task.project.name }}</span>
            <span v-if="task.priority === 'URGENT'" class="text-xs text-red-500 font-medium">Urgent</span>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="px-4 py-4 text-sm text-parchment-400 italic">No tasks completed on this day.</div>
  </section>
</template>

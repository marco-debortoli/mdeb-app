<script setup lang="ts">
import { computed } from "vue";
import { EffortLevel, Priority, TaskStatus } from "@/modules/tasks/types";
import type { TaskSummary } from "@/modules/tasks/types";

const props = defineProps<{ task: TaskSummary }>();
const emit = defineEmits<{ (e: "open", task: TaskSummary): void }>();

const statusConfig: Record<TaskStatus, { label: string; icon: string; classes: string }> = {
  [TaskStatus.TODO]: {
    label: "To Do",
    icon: "M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z",
    classes: "text-slate-500",
  },
  [TaskStatus.IN_PROGRESS]: {
    label: "In Progress",
    icon: "M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z",
    classes: "text-earth-500",
  },
  [TaskStatus.WAITING]: {
    label: "Waiting",
    icon: "M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z",
    classes: "text-slate-400",
  },
  [TaskStatus.COMPLETE]: {
    label: "Complete",
    icon: "M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
    classes: "text-forest-500",
  },
  [TaskStatus.BACKLOG]: {
    label: "Backlog",
    icon: "M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z",
    classes: "text-slate-300",
  },
};

const effortConfig: Record<EffortLevel, { label: string; classes: string }> = {
  [EffortLevel.LOW]: { label: "Low", classes: "bg-forest-100 text-forest-700" },
  [EffortLevel.MEDIUM]: { label: "Medium", classes: "bg-earth-100 text-earth-700" },
  [EffortLevel.HIGH]: { label: "High", classes: "bg-slate-100 text-slate-700" },
};

const priorityConfig: Record<Priority, { label: string; dot: string }> = {
  [Priority.LOW]: { label: "Low priority", dot: "bg-slate-300" },
  [Priority.MEDIUM]: { label: "Medium priority", dot: "bg-earth-400" },
  [Priority.HIGH]: { label: "High priority", dot: "bg-amber-500" },
  [Priority.URGENT]: { label: "Urgent", dot: "bg-red-500" },
};

const status = computed(() => statusConfig[props.task.status]);
const effort = computed(() => (props.task.effort ? effortConfig[props.task.effort] : null));
const priority = computed(() => (props.task.priority ? priorityConfig[props.task.priority] : null));

function formatDate(d: string | null): string {
  if (!d) return "—";
  return new Date(d + "T00:00:00").toLocaleDateString("en-CA", {
    month: "short",
    day: "numeric",
  });
}
</script>

<template>
  <div
    class="flex items-center gap-3 px-4 py-3 bg-parchment-50 border border-parchment-300 rounded-lg cursor-pointer hover:bg-parchment-100 hover:border-parchment-400 transition-colors group"
    @click="emit('open', task)"
  >
    <!-- Status icon -->
    <svg
      :class="['w-5 h-5 shrink-0', status.classes]"
      fill="none"
      stroke="currentColor"
      stroke-width="1.5"
      viewBox="0 0 24 24"
      :title="status.label"
    >
      <path stroke-linecap="round" stroke-linejoin="round" :d="status.icon" />
    </svg>

    <!-- Priority dot -->
    <span v-if="priority" :class="['w-2 h-2 rounded-full shrink-0', priority.dot]" :title="priority.label" />

    <!-- Title -->
    <span
      :class="[
        'flex-1 text-sm font-medium min-w-0 truncate',
        task.status === 'COMPLETE' ? 'line-through text-slate-400' : 'text-slate-800',
      ]"
    >
      {{ task.title }}
    </span>

    <!-- Category chip -->
    <span
      v-if="task.category"
      class="shrink-0 hidden sm:inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
      :style="{ backgroundColor: task.category.color + '22', color: task.category.color }"
    >
      {{ task.category.name }}
    </span>

    <!-- Effort badge -->
    <span
      v-if="effort"
      :class="['shrink-0 hidden md:inline-flex items-center px-2 py-0.5 rounded text-xs font-medium', effort.classes]"
    >
      {{ effort.label }}
    </span>

    <!-- Project -->
    <span
      v-if="task.project"
      class="shrink-0 hidden lg:block text-xs text-slate-400 truncate max-w-[120px]"
      :title="task.project.name"
    >
      {{ task.project.name }}
    </span>

    <!-- Scheduled / completed date -->
    <span class="shrink-0 text-xs font-mono text-slate-400 w-16 text-right">
      {{ task.status === "COMPLETE" ? formatDate(task.completed_date) : formatDate(task.scheduled_date) }}
    </span>
  </div>
</template>

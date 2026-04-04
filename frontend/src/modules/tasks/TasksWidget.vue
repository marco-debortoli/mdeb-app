<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useTasksStore } from "@/modules/tasks/store";
import { taskApi } from "@/modules/tasks/api";
import type { TaskSummary } from "@/modules/tasks/types";
import { TaskStatus, Priority } from "@/modules/tasks/types";
import TaskRow from "@/modules/tasks/components/TaskRow.vue";
import TaskModal from "@/modules/tasks/components/TaskModal.vue";

const d = new Date();
const today = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;

const tasksStore = useTasksStore();
const widgetTasks = ref<TaskSummary[]>([]);
const loading = ref(false);
const selectedTask = ref<TaskSummary | null>(null);
const showModal = ref(false);

const relevantTasks = computed(() =>
  widgetTasks.value
    .filter((task) => {
      if (task.status === TaskStatus.COMPLETE || task.status === TaskStatus.BACKLOG) return false;
      if (task.priority === Priority.URGENT) return true;
      if (task.scheduled_date === today) return true;
      if (task.scheduled_date && task.scheduled_date < today) return true;
      return false;
    })
    .sort((a, b) => {
      const ua = a.priority === Priority.URGENT;
      const ub = b.priority === Priority.URGENT;
      if (ua !== ub) return ua ? -1 : 1;
      const aDate = a.scheduled_date ?? "9999-99-99";
      const bDate = b.scheduled_date ?? "9999-99-99";
      return aDate.localeCompare(bDate);
    }),
);

async function load() {
  loading.value = true;
  try {
    widgetTasks.value = await taskApi.list();
  } finally {
    loading.value = false;
  }
}

function openTask(task: TaskSummary) {
  selectedTask.value = task;
  showModal.value = true;
}

async function onSaved() {
  showModal.value = false;
  selectedTask.value = null;
  await load();
}

async function onDeleted() {
  showModal.value = false;
  selectedTask.value = null;
  await load();
}

onMounted(async () => {
  await Promise.all([load(), tasksStore.fetchCategories(), tasksStore.fetchProjects()]);
});
</script>

<template>
  <section
    class="bg-parchment-50 border border-parchment-300 rounded-xl overflow-hidden shadow-sm flex flex-col h-full"
  >
    <!-- Header -->
    <div class="flex items-center justify-between px-4 py-3 border-b border-parchment-200 shrink-0">
      <div class="flex items-center gap-2">
        <div class="w-7 h-7 rounded-md bg-earth-500 flex items-center justify-center shrink-0">
          <svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.5" class="w-4 h-4">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <h2 class="font-semibold text-slate-800 text-sm">Tasks</h2>
        <span
          v-if="relevantTasks.length"
          class="text-xs bg-earth-500/15 text-earth-700 font-medium px-1.5 py-0.5 rounded-full"
          >{{ relevantTasks.length }}</span
        >
      </div>
      <RouterLink to="/tasks" class="text-xs text-forest-600 hover:text-forest-700 transition-colors"
        >View all →</RouterLink
      >
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto">
      <div v-if="loading" class="px-4 py-8 text-center text-sm text-slate-400">Loading…</div>
      <div v-else-if="relevantTasks.length === 0" class="px-4 py-8 text-center text-sm text-slate-400 italic">
        Nothing due — you're all caught up.
      </div>
      <div v-else class="px-3 py-2.5 space-y-1.5">
        <TaskRow v-for="task in relevantTasks" :key="task.id" :task="task" @open="openTask" />
      </div>
    </div>
  </section>

  <TaskModal
    :open="showModal"
    :task="selectedTask"
    @close="
      showModal = false;
      selectedTask = null;
    "
    @saved="onSaved"
    @deleted="onDeleted"
  />
</template>

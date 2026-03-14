<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import { TaskStatus, Priority } from "@/types/tasks";
import type { TaskSummary } from "@/types/tasks";
import { useTasksStore } from "@/stores/tasks";
import TaskRow from "@/components/tasks/TaskRow.vue";
import TaskModal from "@/components/tasks/TaskModal.vue";

const store = useTasksStore();

// ── Tab state ─────────────────────────────────────────────────────────────────
type Tab = "active" | "completed" | "backlog";
const activeTab = ref<Tab>("active");

// ── Modal state ───────────────────────────────────────────────────────────────
const modalOpen = ref(false);
const selectedTask = ref<TaskSummary | null>(null);

function openNew() {
  selectedTask.value = null;
  modalOpen.value = true;
}

function openEdit(task: TaskSummary) {
  selectedTask.value = task;
  modalOpen.value = true;
}

function onSaved() {
  // fetchTasks already called by store actions; just close modal
}

// ── Manage categories / projects modals ───────────────────────────────────────
const manageCatsOpen = ref(false);
const manageProjOpen = ref(false);

// Inline form state for category manager
const newCatName = ref("");
const newCatColor = ref("#4a7f3d");
const savingCat = ref(false);

async function addCategory() {
  if (!newCatName.value.trim()) return;
  savingCat.value = true;
  try {
    await store.createCategory(newCatName.value.trim(), newCatColor.value);
    newCatName.value = "";
    newCatColor.value = "#4a7f3d";
  } finally {
    savingCat.value = false;
  }
}

// Inline form state for project manager
const newProjName = ref("");
const newProjDesc = ref("");
const savingProj = ref(false);

async function addProject() {
  if (!newProjName.value.trim()) return;
  savingProj.value = true;
  try {
    await store.createProject(newProjName.value.trim(), newProjDesc.value.trim() || undefined);
    newProjName.value = "";
    newProjDesc.value = "";
  } finally {
    savingProj.value = false;
  }
}

// ── Task display ──────────────────────────────────────────────────────────────
const ACTIVE_STATUSES = new Set<TaskStatus>([TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.WAITING]);

const priorityOrder: Record<Priority, number> = {
  [Priority.URGENT]: 0,
  [Priority.HIGH]: 1,
  [Priority.MEDIUM]: 2,
  [Priority.LOW]: 3,
};

const displayedTasks = computed((): TaskSummary[] => {
  const all: TaskSummary[] = store.tasks;

  if (activeTab.value === "active") {
    return [...all.filter((t: TaskSummary) => ACTIVE_STATUSES.has(t.status as TaskStatus))].sort(
      (a: TaskSummary, b: TaskSummary) => {
        const pa = a.priority != null ? priorityOrder[a.priority as Priority] : 4;
        const pb = b.priority != null ? priorityOrder[b.priority as Priority] : 4;
        return pa - pb;
      },
    );
  }

  if (activeTab.value === "completed") {
    return [...all.filter((t: TaskSummary) => t.status === TaskStatus.COMPLETE)].sort(
      (a: TaskSummary, b: TaskSummary) =>
        (b.completed_date ?? b.updated_at).localeCompare(a.completed_date ?? a.updated_at),
    );
  }

  // backlog — sorted by created_at desc
  return [...all.filter((t: TaskSummary) => t.status === TaskStatus.BACKLOG)].sort((a: TaskSummary, b: TaskSummary) =>
    b.created_at.localeCompare(a.created_at),
  );
});

const tabCounts = computed(() => ({
  active: store.tasks.filter((t: TaskSummary) => ACTIVE_STATUSES.has(t.status as TaskStatus)).length,
  completed: store.tasks.filter((t: TaskSummary) => t.status === TaskStatus.COMPLETE).length,
  backlog: store.tasks.filter((t: TaskSummary) => t.status === TaskStatus.BACKLOG).length,
}));

// ── Filters ───────────────────────────────────────────────────────────────────
// Only watch category/project — status is handled client-side by tabs
watch(
  () => ({ category_id: store.filters.category_id, project_id: store.filters.project_id }),
  () => store.fetchTasks(),
  { deep: true },
);

onMounted(() => store.fetchAll());
</script>

<template>
  <div class="max-w-4xl mx-auto">
    <!-- Page header -->
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-semibold text-slate-800">Task List</h2>
      <button
        class="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium bg-forest-600 text-parchment-50 hover:bg-forest-700 transition-colors"
        @click="openNew"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
        </svg>
        New Task
      </button>
    </div>

    <!-- Tabs -->
    <div class="flex items-center gap-0 border-b border-parchment-300 mb-4">
      <button
        v-for="tab in [
          { key: 'active', label: 'Active' },
          { key: 'completed', label: 'Completed' },
          { key: 'backlog', label: 'Backlog' },
        ] as const"
        :key="tab.key"
        :class="[
          'px-4 py-2.5 text-sm font-medium flex items-center gap-2 border-b-2 -mb-px transition-colors',
          activeTab === tab.key
            ? 'border-forest-600 text-forest-700'
            : 'border-transparent text-slate-500 hover:text-slate-700',
        ]"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
        <span
          :class="[
            'text-xs px-1.5 py-0.5 rounded-full font-mono',
            activeTab === tab.key ? 'bg-forest-100 text-forest-700' : 'bg-parchment-200 text-slate-400',
          ]"
          >{{ tabCounts[tab.key] }}</span
        >
      </button>
    </div>

    <!-- Filter bar -->
    <div
      class="bg-parchment-50 border border-parchment-300 rounded-xl p-4 mb-4 flex flex-col sm:flex-row sm:flex-wrap sm:items-center gap-3"
    >
      <!-- Category filter -->
      <select
        v-model="store.filters.category_id"
        class="w-full sm:w-auto text-sm rounded-lg border border-parchment-300 bg-white px-3 pr-8 py-1.5 text-slate-700 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
      >
        <option value="">All categories</option>
        <option v-for="cat in store.categories" :key="cat.id" :value="cat.id">
          {{ cat.name }}
        </option>
      </select>

      <!-- Project filter -->
      <select
        v-model="store.filters.project_id"
        class="w-full sm:w-auto text-sm rounded-lg border border-parchment-300 bg-white px-3 pr-8 py-1.5 text-slate-700 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
      >
        <option value="">All projects</option>
        <option v-for="proj in store.projects" :key="proj.id" :value="proj.id">
          {{ proj.name }}
        </option>
      </select>

      <div class="flex gap-2 sm:ml-auto">
        <button
          class="flex-1 sm:flex-none text-xs font-medium text-slate-500 hover:text-slate-700 px-2 py-1 rounded hover:bg-parchment-200 transition-colors"
          @click="manageCatsOpen = true"
        >
          Manage Categories
        </button>
        <button
          class="flex-1 sm:flex-none text-xs font-medium text-slate-500 hover:text-slate-700 px-2 py-1 rounded hover:bg-parchment-200 transition-colors"
          @click="manageProjOpen = true"
        >
          Manage Projects
        </button>
      </div>
    </div>

    <!-- Task list -->
    <div v-if="store.loading" class="text-sm text-slate-400 py-8 text-center">Loading…</div>
    <div v-else-if="store.error" class="text-sm text-red-600 bg-red-50 rounded-xl px-4 py-3">
      {{ store.error }}
    </div>
    <div v-else-if="displayedTasks.length === 0" class="text-sm text-slate-400 py-12 text-center">
      <template v-if="activeTab === 'active'">
        No active tasks.
        <button class="ml-1 text-forest-600 hover:underline" @click="openNew">Create one.</button>
      </template>
      <template v-else-if="activeTab === 'completed'"> No completed tasks yet. </template>
      <template v-else>
        No backlog tasks.
        <button class="ml-1 text-forest-600 hover:underline" @click="openNew">Add one.</button>
      </template>
    </div>
    <div v-else class="space-y-2">
      <TaskRow v-for="task in displayedTasks" :key="task.id" :task="task" @open="openEdit" />
    </div>

    <!-- Task create/edit modal -->
    <TaskModal :open="modalOpen" :task="selectedTask" @close="modalOpen = false" @saved="onSaved" @deleted="onSaved" />

    <!-- Manage Categories modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div
          v-if="manageCatsOpen"
          class="fixed inset-0 z-50 flex items-center justify-center p-4"
          @click.self="manageCatsOpen = false"
        >
          <div class="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" @click="manageCatsOpen = false" />
          <div class="relative w-full max-w-sm bg-parchment-50 rounded-xl shadow-2xl border border-parchment-300">
            <div class="flex items-center justify-between px-5 py-4 border-b border-parchment-300">
              <h2 class="text-base font-semibold text-slate-800">Manage Categories</h2>
              <button
                class="p-1 rounded-lg text-slate-400 hover:bg-parchment-200 transition-colors"
                @click="manageCatsOpen = false"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div class="px-5 py-4 space-y-3">
              <!-- Existing categories -->
              <div v-if="store.categories.length" class="space-y-2">
                <div
                  v-for="cat in store.categories"
                  :key="cat.id"
                  class="flex items-center gap-2 bg-parchment-100 rounded-lg px-3 py-2"
                >
                  <span class="w-3 h-3 rounded-full shrink-0" :style="{ backgroundColor: cat.color }" />
                  <span class="flex-1 text-sm text-slate-700">{{ cat.name }}</span>
                  <button
                    class="p-1 rounded text-slate-300 hover:text-red-500 hover:bg-red-50 transition-colors"
                    title="Delete"
                    @click="store.deleteCategory(cat.id)"
                  >
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
              <p v-else class="text-xs text-slate-400">No categories yet.</p>

              <!-- Add new -->
              <div class="flex items-center gap-2 pt-1">
                <input
                  v-model="newCatColor"
                  type="color"
                  class="w-8 h-8 rounded cursor-pointer border border-parchment-300"
                  title="Pick color"
                />
                <input
                  v-model="newCatName"
                  type="text"
                  placeholder="Category name"
                  class="flex-1 text-sm rounded-lg border border-parchment-300 bg-white px-3 py-2 text-slate-800 placeholder-slate-400 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
                  @keydown.enter="addCategory"
                />
                <button
                  :disabled="!newCatName.trim() || savingCat"
                  class="px-3 py-2 rounded-lg text-sm font-medium bg-forest-600 text-parchment-50 hover:bg-forest-700 disabled:opacity-40 transition-colors"
                  @click="addCategory"
                >
                  Add
                </button>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Manage Projects modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div
          v-if="manageProjOpen"
          class="fixed inset-0 z-50 flex items-center justify-center p-4"
          @click.self="manageProjOpen = false"
        >
          <div class="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" @click="manageProjOpen = false" />
          <div class="relative w-full max-w-sm bg-parchment-50 rounded-xl shadow-2xl border border-parchment-300">
            <div class="flex items-center justify-between px-5 py-4 border-b border-parchment-300">
              <h2 class="text-base font-semibold text-slate-800">Manage Projects</h2>
              <button
                class="p-1 rounded-lg text-slate-400 hover:bg-parchment-200 transition-colors"
                @click="manageProjOpen = false"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div class="px-5 py-4 space-y-3">
              <!-- Existing projects -->
              <div v-if="store.projects.length" class="space-y-2">
                <div
                  v-for="proj in store.projects"
                  :key="proj.id"
                  class="flex items-center gap-2 bg-parchment-100 rounded-lg px-3 py-2"
                >
                  <span class="flex-1 text-sm text-slate-700">{{ proj.name }}</span>
                  <button
                    class="p-1 rounded text-slate-300 hover:text-red-500 hover:bg-red-50 transition-colors"
                    title="Delete"
                    @click="store.deleteProject(proj.id)"
                  >
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
              <p v-else class="text-xs text-slate-400">No projects yet.</p>

              <!-- Add new -->
              <div class="flex items-center gap-2 pt-1">
                <input
                  v-model="newProjName"
                  type="text"
                  placeholder="Project name"
                  class="flex-1 text-sm rounded-lg border border-parchment-300 bg-white px-3 py-2 text-slate-800 placeholder-slate-400 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
                  @keydown.enter="addProject"
                />
                <button
                  :disabled="!newProjName.trim() || savingProj"
                  class="px-3 py-2 rounded-lg text-sm font-medium bg-forest-600 text-parchment-50 hover:bg-forest-700 disabled:opacity-40 transition-colors"
                  @click="addProject"
                >
                  Add
                </button>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.15s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>

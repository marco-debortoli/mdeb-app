<script setup lang="ts">
import { ref, watch, computed } from "vue";
import { EffortLevel, Priority, TaskStatus } from "@/modules/tasks/types";
import type { Task, TaskSummary } from "@/modules/tasks/types";
import { taskApi } from "@/modules/tasks/api";
import { useTasksStore } from "@/modules/tasks/store";
import BaseModal from "@/shared/components/BaseModal.vue";

const props = defineProps<{
  open: boolean;
  /** Pass a TaskSummary to open in edit mode; omit for create mode */
  task?: TaskSummary | null;
}>();
const emit = defineEmits<{
  (e: "close"): void;
  (e: "saved"): void;
  (e: "deleted"): void;
}>();

const store = useTasksStore();

// ── Form state ────────────────────────────────────────────────────────────────
const title = ref("");
const statusVal = ref<TaskStatus>(TaskStatus.TODO);
const effort = ref<EffortLevel | "">("");
const priorityVal = ref<Priority | "">("");
const categoryId = ref<number | "">("");
const projectId = ref<number | "">("");
const scheduledDate = ref("");
const completedDate = ref("");

// ── Full task (with notes) fetched when editing ───────────────────────────────
const fullTask = ref<Task | null>(null);
const notesLoading = ref(false);
const newNote = ref("");
const addingNote = ref(false);

const saving = ref(false);
const deleting = ref(false);
const error = ref<string | null>(null);

const isEdit = computed(() => !!props.task);
const modalTitle = computed(() => (isEdit.value ? "Edit Task" : "New Task"));

// ── Load task when opening in edit mode ───────────────────────────────────────
watch(
  () => props.open,
  async (open) => {
    error.value = null;
    if (!open) {
      fullTask.value = null;
      return;
    }
    if (props.task) {
      // Populate form from summary
      title.value = props.task.title;
      statusVal.value = props.task.status;
      effort.value = props.task.effort ?? "";
      priorityVal.value = props.task.priority ?? "";
      categoryId.value = props.task.category?.id ?? "";
      projectId.value = props.task.project?.id ?? "";
      scheduledDate.value = props.task.scheduled_date ?? "";
      completedDate.value = props.task.completed_date ?? "";
      // Fetch full task (with notes)
      notesLoading.value = true;
      try {
        fullTask.value = await taskApi.get(props.task.id);
      } finally {
        notesLoading.value = false;
      }
    } else {
      // Reset form for create
      title.value = "";
      statusVal.value = TaskStatus.TODO;
      effort.value = "";
      priorityVal.value = "";
      categoryId.value = "";
      projectId.value = "";
      scheduledDate.value = "";
      completedDate.value = "";
      fullTask.value = null;
    }
  },
);

// ── Save ──────────────────────────────────────────────────────────────────────
async function save() {
  if (!title.value.trim()) return;
  saving.value = true;
  error.value = null;
  try {
    const payload = {
      title: title.value.trim(),
      status: statusVal.value,
      effort: effort.value || null,
      priority: priorityVal.value || null,
      category_id: categoryId.value || null,
      project_id: projectId.value || null,
      scheduled_date: scheduledDate.value || null,
      ...(statusVal.value === TaskStatus.COMPLETE ? { completed_date: completedDate.value || null } : {}),
    };
    if (isEdit.value && props.task) {
      await store.updateTask(props.task.id, payload);
    } else {
      await store.createTask(payload);
    }
    emit("saved");
    emit("close");
  } catch (e) {
    error.value = String(e);
  } finally {
    saving.value = false;
  }
}

// ── Delete ────────────────────────────────────────────────────────────────────
async function confirmDelete() {
  if (!props.task) return;
  if (!confirm(`Delete "${props.task.title}"?`)) return;
  deleting.value = true;
  try {
    await store.deleteTask(props.task.id);
    emit("deleted");
    emit("close");
  } finally {
    deleting.value = false;
  }
}

// ── Notes ─────────────────────────────────────────────────────────────────────
async function addNote() {
  if (!newNote.value.trim() || !fullTask.value) return;
  addingNote.value = true;
  try {
    const note = await taskApi.addNote(fullTask.value.id, newNote.value.trim());
    fullTask.value.notes.push(note);
    newNote.value = "";
  } finally {
    addingNote.value = false;
  }
}

async function deleteNote(noteId: number) {
  if (!fullTask.value) return;
  await taskApi.deleteNote(fullTask.value.id, noteId);
  fullTask.value.notes = fullTask.value.notes.filter((n) => n.id !== noteId);
}

function formatNoteDate(d: string): string {
  return new Date(d).toLocaleDateString("en-CA", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}
</script>

<template>
  <BaseModal
    :open="open"
    :title="modalTitle"
    :mobile="true"
    max-width="sm:max-w-lg"
    height-class="max-h-[92vh] sm:max-h-[90vh]"
    @close="emit('close')"
  >
    <!-- Error -->
    <p v-if="error" class="text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">{{ error }}</p>

    <!-- Title -->
    <div>
      <label class="block text-xs font-medium text-slate-600 mb-1">Title</label>
      <input
        v-model="title"
        type="text"
        placeholder="Task title"
        class="w-full text-sm rounded-lg border border-parchment-300 bg-white px-3 py-2 text-slate-800 placeholder-slate-400 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
        @keydown.enter="save"
      />
    </div>

    <!-- Status + Priority + Effort -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
      <div>
        <label class="block text-xs font-medium text-slate-600 mb-1">Status</label>
        <select
          v-model="statusVal"
          class="w-full text-sm rounded-lg border border-parchment-300 bg-white px-3 py-2 text-slate-800 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
        >
          <option :value="TaskStatus.TODO">To Do</option>
          <option :value="TaskStatus.IN_PROGRESS">In Progress</option>
          <option :value="TaskStatus.WAITING">Waiting</option>
          <option :value="TaskStatus.COMPLETE">Complete</option>
          <option :value="TaskStatus.BACKLOG">Backlog</option>
        </select>
      </div>
      <div>
        <label class="block text-xs font-medium text-slate-600 mb-1">Priority</label>
        <select
          v-model="priorityVal"
          class="w-full text-sm rounded-lg border border-parchment-300 bg-white px-3 py-2 text-slate-800 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
        >
          <option value="">— None</option>
          <option :value="Priority.LOW">Low</option>
          <option :value="Priority.MEDIUM">Medium</option>
          <option :value="Priority.HIGH">High</option>
          <option :value="Priority.URGENT">Urgent</option>
        </select>
      </div>
      <div>
        <label class="block text-xs font-medium text-slate-600 mb-1">Effort</label>
        <select
          v-model="effort"
          class="w-full text-sm rounded-lg border border-parchment-300 bg-white px-3 py-2 text-slate-800 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
        >
          <option value="">— None</option>
          <option :value="EffortLevel.LOW">Low</option>
          <option :value="EffortLevel.MEDIUM">Medium</option>
          <option :value="EffortLevel.HIGH">High</option>
        </select>
      </div>
    </div>

    <!-- Category + Project -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
      <div>
        <label class="block text-xs font-medium text-slate-600 mb-1">Category</label>
        <select
          v-model="categoryId"
          class="w-full text-sm rounded-lg border border-parchment-300 bg-white px-3 py-2 text-slate-800 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
        >
          <option value="">— None</option>
          <option v-for="cat in store.categories" :key="cat.id" :value="cat.id">
            {{ cat.name }}
          </option>
        </select>
      </div>
      <div>
        <label class="block text-xs font-medium text-slate-600 mb-1">Project</label>
        <select
          v-model="projectId"
          class="w-full text-sm rounded-lg border border-parchment-300 bg-white px-3 py-2 text-slate-800 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
        >
          <option value="">— None</option>
          <option v-for="proj in store.projects" :key="proj.id" :value="proj.id">
            {{ proj.name }}
          </option>
        </select>
      </div>
    </div>

    <!-- Scheduled date + Completed date -->
    <div class="flex gap-3">
      <div>
        <label class="block text-xs font-medium text-slate-600 mb-1">Scheduled date</label>
        <input
          v-model="scheduledDate"
          type="date"
          class="text-sm rounded-lg border border-parchment-300 bg-white px-3 py-2 text-slate-800 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
        />
      </div>
      <div v-if="statusVal === TaskStatus.COMPLETE">
        <label class="block text-xs font-medium text-slate-600 mb-1">Completed date</label>
        <input
          v-model="completedDate"
          type="date"
          class="text-sm rounded-lg border border-parchment-300 bg-white px-3 py-2 text-slate-800 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
        />
      </div>
    </div>

    <!-- Notes section (edit mode only) -->
    <div v-if="isEdit" class="border-t border-parchment-200 pt-4">
      <h3 class="text-xs font-semibold text-slate-600 uppercase tracking-wide mb-3">Notes</h3>

      <div v-if="notesLoading" class="text-xs text-slate-400 py-2">Loading notes…</div>
      <div v-else>
        <div v-if="fullTask && fullTask.notes.length" class="space-y-2 mb-3">
          <div
            v-for="note in fullTask.notes"
            :key="note.id"
            class="flex items-start gap-2 bg-parchment-100 rounded-lg px-3 py-2"
          >
            <div class="flex-1 min-w-0">
              <p class="text-xs font-mono text-slate-400 mb-0.5">{{ formatNoteDate(note.created_at) }}</p>
              <p class="text-sm text-slate-700 whitespace-pre-wrap break-words">{{ note.content }}</p>
            </div>
            <button
              class="shrink-0 p-1 rounded text-slate-300 hover:text-red-500 hover:bg-red-50 transition-colors"
              title="Delete note"
              @click="deleteNote(note.id)"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        <p v-else class="text-xs text-slate-400 mb-3">No notes yet.</p>

        <!-- Add note -->
        <div class="flex gap-2">
          <input
            v-model="newNote"
            type="text"
            placeholder="Add a note…"
            class="flex-1 text-sm rounded-lg border border-parchment-300 bg-white px-3 py-2 text-slate-800 placeholder-slate-400 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
            @keydown.enter="addNote"
          />
          <button
            :disabled="!newNote.trim() || addingNote"
            class="px-3 py-2 rounded-lg text-sm font-medium bg-forest-600 text-parchment-50 hover:bg-forest-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            @click="addNote"
          >
            Add
          </button>
        </div>
      </div>
    </div>

    <template #footer-left>
      <button
        v-if="isEdit"
        :disabled="deleting"
        class="px-4 py-2 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 border border-red-200 disabled:opacity-40 transition-colors"
        @click="confirmDelete"
      >
        {{ deleting ? "Deleting…" : "Delete" }}
      </button>
    </template>
    <template #footer-right>
      <div class="flex gap-2">
        <button
          class="px-4 py-2 rounded-lg text-sm font-medium text-slate-600 hover:bg-parchment-200 transition-colors"
          @click="emit('close')"
        >
          Cancel
        </button>
        <button
          :disabled="saving || !title.trim()"
          class="px-4 py-2 rounded-lg text-sm font-medium bg-forest-600 text-parchment-50 hover:bg-forest-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          @click="save"
        >
          {{ saving ? "Saving…" : "Save" }}
        </button>
      </div>
    </template>
  </BaseModal>
</template>

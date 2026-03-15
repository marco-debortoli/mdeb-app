<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from "vue";
import EasyMDE from "easymde";
import { marked } from "marked";
import { useNotesStore } from "@/stores/notes";

const emit = defineEmits<{
  back: [];
}>();

const store = useNotesStore();

// ── EasyMDE ───────────────────────────────────────────────────────────────────

const textareaRef = ref<HTMLTextAreaElement | null>(null);
let mde: EasyMDE | null = null;

function initMDE(content: string) {
  if (!textareaRef.value) return;
  if (mde) {
    mde.toTextArea();
    mde = null;
  }
  textareaRef.value.value = content;
  mde = new EasyMDE({
    element: textareaRef.value,
    autofocus: false,
    spellChecker: false,
    status: false,
    toolbar: [
      "bold",
      "italic",
      "heading",
      "|",
      "quote",
      "unordered-list",
      "ordered-list",
      "|",
      "link",
      "horizontal-rule",
      "|",
      "guide",
    ],
    minHeight: "300px",
    placeholder: "Write your note…",
  });
  mde.codemirror.on("change", () => {
    scheduleAutoSave();
  });
}

function destroyMDE() {
  if (mde) {
    mde.toTextArea();
    mde = null;
  }
}

// ── Title ────────────────────────────────────────────────────────────────────

const titleValue = ref("");

function onTitleInput() {
  scheduleAutoSave();
}

// ── Auto-save ─────────────────────────────────────────────────────────────────

const saveStatus = ref<"idle" | "saving" | "saved" | "error">("idle");
let saveTimer: ReturnType<typeof setTimeout> | null = null;
let idleTimer: ReturnType<typeof setTimeout> | null = null;

function scheduleAutoSave() {
  if (saveTimer) clearTimeout(saveTimer);
  if (idleTimer) clearTimeout(idleTimer);
  saveStatus.value = "saving";
  const noteId = store.activeNote?.id;
  const capturedTitle = titleValue.value;
  saveTimer = setTimeout(async () => {
    if (!noteId || store.activeNote?.id !== noteId) return;
    try {
      await store.saveNote(noteId, {
        title: capturedTitle || "Untitled",
        content: mde?.value() ?? "",
      });
      saveStatus.value = "saved";
      idleTimer = setTimeout(() => {
        saveStatus.value = "idle";
      }, 2500);
    } catch {
      saveStatus.value = "error";
    }
  }, 2500);
}

async function flushSave(noteId?: number) {
  if (!saveTimer) return;
  const id = noteId ?? store.activeNote?.id;
  if (!id) return;
  clearTimeout(saveTimer);
  saveTimer = null;
  try {
    await store.saveNote(id, {
      title: titleValue.value || "Untitled",
      content: mde?.value() ?? "",
    });
  } catch {
    /* ignore */
  }
}

// ── Note switching ────────────────────────────────────────────────────────────

watch(
  () => store.activeNote?.id,
  async (newId, oldId) => {
    if (newId === oldId) return;
    // Flush save for old note before switching
    if (oldId !== undefined && oldId !== null) {
      await flushSave(oldId);
    }
    destroyMDE();
    previewMode.value = false;
    saveStatus.value = "idle";
    if (newId !== undefined && newId !== null) {
      titleValue.value = store.activeNote?.title ?? "";
      await nextTick();
      initMDE(store.activeNote?.content ?? "");
    }
  },
);

// ── Preview mode ──────────────────────────────────────────────────────────────

const previewMode = ref(false);
const previewContent = ref("");

const renderedContent = computed(() => {
  if (!previewContent.value.trim()) return "";
  return marked(previewContent.value) as string;
});

async function togglePreview() {
  if (!previewMode.value) {
    previewContent.value = mde?.value() ?? store.activeNote?.content ?? "";
    await flushSave();
    destroyMDE();
    previewMode.value = true;
  } else {
    previewMode.value = false;
    await nextTick();
    initMDE(previewContent.value);
  }
}

// ── Delete ────────────────────────────────────────────────────────────────────

const confirmingDelete = ref(false);

async function handleDelete() {
  if (!store.activeNote) return;
  if (!confirmingDelete.value) {
    confirmingDelete.value = true;
    return;
  }
  const id = store.activeNote.id;
  destroyMDE();
  saveStatus.value = "idle";
  confirmingDelete.value = false;
  await store.deleteNote(id);
  emit("back");
}

// ── Lifecycle ─────────────────────────────────────────────────────────────────

onBeforeUnmount(() => {
  if (saveTimer) clearTimeout(saveTimer);
  if (idleTimer) clearTimeout(idleTimer);
  destroyMDE();
});
</script>

<template>
  <div class="flex flex-col h-full min-h-0">
    <!-- Empty state -->
    <div v-if="!store.activeNote" class="flex-1 flex items-center justify-center text-slate-400 text-sm">
      Select a note or create one
    </div>

    <!-- Editor -->
    <template v-else>
      <!-- Header -->
      <div class="flex items-center gap-2 mb-3 shrink-0">
        <!-- Mobile back button -->
        <button
          class="md:hidden p-1.5 rounded-lg text-slate-500 hover:bg-parchment-200 transition-colors"
          title="Back to notes"
          @click="emit('back')"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
        </button>

        <!-- Title input -->
        <input
          v-model="titleValue"
          type="text"
          placeholder="Untitled"
          class="flex-1 text-lg font-semibold text-slate-800 bg-transparent border-none outline-none placeholder-slate-300 min-w-0"
          @input="onTitleInput"
          @blur="confirmingDelete = false"
        />

        <!-- Save status -->
        <span
          class="text-xs transition-opacity shrink-0"
          :class="{
            'text-slate-400 opacity-100': saveStatus === 'saving',
            'text-forest-600 opacity-100': saveStatus === 'saved',
            'text-red-500 opacity-100': saveStatus === 'error',
            'opacity-0': saveStatus === 'idle',
          }"
        >
          <template v-if="saveStatus === 'saving'">Saving…</template>
          <template v-else-if="saveStatus === 'saved'">Saved</template>
          <template v-else-if="saveStatus === 'error'">Save failed</template>
        </span>

        <!-- Preview toggle -->
        <button
          :title="previewMode ? 'Switch to edit mode' : 'Switch to preview mode'"
          class="flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium border transition-colors shrink-0"
          :class="
            previewMode
              ? 'border-forest-300 bg-forest-50 text-forest-700 hover:bg-forest-100'
              : 'border-parchment-300 bg-parchment-50 text-slate-600 hover:bg-parchment-100'
          "
          @click="togglePreview"
        >
          <svg v-if="previewMode" class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125" />
          </svg>
          <svg v-else class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          {{ previewMode ? "Edit" : "Preview" }}
        </button>

        <!-- Delete button -->
        <button
          class="p-1.5 rounded-lg transition-colors shrink-0"
          :class="
            confirmingDelete
              ? 'bg-red-100 text-red-600 hover:bg-red-200'
              : 'text-slate-400 hover:bg-parchment-200 hover:text-red-500'
          "
          :title="confirmingDelete ? 'Click again to confirm delete' : 'Delete note'"
          @click="handleDelete"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0"
            />
          </svg>
        </button>
      </div>

      <!-- EasyMDE -->
      <div v-show="!previewMode" class="note-editor mde-editor flex-1 min-h-0">
        <textarea ref="textareaRef" />
      </div>

      <!-- Preview -->
      <div v-if="previewMode" class="flex-1 overflow-y-auto bg-parchment-50 border border-parchment-300 rounded-xl px-8 py-6">
        <div v-if="renderedContent" class="prose prose-slate max-w-none mde-preview" v-html="renderedContent" />
        <p v-else class="text-slate-400 text-sm italic">Nothing to preview.</p>
      </div>
    </template>
  </div>
</template>

<style scoped>
.note-editor :deep(.EasyMDEContainer) {
  @apply rounded-xl overflow-hidden border border-parchment-300;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.note-editor :deep(.CodeMirror) {
  @apply bg-parchment-50 text-slate-800;
  font-family: theme("fontFamily.mono");
  font-size: 0.9rem;
  line-height: 1.7;
  padding: 1.5rem;
  flex: 1;
  height: auto;
}

.note-editor :deep(.CodeMirror-scroll) {
  min-height: 300px;
}

.note-editor :deep(.editor-toolbar) {
  @apply bg-white border-b border-parchment-300;
}

.note-editor :deep(.editor-toolbar button) {
  @apply text-slate-600;
}

.note-editor :deep(.editor-toolbar button:hover),
.note-editor :deep(.editor-toolbar button.active) {
  @apply bg-parchment-100 text-slate-800;
}

.note-editor :deep(.editor-toolbar i.separator) {
  @apply border-parchment-300;
}
</style>

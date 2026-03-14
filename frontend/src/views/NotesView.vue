<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useNotesStore } from "@/stores/notes";
import NotesSidebar from "@/components/notes/NotesSidebar.vue";
import NotesEditor from "@/components/notes/NotesEditor.vue";

const store = useNotesStore();
const mobilePanel = ref<"list" | "editor">("list");

onMounted(() => store.fetchAll());

async function handleNoteSelected(id: number) {
  await store.selectNote(id);
  mobilePanel.value = "editor";
}

async function handleNewNote() {
  await store.createNote();
  mobilePanel.value = "editor";
}

function handleBack() {
  mobilePanel.value = "list";
}
</script>

<template>
  <div class="flex gap-4 h-full min-h-0">
    <!-- Loading / error -->
    <div v-if="store.loading" class="flex-1 flex items-center justify-center text-sm text-slate-400">Loading…</div>
    <div v-else-if="store.error" class="flex-1 text-sm text-red-600 bg-red-50 rounded-xl px-4 py-3">
      {{ store.error }}
    </div>

    <template v-else>
      <!-- Left panel: folder tree + note list -->
      <div class="w-full md:w-72 md:shrink-0" :class="mobilePanel === 'editor' ? 'hidden md:block' : 'block'">
        <NotesSidebar @note-selected="handleNoteSelected" @new-note="handleNewNote" />
      </div>

      <!-- Right panel: editor -->
      <div class="flex-1 min-w-0" :class="mobilePanel === 'list' ? 'hidden md:flex md:flex-col' : 'flex flex-col'">
        <NotesEditor @back="handleBack" />
      </div>
    </template>
  </div>
</template>

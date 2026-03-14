<script setup lang="ts">
import { computed, ref } from "vue";
import { useNotesStore } from "@/stores/notes";
import NoteFolderTree from "./NoteFolderTree.vue";
import NoteFolderModal from "./NoteFolderModal.vue";
import NoteListItem from "./NoteListItem.vue";
import type { NoteFolder } from "@/types/notes";

const emit = defineEmits<{
  noteSelected: [id: number];
  newNote: [];
}>();

const store = useNotesStore();

// ── Mobile: folder vs note panel ──────────────────────────────────────────────
const mobileSidebarView = ref<"folders" | "notes">("folders");

function selectFolderAndShowNotes(folderId: number | "unfiled" | null) {
  store.selectFolder(folderId);
  mobileSidebarView.value = "notes";
}

// ── Folder modal state ────────────────────────────────────────────────────────
const folderModalShow = ref(false);
const folderModalMode = ref<"create" | "rename" | "delete">("create");
const folderModalTarget = ref<NoteFolder | null>(null);
const folderModalParent = ref<NoteFolder | null>(null);

function openCreateFolder(parentFolder: NoteFolder | null = null) {
  folderModalMode.value = "create";
  folderModalTarget.value = null;
  folderModalParent.value = parentFolder;
  folderModalShow.value = true;
}

function openRenameFolder(folder: NoteFolder) {
  folderModalMode.value = "rename";
  folderModalTarget.value = folder;
  folderModalParent.value = null;
  folderModalShow.value = true;
}

function openDeleteFolder(folder: NoteFolder) {
  folderModalMode.value = "delete";
  folderModalTarget.value = folder;
  folderModalParent.value = null;
  folderModalShow.value = true;
}

// ── Selected folder label ─────────────────────────────────────────────────────
const selectedFolderLabel = computed(() => {
  if (store.selectedFolder === null) return "All Notes";
  if (store.selectedFolder === "unfiled") return "Unfiled";
  const folder = store.flatFolders.find((f) => f.id === store.selectedFolder);
  return folder?.name ?? "Notes";
});

async function handleNewNote() {
  emit("newNote");
}
</script>

<template>
  <div class="flex flex-col h-full bg-forest-800 text-parchment-100 rounded-xl overflow-hidden">
    <!-- ── FOLDER PANEL ───────────────────────────────────────────────────── -->
    <div
      :class="['flex flex-col', mobileSidebarView === 'notes' ? 'hidden md:flex' : 'flex', 'md:flex']"
      style="flex: 0 0 auto"
    >
      <!-- Folder section header -->
      <div class="flex items-center justify-between px-3 pt-3 pb-1">
        <span class="text-xs font-semibold uppercase tracking-widest text-parchment-400">Folders</span>
        <button
          class="p-1 rounded text-parchment-400 hover:bg-forest-700 hover:text-parchment-100 transition-colors"
          title="New folder"
          @click="openCreateFolder(null)"
        >
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
        </button>
      </div>

      <!-- Virtual "All Notes" row -->
      <button
        class="flex items-center gap-2 px-3 py-1.5 text-xs transition-colors w-full text-left"
        :class="
          store.selectedFolder === null
            ? 'bg-forest-700 text-parchment-50'
            : 'text-parchment-300 hover:bg-forest-700 hover:text-parchment-100'
        "
        @click="selectFolderAndShowNotes(null)"
      >
        <svg
          class="w-3.5 h-3.5 shrink-0 opacity-70"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
          />
        </svg>
        All Notes
      </button>

      <!-- Virtual "Unfiled" row -->
      <button
        class="flex items-center gap-2 px-3 py-1.5 text-xs transition-colors w-full text-left"
        :class="
          store.selectedFolder === 'unfiled'
            ? 'bg-forest-700 text-parchment-50'
            : 'text-parchment-300 hover:bg-forest-700 hover:text-parchment-100'
        "
        @click="selectFolderAndShowNotes('unfiled')"
      >
        <svg
          class="w-3.5 h-3.5 shrink-0 opacity-70"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M8.25 7.5V6.108c0-1.135.845-2.098 1.976-2.192.373-.03.748-.057 1.123-.08M15.75 18H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08M15.75 18.75v-1.875a3.375 3.375 0 00-3.375-3.375h-1.5a1.125 1.125 0 01-1.125-1.125v-1.5A3.375 3.375 0 006.375 7.5H5.25m11.9-3.664A2.251 2.251 0 0015 2.25h-1.5a2.251 2.251 0 00-2.15 1.586m5.8 0c.065.21.1.433.1.664v.75h-6V4.5c0-.231.035-.454.1-.664M6.75 7.5H4.875c-.621 0-1.125.504-1.125 1.125v12c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V16.5a9 9 0 00-9-9z"
          />
        </svg>
        Unfiled
        <span v-if="store.unfiledCount > 0" class="ml-auto text-xs opacity-60">{{ store.unfiledCount }}</span>
      </button>

      <!-- Folder tree -->
      <div class="px-1 pb-2 max-h-48 md:max-h-none overflow-y-auto">
        <NoteFolderTree
          :folders="store.folderTree"
          @rename="openRenameFolder"
          @delete="openDeleteFolder"
          @add-child="openCreateFolder"
        />
        <p v-if="store.folderTree.length === 0" class="text-xs text-parchment-500 px-2 py-1 italic">No folders yet</p>
      </div>

      <!-- Divider -->
      <div class="border-t border-forest-700 mx-3" />
    </div>

    <!-- ── NOTE LIST PANEL ────────────────────────────────────────────────── -->
    <div
      :class="['flex flex-col flex-1 min-h-0', mobileSidebarView === 'folders' ? 'hidden md:flex' : 'flex', 'md:flex']"
    >
      <!-- Note list header -->
      <div class="flex items-center justify-between px-3 pt-3 pb-2 shrink-0">
        <!-- Mobile: back to folders -->
        <button
          class="md:hidden p-1 rounded text-parchment-400 hover:bg-forest-700 transition-colors mr-1"
          @click="mobileSidebarView = 'folders'"
        >
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <span class="text-xs font-semibold uppercase tracking-widest text-parchment-400 flex-1 truncate">
          {{ selectedFolderLabel }}
        </span>
        <button
          class="p-1 rounded text-parchment-400 hover:bg-forest-700 hover:text-parchment-100 transition-colors"
          title="New note"
          @click="handleNewNote"
        >
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
        </button>
      </div>

      <!-- Note list -->
      <div class="flex-1 overflow-y-auto px-2 pb-3 space-y-0.5">
        <NoteListItem
          v-for="note in store.noteList"
          :key="note.id"
          :note="note"
          :active="store.activeNote?.id === note.id"
          @click="emit('noteSelected', note.id)"
        />
        <p v-if="store.noteList.length === 0" class="text-xs text-parchment-500 px-2 py-3 italic text-center">
          No notes here yet
        </p>
      </div>
    </div>
  </div>

  <!-- Folder modal -->
  <NoteFolderModal
    :show="folderModalShow"
    :mode="folderModalMode"
    :folder="folderModalTarget"
    :parent-folder="folderModalParent"
    @close="folderModalShow = false"
  />
</template>

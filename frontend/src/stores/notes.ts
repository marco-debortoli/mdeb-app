import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { noteApi, noteFolderApi } from "@/api/notes";
import type { FolderSelection, Note, NoteFolder, NoteSummary } from "@/types/notes";

export const useNotesStore = defineStore("notes", () => {
  // ── State ───────────────────────────────────────────────────────────────────
  const folderTree = ref<NoteFolder[]>([]);
  const noteList = ref<NoteSummary[]>([]);
  const activeNote = ref<Note | null>(null);
  const selectedFolder = ref<FolderSelection>(null);
  const unfiledCount = ref(0);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // ── Computed ────────────────────────────────────────────────────────────────
  const flatFolders = computed(() => {
    const result: NoteFolder[] = [];
    function walk(nodes: NoteFolder[]) {
      for (const n of nodes) {
        result.push(n);
        walk(n.children);
      }
    }
    walk(folderTree.value);
    return result;
  });

  // ── Fetchers ────────────────────────────────────────────────────────────────
  async function fetchFolderTree() {
    const [tree, unfiled] = await Promise.all([noteFolderApi.tree(), noteFolderApi.unfiledCount()]);
    folderTree.value = tree;
    unfiledCount.value = unfiled.count;
  }

  async function fetchNotes() {
    const fid = selectedFolder.value;
    noteList.value = fid === null ? await noteApi.list() : await noteApi.list(fid);
  }

  async function fetchAll() {
    loading.value = true;
    error.value = null;
    try {
      await Promise.all([fetchFolderTree(), fetchNotes()]);
    } catch (e) {
      error.value = String(e);
    } finally {
      loading.value = false;
    }
  }

  // ── Folder actions ──────────────────────────────────────────────────────────
  async function selectFolder(folder: FolderSelection) {
    selectedFolder.value = folder;
    activeNote.value = null;
    await fetchNotes();
  }

  async function createFolder(name: string, parentId: number | null = null) {
    await noteFolderApi.create({ name, parent_id: parentId });
    await fetchFolderTree();
  }

  async function renameFolder(id: number, name: string) {
    await noteFolderApi.update(id, { name });
    await fetchFolderTree();
  }

  async function deleteFolder(id: number) {
    await noteFolderApi.delete(id);
    if (selectedFolder.value === id) selectedFolder.value = null;
    await Promise.all([fetchFolderTree(), fetchNotes()]);
  }

  // ── Note actions ────────────────────────────────────────────────────────────
  async function createNote(): Promise<Note> {
    const folderId = typeof selectedFolder.value === "number" ? selectedFolder.value : null;
    const note = await noteApi.create({ title: "Untitled", content: "", folder_id: folderId });
    await fetchNotes();
    activeNote.value = note;
    return note;
  }

  async function selectNote(id: number) {
    activeNote.value = await noteApi.get(id);
  }

  async function saveNote(id: number, data: { title?: string; content?: string }): Promise<void> {
    const saved = await noteApi.update(id, data);
    if (activeNote.value?.id === id) {
      activeNote.value = saved;
    }
    const idx = noteList.value.findIndex((n) => n.id === id);
    if (idx !== -1) {
      noteList.value[idx] = { ...noteList.value[idx], ...saved };
    }
  }

  async function deleteNote(id: number) {
    await noteApi.delete(id);
    if (activeNote.value?.id === id) activeNote.value = null;
    noteList.value = noteList.value.filter((n) => n.id !== id);
  }

  return {
    folderTree,
    noteList,
    activeNote,
    selectedFolder,
    unfiledCount,
    loading,
    error,
    flatFolders,
    fetchAll,
    fetchFolderTree,
    fetchNotes,
    selectFolder,
    createFolder,
    renameFolder,
    deleteFolder,
    createNote,
    selectNote,
    saveNote,
    deleteNote,
  };
});

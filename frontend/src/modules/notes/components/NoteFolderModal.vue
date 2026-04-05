<script setup lang="ts">
import { ref, watch, computed } from "vue";
import { useNotesStore } from "@/modules/notes/store";
import type { NoteFolder } from "@/modules/notes/types";
import BaseModal from "@/shared/components/BaseModal.vue";

const props = defineProps<{
  open: boolean;
  mode: "create" | "rename" | "delete";
  folder?: NoteFolder | null;
  parentFolder?: NoteFolder | null; // for create mode — the parent to nest under
}>();

const emit = defineEmits<{
  close: [];
}>();

const store = useNotesStore();
const nameInput = ref("");
const saving = ref(false);
const errorMsg = ref("");

const modalTitle = computed(() => {
  if (props.mode === "create") return props.parentFolder ? `New Folder in "${props.parentFolder.name}"` : "New Folder";
  if (props.mode === "rename") return "Rename Folder";
  return "Delete Folder";
});

watch(
  () => props.open,
  (val) => {
    if (val) {
      nameInput.value = props.mode === "rename" ? (props.folder?.name ?? "") : "";
      errorMsg.value = "";
      saving.value = false;
    }
  },
);

async function confirm() {
  saving.value = true;
  errorMsg.value = "";
  try {
    if (props.mode === "create") {
      const parentId = props.parentFolder?.id ?? null;
      await store.createFolder(nameInput.value.trim(), parentId);
    } else if (props.mode === "rename" && props.folder) {
      await store.renameFolder(props.folder.id, nameInput.value.trim());
    } else if (props.mode === "delete" && props.folder) {
      await store.deleteFolder(props.folder.id);
    }
    emit("close");
  } catch (e) {
    errorMsg.value = String(e);
  } finally {
    saving.value = false;
  }
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === "Enter" && props.mode !== "delete") confirm();
  if (e.key === "Escape") emit("close");
}
</script>

<template>
  <BaseModal :open="open" :title="modalTitle" :mobile="true" max-width="sm:max-w-sm" @close="emit('close')">
    <!-- Delete warning -->
    <template v-if="mode === 'delete' && folder">
      <p class="text-sm text-slate-600">
        Delete <span class="font-semibold">"{{ folder.name }}"</span>?
      </p>
      <p class="text-sm text-slate-500">
        Any notes and subfolders inside will be moved to the parent folder (or "Unfiled" if this is a root folder).
      </p>
    </template>

    <!-- Name input for create/rename -->
    <template v-else>
      <input
        v-model="nameInput"
        type="text"
        placeholder="Folder name"
        class="w-full border border-parchment-300 rounded-lg px-3 py-2 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-forest-400"
        autofocus
        @keydown="onKeydown"
      />
    </template>

    <p v-if="errorMsg" class="text-xs text-red-600">{{ errorMsg }}</p>

    <template #footer-right>
      <div class="flex gap-2">
        <button
          class="px-4 py-2 text-sm rounded-lg text-slate-600 hover:bg-parchment-200 transition-colors"
          @click="emit('close')"
        >
          Cancel
        </button>
        <button
          :disabled="saving || (mode !== 'delete' && !nameInput.trim())"
          class="px-4 py-2 text-sm rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          :class="mode === 'delete' ? 'bg-red-600 text-white hover:bg-red-700' : 'bg-forest-600 text-white hover:bg-forest-700'"
          @click="confirm"
        >
          <template v-if="saving">Saving…</template>
          <template v-else-if="mode === 'delete'">Delete</template>
          <template v-else-if="mode === 'create'">Create</template>
          <template v-else>Rename</template>
        </button>
      </div>
    </template>
  </BaseModal>
</template>

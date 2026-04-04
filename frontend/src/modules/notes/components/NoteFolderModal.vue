<script setup lang="ts">
import { ref, watch } from "vue";
import { useNotesStore } from "@/modules/notes/store";
import type { NoteFolder } from "@/modules/notes/types";

const props = defineProps<{
  show: boolean;
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

watch(
  () => props.show,
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
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-150"
      leave-active-class="transition-opacity duration-150"
      enter-from-class="opacity-0"
      leave-to-class="opacity-0"
    >
      <div
        v-if="show"
        class="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/50 px-0 sm:px-4"
        @click.self="emit('close')"
      >
        <div class="bg-white rounded-t-xl sm:rounded-xl shadow-xl w-full sm:max-w-sm p-5">
          <!-- Header -->
          <h3 class="text-base font-semibold text-slate-800 mb-4">
            <template v-if="mode === 'create'">
              New Folder{{ parentFolder ? ` in "${parentFolder.name}"` : "" }}
            </template>
            <template v-else-if="mode === 'rename'">Rename Folder</template>
            <template v-else>Delete Folder</template>
          </h3>

          <!-- Delete warning -->
          <template v-if="mode === 'delete' && folder">
            <p class="text-sm text-slate-600 mb-2">
              Delete <span class="font-semibold">"{{ folder.name }}"</span>?
            </p>
            <p class="text-sm text-slate-500 mb-4">
              Any notes and subfolders inside will be moved to the parent folder (or "Unfiled" if this is a root
              folder).
            </p>
          </template>

          <!-- Name input for create/rename -->
          <template v-else>
            <input
              v-model="nameInput"
              type="text"
              placeholder="Folder name"
              class="w-full border border-parchment-300 rounded-lg px-3 py-2 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-forest-400 mb-4"
              autofocus
              @keydown="onKeydown"
            />
          </template>

          <p v-if="errorMsg" class="text-xs text-red-600 mb-3">{{ errorMsg }}</p>

          <!-- Actions -->
          <div class="flex justify-end gap-2">
            <button
              class="px-4 py-2 text-sm rounded-lg text-slate-600 hover:bg-parchment-100 transition-colors"
              @click="emit('close')"
            >
              Cancel
            </button>
            <button
              :disabled="saving || (mode !== 'delete' && !nameInput.trim())"
              class="px-4 py-2 text-sm rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              :class="
                mode === 'delete'
                  ? 'bg-red-600 text-white hover:bg-red-700'
                  : 'bg-forest-600 text-white hover:bg-forest-700'
              "
              @click="confirm"
            >
              <template v-if="saving">Saving…</template>
              <template v-else-if="mode === 'delete'">Delete</template>
              <template v-else-if="mode === 'create'">Create</template>
              <template v-else>Rename</template>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useNotesStore } from "@/modules/notes/store";
import type { NoteFolder } from "@/modules/notes/types";

const props = defineProps<{
  folders: NoteFolder[];
  depth?: number;
}>();

const emit = defineEmits<{
  select: [id: number];
  rename: [folder: NoteFolder];
  delete: [folder: NoteFolder];
  addChild: [folder: NoteFolder];
}>();

const store = useNotesStore();
const expanded = ref<Set<number>>(new Set());

function toggleExpand(id: number) {
  const next = new Set(expanded.value);
  if (next.has(id)) next.delete(id);
  else next.add(id);
  expanded.value = next;
}

const depth = props.depth ?? 0;
</script>

<template>
  <div>
    <div v-for="folder in folders" :key="folder.id">
      <!-- Folder row -->
      <div
        class="group flex items-center gap-1 rounded-lg pr-1 transition-colors cursor-pointer"
        :class="
          store.selectedFolder === folder.id
            ? 'bg-forest-700 text-parchment-50'
            : 'text-parchment-300 hover:bg-forest-700 hover:text-parchment-100'
        "
        :style="{ paddingLeft: `${depth * 12 + 8}px` }"
        @click="emit('select', folder.id)"
      >
        <!-- Expand/collapse toggle -->
        <button v-if="folder.children.length > 0" class="p-0.5 shrink-0" @click.stop="toggleExpand(folder.id)">
          <svg
            :class="['w-3 h-3 transition-transform', expanded.has(folder.id) ? 'rotate-90' : '']"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
          </svg>
        </button>
        <span v-else class="w-4 shrink-0" />

        <!-- Folder icon -->
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
            d="M2.25 12.75V12A2.25 2.25 0 014.5 9.75h15A2.25 2.25 0 0121.75 12v.75m-8.69-6.44l-2.12-2.12a1.5 1.5 0 00-1.061-.44H4.5A2.25 2.25 0 002.25 6v12a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9a2.25 2.25 0 00-2.25-2.25h-5.379a1.5 1.5 0 01-1.06-.44z"
          />
        </svg>

        <!-- Folder name -->
        <span class="flex-1 text-xs py-1.5 truncate">{{ folder.name }}</span>

        <!-- Note count badge -->
        <span
          v-if="folder.note_count > 0"
          class="text-xs px-1.5 py-0.5 rounded-full shrink-0 opacity-60"
          :class="store.selectedFolder === folder.id ? 'bg-forest-600' : 'bg-forest-800'"
          >{{ folder.note_count }}</span
        >

        <!-- Action buttons (hover) -->
        <div class="hidden group-hover:flex items-center gap-0.5 shrink-0">
          <button
            class="p-1 rounded hover:bg-forest-600 transition-colors"
            title="Add subfolder"
            @click.stop="emit('addChild', folder)"
          >
            <svg class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
            </svg>
          </button>
          <button
            class="p-1 rounded hover:bg-forest-600 transition-colors"
            title="Rename folder"
            @click.stop="emit('rename', folder)"
          >
            <svg class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L6.832 19.82a4.5 4.5 0 01-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 011.13-1.897L16.863 4.487zm0 0L19.5 7.125"
              />
            </svg>
          </button>
          <button
            class="p-1 rounded hover:bg-red-700 transition-colors"
            title="Delete folder"
            @click.stop="emit('delete', folder)"
          >
            <svg class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0"
              />
            </svg>
          </button>
        </div>
      </div>

      <!-- Children (recursive) -->
      <NoteFolderTree
        v-if="expanded.has(folder.id) && folder.children.length > 0"
        :folders="folder.children"
        :depth="depth + 1"
        @select="emit('select', $event)"
        @rename="emit('rename', $event)"
        @delete="emit('delete', $event)"
        @add-child="emit('addChild', $event)"
      />
    </div>
  </div>
</template>

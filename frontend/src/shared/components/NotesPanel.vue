<script setup lang="ts">
interface Note {
  id: number;
  content: string;
  created_at: string;
}

defineProps<{
  notes: Note[];
  loading?: boolean;
  adding?: boolean;
  modelValue: string;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: string): void;
  (e: "add"): void;
  (e: "delete", id: number): void;
}>();

function formatDate(d: string): string {
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
  <div class="flex flex-col h-full min-h-0">
    <!-- Notes list -->
    <div class="flex-1 overflow-y-auto px-4 py-3 space-y-2">
      <div v-if="loading" class="text-xs text-slate-400 py-2">Loading notes…</div>
      <template v-else>
        <p v-if="!notes.length" class="text-xs text-slate-400 py-2">No notes yet.</p>
        <div
          v-for="note in notes"
          :key="note.id"
          class="group flex flex-col bg-parchment-100 rounded-lg px-3 py-2"
        >
          <div class="flex items-start justify-between gap-2">
            <p class="flex-1 text-sm text-slate-700 whitespace-pre-wrap break-words">{{ note.content }}</p>
            <button
              class="shrink-0 p-0.5 rounded text-slate-300 hover:text-red-500 hover:bg-red-50 transition-colors opacity-0 group-hover:opacity-100 focus:opacity-100"
              title="Delete note"
              @click="emit('delete', note.id)"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <p class="text-xs font-mono text-slate-400 mt-1">{{ formatDate(note.created_at) }}</p>
        </div>
      </template>
    </div>

    <!-- Input -->
    <div class="shrink-0 border-t border-parchment-200 px-4 py-3 space-y-2">
      <input
        :value="modelValue"
        type="text"
        placeholder="Add a note…"
        class="w-full text-sm rounded-lg border border-parchment-300 bg-white px-3 py-2 text-slate-800 placeholder-slate-400 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
        @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        @keydown.enter="emit('add')"
      />
      <button
        :disabled="!modelValue.trim() || adding"
        class="w-full py-1.5 rounded-lg text-sm font-medium bg-forest-600 text-parchment-50 hover:bg-forest-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        @click="emit('add')"
      >
        {{ adding ? "Adding…" : "Add note" }}
      </button>
    </div>
  </div>
</template>

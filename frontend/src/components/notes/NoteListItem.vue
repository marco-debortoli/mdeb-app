<script setup lang="ts">
import type { NoteSummary } from "@/types/notes";

defineProps<{
  note: NoteSummary;
  active: boolean;
}>();

function formatDate(iso: string): string {
  const date = new Date(iso);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMin = Math.floor(diffMs / 60000);
  const diffHr = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHr / 24);

  if (diffMin < 1) return "just now";
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHr < 24) return `${diffHr}h ago`;
  if (diffDay < 7) return `${diffDay}d ago`;
  return date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}
</script>

<template>
  <button
    class="w-full text-left px-3 py-2.5 rounded-lg transition-colors border-l-2 group"
    :class="
      active
        ? 'bg-parchment-100 border-forest-500 text-slate-800'
        : 'border-transparent hover:bg-forest-700 text-parchment-200'
    "
  >
    <div class="text-sm font-medium truncate leading-snug">
      {{ note.title || "Untitled" }}
    </div>
    <div class="text-xs mt-0.5" :class="active ? 'text-slate-400' : 'text-parchment-400'">
      {{ formatDate(note.updated_at) }}
    </div>
  </button>
</template>

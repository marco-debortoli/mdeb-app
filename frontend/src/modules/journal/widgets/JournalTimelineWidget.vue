<script setup lang="ts">
import { computed } from "vue";
import { marked } from "marked";
import type { JournalEntry, DayRating } from "@/modules/journal/types";

const props = defineProps<{
  journal: JournalEntry | null;
  rating: DayRating | null;
}>();

const renderedJournal = computed(() => {
  if (!props.journal?.content) return "";
  return marked(props.journal.content) as string;
});
</script>

<template>
  <section class="bg-white rounded-lg border border-parchment-200 overflow-hidden">
    <div class="flex items-center gap-2 px-4 py-2.5 bg-forest-50 border-b border-parchment-200">
      <span class="w-2.5 h-2.5 rounded-full bg-forest-500 shrink-0"></span>
      <h3 class="text-sm font-semibold text-forest-800 uppercase tracking-wider">Journal</h3>
      <!-- Star rating -->
      <div v-if="rating" class="ml-auto flex gap-0.5">
        <svg
          v-for="n in 5"
          :key="n"
          class="w-4 h-4"
          :class="n <= rating.rating ? 'text-earth-500' : 'text-parchment-300'"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
          />
        </svg>
      </div>
    </div>
    <div v-if="journal" class="px-4 py-3">
      <div
        class="prose prose-sm max-w-none text-slate-700 prose-headings:text-slate-800 prose-a:text-forest-600"
        v-html="renderedJournal"
      />
    </div>
    <div v-else class="px-4 py-4 text-sm text-parchment-400 italic">No journal entry for this day.</div>
  </section>
</template>

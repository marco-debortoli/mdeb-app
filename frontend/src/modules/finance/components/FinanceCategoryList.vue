<script setup lang="ts">
import { ref } from "vue";
import type { CategoriesByType } from "@/modules/finance/types";
import { formatAmount } from "@/modules/finance/utils";

defineProps<{
  summary: CategoriesByType;
}>();

const expanded = ref<Record<string, boolean>>({
  credit: false,
  debit: false,
  transfer: false,
});

const groups = [
  { type: "debit" as const, label: "Debit" },
  { type: "credit" as const, label: "Credit" },
  { type: "transfer" as const, label: "Transfer" },
];
</script>

<template>
  <div class="bg-parchment-50 border border-parchment-300 rounded-xl overflow-hidden h-full flex flex-col">
    <div class="px-4 py-3 border-b border-parchment-200 shrink-0">
      <span class="text-xs font-semibold uppercase tracking-widest text-slate-500">Categories</span>
    </div>

    <div class="divide-y divide-parchment-200 overflow-y-auto flex-1 min-h-0">
      <div v-for="group in groups" :key="group.type">
        <!-- Group header (toggle) -->
        <button
          class="w-full flex items-center justify-between px-4 py-2.5 hover:bg-parchment-100 transition-colors"
          @click="expanded[group.type] = !expanded[group.type]"
        >
          <span
            class="text-xs font-semibold uppercase tracking-widest"
            :class="
              group.type === 'credit' ? 'text-earth-600' : group.type === 'debit' ? 'text-forest-600' : 'text-slate-500'
            "
          >
            {{ group.label }}
          </span>
          <div class="flex items-center gap-2">
            <span v-if="summary[group.type].length" class="text-xs font-mono text-slate-500">
              {{ formatAmount(summary[group.type].reduce((s, i) => s + parseFloat(i.total), 0)) }}
            </span>
            <svg
              class="w-3.5 h-3.5 text-slate-400 transition-transform duration-150"
              :class="expanded[group.type] ? 'rotate-180' : ''"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
            </svg>
          </div>
        </button>

        <!-- Group rows -->
        <div v-if="expanded[group.type]">
          <div
            v-for="item in summary[group.type]"
            :key="item.category.id"
            class="flex items-center gap-2 px-4 py-2 border-t border-parchment-100"
          >
            <span class="flex-1 text-xs text-slate-700 truncate">{{ item.category.name }}</span>
            <span class="text-xs font-mono text-slate-600 shrink-0">{{ formatAmount(item.total) }}</span>
          </div>

          <p v-if="!summary[group.type].length" class="px-4 py-2 text-xs text-slate-400 border-t border-parchment-100">
            No {{ group.label.toLowerCase() }} categories this month.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { FinanceCategoryType } from "@/types/finance";

defineProps<{
  type: FinanceCategoryType;
  name: string;
}>();

const typeColors: Record<FinanceCategoryType, string> = {
  credit: "bg-earth-100 text-earth-700",
  debit: "bg-forest-100 text-forest-700",
  transfer: "bg-slate-100 text-slate-600",
};
</script>

<template>
  <span class="inline-block text-xs font-medium px-2 py-0.5 rounded-full" :class="typeColors[type]">
    {{ name }}
  </span>
</template>

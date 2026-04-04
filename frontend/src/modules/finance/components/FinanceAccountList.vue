<script setup lang="ts">
import type { AccountMonthlySummary, FinanceAccount } from "@/modules/finance/types";
import FinanceAccountItem from "@/modules/finance/components/FinanceAccountItem.vue";

defineProps<{
  accounts: AccountMonthlySummary[];
}>();

const emit = defineEmits<{
  create: [];
  edit: [account: FinanceAccount];
}>();
</script>

<template>
  <div class="bg-parchment-50 border border-parchment-300 rounded-xl overflow-hidden h-full flex flex-col">
    <div class="flex items-center justify-between px-4 py-3 border-b border-parchment-200 shrink-0">
      <span class="text-xs font-semibold uppercase tracking-widest text-slate-500">Accounts</span>
      <button
        class="text-xs font-medium text-forest-600 hover:text-forest-700 transition-colors"
        @click="emit('create')"
      >
        + New
      </button>
    </div>

    <div v-if="accounts.length" class="divide-y divide-parchment-200 overflow-y-auto flex-1 min-h-0">
      <FinanceAccountItem
        v-for="item in accounts"
        :key="item.account.id"
        :item="item"
        @edit="emit('edit', $event)"
      />
    </div>

    <div v-else class="px-4 py-6 text-sm text-slate-400 text-center">
      No accounts yet.
      <button class="ml-1 text-forest-600 hover:underline" @click="emit('create')">Add one.</button>
    </div>
  </div>
</template>

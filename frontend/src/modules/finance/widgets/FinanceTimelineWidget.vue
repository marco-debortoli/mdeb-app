<script setup lang="ts">
import type { Transaction } from "@/modules/finance/types";

defineProps<{
  transactions: Transaction[];
}>();

function formatAmount(amount: string, type: string): string {
  const n = parseFloat(amount);
  const formatted = Math.abs(n).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  switch (type) {
    case "credit":
      return `-$${formatted}`;
    case "transfer":
      return `$${formatted}`;
    default:
      return `+$${formatted}`;
  }
}

function amountClass(type: string): string {
  switch (type) {
    case "debit":
      return "text-forest-600 font-medium";
    case "credit":
      return "text-red-600 font-medium";
    default:
      return "font-medium";
  }
}
</script>

<template>
  <section class="bg-white rounded-lg border border-parchment-200 overflow-hidden">
    <div class="flex items-center gap-2 px-4 py-2.5 bg-earth-50 border-b border-parchment-200">
      <span class="w-2.5 h-2.5 rounded-full bg-earth-500 shrink-0"></span>
      <h3 class="text-sm font-semibold text-earth-800 uppercase tracking-wider">Finance</h3>
      <span v-if="transactions.length" class="ml-auto text-xs text-parchment-500">
        {{ transactions.length }} transaction{{ transactions.length !== 1 ? "s" : "" }}
      </span>
    </div>
    <div v-if="transactions.length">
      <div
        v-for="tx in transactions"
        :key="tx.id"
        class="flex items-center gap-3 px-4 py-2.5 border-b border-parchment-100 last:border-b-0"
      >
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-slate-800 truncate">
            {{ tx.merchant?.name ?? tx.category.name }}
          </p>
          <p class="text-xs text-parchment-500 truncate">
            <template v-if="tx.account">{{ tx.account.name }}</template>
            <span v-else class="italic">External</span>
            <span v-if="tx.to_account"> → {{ tx.to_account.name }}</span>
            · {{ tx.category.name }}
          </p>
        </div>
        <span :class="amountClass(tx.category.type)">
          {{ formatAmount(tx.amount, tx.category.type) }}
        </span>
      </div>
    </div>
    <div v-else class="px-4 py-4 text-sm text-parchment-400 italic">No transactions for this day.</div>
  </section>
</template>

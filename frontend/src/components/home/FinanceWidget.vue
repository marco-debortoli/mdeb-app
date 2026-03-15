<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useFinanceStore } from "@/stores/finance";
import { formatAmount } from "@/utils/finance";

const store = useFinanceStore();

const monthLabel = computed(() =>
  new Date(store.currentYear, store.currentMonth - 1).toLocaleDateString("en-US", { month: "long", year: "numeric" }),
);

const totalTransactions = computed(() => store.summary?.transactions.length ?? 0);
const monthlyProfit = computed(() => store.summary?.monthly_profit ?? "0.00");
const profitIsPositive = computed(() => parseFloat(monthlyProfit.value) >= 0);

onMounted(() => store.fetchSummary());
</script>

<template>
  <section
    class="bg-parchment-50 border border-parchment-300 rounded-xl overflow-hidden shadow-sm flex flex-col h-full"
  >
    <!-- Header -->
    <div class="flex items-center justify-between px-4 py-3 border-b border-parchment-200 shrink-0">
      <div class="flex items-center gap-2">
        <div class="w-7 h-7 rounded-md bg-slate-600 flex items-center justify-center shrink-0">
          <svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.5" class="w-4 h-4">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <h2 class="font-semibold text-slate-800 text-sm">Finance</h2>
        <span class="text-xs text-slate-400">{{ monthLabel }}</span>
      </div>
      <RouterLink to="/finance" class="text-xs text-forest-600 hover:text-forest-700 transition-colors"
        >View all →</RouterLink
      >
    </div>

    <!-- Stats -->
    <div v-if="store.loading" class="flex-1 flex items-center justify-center text-sm text-slate-400">Loading…</div>
    <div v-else-if="!store.summary" class="flex-1 flex items-center justify-center text-sm text-slate-400 italic">
      No data for this month.
    </div>
    <div v-else class="flex-1 flex flex-col px-5 py-5 gap-5">
      <div class="flex items-center justify-between">
        <span class="text-sm text-slate-500">Monthly Profit</span>
        <span class="text-2xl font-semibold font-mono" :class="profitIsPositive ? 'text-forest-600' : 'text-red-600'">{{
          formatAmount(monthlyProfit)
        }}</span>
      </div>
      <div class="h-px bg-parchment-200" />
      <div class="flex items-center justify-between">
        <span class="text-sm text-slate-500">Transactions</span>
        <span class="text-2xl font-semibold text-slate-700">{{ totalTransactions }}</span>
      </div>
    </div>
  </section>
</template>

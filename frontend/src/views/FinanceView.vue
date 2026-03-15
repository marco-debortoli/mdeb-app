<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useFinanceStore } from "@/stores/finance";
import type { FinanceAccount, Transaction } from "@/types/finance";
import { formatAmount } from "@/utils/finance";
import FinanceTransactionTable from "@/components/finance/FinanceTransactionTable.vue";
import FinanceAccountList from "@/components/finance/FinanceAccountList.vue";
import FinanceCategoryList from "@/components/finance/FinanceCategoryList.vue";
import FinanceTransactionModal from "@/components/finance/FinanceTransactionModal.vue";
import FinanceAccountModal from "@/components/finance/FinanceAccountModal.vue";
import FinanceCategoryModal from "@/components/finance/FinanceCategoryModal.vue";
import FinanceMerchantModal from "@/components/finance/FinanceMerchantModal.vue";
import FinanceMonthPicker from "@/components/finance/FinanceMonthPicker.vue";

const store = useFinanceStore();

const monthLabel = computed(() => {
  const MONTH_NAMES = ["January","February","March","April","May","June","July","August","September","October","November","December"];
  return `${MONTH_NAMES[store.currentMonth - 1]} ${store.currentYear}`;
});

onMounted(() => store.fetchAll());

// ── Transaction modal ─────────────────────────────────────────────────────────
const txnModalOpen = ref(false);
const txnModalMode = ref<"create" | "edit">("create");
const editingTxn = ref<Transaction | null>(null);

function openCreateTxn() {
  txnModalMode.value = "create";
  editingTxn.value = null;
  txnModalOpen.value = true;
}

function openEditTxn(txn: Transaction) {
  txnModalMode.value = "edit";
  editingTxn.value = txn;
  txnModalOpen.value = true;
}

// ── Account modal ─────────────────────────────────────────────────────────────
const accModalOpen = ref(false);
const accModalMode = ref<"create" | "edit">("create");
const editingAcc = ref<FinanceAccount | null>(null);

function openCreateAcc() {
  accModalMode.value = "create";
  editingAcc.value = null;
  accModalOpen.value = true;
}

function openEditAcc(acc: FinanceAccount) {
  accModalMode.value = "edit";
  editingAcc.value = acc;
  accModalOpen.value = true;
}

// ── Category modal ────────────────────────────────────────────────────────────
const catModalOpen = ref(false);

// ── Merchant modal ────────────────────────────────────────────────────────────
const merchantModalOpen = ref(false);

</script>

<template>
  <div class="max-w-7xl mx-auto">
    <!-- Page header: month nav + actions -->
    <div class="flex flex-wrap items-center justify-between gap-4 mb-4">
      <div class="flex items-center gap-3">
        <button
          class="p-1.5 rounded-lg text-slate-500 hover:bg-parchment-200 hover:text-slate-700 transition-colors"
          title="Previous month"
          @click="store.prevMonth()"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
          </svg>
        </button>
        <FinanceMonthPicker
          :current-year="store.currentYear"
          :current-month="store.currentMonth"
          @select="(y, m) => store.goToMonth(y, m)"
        />
        <button
          class="p-1.5 rounded-lg text-slate-500 hover:bg-parchment-200 hover:text-slate-700 transition-colors"
          title="Next month"
          @click="store.nextMonth()"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
          </svg>
        </button>
      </div>

      <div class="flex gap-2">
        <button
          class="text-xs font-medium text-slate-500 hover:text-slate-700 px-2 py-1 rounded hover:bg-parchment-200 transition-colors"
          @click="catModalOpen = true"
        >
          Categories
        </button>
        <button
          class="text-xs font-medium text-slate-500 hover:text-slate-700 px-2 py-1 rounded hover:bg-parchment-200 transition-colors"
          @click="merchantModalOpen = true"
        >
          Merchants
        </button>
      </div>
    </div>

    <!-- Loading / error -->
    <div v-if="store.loading" class="text-sm text-slate-400 py-8 text-center">Loading…</div>
    <div v-else-if="store.error" class="text-sm text-red-600 bg-red-50 rounded-xl px-4 py-3 mb-4">
      {{ store.error }}
    </div>

    <!-- Main content: transactions (left) + sidebar (right) -->
    <div v-else class="grid gap-4 items-start grid-cols-1 md:grid-cols-[1fr_272px]">
      <FinanceTransactionTable
        :transactions="store.summary?.transactions ?? []"
        :month-label="monthLabel"
        :current-month="store.currentMonth"
        @create="openCreateTxn"
        @edit="openEditTxn"
      />

      <div class="flex flex-col gap-4">
        <!-- Monthly profit -->
        <div
          v-if="store.summary"
          class="flex items-center justify-between px-4 py-2.5 rounded-xl border font-mono shrink-0"
          :class="
            parseFloat(store.summary.monthly_profit) >= 0
              ? 'bg-forest-50 border-forest-200'
              : 'bg-red-50 border-red-200'
          "
        >
          <span class="text-xs font-sans text-slate-500 uppercase tracking-widest">Profit</span>
          <span
            class="text-sm font-semibold"
            :class="parseFloat(store.summary.monthly_profit) >= 0 ? 'text-forest-700' : 'text-red-600'"
          >
            {{ formatAmount(store.summary.monthly_profit) }}
          </span>
        </div>

        <!-- Accounts + Categories: fixed height on desktop, natural height on mobile -->
        <div class="flex flex-col gap-4 md:h-[600px]">
          <div class="md:flex-1 md:min-h-0 md:overflow-hidden">
            <FinanceAccountList :accounts="store.summary?.accounts ?? []" @create="openCreateAcc" @edit="openEditAcc" />
          </div>
          <div class="md:flex-1 md:min-h-0 md:overflow-hidden">
            <FinanceCategoryList v-if="store.summary" :summary="store.summary.categories" />
          </div>
        </div>
      </div>
    </div>

    <FinanceTransactionModal
      :open="txnModalOpen"
      :mode="txnModalMode"
      :transaction="editingTxn"
      @close="txnModalOpen = false"
    />
    <FinanceAccountModal
      :open="accModalOpen"
      :mode="accModalMode"
      :account="editingAcc"
      @close="accModalOpen = false"
    />
    <FinanceCategoryModal :open="catModalOpen" @close="catModalOpen = false" />
    <FinanceMerchantModal :open="merchantModalOpen" @close="merchantModalOpen = false" />
  </div>
</template>

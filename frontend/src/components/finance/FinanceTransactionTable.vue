<script setup lang="ts">
import type { Transaction } from "@/types/finance";
import CategoryBadge from "./CategoryBadge.vue";
import { formatAmount, formatDate } from "@/utils/finance";

const props = defineProps<{
  transactions: Transaction[];
  monthLabel: string;
  currentMonth: number;
}>();

const emit = defineEmits<{
  create: [];
  edit: [txn: Transaction];
}>();
</script>

<template>
  <div>
    <div class="bg-parchment-50 border border-parchment-300 rounded-xl overflow-hidden">
      <div class="flex items-center justify-between px-4 py-3 border-b border-parchment-200">
        <span class="text-xs font-semibold uppercase tracking-widest text-slate-500">Transactions</span>
        <button
          class="text-xs font-medium text-forest-600 hover:text-forest-700 transition-colors"
          @click="emit('create')"
        >
          + New
        </button>
      </div>
      <!-- Mobile: card list -->
      <div class="sm:hidden divide-y divide-parchment-200">
        <template v-if="props.transactions.length">
          <div
            v-for="txn in props.transactions"
            :key="txn.id"
            class="px-4 py-3 hover:bg-parchment-100 active:bg-parchment-100 transition-colors cursor-pointer"
            @click="emit('edit', txn)"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1 flex-wrap">
                  <CategoryBadge :type="txn.category.type" :name="txn.category.name" />
                  <span class="text-xs text-slate-400 truncate">{{ txn.merchant?.name ?? "—" }}</span>
                </div>
                <div class="text-xs font-mono text-slate-400">
                  {{ formatDate(txn.date, props.currentMonth) }}
                  <span class="ml-1 text-slate-300">·
                    <template v-if="!txn.account">External<template v-if="txn.to_account"> → {{ txn.to_account.name }}</template></template>
                    <template v-else>{{ txn.account.name }}<template v-if="txn.to_account"> → {{ txn.to_account.name }}</template></template>
                  </span>
                </div>
              </div>
              <span
                class="font-mono font-semibold text-sm shrink-0"
                :class="
                  txn.category.type === 'credit'
                    ? 'text-earth-700'
                    : txn.category.type === 'debit'
                      ? 'text-forest-700'
                      : 'text-slate-600'
                "
              >
                {{ formatAmount(txn.amount) }}
              </span>
            </div>
          </div>
        </template>
        <div v-else class="px-4 py-10 text-center text-sm text-slate-400">
          No transactions for {{ props.monthLabel }}.
          <button class="ml-1 text-forest-600 hover:underline" @click="emit('create')">Add one.</button>
        </div>
      </div>

      <!-- Desktop: table -->
      <div class="hidden sm:block overflow-y-auto" style="max-height: 600px">
        <table class="w-full text-sm">
          <thead class="sticky top-0 bg-parchment-100 border-b border-parchment-300 z-10">
            <tr>
              <th class="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider text-slate-500">Date</th>
              <th class="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
                Category
              </th>
              <th class="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider text-slate-500">Account</th>
              <th class="text-right px-4 py-3 text-xs font-semibold uppercase tracking-wider text-slate-500">Amount</th>
              <th class="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
                Merchant
              </th>
              <th class="px-4 py-3 w-12"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-parchment-200">
            <template v-if="props.transactions.length">
              <tr v-for="txn in props.transactions" :key="txn.id" class="hover:bg-parchment-100 transition-colors">
                <td class="px-4 py-3 font-mono text-xs text-slate-500 whitespace-nowrap">
                  {{ formatDate(txn.date, props.currentMonth) }}
                </td>
                <td class="px-4 py-3">
                  <CategoryBadge :type="txn.category.type" :name="txn.category.name" />
                </td>
                <td class="px-4 py-3 text-slate-600 text-xs">
                  <template v-if="!txn.account">
                    <span class="text-slate-400 italic">External</span>
                    <span v-if="txn.to_account" class="text-slate-400"> → {{ txn.to_account.name }}</span>
                  </template>
                  <template v-else>
                    {{ txn.account.name }}
                    <span v-if="txn.to_account" class="text-slate-400"> → {{ txn.to_account.name }}</span>
                  </template>
                </td>
                <td
                  class="px-4 py-3 text-right font-mono font-medium"
                  :class="
                    txn.category.type === 'credit'
                      ? 'text-earth-700'
                      : txn.category.type === 'debit'
                        ? 'text-forest-700'
                        : 'text-slate-600'
                  "
                >
                  {{ formatAmount(txn.amount) }}
                </td>
                <td class="px-4 py-3 text-slate-600 text-xs">{{ txn.merchant?.name ?? "—" }}</td>
                <td class="px-4 py-3">
                  <button
                    class="p-1 rounded text-slate-400 hover:text-slate-700 hover:bg-parchment-200 transition-colors"
                    title="Edit"
                    @click="emit('edit', txn)"
                  >
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125"
                      />
                    </svg>
                  </button>
                </td>
              </tr>
            </template>
            <tr v-else>
              <td colspan="6" class="px-4 py-10 text-center text-sm text-slate-400">
                No transactions for {{ props.monthLabel }}.
                <button class="ml-1 text-forest-600 hover:underline" @click="emit('create')">Add one.</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <p v-if="props.transactions.length" class="text-xs text-slate-400 mt-2 px-1">
      Showing {{ props.transactions.length }}
      {{ props.transactions.length === 1 ? "entry" : "entries" }}
    </p>
  </div>
</template>

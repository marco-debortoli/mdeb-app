<script setup lang="ts">
import { ref } from "vue";
import { useFinanceStore } from "@/stores/finance";
import type { AccountMonthlySummary, FinanceAccount } from "@/types/finance";
import { formatAmount } from "@/utils/finance";

const props = defineProps<{
  item: AccountMonthlySummary;
}>();

const emit = defineEmits<{
  edit: [account: FinanceAccount];
}>();

const store = useFinanceStore();

const editingValue = ref(false);
const editingValueAmount = ref("");
const saving = ref(false);

function startEditValue() {
  editingValueAmount.value = props.item.value?.amount ?? "";
  editingValue.value = true;
}

function deltaIsGood(): boolean {
  const v = parseFloat(props.item.delta);
  return props.item.account.type === "credit" ? v <= 0 : v >= 0;
}

async function saveValue() {
  if (editingValueAmount.value === "") {
    editingValue.value = false;
    return;
  }
  saving.value = true;
  try {
    await store.upsertAccountValue(props.item.account.id, editingValueAmount.value);
    editingValue.value = false;
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <div class="px-4 py-3">
    <!-- Name + controls row -->
    <div class="flex items-start justify-between gap-2">
      <div class="min-w-0">
        <span class="text-sm font-medium text-slate-800 truncate block leading-tight">{{ item.account.name }}</span>
        <span class="text-xs text-slate-400 font-mono uppercase">{{ item.account.type }}</span>
      </div>
      <div class="flex items-center gap-1 shrink-0 mt-0.5">
        <!-- Reconciliation indicator -->
        <template v-if="item.account.type !== 'investment'">
          <svg
            v-if="item.reconciled"
            class="w-4 h-4 text-forest-500"
            fill="none"
            stroke="currentColor"
            stroke-width="1.75"
            viewBox="0 0 24 24"
            title="Reconciled"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <svg
            v-else
            class="w-4 h-4 text-slate-300"
            fill="none"
            stroke="currentColor"
            stroke-width="1.75"
            viewBox="0 0 24 24"
            title="Not reconciled"
          >
            <circle cx="12" cy="12" r="9" />
          </svg>
        </template>
        <!-- Edit account -->
        <button
          class="p-1 rounded text-slate-400 hover:text-slate-700 hover:bg-parchment-200 transition-colors"
          title="Edit account"
          @click="emit('edit', item.account)"
        >
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125"
            />
          </svg>
        </button>
      </div>
    </div>

    <!-- Balance + delta -->
    <div class="mt-1.5 flex items-baseline gap-2">
      <template v-if="editingValue">
        <input
          v-model="editingValueAmount"
          type="number"
          step="0.01"
          class="w-28 text-sm rounded-lg border border-parchment-300 bg-white px-2 py-1 font-mono text-slate-800 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
          @keydown.enter="saveValue"
          @keydown.escape="editingValue = false"
          @blur="saveValue"
        />
      </template>
      <template v-else>
        <button
          class="font-mono text-sm font-semibold text-slate-700 hover:text-forest-700 hover:underline transition-colors"
          :class="saving ? 'opacity-50 cursor-wait' : ''"
          title="Click to edit balance"
          @click="startEditValue"
        >
          {{ item.value ? formatAmount(item.value.amount) : "—" }}
        </button>
      </template>
      <span class="text-xs font-mono" :class="deltaIsGood() ? 'text-forest-600' : 'text-earth-600'">
        ({{ parseFloat(item.delta) >= 0 ? "+" : "" }}{{ formatAmount(item.delta) }})
      </span>
    </div>
  </div>
</template>

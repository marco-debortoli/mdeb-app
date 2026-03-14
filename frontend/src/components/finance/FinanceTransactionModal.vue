<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useFinanceStore } from "@/stores/finance";
import type { FinanceAccount, FinanceCategory, Merchant, Transaction } from "@/types/finance";
import BaseModal from "@/components/ui/BaseModal.vue";
import SearchableSelect from "@/components/ui/SearchableSelect.vue";
import type { SelectGroup, SelectOption } from "@/components/ui/SearchableSelect.vue";

const props = defineProps<{
  open: boolean;
  mode: "create" | "edit";
  transaction: Transaction | null;
}>();

const emit = defineEmits<{
  close: [];
}>();

const store = useFinanceStore();

const form = ref({
  date: "",
  amount: "",
  account_id: "" as number | "",
  category_id: "" as number | "",
  merchant_id: null as number | null,
  to_account_id: null as number | null,
});
const error = ref<string | null>(null);
const saving = ref(false);

const selectedCategory = computed(
  () => store.categories.find((c: FinanceCategory) => c.id === form.value.category_id) ?? null,
);
const isTransfer = computed(() => selectedCategory.value?.type === "transfer");

const categoryGroups = computed<SelectGroup[]>(() =>
  [
    {
      label: "Credit",
      options: store.categories
        .filter((c: FinanceCategory) => c.type === "credit")
        .map((c: FinanceCategory) => ({ value: c.id, label: c.name })),
    },
    {
      label: "Debit",
      options: store.categories
        .filter((c: FinanceCategory) => c.type === "debit")
        .map((c: FinanceCategory) => ({ value: c.id, label: c.name })),
    },
    {
      label: "Transfer",
      options: store.categories
        .filter((c: FinanceCategory) => c.type === "transfer")
        .map((c: FinanceCategory) => ({ value: c.id, label: c.name })),
    },
  ].filter((g) => g.options.length > 0),
);

const merchantOptions = computed<SelectOption[]>(() => [
  { value: null, label: "— none —" },
  ...store.merchants.filter((m: Merchant) => !m.archived).map((m: Merchant) => ({ value: m.id, label: m.name })),
]);

const dateMin = computed(() => {
  const m = store.currentMonth.toString().padStart(2, "0");
  return `${store.currentYear}-${m}-01`;
});
const dateMax = computed(() => {
  const lastDay = new Date(store.currentYear, store.currentMonth, 0).getDate();
  const m = store.currentMonth.toString().padStart(2, "0");
  return `${store.currentYear}-${m}-${lastDay.toString().padStart(2, "0")}`;
});

function defaultDate() {
  const y = store.currentYear;
  const m = store.currentMonth.toString().padStart(2, "0");
  const today = new Date();
  const viewingCurrent = today.getFullYear() === y && today.getMonth() + 1 === store.currentMonth;
  const d = viewingCurrent ? today.getDate().toString().padStart(2, "0") : "01";
  return `${y}-${m}-${d}`;
}

watch(
  () => props.open,
  (open) => {
    if (!open) return;
    error.value = null;
    if (props.mode === "create" || !props.transaction) {
      form.value = {
        date: defaultDate(),
        amount: "",
        account_id: "",
        category_id: "",
        merchant_id: null,
        to_account_id: null,
      };
    } else {
      const t = props.transaction;
      form.value = {
        date: t.date,
        amount: t.amount,
        account_id: t.account_id,
        category_id: t.category_id,
        merchant_id: t.merchant_id,
        to_account_id: t.to_account_id,
      };
    }
  },
);

async function save() {
  if (!form.value.date || !form.value.amount || form.value.account_id === "" || form.value.category_id === "") {
    error.value = "Please fill in all required fields.";
    return;
  }
  saving.value = true;
  error.value = null;
  try {
    const payload = {
      date: form.value.date,
      amount: form.value.amount,
      account_id: form.value.account_id as number,
      category_id: form.value.category_id as number,
      merchant_id: form.value.merchant_id,
      to_account_id: isTransfer.value ? form.value.to_account_id : null,
    };
    if (props.mode === "create") {
      await store.createTransaction(payload);
    } else if (props.transaction) {
      await store.updateTransaction(props.transaction.id, payload);
    }
    emit("close");
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : "Failed to save transaction";
  } finally {
    saving.value = false;
  }
}

async function remove() {
  if (!props.transaction) return;
  saving.value = true;
  try {
    await store.deleteTransaction(props.transaction.id);
    emit("close");
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : "Failed to delete transaction";
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <BaseModal :open="open" :title="mode === 'create' ? 'New Transaction' : 'Edit Transaction'" @close="emit('close')">
    <!-- Date -->
    <div>
      <label class="block text-xs font-medium text-slate-600 mb-1">Date</label>
      <input
        v-model="form.date"
        type="date"
        :min="dateMin"
        :max="dateMax"
        class="w-full text-sm rounded-lg border border-parchment-300 bg-white px-3 py-2 text-slate-800 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
      />
    </div>

    <!-- Category + Amount -->
    <div class="grid grid-cols-2 gap-3">
      <div>
        <label class="block text-xs font-medium text-slate-600 mb-1">Category</label>
        <SearchableSelect v-model="form.category_id" :groups="categoryGroups" placeholder="— select —" />
      </div>
      <div>
        <label class="block text-xs font-medium text-slate-600 mb-1">Amount</label>
        <input
          v-model="form.amount"
          type="number"
          step="0.01"
          min="0"
          placeholder="0.00"
          class="w-full text-sm rounded-lg border border-parchment-300 bg-white px-3 py-2 font-mono text-slate-800 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
        />
      </div>
    </div>

    <!-- Account -->
    <div>
      <label class="block text-xs font-medium text-slate-600 mb-1">Account</label>
      <select
        v-model="form.account_id"
        class="w-full text-sm rounded-lg border border-parchment-300 bg-white px-3 py-2 text-slate-800 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
      >
        <option value="">— select —</option>
        <option v-for="acc in store.accounts.filter((a: FinanceAccount) => !a.archived)" :key="acc.id" :value="acc.id">
          {{ acc.name }}
        </option>
      </select>
    </div>

    <!-- To Account (transfers only) -->
    <div v-if="isTransfer">
      <label class="block text-xs font-medium text-slate-600 mb-1">To Account</label>
      <select
        v-model="form.to_account_id"
        class="w-full text-sm rounded-lg border border-parchment-300 bg-white px-3 py-2 text-slate-800 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
      >
        <option :value="null">— select —</option>
        <option
          v-for="acc in store.accounts.filter((a: FinanceAccount) => !a.archived && a.id !== form.account_id)"
          :key="acc.id"
          :value="acc.id"
        >
          {{ acc.name }}
        </option>
      </select>
    </div>

    <!-- Merchant -->
    <div>
      <label class="block text-xs font-medium text-slate-600 mb-1"
        >Merchant <span class="text-slate-400">(optional)</span></label
      >
      <SearchableSelect v-model="form.merchant_id" :options="merchantOptions" placeholder="— none —" />
    </div>

    <p v-if="error" class="text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">{{ error }}</p>

    <template #footer-left>
      <button
        v-if="mode === 'edit'"
        :disabled="saving"
        class="px-3 py-2 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 disabled:opacity-40 transition-colors"
        @click="remove"
      >
        Delete
      </button>
    </template>
    <template #footer-right>
      <div class="flex gap-2">
        <button
          class="px-3 py-2 rounded-lg text-sm font-medium text-slate-600 hover:bg-parchment-200 transition-colors"
          @click="emit('close')"
        >
          Cancel
        </button>
        <button
          :disabled="saving"
          class="px-4 py-2 rounded-lg text-sm font-medium bg-forest-600 text-parchment-50 hover:bg-forest-700 disabled:opacity-40 transition-colors"
          @click="save"
        >
          {{ saving ? "Saving…" : "Save" }}
        </button>
      </div>
    </template>
  </BaseModal>
</template>

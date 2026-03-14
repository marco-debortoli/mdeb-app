<script setup lang="ts">
import { ref, watch } from "vue";
import { useFinanceStore } from "@/stores/finance";
import type { FinanceAccount } from "@/types/finance";
import BaseModal from "@/components/ui/BaseModal.vue";

const props = defineProps<{
  open: boolean;
  mode: "create" | "edit";
  account: FinanceAccount | null;
}>();

const emit = defineEmits<{
  close: [];
}>();

const store = useFinanceStore();

const form = ref({
  name: "",
  type: "debit" as FinanceAccount["type"],
  start_date: "",
  end_date: "",
  archived: false,
  profit_eligible: true,
});
const error = ref<string | null>(null);
const saving = ref(false);

watch(
  () => props.open,
  (open) => {
    if (!open) return;
    error.value = null;
    if (props.mode === "create" || !props.account) {
      form.value = { name: "", type: "debit", start_date: "", end_date: "", archived: false, profit_eligible: true };
    } else {
      const a = props.account;
      form.value = {
        name: a.name,
        type: a.type,
        start_date: a.start_date,
        end_date: a.end_date ?? "",
        archived: a.archived,
        profit_eligible: a.profit_eligible,
      };
    }
  },
);

async function save() {
  if (!form.value.name.trim() || !form.value.start_date) {
    error.value = "Name and start date are required.";
    return;
  }
  saving.value = true;
  error.value = null;
  try {
    const payload = {
      name: form.value.name.trim(),
      type: form.value.type,
      start_date: form.value.start_date,
      end_date: form.value.end_date || null,
      archived: form.value.archived,
      profit_eligible: form.value.profit_eligible,
    };
    if (props.mode === "create") {
      await store.createAccount(payload);
    } else if (props.account) {
      await store.updateAccount(props.account.id, payload);
    }
    emit("close");
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : "Failed to save account";
  } finally {
    saving.value = false;
  }
}

async function remove() {
  if (!props.account) return;
  saving.value = true;
  try {
    await store.deleteAccount(props.account.id);
    emit("close");
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : "Failed to delete account";
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <BaseModal :open="open" :title="mode === 'create' ? 'New Account' : 'Edit Account'" @close="emit('close')">
    <div>
      <label class="block text-xs font-medium text-slate-600 mb-1">Name</label>
      <input
        v-model="form.name"
        type="text"
        placeholder="e.g. Checking Account"
        class="w-full text-sm rounded-lg border border-parchment-300 bg-white px-3 py-2 text-slate-800 placeholder-slate-400 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
      />
    </div>

    <div class="grid grid-cols-2 gap-3">
      <div>
        <label class="block text-xs font-medium text-slate-600 mb-1">Type</label>
        <select
          v-model="form.type"
          class="w-full text-sm rounded-lg border border-parchment-300 bg-white px-3 py-2 text-slate-800 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
        >
          <option value="debit">Debit</option>
          <option value="credit">Credit</option>
          <option value="investment">Investment</option>
          <option value="other">Other</option>
        </select>
      </div>
      <div>
        <label class="block text-xs font-medium text-slate-600 mb-1">Start Date</label>
        <input
          v-model="form.start_date"
          type="date"
          class="w-full text-sm rounded-lg border border-parchment-300 bg-white px-3 py-2 text-slate-800 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
        />
      </div>
    </div>

    <div>
      <label class="block text-xs font-medium text-slate-600 mb-1"
        >End Date <span class="text-slate-400">(optional)</span></label
      >
      <input
        v-model="form.end_date"
        type="date"
        class="w-full text-sm rounded-lg border border-parchment-300 bg-white px-3 py-2 text-slate-800 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
      />
    </div>

    <div class="flex gap-6">
      <label class="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
        <input v-model="form.archived" type="checkbox" class="rounded" />
        Archived
      </label>
      <label class="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
        <input v-model="form.profit_eligible" type="checkbox" class="rounded" />
        Profit eligible
      </label>
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

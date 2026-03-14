<script setup lang="ts">
import { ref, computed } from "vue";
import { useFinanceStore } from "@/stores/finance";
import type { Merchant } from "@/types/finance";

defineProps<{
  open: boolean;
}>();

const emit = defineEmits<{
  close: [];
}>();

const store = useFinanceStore();

const search = ref("");
const newMerchantName = ref("");
const editingMerchant = ref<Merchant | null>(null);
const editMerchantName = ref("");
const saving = ref(false);
const error = ref<string | null>(null);

const filteredMerchants = computed(() => {
  const q = search.value.trim().toLowerCase();
  if (!q) return store.merchants;
  return store.merchants.filter((m: Merchant) => m.name.toLowerCase().includes(q));
});

async function addMerchant() {
  if (!newMerchantName.value.trim()) return;
  saving.value = true;
  error.value = null;
  try {
    await store.createMerchant(newMerchantName.value.trim());
    newMerchantName.value = "";
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : "Failed to add merchant";
  } finally {
    saving.value = false;
  }
}

function startEdit(m: Merchant) {
  editingMerchant.value = m;
  editMerchantName.value = m.name;
}

async function saveEdit() {
  if (!editingMerchant.value || !editMerchantName.value.trim()) return;
  saving.value = true;
  try {
    await store.updateMerchant(editingMerchant.value.id, { name: editMerchantName.value.trim() });
    editingMerchant.value = null;
  } finally {
    saving.value = false;
  }
}

async function deleteMerchant(id: number) {
  try {
    await store.deleteMerchant(id);
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : "Failed to delete merchant";
  }
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" @click="emit('close')" />
        <div
          class="relative w-full max-w-lg bg-parchment-50 rounded-xl shadow-2xl border border-parchment-300 flex flex-col"
          style="max-height: 60vh"
        >
          <!-- Header -->
          <div class="flex items-center justify-between px-5 py-4 border-b border-parchment-300 shrink-0">
            <h2 class="text-base font-semibold text-slate-800">Merchants</h2>
            <button
              class="p-1 rounded-lg text-slate-400 hover:bg-parchment-200 transition-colors"
              @click="emit('close')"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Search -->
          <div class="px-4 py-2.5 border-b border-parchment-200 shrink-0">
            <input
              v-model="search"
              type="text"
              placeholder="Search merchants…"
              class="w-full text-sm rounded-lg border border-parchment-300 bg-white px-3 py-1.5 text-slate-800 placeholder-slate-400 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
            />
          </div>

          <p v-if="error" class="mx-4 mt-3 shrink-0 text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">{{ error }}</p>

          <!-- Table -->
          <div class="overflow-y-auto flex-1">
            <table class="w-full text-sm">
              <thead class="sticky top-0 bg-parchment-100 border-b border-parchment-200 z-10">
                <tr>
                  <th class="text-left px-4 py-2.5 text-xs font-semibold uppercase tracking-wider text-slate-500">
                    Name
                  </th>
                  <th class="px-4 py-2.5 w-20"></th>
                </tr>
              </thead>
              <tbody class="divide-y divide-parchment-200">
                <template v-if="filteredMerchants.length">
                  <tr v-for="m in filteredMerchants" :key="m.id" class="hover:bg-parchment-100 transition-colors">
                    <td class="px-4 py-2.5">
                      <template v-if="editingMerchant?.id === m.id">
                        <input
                          v-model="editMerchantName"
                          type="text"
                          class="w-full text-sm rounded border border-parchment-300 bg-white px-2 py-1 text-slate-800 focus:border-forest-500 outline-none"
                          @keydown.enter="saveEdit"
                          @keydown.escape="editingMerchant = null"
                        />
                      </template>
                      <template v-else>
                        <span class="text-slate-700">{{ m.name }}</span>
                        <span v-if="m.archived" class="ml-1.5 text-xs text-slate-400">(archived)</span>
                      </template>
                    </td>
                    <td class="px-4 py-2.5">
                      <div class="flex items-center justify-end gap-1">
                        <template v-if="editingMerchant?.id === m.id">
                          <button
                            :disabled="saving"
                            class="text-xs px-2 py-1 rounded bg-forest-600 text-parchment-50 hover:bg-forest-700 disabled:opacity-40 transition-colors"
                            @click="saveEdit"
                          >
                            Save
                          </button>
                          <button
                            class="text-xs px-2 py-1 rounded text-slate-500 hover:bg-parchment-200 transition-colors"
                            @click="editingMerchant = null"
                          >
                            Cancel
                          </button>
                        </template>
                        <template v-else>
                          <button
                            class="p-1 rounded text-slate-400 hover:text-slate-700 hover:bg-parchment-200 transition-colors"
                            title="Edit"
                            @click="startEdit(m)"
                          >
                            <svg
                              class="w-3.5 h-3.5"
                              fill="none"
                              stroke="currentColor"
                              stroke-width="2"
                              viewBox="0 0 24 24"
                            >
                              <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125"
                              />
                            </svg>
                          </button>
                          <button
                            class="p-1 rounded text-slate-300 hover:text-red-500 hover:bg-red-50 transition-colors"
                            title="Delete"
                            @click="deleteMerchant(m.id)"
                          >
                            <svg
                              class="w-3.5 h-3.5"
                              fill="none"
                              stroke="currentColor"
                              stroke-width="2"
                              viewBox="0 0 24 24"
                            >
                              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                        </template>
                      </div>
                    </td>
                  </tr>
                </template>
                <tr v-else>
                  <td colspan="2" class="px-4 py-6 text-center text-sm text-slate-400">
                    {{ search ? "No merchants match your search." : "No merchants yet." }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Add new -->
          <div class="flex items-center gap-2 px-4 py-3 border-t border-parchment-200 shrink-0">
            <input
              v-model="newMerchantName"
              type="text"
              placeholder="New merchant name…"
              class="flex-1 text-sm rounded-lg border border-parchment-300 bg-white px-3 py-2 text-slate-800 placeholder-slate-400 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
              @keydown.enter="addMerchant"
            />
            <button
              :disabled="!newMerchantName.trim() || saving"
              class="px-3 py-2 rounded-lg text-sm font-medium bg-forest-600 text-parchment-50 hover:bg-forest-700 disabled:opacity-40 transition-colors"
              @click="addMerchant"
            >
              Add
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.15s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>

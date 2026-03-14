<script setup lang="ts">
import { ref, computed } from "vue";
import { useFinanceStore } from "@/stores/finance";
import type { FinanceCategory, FinanceCategoryType } from "@/types/finance";

defineProps<{
  open: boolean;
}>();

const emit = defineEmits<{
  close: [];
}>();

const store = useFinanceStore();

const search = ref("");
const editingCategory = ref<FinanceCategory | null>(null);
const editForm = ref({ name: "", type: "debit" as FinanceCategoryType });
const newForm = ref({ name: "", type: "debit" as FinanceCategoryType });
const saving = ref(false);
const error = ref<string | null>(null);

const TYPE_LABELS: Record<FinanceCategoryType, string> = {
  credit: "Credit",
  debit: "Debit",
  transfer: "Transfer",
};

const filteredCategories = computed(() => {
  const q = search.value.trim().toLowerCase();
  if (!q) return store.categories;
  return store.categories.filter((c: FinanceCategory) => c.name.toLowerCase().includes(q));
});

function startEdit(cat: FinanceCategory) {
  editingCategory.value = cat;
  editForm.value = { name: cat.name, type: cat.type };
}

async function saveEdit() {
  if (!editingCategory.value || !editForm.value.name.trim()) return;
  saving.value = true;
  error.value = null;
  try {
    await store.updateCategory(editingCategory.value.id, {
      name: editForm.value.name.trim(),
      type: editForm.value.type,
    });
    editingCategory.value = null;
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : "Failed to update category";
  } finally {
    saving.value = false;
  }
}

async function deleteCategory(id: number) {
  error.value = null;
  try {
    await store.deleteCategory(id);
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : "Failed to delete category";
  }
}

async function addCategory() {
  if (!newForm.value.name.trim()) return;
  saving.value = true;
  error.value = null;
  try {
    await store.createCategory({ name: newForm.value.name.trim(), type: newForm.value.type });
    newForm.value.name = "";
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : "Failed to add category";
  } finally {
    saving.value = false;
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
          style="max-height: 65vh"
        >
          <!-- Header -->
          <div class="flex items-center justify-between px-5 py-4 border-b border-parchment-300 shrink-0">
            <h2 class="text-base font-semibold text-slate-800">Categories</h2>
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
              placeholder="Search categories…"
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
                  <th class="text-left px-4 py-2.5 text-xs font-semibold uppercase tracking-wider text-slate-500 w-28">
                    Type
                  </th>
                  <th class="px-4 py-2.5 w-24"></th>
                </tr>
              </thead>
              <tbody class="divide-y divide-parchment-200">
                <template v-if="filteredCategories.length">
                  <tr v-for="cat in filteredCategories" :key="cat.id" class="hover:bg-parchment-100 transition-colors">
                    <td class="px-4 py-2.5">
                      <template v-if="editingCategory?.id === cat.id">
                        <input
                          v-model="editForm.name"
                          type="text"
                          class="w-full text-sm rounded border border-parchment-300 bg-white px-2 py-1 text-slate-800 focus:border-forest-500 outline-none"
                          @keydown.enter="saveEdit"
                          @keydown.escape="editingCategory = null"
                        />
                      </template>
                      <template v-else>
                        <span class="text-slate-700">{{ cat.name }}</span>
                      </template>
                    </td>
                    <td class="px-4 py-2.5">
                      <template v-if="editingCategory?.id === cat.id">
                        <select
                          v-model="editForm.type"
                          class="w-full text-sm rounded border border-parchment-300 bg-white px-2 py-1 text-slate-800 focus:border-forest-500 outline-none"
                        >
                          <option value="credit">Credit</option>
                          <option value="debit">Debit</option>
                          <option value="transfer">Transfer</option>
                        </select>
                      </template>
                      <template v-else>
                        <span
                          class="text-xs font-medium"
                          :class="
                            cat.type === 'credit'
                              ? 'text-forest-600'
                              : cat.type === 'debit'
                                ? 'text-earth-600'
                                : 'text-slate-500'
                          "
                          >{{ TYPE_LABELS[cat.type] }}</span
                        >
                      </template>
                    </td>
                    <td class="px-4 py-2.5">
                      <div class="flex items-center justify-end gap-1">
                        <template v-if="editingCategory?.id === cat.id">
                          <button
                            :disabled="saving"
                            class="text-xs px-2 py-1 rounded bg-forest-600 text-parchment-50 hover:bg-forest-700 disabled:opacity-40 transition-colors"
                            @click="saveEdit"
                          >
                            Save
                          </button>
                          <button
                            class="text-xs px-2 py-1 rounded text-slate-500 hover:bg-parchment-200 transition-colors"
                            @click="editingCategory = null"
                          >
                            Cancel
                          </button>
                        </template>
                        <template v-else>
                          <button
                            class="p-1 rounded text-slate-400 hover:text-slate-700 hover:bg-parchment-200 transition-colors"
                            title="Edit"
                            @click="startEdit(cat)"
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
                            @click="deleteCategory(cat.id)"
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
                  <td colspan="3" class="px-4 py-6 text-center text-sm text-slate-400">
                    {{ search ? "No categories match your search." : "No categories yet." }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Add new -->
          <div class="flex items-center gap-2 px-4 py-3 border-t border-parchment-200 shrink-0">
            <input
              v-model="newForm.name"
              type="text"
              placeholder="New category name…"
              class="flex-1 text-sm rounded-lg border border-parchment-300 bg-white px-3 py-2 text-slate-800 placeholder-slate-400 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
              @keydown.enter="addCategory"
            />
            <select
              v-model="newForm.type"
              class="text-sm rounded-lg border border-parchment-300 bg-white px-2 py-2 text-slate-800 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
            >
              <option value="credit">Credit</option>
              <option value="debit">Debit</option>
              <option value="transfer">Transfer</option>
            </select>
            <button
              :disabled="!newForm.name.trim() || saving"
              class="px-3 py-2 rounded-lg text-sm font-medium bg-forest-600 text-parchment-50 hover:bg-forest-700 disabled:opacity-40 transition-colors"
              @click="addCategory"
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

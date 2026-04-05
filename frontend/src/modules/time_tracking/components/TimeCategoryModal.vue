<script setup lang="ts">
import { ref, computed } from "vue";
import { useTimeStore } from "@/modules/time_tracking/store";
import type { TimeCategory, TimeSubcategory } from "@/modules/time_tracking/types";

defineProps<{ open: boolean }>();
const emit = defineEmits<{ close: [] }>();

const store = useTimeStore();

const error = ref<string | null>(null);
const saving = ref(false);

// ── Category editing ─────────────────────────────────────────────────────────

const editingCatId = ref<number | null>(null);
const editCatForm = ref({ name: "", color: "" });

const newCatForm = ref({ name: "", color: "#4A90D9" });

function startEditCat(cat: TimeCategory) {
  editingCatId.value = cat.id;
  editCatForm.value = { name: cat.name, color: cat.color };
}

async function saveEditCat() {
  if (!editingCatId.value || !editCatForm.value.name.trim()) return;
  saving.value = true;
  error.value = null;
  try {
    await store.updateCategory(editingCatId.value, {
      name: editCatForm.value.name.trim(),
      color: editCatForm.value.color,
    });
    editingCatId.value = null;
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : "Failed to update category";
  } finally {
    saving.value = false;
  }
}

async function addCategory() {
  if (!newCatForm.value.name.trim()) return;
  saving.value = true;
  error.value = null;
  try {
    await store.createCategory({
      name: newCatForm.value.name.trim(),
      color: newCatForm.value.color,
    });
    newCatForm.value.name = "";
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : "Failed to add category";
  } finally {
    saving.value = false;
  }
}

async function softDeleteCat(id: number) {
  error.value = null;
  try {
    await store.deleteCategory(id);
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : "Failed to deactivate category";
  }
}

// ── Subcategory editing ──────────────────────────────────────────────────────

const expandedCatId = ref<number | null>(null);

function toggleExpand(catId: number) {
  expandedCatId.value = expandedCatId.value === catId ? null : catId;
}

const editingSubId = ref<number | null>(null);
const editSubName = ref("");

function startEditSub(sub: TimeSubcategory) {
  editingSubId.value = sub.id;
  editSubName.value = sub.name;
}

async function saveEditSub() {
  if (!editingSubId.value || !editSubName.value.trim()) return;
  saving.value = true;
  error.value = null;
  try {
    await store.updateSubcategory(editingSubId.value, { name: editSubName.value.trim() });
    editingSubId.value = null;
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : "Failed to update subcategory";
  } finally {
    saving.value = false;
  }
}

async function softDeleteSub(id: number) {
  error.value = null;
  try {
    await store.deleteSubcategory(id);
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : "Failed to deactivate subcategory";
  }
}

const newSubName = ref<Record<number, string>>({});

async function addSubcategory(catId: number) {
  const name = (newSubName.value[catId] ?? "").trim();
  if (!name) return;
  saving.value = true;
  error.value = null;
  try {
    await store.createSubcategory({ time_category_id: catId, name });
    newSubName.value[catId] = "";
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : "Failed to add subcategory";
  } finally {
    saving.value = false;
  }
}

const activeCategories = computed(() => store.categories.filter((c) => c.is_active));
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="open" class="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4">
        <div class="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" @click="emit('close')" />
        <div
          class="relative w-full sm:max-w-lg bg-parchment-50 rounded-t-xl sm:rounded-xl shadow-2xl border border-parchment-300 flex flex-col"
          style="max-height: 80vh"
        >
          <!-- Header -->
          <div class="flex items-center justify-between px-5 py-4 border-b border-parchment-300 shrink-0">
            <h2 class="text-base font-semibold text-slate-800">Time Categories</h2>
            <button
              class="p-1 rounded-lg text-slate-400 hover:bg-parchment-200 transition-colors"
              @click="emit('close')"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <p v-if="error" class="mx-4 mt-3 shrink-0 text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">{{ error }}</p>

          <!-- Category list -->
          <div class="overflow-y-auto flex-1">
            <div v-for="cat in activeCategories" :key="cat.id" class="border-b border-parchment-200 last:border-b-0">
              <!-- Category row -->
              <div class="flex items-center gap-2 px-4 py-2.5 hover:bg-parchment-100 transition-colors">
                <!-- Color swatch -->
                <span class="w-3 h-3 rounded-full shrink-0" :style="{ backgroundColor: cat.color }" />

                <template v-if="editingCatId === cat.id">
                  <input
                    v-model="editCatForm.name"
                    type="text"
                    class="flex-1 text-sm rounded border border-parchment-300 bg-white px-2 py-1 text-slate-800 focus:border-forest-500 outline-none"
                    @keydown.enter="saveEditCat"
                    @keydown.escape="editingCatId = null"
                  />
                  <input
                    v-model="editCatForm.color"
                    type="color"
                    class="w-7 h-7 rounded cursor-pointer border border-parchment-300"
                    title="Pick color"
                  />
                  <button
                    :disabled="saving"
                    class="text-xs px-2 py-1 rounded bg-forest-600 text-parchment-50 hover:bg-forest-700 disabled:opacity-40 transition-colors"
                    @click="saveEditCat"
                  >
                    Save
                  </button>
                  <button
                    class="text-xs px-2 py-1 rounded text-slate-500 hover:bg-parchment-200 transition-colors"
                    @click="editingCatId = null"
                  >
                    Cancel
                  </button>
                </template>
                <template v-else>
                  <span class="flex-1 text-sm text-slate-700 font-medium">{{ cat.name }}</span>
                  <!-- Expand subcategories toggle -->
                  <button
                    class="text-xs text-slate-400 hover:text-slate-600 transition-colors px-1"
                    :title="expandedCatId === cat.id ? 'Hide subcategories' : 'Show subcategories'"
                    @click="toggleExpand(cat.id)"
                  >
                    <svg
                      :class="['w-3.5 h-3.5 transition-transform', expandedCatId === cat.id ? 'rotate-180' : '']"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      viewBox="0 0 24 24"
                    >
                      <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  <button
                    class="p-1 rounded text-slate-400 hover:text-slate-700 hover:bg-parchment-200 transition-colors"
                    title="Edit"
                    @click="startEditCat(cat)"
                  >
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125"
                      />
                    </svg>
                  </button>
                  <button
                    class="p-1 rounded text-slate-300 hover:text-red-500 hover:bg-red-50 transition-colors"
                    title="Deactivate"
                    @click="softDeleteCat(cat.id)"
                  >
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </template>
              </div>

              <!-- Subcategory list (expanded) -->
              <div v-if="expandedCatId === cat.id" class="bg-parchment-100 border-t border-parchment-200">
                <div
                  v-for="sub in cat.subcategories.filter((s) => s.is_active)"
                  :key="sub.id"
                  class="flex items-center gap-2 pl-8 pr-4 py-2 hover:bg-parchment-200 transition-colors"
                >
                  <span class="w-1.5 h-1.5 rounded-full bg-slate-400 shrink-0" />
                  <template v-if="editingSubId === sub.id">
                    <input
                      v-model="editSubName"
                      type="text"
                      class="flex-1 text-sm rounded border border-parchment-300 bg-white px-2 py-1 text-slate-800 focus:border-forest-500 outline-none"
                      @keydown.enter="saveEditSub"
                      @keydown.escape="editingSubId = null"
                    />
                    <button
                      :disabled="saving"
                      class="text-xs px-2 py-1 rounded bg-forest-600 text-parchment-50 hover:bg-forest-700 disabled:opacity-40 transition-colors"
                      @click="saveEditSub"
                    >
                      Save
                    </button>
                    <button
                      class="text-xs px-2 py-1 rounded text-slate-500 hover:bg-parchment-200 transition-colors"
                      @click="editingSubId = null"
                    >
                      Cancel
                    </button>
                  </template>
                  <template v-else>
                    <span class="flex-1 text-sm text-slate-600">{{ sub.name }}</span>
                    <button
                      class="p-1 rounded text-slate-400 hover:text-slate-700 hover:bg-parchment-200 transition-colors"
                      title="Edit"
                      @click="startEditSub(sub)"
                    >
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125"
                        />
                      </svg>
                    </button>
                    <button
                      class="p-1 rounded text-slate-300 hover:text-red-500 hover:bg-red-50 transition-colors"
                      title="Deactivate"
                      @click="softDeleteSub(sub.id)"
                    >
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </template>
                </div>
                <!-- Add subcategory -->
                <div class="flex items-center gap-2 pl-8 pr-4 py-2 border-t border-parchment-200">
                  <input
                    v-model="newSubName[cat.id]"
                    type="text"
                    placeholder="New subcategory…"
                    class="flex-1 text-sm rounded-lg border border-parchment-300 bg-white px-3 py-1.5 text-slate-800 placeholder-slate-400 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
                    @keydown.enter="addSubcategory(cat.id)"
                  />
                  <button
                    :disabled="!newSubName[cat.id]?.trim() || saving"
                    class="text-xs px-2 py-1.5 rounded-lg bg-forest-600 text-parchment-50 hover:bg-forest-700 disabled:opacity-40 transition-colors whitespace-nowrap"
                    @click="addSubcategory(cat.id)"
                  >
                    + Add
                  </button>
                </div>
              </div>
            </div>

            <div v-if="!activeCategories.length" class="px-4 py-8 text-center text-sm text-slate-400">
              No categories yet.
            </div>
          </div>

          <!-- Add new category -->
          <div class="flex items-center gap-2 px-4 py-3 border-t border-parchment-200 shrink-0">
            <input
              v-model="newCatForm.name"
              type="text"
              placeholder="New category name…"
              class="flex-1 text-sm rounded-lg border border-parchment-300 bg-white px-3 py-2 text-slate-800 placeholder-slate-400 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
              @keydown.enter="addCategory"
            />
            <input
              v-model="newCatForm.color"
              type="color"
              class="w-9 h-9 rounded cursor-pointer border border-parchment-300 shrink-0"
              title="Pick color"
            />
            <button
              :disabled="!newCatForm.name.trim() || saving"
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

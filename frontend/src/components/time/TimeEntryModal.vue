<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useTimeStore } from "@/stores/time_tracking";
import type { TimeEntry } from "@/types/time_tracking";
import { generateStartOptions, generateEndOptions } from "@/utils/time_tracking";

const props = defineProps<{
  open: boolean;
  mode: "create" | "edit";
  entry?: TimeEntry | null;
  defaultDate?: string;
}>();

const emit = defineEmits<{
  close: [];
}>();

const store = useTimeStore();

// ── Form state ─────────────────────────────────────────────────────────────

const form = ref({
  date: "",
  time_category_id: 0,
  time_subcategory_id: null as number | null,
  start_time: "",
  end_time: "",
  notes: "",
});

const saving = ref(false);
const error = ref<string | null>(null);
const overlapWarning = ref(false);

// ── Category/subcategory helpers ────────────────────────────────────────────

const activeCategories = computed(() => store.categories.filter((c) => c.is_active));

const activeSubcategories = computed(() => {
  const cat = activeCategories.value.find((c) => c.id === form.value.time_category_id);
  return cat ? cat.subcategories.filter((s) => s.is_active) : [];
});

watch(
  () => form.value.time_category_id,
  () => {
    form.value.time_subcategory_id = null;
  },
);

// ── Time options ────────────────────────────────────────────────────────────

const startOptions = computed(() => (form.value.date ? generateStartOptions(form.value.date) : []));

const endOptions = computed(() => (form.value.date ? generateEndOptions(form.value.date) : []));

// ── Validation ──────────────────────────────────────────────────────────────

const timeError = computed(() => {
  if (!form.value.start_time || !form.value.end_time) return null;
  if (form.value.end_time <= form.value.start_time) {
    return "End time must be after start time";
  }
  const durationMs = new Date(form.value.end_time).getTime() - new Date(form.value.start_time).getTime();
  if (durationMs > 86_400_000) {
    return "Duration cannot exceed 24 hours";
  }
  return null;
});

// ── Reset / populate form ────────────────────────────────────────────────────

function resetForm(date?: string) {
  const d = date ?? store.currentMonth + "-01";
  form.value = {
    date: d,
    time_category_id: 0,
    time_subcategory_id: null,
    start_time: "",
    end_time: "",
    notes: "",
  };
  error.value = null;
  overlapWarning.value = false;
}

function populateFromEntry(entry: TimeEntry) {
  form.value = {
    date: entry.date,
    time_category_id: entry.time_category_id,
    time_subcategory_id: entry.time_subcategory_id,
    start_time: entry.start_time.slice(0, 19), // strip timezone
    end_time: entry.end_time.slice(0, 19),
    notes: entry.notes ?? "",
  };
  error.value = null;
  overlapWarning.value = false;
}

watch(
  () => props.open,
  (open) => {
    if (!open) return;
    if (props.mode === "edit" && props.entry) {
      populateFromEntry(props.entry);
    } else {
      resetForm(props.defaultDate);
    }
  },
  { immediate: true },
);

// ── Save ────────────────────────────────────────────────────────────────────

async function save() {
  if (!form.value.date || !form.value.start_time || !form.value.end_time) {
    error.value = "Date, start time, and end time are required";
    return;
  }
  if (form.value.time_category_id === 0) {
    error.value = "Please select a category";
    return;
  }
  if (timeError.value) {
    error.value = timeError.value;
    return;
  }

  saving.value = true;
  error.value = null;
  overlapWarning.value = false;

  try {
    const payload = {
      date: form.value.date,
      start_time: form.value.start_time,
      end_time: form.value.end_time,
      time_category_id: form.value.time_category_id,
      time_subcategory_id: form.value.time_subcategory_id,
      notes: form.value.notes.trim() || null,
    };

    let res;
    if (props.mode === "edit" && props.entry) {
      res = await store.updateEntry(props.entry.id, payload);
    } else {
      res = await store.createEntry(payload);
    }

    if (res.has_overlap) {
      overlapWarning.value = true;
      // Still close the modal — the warning was just informational
    }

    emit("close");
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : "Failed to save entry";
  } finally {
    saving.value = false;
  }
}

// ── Delete ───────────────────────────────────────────────────────────────────

async function deleteEntry() {
  if (!props.entry) return;
  saving.value = true;
  try {
    await store.deleteEntry(props.entry.id);
    emit("close");
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : "Failed to delete entry";
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="open" class="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4">
        <div class="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" @click="emit('close')" />
        <div
          class="relative w-full sm:max-w-md bg-parchment-50 rounded-t-xl sm:rounded-xl shadow-2xl border border-parchment-300 flex flex-col max-h-[90vh]"
        >
          <!-- Header -->
          <div class="flex items-center justify-between px-5 py-4 border-b border-parchment-300 shrink-0">
            <h2 class="text-base font-semibold text-slate-800">
              {{ mode === "edit" ? "Edit Entry" : "Add Time Entry" }}
            </h2>
            <button
              class="p-1 rounded-lg text-slate-400 hover:bg-parchment-200 transition-colors"
              @click="emit('close')"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Body -->
          <div class="overflow-y-auto flex-1 px-5 py-4 space-y-4">
            <!-- Error -->
            <p v-if="error" class="text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">{{ error }}</p>

            <!-- Overlap warning -->
            <p
              v-if="overlapWarning"
              class="text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2"
            >
              ⚠ This entry overlaps with another entry on this day.
            </p>

            <!-- Date -->
            <div>
              <label class="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">Date</label>
              <input
                v-model="form.date"
                type="date"
                class="w-full text-sm rounded-lg border border-parchment-300 bg-white px-3 py-2 text-slate-800 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
              />
            </div>

            <!-- Category -->
            <div>
              <label class="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">Category</label>
              <select
                v-model="form.time_category_id"
                class="w-full text-sm rounded-lg border border-parchment-300 bg-white px-3 py-2 text-slate-800 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
              >
                <option :value="0" disabled>Select category…</option>
                <option v-for="cat in activeCategories" :key="cat.id" :value="cat.id">
                  {{ cat.name }}
                </option>
              </select>
            </div>

            <!-- Subcategory -->
            <div v-if="form.time_category_id && activeSubcategories.length">
              <label class="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1"
                >Subcategory <span class="font-normal text-slate-400">(optional)</span></label
              >
              <select
                v-model="form.time_subcategory_id"
                class="w-full text-sm rounded-lg border border-parchment-300 bg-white px-3 py-2 text-slate-800 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
              >
                <option :value="null">None</option>
                <option v-for="sub in activeSubcategories" :key="sub.id" :value="sub.id">
                  {{ sub.name }}
                </option>
              </select>
            </div>

            <!-- Start / End time -->
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">Start</label>
                <select
                  v-model="form.start_time"
                  :disabled="!form.date"
                  class="w-full text-sm rounded-lg border border-parchment-300 bg-white px-3 py-2 text-slate-800 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none disabled:opacity-50"
                >
                  <option value="" disabled>Time…</option>
                  <option v-for="opt in startOptions" :key="opt.value" :value="opt.value">
                    {{ opt.label }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">End</label>
                <select
                  v-model="form.end_time"
                  :disabled="!form.date"
                  class="w-full text-sm rounded-lg border border-parchment-300 bg-white px-3 py-2 text-slate-800 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none disabled:opacity-50"
                >
                  <option value="" disabled>Time…</option>
                  <option v-for="opt in endOptions" :key="opt.value" :value="opt.value">
                    {{ opt.label }}
                  </option>
                </select>
              </div>
            </div>
            <p v-if="timeError" class="text-xs text-red-500">{{ timeError }}</p>

            <!-- Notes -->
            <div>
              <label class="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1"
                >Notes <span class="font-normal text-slate-400">(optional)</span></label
              >
              <input
                v-model="form.notes"
                type="text"
                placeholder="Optional note…"
                maxlength="500"
                class="w-full text-sm rounded-lg border border-parchment-300 bg-white px-3 py-2 text-slate-800 placeholder-slate-400 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
              />
            </div>
          </div>

          <!-- Footer -->
          <div class="flex items-center justify-between gap-3 px-5 py-4 border-t border-parchment-300 shrink-0">
            <button
              v-if="mode === 'edit'"
              :disabled="saving"
              class="text-sm text-red-500 hover:text-red-700 disabled:opacity-40 transition-colors"
              @click="deleteEntry"
            >
              Delete
            </button>
            <div v-else />
            <div class="flex gap-2">
              <button
                class="px-3 py-2 rounded-lg text-sm text-slate-600 hover:bg-parchment-200 transition-colors"
                @click="emit('close')"
              >
                Cancel
              </button>
              <button
                :disabled="saving || !!timeError"
                class="px-4 py-2 rounded-lg text-sm font-medium bg-forest-600 text-parchment-50 hover:bg-forest-700 disabled:opacity-40 transition-colors"
                @click="save"
              >
                {{ saving ? "Saving…" : mode === "edit" ? "Save" : "Add" }}
              </button>
            </div>
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

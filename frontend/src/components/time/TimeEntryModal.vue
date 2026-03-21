<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useTimeStore } from "@/stores/time_tracking";
import type { TimeEntry } from "@/types/time_tracking";

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
  notes: "",
});

const startH = ref<number | "">("");
const startM = ref<number>(0);
const endH = ref<number | "">("");
const endM = ref<number>(0);

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

// ── Time helpers ────────────────────────────────────────────────────────────

const HOURS = Array.from({ length: 24 }, (_, i) => i);
const MINUTES = [0, 15, 30, 45];

function pad2(n: number): string {
  return String(n).padStart(2, "0");
}

function formatHour(h: number): string {
  return pad2(h);
}

// ── Computed ISO strings ─────────────────────────────────────────────────────

/** End is on the next calendar day when its H:M is strictly before start's H:M */
const isOvernight = computed(() => {
  if (startH.value === "" || endH.value === "") return false;
  return (endH.value as number) * 60 + endM.value < (startH.value as number) * 60 + startM.value;
});

const endDate = computed(() => {
  if (!form.value.date || !isOvernight.value) return form.value.date;
  const [y, mo, d] = form.value.date.split("-").map(Number);
  const dt = new Date(y, mo - 1, d + 1);
  return `${dt.getFullYear()}-${pad2(dt.getMonth() + 1)}-${pad2(dt.getDate())}`;
});

const startTimeISO = computed((): string => {
  if (startH.value === "" || !form.value.date) return "";
  return `${form.value.date}T${pad2(startH.value as number)}:${pad2(startM.value)}:00`;
});

const endTimeISO = computed((): string => {
  if (endH.value === "" || !endDate.value) return "";
  return `${endDate.value}T${pad2(endH.value as number)}:${pad2(endM.value)}:00`;
});

// ── Validation ──────────────────────────────────────────────────────────────

const timeError = computed(() => {
  if (!startTimeISO.value || !endTimeISO.value) return null;
  if (endTimeISO.value <= startTimeISO.value) {
    return "End time must be after start time";
  }
  const durationMs = new Date(endTimeISO.value).getTime() - new Date(startTimeISO.value).getTime();
  if (durationMs > 86_400_000) {
    return "Duration cannot exceed 24 hours";
  }
  return null;
});

// ── Pre-fill helpers ─────────────────────────────────────────────────────────

function lastEndTimeForDate(date: string): { h: number; m: number } | null {
  const day = store.days.find((d) => d.date === date);
  if (!day || !day.entries.length) return null;
  const sorted = [...day.entries].sort((a, b) => a.end_time.localeCompare(b.end_time));
  const last = sorted[sorted.length - 1];
  const [, timePart] = last.end_time.split("T");
  const [hStr, mStr] = timePart.split(":");
  const h = parseInt(hStr, 10) % 24;
  const rawM = parseInt(mStr, 10);
  // Snap to nearest 15-min slot
  const m = MINUTES.includes(rawM) ? rawM : Math.min(45, Math.round(rawM / 15) * 15);
  return { h, m };
}

function applyStartPrefill(date: string) {
  const last = lastEndTimeForDate(date);
  if (last) {
    startH.value = last.h;
    startM.value = last.m;
  } else {
    startH.value = "";
    startM.value = 0;
  }
  endH.value = "";
  endM.value = 0;
}

// ── Reset / populate form ────────────────────────────────────────────────────

function resetForm(date?: string) {
  const d = date ?? store.currentMonth + "-01";
  form.value = { date: d, time_category_id: 0, time_subcategory_id: null, notes: "" };
  error.value = null;
  overlapWarning.value = false;
  applyStartPrefill(d);
}

function populateFromEntry(entry: TimeEntry) {
  form.value = {
    date: entry.date,
    time_category_id: entry.time_category_id,
    time_subcategory_id: entry.time_subcategory_id,
    notes: entry.notes ?? "",
  };
  error.value = null;
  overlapWarning.value = false;

  const [, startT] = entry.start_time.split("T");
  const [sh, sm] = startT.split(":").map(Number);
  startH.value = sh;
  startM.value = sm;

  const [, endT] = entry.end_time.split("T");
  const [eh, em] = endT.split(":").map(Number);
  endH.value = eh;
  endM.value = em;
}

// Re-apply prefill when date changes in create mode
watch(
  () => form.value.date,
  (newDate) => {
    if (props.mode === "create" && newDate) {
      applyStartPrefill(newDate);
    }
  },
);

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
  if (!form.value.date || startH.value === "" || endH.value === "") {
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
      start_time: startTimeISO.value,
      end_time: endTimeISO.value,
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
              <!-- Start -->
              <div>
                <label class="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">Start</label>
                <div class="flex gap-1">
                  <select
                    v-model="startH"
                    :disabled="!form.date"
                    class="flex-1 min-w-0 text-sm rounded-lg border border-parchment-300 bg-white px-2 py-2 text-slate-800 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none disabled:opacity-50"
                  >
                    <option value="" disabled>Hr</option>
                    <option v-for="h in HOURS" :key="h" :value="h">{{ formatHour(h) }}</option>
                  </select>
                  <select
                    v-model="startM"
                    :disabled="!form.date || startH === ''"
                    class="w-16 text-sm rounded-lg border border-parchment-300 bg-white px-2 py-2 text-slate-800 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none disabled:opacity-50"
                  >
                    <option v-for="m in MINUTES" :key="m" :value="m">:{{ pad2(m) }}</option>
                  </select>
                </div>
              </div>

              <!-- End -->
              <div>
                <label class="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                  End
                  <span v-if="isOvernight" class="text-[10px] font-medium normal-case tracking-normal text-slate-400 bg-slate-100 px-1 rounded">+1 day</span>
                </label>
                <div class="flex gap-1">
                  <select
                    v-model="endH"
                    :disabled="!form.date"
                    class="flex-1 min-w-0 text-sm rounded-lg border border-parchment-300 bg-white px-2 py-2 text-slate-800 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none disabled:opacity-50"
                  >
                    <option value="" disabled>Hr</option>
                    <option v-for="h in HOURS" :key="h" :value="h">{{ formatHour(h) }}</option>
                  </select>
                  <select
                    v-model="endM"
                    :disabled="!form.date || endH === ''"
                    class="w-16 text-sm rounded-lg border border-parchment-300 bg-white px-2 py-2 text-slate-800 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none disabled:opacity-50"
                  >
                    <option v-for="m in MINUTES" :key="m" :value="m">:{{ pad2(m) }}</option>
                  </select>
                </div>
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

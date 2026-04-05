<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useTimeStore } from "@/modules/time_tracking/store";
import { formatTime, formatDuration, clippedMinutesForDate } from "@/modules/time_tracking/utils";
import { useDayEntries } from "@/modules/time_tracking/useDayEntries";
import type { TimeEntry } from "@/modules/time_tracking/types";
import TimeEntryModal from "@/modules/time_tracking/components/TimeEntryModal.vue";

const d = new Date();
const today = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;

const store = useTimeStore();
const showModal = ref(false);
const modalMode = ref<"create" | "edit">("create");
const editingEntry = ref<TimeEntry | null>(null);

const todayData = useDayEntries(today);
const todayEntries = computed(
  () => todayData.value ?? { date: today, entries: [], total_minutes: 0, has_overlap: false },
);

function openCreate() {
  modalMode.value = "create";
  editingEntry.value = null;
  showModal.value = true;
}

function openEdit(entry: TimeEntry) {
  modalMode.value = "edit";
  editingEntry.value = entry;
  showModal.value = true;
}

onMounted(() => store.fetchAll());
</script>

<template>
  <section
    class="bg-parchment-50 border border-parchment-300 rounded-xl overflow-hidden shadow-sm flex flex-col h-full"
  >
    <!-- Header -->
    <div class="flex items-center justify-between px-4 py-3 border-b border-parchment-200 shrink-0">
      <div class="flex items-center gap-2">
        <div class="w-7 h-7 rounded-md bg-forest-700 flex items-center justify-center shrink-0">
          <svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.5" class="w-4 h-4">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h2 class="font-semibold text-slate-800 text-sm">Time Today</h2>
        <span v-if="todayEntries.total_minutes > 0" class="text-xs text-slate-400 font-mono">
          {{ formatDuration(todayEntries.total_minutes) }} tracked
        </span>
      </div>
      <RouterLink to="/time" class="text-xs text-forest-600 hover:text-forest-700 transition-colors"
        >View all →</RouterLink
      >
    </div>

    <!-- Content -->
    <div v-if="store.loading" class="flex-1 flex items-center justify-center text-sm text-slate-400">Loading…</div>
    <div v-else class="flex flex-col flex-1 min-h-0">
      <!-- Empty state -->
      <div v-if="!todayEntries.entries.length" class="flex-1 flex flex-col items-center justify-center gap-2 px-4 py-6">
        <p class="text-sm text-slate-400 italic">No entries for today.</p>
        <button class="text-xs font-medium text-forest-600 hover:text-forest-700 transition-colors" @click="openCreate">
          + Add Entry
        </button>
      </div>

      <template v-else>
        <!-- Mobile: card list -->
        <div class="sm:hidden flex-1 overflow-y-auto divide-y divide-parchment-200">
          <div
            v-for="entry in todayEntries.entries"
            :key="entry.id"
            class="px-4 py-3 hover:bg-parchment-100 cursor-pointer transition-colors"
            @click="openEdit(entry)"
          >
            <div class="flex items-center gap-2 mb-1 flex-wrap">
              <span
                class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium text-white"
                :style="{ backgroundColor: entry.category.color }"
                >{{ entry.category.name }}</span
              >
              <span v-if="entry.subcategory" class="text-xs text-slate-500">{{ entry.subcategory.name }}</span>
            </div>
            <div class="text-xs font-mono text-slate-400">
              {{ formatTime(entry.start_time) }} – {{ formatTime(entry.end_time) }} ·
              {{ formatDuration(clippedMinutesForDate(entry, today)) }}
            </div>
            <p v-if="entry.notes" class="text-xs text-slate-400 mt-0.5 truncate">{{ entry.notes }}</p>
          </div>
        </div>

        <!-- Desktop: table -->
        <div class="hidden sm:block flex-1 overflow-y-auto">
          <table class="w-full text-sm">
            <thead class="bg-parchment-100 border-b border-parchment-200 sticky top-0">
              <tr>
                <th class="text-left px-4 py-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
                  Category
                </th>
                <th class="text-left px-4 py-2 text-xs font-semibold uppercase tracking-wider text-slate-500">Sub</th>
                <th class="text-left px-4 py-2 text-xs font-semibold uppercase tracking-wider text-slate-500 font-mono">
                  Time
                </th>
                <th class="text-left px-4 py-2 text-xs font-semibold uppercase tracking-wider text-slate-500 font-mono">
                  Duration
                </th>
                <th class="px-4 py-2 w-12" />
              </tr>
            </thead>
            <tbody class="divide-y divide-parchment-200">
              <tr
                v-for="entry in todayEntries.entries"
                :key="entry.id"
                class="hover:bg-parchment-100 transition-colors"
              >
                <td class="px-4 py-2.5">
                  <span
                    class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium text-white whitespace-nowrap"
                    :style="{ backgroundColor: entry.category.color }"
                    >{{ entry.category.name }}</span
                  >
                </td>
                <td class="px-4 py-2.5 text-sm text-slate-500">{{ entry.subcategory?.name ?? "—" }}</td>
                <td class="px-4 py-2.5 text-xs font-mono text-slate-600 whitespace-nowrap">
                  {{ formatTime(entry.start_time) }} – {{ formatTime(entry.end_time) }}
                </td>
                <td class="px-4 py-2.5 text-xs font-mono text-slate-600">
                  {{ formatDuration(clippedMinutesForDate(entry, today)) }}
                </td>
                <td class="px-4 py-2.5">
                  <button
                    class="p-1 rounded text-slate-400 hover:text-slate-700 hover:bg-parchment-200 transition-colors"
                    title="Edit"
                    @click="openEdit(entry)"
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
            </tbody>
          </table>
        </div>

        <!-- Add entry footer -->
        <div class="px-4 py-3 border-t border-parchment-200 shrink-0">
          <button
            class="text-xs font-medium text-forest-600 hover:text-forest-700 transition-colors"
            @click="openCreate"
          >
            + Add Entry
          </button>
        </div>
      </template>
    </div>
  </section>

  <TimeEntryModal
    :open="showModal"
    :mode="modalMode"
    :entry="editingEntry"
    :default-date="today"
    @close="showModal = false"
  />
</template>

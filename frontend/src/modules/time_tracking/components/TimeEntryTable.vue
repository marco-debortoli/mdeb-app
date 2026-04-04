<script setup lang="ts">
import type { DayEntries, TimeEntry } from "@/modules/time_tracking/types";
import { formatTime, formatDuration, isNextDay, formatDayHeader } from "@/modules/time_tracking/utils";

defineProps<{
  day: DayEntries;
}>();

const emit = defineEmits<{
  create: [date: string];
  edit: [entry: TimeEntry];
}>();
</script>

<template>
  <div class="bg-parchment-50 border border-parchment-300 rounded-xl overflow-hidden">
    <!-- Day header -->
    <div class="flex items-center justify-between px-4 py-3 border-b border-parchment-200">
      <div class="flex items-center gap-3">
        <span class="text-sm font-semibold text-slate-700">{{ formatDayHeader(day.date) }}</span>
        <span v-if="day.total_minutes > 0" class="text-xs text-slate-400 font-mono">
          {{ formatDuration(day.total_minutes) }} tracked
        </span>
        <!-- Overlap warning -->
        <span
          v-if="day.has_overlap"
          title="Some entries on this day overlap"
          class="inline-flex items-center gap-0.5 text-amber-600 text-xs font-medium"
        >
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
            />
          </svg>
          Overlap
        </span>
      </div>
      <button
        class="text-xs font-medium text-forest-600 hover:text-forest-700 transition-colors"
        @click="emit('create', day.date)"
      >
        + Add Entry
      </button>
    </div>

    <!-- Empty state -->
    <div v-if="!day.entries.length" class="px-4 py-5 text-sm text-slate-400 text-center italic">
      No entries recorded.
    </div>

    <!-- Mobile: card list -->
    <div v-else class="sm:hidden divide-y divide-parchment-200">
      <div
        v-for="entry in day.entries"
        :key="entry.id"
        class="px-4 py-3 hover:bg-parchment-100 active:bg-parchment-100 transition-colors cursor-pointer"
        @click="emit('edit', entry)"
      >
        <div class="flex items-start justify-between gap-2">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1 flex-wrap">
              <!-- Category pill -->
              <span
                class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium text-white"
                :style="{ backgroundColor: entry.category.color }"
              >
                {{ entry.category.name }}
              </span>
              <span v-if="entry.subcategory" class="text-xs text-slate-500">
                {{ entry.subcategory.name }}
              </span>
            </div>
            <div class="flex items-center gap-2 text-xs text-slate-400 font-mono">
              <span
                >{{ formatTime(entry.start_time) }} – {{ formatTime(entry.end_time)
                }}<span v-if="isNextDay(entry.start_time, entry.end_time)" class="ml-0.5 text-slate-300"
                  >+1d</span
                ></span
              >
              <span class="text-slate-300">·</span>
              <span>{{ formatDuration(entry.duration_minutes) }}</span>
            </div>
            <p v-if="entry.notes" class="text-xs text-slate-400 mt-0.5 truncate" :title="entry.notes">
              {{ entry.notes }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Desktop: table -->
    <div v-if="day.entries.length" class="hidden sm:block">
      <table class="w-full text-sm">
        <thead class="bg-parchment-100 border-b border-parchment-200">
          <tr>
            <th class="text-left px-4 py-2 text-xs font-semibold uppercase tracking-wider text-slate-500">Category</th>
            <th class="text-left px-4 py-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
              Subcategory
            </th>
            <th class="text-left px-4 py-2 text-xs font-semibold uppercase tracking-wider text-slate-500 font-mono">
              Start
            </th>
            <th class="text-left px-4 py-2 text-xs font-semibold uppercase tracking-wider text-slate-500 font-mono">
              End
            </th>
            <th class="text-left px-4 py-2 text-xs font-semibold uppercase tracking-wider text-slate-500 font-mono">
              Duration
            </th>
            <th class="text-left px-4 py-2 text-xs font-semibold uppercase tracking-wider text-slate-500">Notes</th>
            <th class="px-4 py-2 w-16" />
          </tr>
        </thead>
        <tbody class="divide-y divide-parchment-200">
          <tr v-for="entry in day.entries" :key="entry.id" class="hover:bg-parchment-100 transition-colors">
            <!-- Category pill -->
            <td class="px-4 py-2.5">
              <span
                class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium text-white whitespace-nowrap"
                :style="{ backgroundColor: entry.category.color }"
              >
                {{ entry.category.name }}
              </span>
            </td>
            <!-- Subcategory -->
            <td class="px-4 py-2.5 text-sm text-slate-500">
              {{ entry.subcategory?.name ?? "—" }}
            </td>
            <!-- Start -->
            <td class="px-4 py-2.5 text-sm font-mono text-slate-600 whitespace-nowrap">
              {{ formatTime(entry.start_time) }}
            </td>
            <!-- End -->
            <td class="px-4 py-2.5 text-sm font-mono text-slate-600 whitespace-nowrap">
              {{ formatTime(entry.end_time)
              }}<span v-if="isNextDay(entry.start_time, entry.end_time)" class="text-xs text-slate-400 ml-0.5"
                >+1d</span
              >
            </td>
            <!-- Duration -->
            <td class="px-4 py-2.5 text-sm font-mono text-slate-600 whitespace-nowrap">
              {{ formatDuration(entry.duration_minutes) }}
            </td>
            <!-- Notes -->
            <td class="px-4 py-2.5 text-sm text-slate-400 max-w-[180px]">
              <span v-if="entry.notes" class="truncate block" :title="entry.notes">{{ entry.notes }}</span>
              <span v-else class="text-slate-300">—</span>
            </td>
            <!-- Actions -->
            <td class="px-4 py-2.5">
              <button
                class="p-1 rounded text-slate-400 hover:text-slate-700 hover:bg-parchment-200 transition-colors"
                title="Edit"
                @click="emit('edit', entry)"
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
  </div>
</template>

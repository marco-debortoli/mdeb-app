<script setup lang="ts">
import { computed } from "vue";
import { marked } from "marked";
import type { DayProfile } from "@/types/timeline";
import { formatDuration, formatTime, isNextDay, clippedMinutesForDate } from "@/utils/time_tracking";
import { MONTH_NAMES, DAY_NAMES } from "@/utils/date";

const props = defineProps<{
  date: string;
  profile: DayProfile | null;
  loading: boolean;
}>();

const emit = defineEmits<{
  close: [];
}>();

// ── Helpers ───────────────────────────────────────────────────────────────────

const formattedDate = computed(() => {
  const [y, m, d] = props.date.split("-").map(Number);
  const dt = new Date(y, m - 1, d);
  return `${DAY_NAMES[dt.getDay()]}, ${d} ${MONTH_NAMES[m - 1]} ${y}`;
});

const renderedJournal = computed(() => {
  if (!props.profile?.journal?.content) return "";
  return marked(props.profile.journal.content) as string;
});

function formatAmount(amount: string, type: string): string {
  const n = parseFloat(amount);
  const formatted = Math.abs(n).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  switch(type) {
    case "credit":
      return `-$${formatted}`;
    case "transfer":
      return `$${formatted}`;
    default:
      return `+$${formatted}`
  }
}

function amountClass(type: string): string {
  switch(type) {
    case "debit":
      return "text-forest-600 font-medium";
    case "credit":
      return "text-red-600 font-medium";
    default:
      return "font-medium"
  }
}
</script>

<template>
  <!-- Backdrop -->
  <div class="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/40" @click.self="emit('close')">
    <!-- Panel -->
    <div
      class="relative w-full sm:max-w-2xl max-h-[92vh] sm:max-h-[88vh] bg-parchment-50 sm:rounded-xl rounded-t-xl flex flex-col overflow-hidden shadow-2xl"
    >
      <!-- Header -->
      <div
        class="flex items-center justify-between px-5 py-4 border-b border-parchment-200 bg-forest-800 text-parchment-100 shrink-0 rounded-t-xl"
      >
        <div>
          <p class="text-xs font-medium text-parchment-300 uppercase tracking-widest mb-0.5">Day Profile</p>
          <h2 class="text-lg font-semibold">{{ formattedDate }}</h2>
        </div>
        <button class="p-2 rounded-lg hover:bg-forest-700 transition-colors" aria-label="Close" @click="emit('close')">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Scrollable body -->
      <div class="flex-1 overflow-y-auto p-5 space-y-5">
        <!-- Loading skeleton -->
        <div v-if="loading" class="space-y-4">
          <div v-for="i in 4" :key="i" class="bg-parchment-100 rounded-lg h-24 animate-pulse" />
        </div>

        <template v-else-if="profile">
          <!-- ── Journal ──────────────────────────────────────────────────── -->
          <section class="bg-white rounded-lg border border-parchment-200 overflow-hidden">
            <div class="flex items-center gap-2 px-4 py-2.5 bg-forest-50 border-b border-parchment-200">
              <span class="w-2.5 h-2.5 rounded-full bg-forest-500 shrink-0"></span>
              <h3 class="text-sm font-semibold text-forest-800 uppercase tracking-wider">Journal</h3>
              <!-- Star rating -->
              <div v-if="profile.rating" class="ml-auto flex gap-0.5">
                <svg
                  v-for="n in 5"
                  :key="n"
                  class="w-4 h-4"
                  :class="n <= profile.rating.rating ? 'text-earth-500' : 'text-parchment-300'"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
                  />
                </svg>
              </div>
            </div>
            <div v-if="profile.journal" class="px-4 py-3">
              <div
                class="prose prose-sm max-w-none text-slate-700 prose-headings:text-slate-800 prose-a:text-forest-600"
                v-html="renderedJournal"
              />
            </div>
            <div v-else class="px-4 py-4 text-sm text-parchment-400 italic">No journal entry for this day.</div>
          </section>

          <!-- ── Finance ─────────────────────────────────────────────────── -->
          <section class="bg-white rounded-lg border border-parchment-200 overflow-hidden">
            <div class="flex items-center gap-2 px-4 py-2.5 bg-earth-50 border-b border-parchment-200">
              <span class="w-2.5 h-2.5 rounded-full bg-earth-500 shrink-0"></span>
              <h3 class="text-sm font-semibold text-earth-800 uppercase tracking-wider">Finance</h3>
              <span v-if="profile.transactions.length" class="ml-auto text-xs text-parchment-500">
                {{ profile.transactions.length }} transaction{{ profile.transactions.length !== 1 ? "s" : "" }}
              </span>
            </div>
            <div v-if="profile.transactions.length">
              <div
                v-for="tx in profile.transactions"
                :key="tx.id"
                class="flex items-center gap-3 px-4 py-2.5 border-b border-parchment-100 last:border-b-0"
              >
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-slate-800 truncate">
                    {{ tx.merchant?.name ?? tx.category.name }}
                  </p>
                  <p class="text-xs text-parchment-500 truncate">
                    <template v-if="tx.account">{{ tx.account.name }}</template>
                    <span v-else class="italic">External</span>
                    <span v-if="tx.to_account"> → {{ tx.to_account.name }}</span>
                    · {{ tx.category.name }}
                  </p>
                </div>
                <span :class="amountClass(tx.category.type)">
                  {{ formatAmount(tx.amount, tx.category.type) }}
                </span>
              </div>
            </div>
            <div v-else class="px-4 py-4 text-sm text-parchment-400 italic">No transactions for this day.</div>
          </section>

          <!-- ── Completed Tasks ─────────────────────────────────────────── -->
          <section class="bg-white rounded-lg border border-parchment-200 overflow-hidden">
            <div class="flex items-center gap-2 px-4 py-2.5 bg-slate-50 border-b border-parchment-200">
              <span class="w-2.5 h-2.5 rounded-full bg-slate-500 shrink-0"></span>
              <h3 class="text-sm font-semibold text-slate-700 uppercase tracking-wider">Completed Tasks</h3>
              <span v-if="profile.completed_tasks.length" class="ml-auto text-xs text-parchment-500">
                {{ profile.completed_tasks.length }} task{{ profile.completed_tasks.length !== 1 ? "s" : "" }}
              </span>
            </div>
            <div v-if="profile.completed_tasks.length">
              <div
                v-for="task in profile.completed_tasks"
                :key="task.id"
                class="flex items-start gap-3 px-4 py-2.5 border-b border-parchment-100 last:border-b-0"
              >
                <!-- Checkmark -->
                <svg
                  class="w-4 h-4 text-forest-500 mt-0.5 shrink-0"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <div class="flex-1 min-w-0">
                  <p class="text-sm text-slate-800">{{ task.title }}</p>
                  <div class="flex flex-wrap gap-1.5 mt-1">
                    <span
                      v-if="task.category"
                      class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium text-white"
                      :style="{ backgroundColor: task.category.color }"
                    >
                      {{ task.category.name }}
                    </span>
                    <span v-if="task.project" class="text-xs text-parchment-500">{{ task.project.name }}</span>
                    <span v-if="task.priority === 'URGENT'" class="text-xs text-red-500 font-medium">Urgent</span>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="px-4 py-4 text-sm text-parchment-400 italic">No tasks completed on this day.</div>
          </section>

          <!-- ── Time Entries ────────────────────────────────────────────── -->
          <section class="bg-white rounded-lg border border-parchment-200 overflow-hidden">
            <div class="flex items-center gap-2 px-4 py-2.5 bg-blue-50 border-b border-parchment-200">
              <span class="w-2.5 h-2.5 rounded-full bg-blue-500 shrink-0"></span>
              <h3 class="text-sm font-semibold text-blue-800 uppercase tracking-wider">Time Entries</h3>
              <span v-if="profile.time_entries.length" class="ml-auto text-xs text-parchment-500">
                {{ formatDuration(profile.time_entries.reduce((s, e) => s + clippedMinutesForDate(e, date), 0)) }} total
              </span>
            </div>
            <div v-if="profile.time_entries.length">
              <div
                v-for="entry in profile.time_entries"
                :key="entry.id"
                class="flex items-center gap-3 px-4 py-2.5 border-b border-parchment-100 last:border-b-0"
              >
                <span class="w-2.5 h-2.5 rounded-full shrink-0" :style="{ backgroundColor: entry.category.color }" />
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-slate-800">{{ entry.category.name }}</p>
                  <p class="text-xs text-parchment-500">
                    {{ entry.subcategory?.name }}
                    <span v-if="entry.notes" class="italic"> — {{ entry.notes }}</span>
                  </p>
                </div>
                <div class="text-right shrink-0">
                  <p class="text-xs text-slate-600">
                    {{ formatTime(entry.start_time) }} – {{ formatTime(entry.end_time) }}
                    <span v-if="isNextDay(entry.start_time, entry.end_time)" class="text-parchment-400">+1d</span>
                  </p>
                  <p class="text-xs font-medium text-slate-700">{{ formatDuration(clippedMinutesForDate(entry, date)) }}</p>
                </div>
              </div>
            </div>
            <div v-else class="px-4 py-4 text-sm text-parchment-400 italic">No time entries for this day.</div>
          </section>
        </template>

        <!-- Empty state if profile is null and not loading -->
        <div v-else class="flex flex-col items-center justify-center py-12 text-parchment-400">
          <svg class="w-12 h-12 mb-3 opacity-40" fill="none" stroke="currentColor" stroke-width="1" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 9v7.5"
            />
          </svg>
          <p class="text-sm">No data available for this day.</p>
        </div>
      </div>
    </div>
  </div>
</template>

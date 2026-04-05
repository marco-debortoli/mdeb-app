<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import EasyMDE from "easymde";
import { marked } from "marked";
import { useJournalStore } from "@/modules/journal/store";
import MiniDatePicker from "@/shared/components/MiniDatePicker.vue";
import { MONTH_NAMES } from "@/shared/utils/date";

// ── Date helpers ───────────────────────────────────────────────────────────────

function toISODate(d: Date): string {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function todayISO(): string {
  return toISODate(new Date());
}

function parseDate(iso: string): Date {
  // Parse as local date (avoid UTC shift)
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(y, m - 1, d);
}

function shiftDate(iso: string, days: number): string {
  const d = parseDate(iso);
  d.setDate(d.getDate() + days);
  return toISODate(d);
}

function formatDateHeader(iso: string): string {
  const d = parseDate(iso);
  const dayName = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][d.getDay()];
  return `${dayName}, ${d.getDate()} ${MONTH_NAMES[d.getMonth()]} ${d.getFullYear()}`;
}

// ── Store & state ──────────────────────────────────────────────────────────────

const store = useJournalStore();

const currentDate = ref<string>(todayISO());
const writeMode = ref(true);
const showDatePicker = ref(false);

// Save status: 'idle' | 'saving' | 'saved' | 'error'
const saveStatus = ref<"idle" | "saving" | "saved" | "error">("idle");
let saveTimer: ReturnType<typeof setTimeout> | null = null;
let idleTimer: ReturnType<typeof setTimeout> | null = null;

// ── EasyMDE ───────────────────────────────────────────────────────────────────

const textareaRef = ref<HTMLTextAreaElement | null>(null);
let mde: EasyMDE | null = null;

function initMDE(content: string) {
  if (!textareaRef.value) return;
  if (mde) {
    mde.toTextArea();
    mde = null;
  }
  textareaRef.value.value = content;
  mde = new EasyMDE({
    element: textareaRef.value,
    autofocus: true,
    spellChecker: false,
    status: false, // disable built-in status bar (we have our own)
    toolbar: [
      "bold",
      "italic",
      "heading",
      "|",
      "quote",
      "unordered-list",
      "ordered-list",
      "|",
      "link",
      "horizontal-rule",
      "|",
      "preview",
      "guide",
    ],
    minHeight: "400px",
    placeholder: "Write your thoughts for today…",
  });
  mde.codemirror.on("change", () => {
    scheduleAutoSave(mde!.value());
  });
}

function destroyMDE() {
  if (mde) {
    mde.toTextArea();
    mde = null;
  }
}

function scheduleAutoSave(content: string) {
  if (saveTimer) clearTimeout(saveTimer);
  if (idleTimer) clearTimeout(idleTimer);
  saveStatus.value = "saving";
  saveTimer = setTimeout(async () => {
    try {
      await store.saveEntry(currentDate.value, content);
      saveStatus.value = "saved";
      idleTimer = setTimeout(() => {
        saveStatus.value = "idle";
      }, 2500);
    } catch {
      saveStatus.value = "error";
    }
  }, 1000);
}

// ── Date navigation ────────────────────────────────────────────────────────────

async function navigateTo(date: string) {
  // Flush any pending auto-save before navigating away
  if (saveTimer) {
    clearTimeout(saveTimer);
    saveTimer = null;
    if (mde) {
      try {
        await store.saveEntry(currentDate.value, mde.value());
      } catch {
        /* ignore */
      }
    }
  }
  destroyMDE();
  currentDate.value = date;
  showDatePicker.value = false;
  await loadDate(date);
}

function prevDay() {
  navigateTo(shiftDate(currentDate.value, -1));
}
function nextDay() {
  navigateTo(shiftDate(currentDate.value, 1));
}
const isToday = computed(() => currentDate.value === todayISO());

async function loadDate(date: string) {
  await store.fetchAll(date);
  // Default mode: write if no entry, read if entry exists
  writeMode.value = !store.entry;
  if (writeMode.value) {
    await nextTick();
    initMDE(store.entry?.content ?? "");
  }
}

watch(writeMode, async (write) => {
  if (write) {
    await nextTick();
    initMDE(store.entry?.content ?? "");
  } else {
    destroyMDE();
  }
});

onMounted(() => loadDate(currentDate.value));
onBeforeUnmount(() => {
  if (saveTimer) clearTimeout(saveTimer);
  if (idleTimer) clearTimeout(idleTimer);
  destroyMDE();
});

// ── Markdown preview ───────────────────────────────────────────────────────────

const renderedContent = computed(() => {
  const content = store.entry?.content ?? "";
  if (!content.trim()) return "";
  return marked(content) as string;
});

// ── Star rating ────────────────────────────────────────────────────────────────

const hoverRating = ref(0);
const currentRating = computed(() => store.rating?.rating ?? 0);

async function setRating(value: number) {
  try {
    await store.saveRating(currentDate.value, value);
  } catch {
    // rating save failure is non-critical
  }
}

// ── Mini date picker ───────────────────────────────────────────────────────────

// ── "On This Day" expand state ────────────────────────────────────────────────

const expandedPastYears = ref<Set<number>>(new Set());

function toggleExpand(id: number) {
  const next = new Set(expandedPastYears.value);
  if (next.has(id)) next.delete(id);
  else next.add(id);
  expandedPastYears.value = next;
}
</script>

<template>
  <div class="flex flex-col md:flex-row gap-6 max-w-6xl mx-auto" @click.self="showDatePicker = false">
    <!-- ── Main column ──────────────────────────────────────────────────────── -->
    <div class="flex-1 min-w-0">
      <!-- Header -->
      <div class="flex flex-wrap items-center gap-3 mb-5">
        <!-- Day navigation + date title -->
        <div class="flex items-center gap-1">
          <button
            class="p-1.5 rounded-lg text-slate-400 hover:bg-parchment-200 hover:text-slate-700 transition-colors"
            title="Previous day"
            @click="prevDay"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
          </button>

          <!-- Date button opens mini-picker -->
          <div class="relative">
            <button
              class="px-3 py-1.5 rounded-lg text-xl font-semibold text-slate-800 hover:bg-parchment-200 transition-colors leading-tight"
              @click.stop="showDatePicker = !showDatePicker"
            >
              {{ formatDateHeader(currentDate) }}
            </button>

            <!-- Mini date picker popup -->
            <MiniDatePicker
              :show="showDatePicker"
              :current-date="currentDate"
              :dates-with-entries="store.datesWithEntries"
              @select="navigateTo"
            />
          </div>

          <button
            :disabled="isToday"
            class="p-1.5 rounded-lg text-slate-400 hover:bg-parchment-200 hover:text-slate-700 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            title="Next day"
            @click="nextDay"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>

        <!-- Star rating -->
        <div class="flex items-center gap-0.5" @mouseleave="hoverRating = 0">
          <button
            v-for="star in 5"
            :key="star"
            class="text-xl leading-none transition-colors p-0.5"
            :class="star <= (hoverRating || currentRating) ? 'text-earth-400' : 'text-parchment-300'"
            :title="`Rate this day ${star} star${star !== 1 ? 's' : ''}`"
            @mouseenter="hoverRating = star"
            @click="setRating(star)"
          >
            ★
          </button>
        </div>

        <!-- Spacer -->
        <div class="flex-1" />

        <!-- Save status -->
        <span
          class="text-xs transition-opacity"
          :class="{
            'text-slate-400 opacity-100': saveStatus === 'saving',
            'text-forest-600 opacity-100': saveStatus === 'saved',
            'text-red-500 opacity-100': saveStatus === 'error',
            'opacity-0': saveStatus === 'idle',
          }"
        >
          <template v-if="saveStatus === 'saving'">Saving…</template>
          <template v-else-if="saveStatus === 'saved'">Saved</template>
          <template v-else-if="saveStatus === 'error'">Save failed</template>
        </span>

        <!-- Read/write toggle -->
        <button
          :title="writeMode ? 'Switch to read mode' : 'Switch to edit mode'"
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium border transition-colors"
          :class="
            writeMode
              ? 'border-forest-300 bg-forest-50 text-forest-700 hover:bg-forest-100'
              : 'border-parchment-300 bg-parchment-50 text-slate-600 hover:bg-parchment-100'
          "
          @click="writeMode = !writeMode"
        >
          <svg
            v-if="writeMode"
            class="w-4 h-4"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"
            />
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125"
            />
          </svg>
          {{ writeMode ? "Preview" : "Edit" }}
        </button>
      </div>

      <!-- Loading / error -->
      <div v-if="store.loading" class="text-sm text-slate-400 py-16 text-center">Loading…</div>
      <div v-else-if="store.error" class="text-sm text-red-600 bg-red-50 rounded-xl px-4 py-3">
        {{ store.error }}
      </div>

      <template v-else>
        <!-- Write mode: EasyMDE editor -->
        <div :class="['journal-editor', 'mde-editor', { hidden: !writeMode }]">
          <textarea ref="textareaRef" />
        </div>

        <!-- Read mode: rendered markdown -->
        <div v-if="!writeMode" class="bg-parchment-50 border border-parchment-300 rounded-xl px-8 py-6 min-h-64">
          <div v-if="renderedContent" class="prose prose-slate max-w-none mde-preview" v-html="renderedContent" />
          <p v-else class="text-slate-400 text-sm italic">No entry for this day yet.</p>
        </div>
      </template>
    </div>

    <!-- ── On This Day sidebar ──────────────────────────────────────────────── -->
    <aside v-if="store.onThisDayEntries.length > 0" class="w-full md:w-72 md:shrink-0">
      <h3 class="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-3 px-1">On This Day</h3>
      <div class="space-y-3">
        <div
          v-for="past in store.onThisDayEntries"
          :key="past.id"
          class="bg-parchment-50 border border-parchment-300 rounded-xl overflow-hidden"
        >
          <!-- Year header + expand toggle -->
          <button
            class="w-full flex items-center justify-between px-4 py-3 hover:bg-parchment-100 transition-colors text-left"
            @click="toggleExpand(past.id)"
          >
            <span class="text-sm font-semibold text-slate-700">
              {{ parseDate(past.date).getFullYear() }}
            </span>
            <svg
              :class="[
                'w-4 h-4 text-slate-400 transition-transform',
                expandedPastYears.has(past.id) ? 'rotate-180' : '',
              ]"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          <!-- Preview (always visible, truncated) -->
          <div
            v-if="!expandedPastYears.has(past.id)"
            class="px-4 pb-3 text-xs text-slate-500 line-clamp-3 leading-relaxed"
          >
            {{ past.content.slice(0, 200) }}{{ past.content.length > 200 ? "…" : "" }}
          </div>

          <!-- Full rendered markdown (expanded) -->
          <div
            v-else
            class="px-4 pb-4 prose prose-sm prose-slate max-w-none mde-preview border-t border-parchment-200 pt-3"
            v-html="marked(past.content) as string"
          />
        </div>
      </div>
    </aside>
  </div>
</template>

<style scoped>
/* EasyMDE container styling */
.journal-editor :deep(.EasyMDEContainer) {
  @apply rounded-xl overflow-hidden border border-parchment-300;
}

.journal-editor :deep(.CodeMirror) {
  @apply bg-parchment-50 text-slate-800;
  font-family: theme("fontFamily.mono");
  font-size: 0.9rem;
  line-height: 1.7;
  padding: 1.5rem;
  min-height: 400px;
}

.journal-editor :deep(.editor-toolbar) {
  @apply bg-white border-b border-parchment-300;
}

.journal-editor :deep(.editor-toolbar button) {
  @apply text-slate-600;
}

.journal-editor :deep(.editor-toolbar button:hover),
.journal-editor :deep(.editor-toolbar button.active) {
  @apply bg-parchment-100 text-slate-800;
}

.journal-editor :deep(.editor-toolbar i.separator) {
  @apply border-parchment-300;
}

/* Line clamp for sidebar previews */
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

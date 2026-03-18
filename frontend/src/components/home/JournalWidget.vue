<script setup lang="ts">
import { ref, computed, nextTick, onBeforeUnmount, onMounted } from "vue";
import EasyMDE from "easymde";
import { useJournalStore } from "@/stores/journal";

const d = new Date();
const today = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;

const store = useJournalStore();
const textareaRef = ref<HTMLTextAreaElement | null>(null);
let mde: EasyMDE | null = null;

const saveStatus = ref<"idle" | "saving" | "saved" | "error">("idle");
let saveTimer: ReturnType<typeof setTimeout> | null = null;
let idleTimer: ReturnType<typeof setTimeout> | null = null;

const hoverRating = ref(0);
const currentRating = computed(() => store.rating?.rating ?? 0);

function initMDE(content: string) {
  if (!textareaRef.value) return;
  if (mde) {
    mde.toTextArea();
    mde = null;
  }
  mde = new EasyMDE({
    element: textareaRef.value,
    initialValue: content,
    autofocus: false,
    spellChecker: false,
    status: false,
    toolbar: ["bold", "italic", "|", "quote", "unordered-list", "|", "preview"],
    minHeight: "160px",
    placeholder: "Write your thoughts for today…",
  });
  mde.codemirror.on("change", () => scheduleSave(mde!.value()));
}

function scheduleSave(content: string) {
  if (saveTimer) clearTimeout(saveTimer);
  if (idleTimer) clearTimeout(idleTimer);
  saveStatus.value = "saving";
  saveTimer = setTimeout(async () => {
    try {
      await store.saveEntry(today, content);
      saveStatus.value = "saved";
      idleTimer = setTimeout(() => {
        saveStatus.value = "idle";
      }, 2500);
    } catch {
      saveStatus.value = "error";
    }
  }, 1000);
}

async function setRating(value: number) {
  try {
    await store.saveRating(today, value);
  } catch {
    /* non-critical */
  }
}

onMounted(async () => {
  await Promise.all([store.fetchEntry(today), store.fetchRating(today)]);
  await nextTick();
  initMDE(store.entry?.content ?? "");
});

onBeforeUnmount(() => {
  if (saveTimer) clearTimeout(saveTimer);
  if (idleTimer) clearTimeout(idleTimer);
  if (mde) {
    mde.toTextArea();
    mde = null;
  }
});
</script>

<template>
  <section
    class="bg-parchment-50 border border-parchment-300 rounded-xl overflow-hidden shadow-sm flex flex-col h-full"
  >
    <!-- Header -->
    <div class="flex items-center justify-between px-4 py-3 border-b border-parchment-200 shrink-0">
      <div class="flex items-center gap-2">
        <div class="w-7 h-7 rounded-md bg-slate-500 flex items-center justify-center shrink-0">
          <svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.5" class="w-4 h-4">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25"
            />
          </svg>
        </div>
        <h2 class="font-semibold text-slate-800 text-sm">Journal</h2>
        <!-- Star rating -->
        <div class="flex items-center gap-0.5 ml-1" @mouseleave="hoverRating = 0">
          <button
            v-for="star in 5"
            :key="star"
            class="text-base leading-none transition-colors p-0.5"
            :class="star <= (hoverRating || currentRating) ? 'text-earth-400' : 'text-parchment-300'"
            :title="`Rate today ${star} star${star !== 1 ? 's' : ''}`"
            @mouseenter="hoverRating = star"
            @click="setRating(star)"
          >
            ★
          </button>
        </div>
      </div>
      <div class="flex items-center gap-2">
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
          <template v-else-if="saveStatus === 'error'">Error</template>
        </span>
        <RouterLink to="/journal" class="text-xs text-forest-600 hover:text-forest-700 transition-colors"
          >Full view →</RouterLink
        >
      </div>
    </div>

    <!-- Editor (fills remaining height) -->
    <div class="journal-widget-editor flex-1 p-2">
      <textarea ref="textareaRef" />
    </div>
  </section>
</template>

<style scoped>
.journal-widget-editor :deep(.EasyMDEContainer) {
  @apply rounded-lg overflow-hidden border border-parchment-300 h-full flex flex-col;
}

.journal-widget-editor :deep(.editor-toolbar) {
  @apply bg-white border-b border-parchment-300 shrink-0;
}

.journal-widget-editor :deep(.editor-toolbar button) {
  @apply text-slate-600;
}

.journal-widget-editor :deep(.editor-toolbar button:hover),
.journal-widget-editor :deep(.editor-toolbar button.active) {
  @apply bg-parchment-100 text-slate-800;
}

.journal-widget-editor :deep(.editor-toolbar i.separator) {
  @apply border-parchment-300;
}

.journal-widget-editor :deep(.CodeMirror) {
  @apply bg-parchment-50 text-slate-800 flex-1;
  font-family: theme("fontFamily.mono");
  font-size: 0.875rem;
  line-height: 1.7;
  padding: 0.75rem 1rem;
  min-height: 160px;
  height: 100%;
}

.journal-widget-editor :deep(.CodeMirror-scroll) {
  min-height: 160px;
}
</style>

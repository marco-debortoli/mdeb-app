<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from "vue";

export interface SelectOption {
  value: number | null | "";
  label: string;
}

export interface SelectGroup {
  label: string;
  options: SelectOption[];
}

const props = withDefaults(
  defineProps<{
    modelValue: number | null | "";
    options?: SelectOption[];
    groups?: SelectGroup[];
    placeholder?: string;
    pageSize?: number;
  }>(),
  { options: () => [], groups: () => [], placeholder: "— select —", pageSize: 15 },
);

const emit = defineEmits<{
  "update:modelValue": [value: number | null | ""];
}>();

const open = ref(false);
const search = ref("");
const page = ref(1);
const triggerEl = ref<HTMLElement | null>(null);
const panelEl = ref<HTMLElement | null>(null);
const searchInputEl = ref<HTMLInputElement | null>(null);

// Dropdown panel position (teleported to body)
const panelStyle = ref<Record<string, string>>({});

function computePosition() {
  if (!triggerEl.value) return;
  const rect = triggerEl.value.getBoundingClientRect();
  const spaceBelow = window.innerHeight - rect.bottom;
  const spaceAbove = rect.top;
  const panelHeight = 260;

  if (spaceBelow >= panelHeight || spaceBelow >= spaceAbove) {
    panelStyle.value = {
      top: `${rect.bottom + window.scrollY + 4}px`,
      left: `${rect.left + window.scrollX}px`,
      width: `${rect.width}px`,
    };
  } else {
    panelStyle.value = {
      top: `${rect.top + window.scrollY - panelHeight - 4}px`,
      left: `${rect.left + window.scrollX}px`,
      width: `${rect.width}px`,
    };
  }
}

async function openDropdown() {
  open.value = true;
  search.value = "";
  page.value = 1;
  computePosition();
  await nextTick();
  searchInputEl.value?.focus();
}

function closeDropdown() {
  open.value = false;
}

function select(value: number | null | "") {
  emit("update:modelValue", value);
  closeDropdown();
}

// All options flattened (for flat mode)
const allOptions = computed<SelectOption[]>(() => {
  if (props.groups) return props.groups.flatMap((g) => g.options);
  return props.options ?? [];
});

const selectedLabel = computed(() => {
  if (props.modelValue === "" || props.modelValue === undefined) return null;
  return allOptions.value.find((o) => o.value === props.modelValue)?.label ?? null;
});

// Filtered flat options
const filteredOptions = computed(() => {
  const q = search.value.toLowerCase();
  return allOptions.value.filter((o) => o.label.toLowerCase().includes(q));
});

// Filtered groups
const filteredGroups = computed<SelectGroup[]>(() => {
  if (!props.groups) return [];
  const q = search.value.toLowerCase();
  return props.groups
    .map((g) => ({ label: g.label, options: g.options.filter((o) => o.label.toLowerCase().includes(q)) }))
    .filter((g) => g.options.length > 0);
});

const totalFiltered = computed(() =>
  props.groups ? filteredGroups.value.reduce((s, g) => s + g.options.length, 0) : filteredOptions.value.length,
);

const visibleCount = computed(() => page.value * props.pageSize);
const hasMore = computed(() => totalFiltered.value > visibleCount.value);
const remaining = computed(() => totalFiltered.value - visibleCount.value);

// Paginated flat options
const pagedOptions = computed(() => filteredOptions.value.slice(0, visibleCount.value));

// Paginated groups
const pagedGroups = computed<SelectGroup[]>(() => {
  if (!props.groups) return [];
  let remaining = visibleCount.value;
  const result: SelectGroup[] = [];
  for (const g of filteredGroups.value) {
    if (remaining <= 0) break;
    result.push({ label: g.label, options: g.options.slice(0, remaining) });
    remaining -= g.options.length;
  }
  return result;
});

watch(search, () => {
  page.value = 1;
});

// Close on outside click
function onDocClick(e: MouseEvent) {
  if (!open.value) return;
  const target = e.target as Node;
  if (!triggerEl.value?.contains(target) && !panelEl.value?.contains(target)) {
    closeDropdown();
  }
}

// Reposition on scroll/resize
function onScrollResize() {
  if (open.value) computePosition();
}

onMounted(() => {
  document.addEventListener("mousedown", onDocClick);
  window.addEventListener("scroll", onScrollResize, true);
  window.addEventListener("resize", onScrollResize);
});
onBeforeUnmount(() => {
  document.removeEventListener("mousedown", onDocClick);
  window.removeEventListener("scroll", onScrollResize, true);
  window.removeEventListener("resize", onScrollResize);
});
</script>

<template>
  <div class="relative">
    <!-- Trigger -->
    <button
      ref="triggerEl"
      type="button"
      class="w-full text-sm rounded-lg border border-parchment-300 bg-white px-3 py-2 text-left text-slate-800 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none flex items-center justify-between gap-2"
      @click="open ? closeDropdown() : openDropdown()"
    >
      <span :class="selectedLabel ? 'text-slate-800' : 'text-slate-400'">
        {{ selectedLabel ?? placeholder }}
      </span>
      <svg
        class="w-4 h-4 text-slate-400 shrink-0 transition-transform"
        :class="open ? 'rotate-180' : ''"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <!-- Dropdown panel (teleported) -->
    <Teleport to="body">
      <div
        v-if="open"
        ref="panelEl"
        :style="panelStyle"
        class="fixed z-[200] bg-white border border-parchment-300 rounded-lg shadow-lg flex flex-col"
        style="max-height: 260px"
      >
        <!-- Search -->
        <div class="px-2 pt-2 pb-1 border-b border-parchment-100">
          <input
            ref="searchInputEl"
            v-model="search"
            type="text"
            placeholder="Search…"
            class="w-full text-sm rounded border border-parchment-300 bg-parchment-50 px-2 py-1 text-slate-800 focus:border-forest-500 focus:ring-1 focus:ring-forest-500 outline-none"
          />
        </div>

        <!-- Options -->
        <div class="overflow-y-auto flex-1">
          <!-- Flat mode -->
          <template v-if="!groups">
            <div v-if="pagedOptions.length === 0" class="px-3 py-2 text-sm text-slate-400">No results</div>
            <button
              v-for="opt in pagedOptions"
              :key="String(opt.value)"
              type="button"
              class="w-full text-left px-3 py-1.5 text-sm hover:bg-parchment-100 transition-colors"
              :class="modelValue === opt.value ? 'text-forest-700 font-medium bg-parchment-50' : 'text-slate-800'"
              @click="select(opt.value)"
            >
              {{ opt.label }}
            </button>
          </template>

          <!-- Grouped mode -->
          <template v-else>
            <div v-if="filteredGroups.length === 0" class="px-3 py-2 text-sm text-slate-400">No results</div>
            <template v-for="group in pagedGroups" :key="group.label">
              <div
                class="px-3 py-1 text-xs font-semibold text-slate-400 uppercase tracking-wide bg-parchment-50 sticky top-0"
              >
                {{ group.label }}
              </div>
              <button
                v-for="opt in group.options"
                :key="String(opt.value)"
                type="button"
                class="w-full text-left px-3 py-1.5 text-sm hover:bg-parchment-100 transition-colors"
                :class="modelValue === opt.value ? 'text-forest-700 font-medium bg-parchment-50' : 'text-slate-800'"
                @click="select(opt.value)"
              >
                {{ opt.label }}
              </button>
            </template>
          </template>

          <!-- Load more -->
          <button
            v-if="hasMore"
            type="button"
            class="w-full text-left px-3 py-1.5 text-xs text-forest-600 hover:bg-parchment-100 transition-colors font-medium"
            @click="page++"
          >
            Show {{ remaining }} more…
          </button>
        </div>
      </div>
    </Teleport>
  </div>
</template>

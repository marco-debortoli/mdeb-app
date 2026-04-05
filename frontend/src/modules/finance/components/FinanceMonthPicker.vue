<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { MONTH_NAMES } from "@/shared/utils/date";

const props = defineProps<{
  currentYear: number;
  currentMonth: number;
}>();

const emit = defineEmits<{
  select: [year: number, month: number];
}>();

const monthLabel = () => `${MONTH_NAMES[props.currentMonth - 1]} ${props.currentYear}`;

const open = ref(false);
const pickerYear = ref(props.currentYear);
const rootRef = ref<HTMLElement | null>(null);

function openPicker() {
  pickerYear.value = props.currentYear;
  open.value = true;
}

function selectMonth(month: number) {
  emit("select", pickerYear.value, month);
  open.value = false;
}

function onClickOutside(e: MouseEvent) {
  if (rootRef.value && !rootRef.value.contains(e.target as Node)) {
    open.value = false;
  }
}

onMounted(() => document.addEventListener("mousedown", onClickOutside));
onUnmounted(() => document.removeEventListener("mousedown", onClickOutside));
</script>

<template>
  <div ref="rootRef" class="relative">
    <button
      class="text-lg font-semibold text-slate-800 min-w-[150px] text-center font-mono tracking-wide hover:text-slate-600 transition-colors"
      @click="openPicker"
    >
      {{ monthLabel() }}
    </button>
    <div
      v-if="open"
      class="absolute left-1/2 -translate-x-1/2 top-full mt-1 z-50 bg-white border border-parchment-200 rounded-xl shadow-lg p-3 w-56"
    >
      <!-- Year input -->
      <input
        v-model.number="pickerYear"
        type="number"
        class="w-full mb-2 px-3 py-1.5 text-sm font-mono border border-parchment-200 rounded-lg text-slate-700 focus:outline-none focus:ring-1 focus:ring-forest-400"
      />
      <!-- Month grid -->
      <div class="grid grid-cols-3 gap-1">
        <button
          v-for="(name, i) in MONTH_NAMES"
          :key="i"
          class="px-1 py-1 text-xs font-mono rounded-lg transition-colors"
          :class="
            pickerYear === currentYear && i + 1 === currentMonth
              ? 'bg-forest-600 text-white'
              : 'text-slate-700 hover:bg-parchment-100'
          "
          @click="selectMonth(i + 1)"
        >
          {{ name.slice(0, 3) }}
        </button>
      </div>
    </div>
  </div>
</template>

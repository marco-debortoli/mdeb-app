<script setup lang="ts">
defineProps<{
  open: boolean;
  title: string;
  maxWidth?: string;
  heightClass?: string;
  mobile?: boolean;
}>();

const emit = defineEmits<{
  close: [];
}>();
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="open"
        class="fixed inset-0 z-50 flex justify-center"
        :class="mobile ? 'items-end sm:items-center p-0 sm:p-4' : 'items-center p-4'"
      >
        <div class="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" @click="emit('close')" />
        <div
          class="relative w-full bg-parchment-50 shadow-2xl border border-parchment-300 flex flex-col"
          :class="[
            maxWidth ?? 'max-w-md',
            mobile ? 'rounded-t-xl sm:rounded-xl' : 'rounded-xl',
            heightClass,
          ]"
        >
          <!-- Header -->
          <div class="flex items-center justify-between px-5 py-4 border-b border-parchment-300 shrink-0">
            <h2 class="text-base font-semibold text-slate-800">{{ title }}</h2>
            <button
              class="p-1 rounded-lg text-slate-400 hover:bg-parchment-200 transition-colors"
              @click="emit('close')"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Custom body slot (for table-based layouts) -->
          <template v-if="$slots.body">
            <slot name="body" />
          </template>

          <!-- Standard body + footer -->
          <template v-else>
            <div class="flex-1 overflow-y-auto px-5 py-4 space-y-4">
              <slot />
            </div>
            <div class="flex items-center justify-between px-5 py-4 border-t border-parchment-300 shrink-0">
              <slot name="footer-left"><span /></slot>
              <slot name="footer-right" />
            </div>
          </template>
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

<script setup lang="ts">
import { useRoute } from "vue-router";
import { computed } from "vue";

const route = useRoute();

const pageTitle = computed(() => {
  return (
    String(route.name ?? "Dashboard")
      .charAt(0)
      .toUpperCase() + String(route.name ?? "Dashboard").slice(1)
  );
});

// Simple date display — cartographic coordinate style
const today = new Date();
const dateStr = today.toLocaleDateString("en-CA", {
  year: "numeric",
  month: "long",
  day: "numeric",
});
</script>

<template>
  <header
    class="h-16 bg-parchment-50 border-b border-parchment-300 px-6 flex items-center justify-between shrink-0 shadow-sm"
  >
    <h1 class="text-lg font-semibold text-slate-800 tracking-wide">
      {{ pageTitle }}
    </h1>

    <!-- Right side: date in coordinate-label style (hidden on mobile) -->
    <div class="hidden sm:flex items-center gap-3 text-sm text-slate-500 font-mono">
      <span class="text-earth-500 font-medium">{{ dateStr }}</span>
      <span class="text-earth-500 font-medium">&nbsp;/&nbsp;</span>
      <!-- Elevation/coordinate decoration -->
      <span class="text-parchment-400 select-none">49°N 116°W</span>
    </div>
  </header>
</template>

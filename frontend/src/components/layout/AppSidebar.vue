<script setup lang="ts">
import { useRoute } from "vue-router";
import { useAppStore } from "@/stores/app";

const route = useRoute();
const app = useAppStore();

const navItems = [
  {
    name: "Home",
    path: "/",
    icon: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6",
  },
  { name: "Tasks", path: "/tasks", icon: "M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" },
  {
    name: "Journal",
    path: "/journal",
    icon: "M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25",
  },
  {
    name: "Finance",
    path: "/finance",
    icon: "M12 6v12m-3-2.818.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
  },
  { name: "Time", path: "/time", icon: "M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" },
  {
    name: "Timeline",
    path: "/timeline",
    icon: "M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 9v7.5",
  },
  {
    name: "Notes",
    path: "/notes",
    icon: "M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z",
  },
];

function isActive(path: string) {
  return route.path === path;
}
</script>

<template>
  <aside
    :class="[
      'hidden md:flex flex-col bg-forest-800 text-parchment-100 transition-all duration-300 ease-in-out topo-bg',
      app.sidebarOpen ? 'w-64' : 'w-16',
    ]"
  >
    <!-- Logo / App name -->
    <div class="flex items-center h-16 px-4 border-b border-forest-700 shrink-0">
      <!-- Coordinate-grid icon mark -->
      <div class="flex items-center justify-center w-8 h-8 rounded bg-earth-500 shrink-0">
        <svg
          viewBox="0 0 24 24"
          class="w-5 h-5 text-parchment-100"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path
            d="M9 6.75V15m6-6v8.25m.503 3.498l4.875-2.437c.381-.19.622-.58.622-1.006V4.82c0-.836-.88-1.38-1.628-1.006l-3.869 1.934c-.317.159-.69.159-1.006 0L9.503 3.252a1.125 1.125 0 00-1.006 0L3.622 5.689C3.24 5.88 3 6.27 3 6.695V19.18c0 .836.88 1.38 1.628 1.006l3.869-1.934c.317-.159.69-.159 1.006 0l4.994 2.497c.317.158.69.158 1.006 0z"
          />
        </svg>
      </div>
      <span
        v-if="app.sidebarOpen"
        class="ml-3 text-lg font-semibold tracking-wide text-parchment-100 whitespace-nowrap"
      >
        MDEB
      </span>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 py-4 space-y-1 overflow-y-auto">
      <RouterLink
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        :class="[
          'flex items-center px-4 py-2.5 mx-2 rounded-lg text-sm font-medium transition-colors',
          isActive(item.path)
            ? 'bg-forest-600 text-parchment-50'
            : 'text-parchment-300 hover:bg-forest-700 hover:text-parchment-100',
        ]"
      >
        <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" :d="item.icon" />
        </svg>
        <span v-if="app.sidebarOpen" class="ml-3 whitespace-nowrap">{{ item.name }}</span>
      </RouterLink>
    </nav>

    <!-- Collapse toggle -->
    <div class="border-t border-forest-700 p-3 shrink-0">
      <button
        class="flex items-center justify-center w-full p-2 rounded-lg text-parchment-300 hover:bg-forest-700 hover:text-parchment-100 transition-colors"
        :title="app.sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'"
        @click="app.toggleSidebar()"
      >
        <svg
          :class="['w-5 h-5 transition-transform', app.sidebarOpen ? 'rotate-180' : '']"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" d="M11.25 4.5l7.5 7.5-7.5 7.5m-6-15l7.5 7.5-7.5 7.5" />
        </svg>
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import AppSidebar from "@/shared/components/AppSidebar.vue";
import AppHeader from "@/shared/components/AppHeader.vue";
import { useRoute } from "vue-router";
import { ref } from "vue";

const route = useRoute();

const primaryNav = [
  {
    name: "Dashboard",
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
    name: "Notes",
    path: "/notes",
    icon: "M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z",
  },
];

const moreNav = [
  { name: "Time", path: "/time", icon: "M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" },
  {
    name: "Finance",
    path: "/finance",
    icon: "M12 6v12m-3-2.818.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
  },
  {
    name: "Timeline",
    path: "/timeline",
    icon: "M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 9v7.5",
  },
  {
    name: "Health",
    path: "/health",
    icon: "M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z",
  },
];

const showMore = ref(false);
const isMoreActive = moreNav.some((item) => item.path === route.path);

function toggleMore() {
  showMore.value = !showMore.value;
}

function closeMore() {
  showMore.value = false;
}
</script>

<template>
  <div class="flex h-screen overflow-hidden bg-parchment-100">
    <!-- Sidebar (desktop only) -->
    <AppSidebar />

    <!-- Main content area -->
    <div class="flex flex-col flex-1 min-w-0 overflow-hidden">
      <AppHeader />

      <main class="flex-1 overflow-y-auto grid-bg p-4 md:p-6 pb-24 md:pb-6">
        <RouterView />
      </main>
    </div>

    <!-- "More" slide-up drawer backdrop -->
    <Transition name="fade">
      <div v-if="showMore" class="md:hidden fixed inset-0 bg-black/40 z-40" @click="closeMore" />
    </Transition>

    <!-- "More" slide-up drawer -->
    <Transition name="slide-up">
      <div
        v-if="showMore"
        class="md:hidden fixed bottom-16 inset-x-0 bg-forest-800 border-t border-forest-700 rounded-t-2xl z-50 pb-2"
      >
        <div class="flex items-center justify-between px-4 py-3 border-b border-forest-700">
          <span class="text-parchment-300 text-xs font-semibold uppercase tracking-widest">More</span>
          <button class="text-parchment-400 hover:text-parchment-200 transition-colors" @click="closeMore">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="flex justify-around px-4 py-3">
          <RouterLink
            v-for="item in moreNav"
            :key="item.path"
            :to="item.path"
            class="flex flex-col items-center gap-1 px-4 py-2 rounded-xl transition-colors"
            :class="
              route.path === item.path
                ? 'text-parchment-50 bg-forest-700'
                : 'text-parchment-400 hover:text-parchment-200'
            "
            @click="closeMore"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" :d="item.icon" />
            </svg>
            <span class="text-xs font-medium">{{ item.name }}</span>
          </RouterLink>
        </div>
      </div>
    </Transition>

    <!-- Mobile bottom navigation bar -->
    <nav
      class="md:hidden fixed bottom-0 inset-x-0 bg-forest-800 border-t border-forest-700 flex z-50 safe-area-inset-bottom"
    >
      <RouterLink
        v-for="item in primaryNav"
        :key="item.path"
        :to="item.path"
        class="flex-1 flex flex-col items-center justify-center py-2 gap-0.5 transition-colors"
        :class="route.path === item.path ? 'text-parchment-50' : 'text-parchment-400 hover:text-parchment-200'"
        @click="closeMore"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" :d="item.icon" />
        </svg>
        <span class="text-xs font-medium">{{ item.name }}</span>
      </RouterLink>

      <!-- More button -->
      <button
        class="flex-1 flex flex-col items-center justify-center py-2 gap-0.5 transition-colors"
        :class="isMoreActive || showMore ? 'text-parchment-50' : 'text-parchment-400 hover:text-parchment-200'"
        @click="toggleMore"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M6.75 12a.75.75 0 11-1.5 0 .75.75 0 011.5 0zM12.75 12a.75.75 0 11-1.5 0 .75.75 0 011.5 0zM18.75 12a.75.75 0 11-1.5 0 .75.75 0 011.5 0z"
          />
        </svg>
        <span class="text-xs font-medium">More</span>
      </button>
    </nav>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition:
    transform 0.25s ease,
    opacity 0.25s ease;
}
.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}
</style>

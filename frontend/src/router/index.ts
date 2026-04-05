import { createRouter, createWebHistory } from "vue-router";
import HomeView from "@/views/HomeView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "home",
      component: HomeView,
    },
    { path: "/tasks", name: "tasks", component: () => import("@/modules/tasks/TasksView.vue") },
    { path: "/journal", name: "journal", component: () => import("@/modules/journal/JournalView.vue") },
    { path: "/finance", name: "finance", component: () => import("@/modules/finance/FinanceView.vue") },
    { path: "/time", name: "time", component: () => import("@/modules/time_tracking/TimeView.vue") },
    { path: "/timeline", name: "timeline", component: () => import("@/modules/timeline/TimelineView.vue") },
    { path: "/notes", name: "notes", component: () => import("@/modules/notes/NotesView.vue") },
    { path: "/health", name: "health", component: () => import("@/modules/health/HealthView.vue") },
  ],
});

export default router;

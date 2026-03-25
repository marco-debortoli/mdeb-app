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
    { path: "/tasks", name: "tasks", component: () => import("@/views/TasksView.vue") },
    { path: "/journal", name: "journal", component: () => import("@/views/JournalView.vue") },
    { path: "/finance", name: "finance", component: () => import("@/views/FinanceView.vue") },
    { path: "/time", name: "time", component: () => import("@/views/TimeView.vue") },
    { path: "/timeline", name: "timeline", component: () => import("@/views/TimelineView.vue") },
    { path: "/notes", name: "notes", component: () => import("@/views/NotesView.vue") },
    { path: "/health", name: "health", component: () => import("@/views/HealthView.vue") },
    { path: "/health/overview", name: "health-overview", component: () => import("@/views/HealthOverviewView.vue") },
  ],
});

export default router;

import { ref } from "vue";
import { defineStore } from "pinia";
import { categoryApi, projectApi, taskApi } from "@/api/tasks";
import type { Category, Project, Task, TaskCreate, TaskFilters, TaskSummary, TaskUpdate } from "@/types/tasks";

export const useTasksStore = defineStore("tasks", () => {
  const tasks = ref<TaskSummary[]>([]);
  const categories = ref<Category[]>([]);
  const projects = ref<Project[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const filters = ref<TaskFilters>({
    status: "",
    category_id: "",
    project_id: "",
  });

  // ── Fetch ──────────────────────────────────────────────────────────────────

  async function fetchTasks() {
    loading.value = true;
    error.value = null;
    try {
      tasks.value = await taskApi.list(filters.value);
    } catch (e) {
      error.value = String(e);
    } finally {
      loading.value = false;
    }
  }

  async function fetchCategories() {
    categories.value = await categoryApi.list();
  }

  async function fetchProjects() {
    projects.value = await projectApi.list();
  }

  async function fetchAll() {
    await Promise.all([fetchTasks(), fetchCategories(), fetchProjects()]);
  }

  // ── Task actions ───────────────────────────────────────────────────────────

  async function createTask(data: TaskCreate): Promise<Task> {
    const task = await taskApi.create(data);
    await fetchTasks();
    return task;
  }

  async function updateTask(id: number, data: TaskUpdate): Promise<Task> {
    const task = await taskApi.update(id, data);
    await fetchTasks();
    return task;
  }

  async function deleteTask(id: number): Promise<void> {
    await taskApi.delete(id);
    tasks.value = tasks.value.filter((t) => t.id !== id);
  }

  // ── Category actions ───────────────────────────────────────────────────────

  async function createCategory(name: string, color: string) {
    const cat = await categoryApi.create(name, color);
    categories.value.push(cat);
    categories.value.sort((a, b) => a.name.localeCompare(b.name));
    return cat;
  }

  async function updateCategory(id: number, data: Partial<{ name: string; color: string }>) {
    const cat = await categoryApi.update(id, data);
    const idx = categories.value.findIndex((c) => c.id === id);
    if (idx !== -1) categories.value[idx] = cat;
    return cat;
  }

  async function deleteCategory(id: number) {
    await categoryApi.delete(id);
    categories.value = categories.value.filter((c) => c.id !== id);
    await fetchTasks();
  }

  // ── Project actions ────────────────────────────────────────────────────────

  async function createProject(name: string, description?: string) {
    const proj = await projectApi.create(name, description);
    projects.value.push(proj);
    projects.value.sort((a, b) => a.name.localeCompare(b.name));
    return proj;
  }

  async function updateProject(id: number, data: Partial<{ name: string; description: string | null }>) {
    const proj = await projectApi.update(id, data);
    const idx = projects.value.findIndex((p) => p.id === id);
    if (idx !== -1) projects.value[idx] = proj;
    return proj;
  }

  async function deleteProject(id: number) {
    await projectApi.delete(id);
    projects.value = projects.value.filter((p) => p.id !== id);
    await fetchTasks();
  }

  return {
    tasks,
    categories,
    projects,
    filters,
    loading,
    error,
    fetchTasks,
    fetchCategories,
    fetchProjects,
    fetchAll,
    createTask,
    updateTask,
    deleteTask,
    createCategory,
    updateCategory,
    deleteCategory,
    createProject,
    updateProject,
    deleteProject,
  };
});

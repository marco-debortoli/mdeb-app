import { defineStore } from "pinia";
import { ref } from "vue";
import { healthApi } from "@/api/health";
import type { HealthLog, SyncResponse } from "@/types/health";

export const useHealthStore = defineStore("health", () => {
  const log = ref<HealthLog | null>(null);
  const logs = ref<HealthLog[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function fetchLog(date: string) {
    loading.value = true;
    error.value = null;
    try {
      log.value = await healthApi.getLog(date);
    } catch (e: any) {
      if (e.message?.includes("404")) {
        log.value = null;
      } else {
        error.value = e.message;
      }
    } finally {
      loading.value = false;
    }
  }

  async function fetchLogs(start: string, end: string) {
    loading.value = true;
    error.value = null;
    try {
      logs.value = await healthApi.listLogs(start, end);
    } catch (e: any) {
      error.value = e.message;
    } finally {
      loading.value = false;
    }
  }

  async function saveManual(date: string, energy_rating: number | null, weight_kg: number | null) {
    const result = await healthApi.upsertLog(date, { energy_rating, weight_kg });
    log.value = result;
    return result;
  }

  async function sync(startDate?: string, endDate?: string): Promise<SyncResponse> {
    return healthApi.triggerSync(startDate, endDate);
  }

  return { log, logs, loading, error, fetchLog, fetchLogs, saveManual, sync };
});

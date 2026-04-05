import { ref } from "vue";
import { defineStore } from "pinia";
import {
  accountApi,
  accountValueApi,
  financeCategoryApi,
  merchantApi,
  transactionApi,
  financeSummaryApi,
} from "@/modules/finance/api";
import type {
  FinanceAccount,
  FinanceCategory,
  Merchant,
  MonthlySummary,
  TransactionCreate,
  TransactionUpdate,
} from "@/modules/finance/types";

export const useFinanceStore = defineStore("finance", () => {
  // ── State ──────────────────────────────────────────────────────────────────
  const accounts = ref<FinanceAccount[]>([]);
  const categories = ref<FinanceCategory[]>([]);
  const merchants = ref<Merchant[]>([]);
  const summary = ref<MonthlySummary | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Current month being viewed
  const today = new Date();
  const currentYear = ref(today.getFullYear());
  const currentMonth = ref(today.getMonth() + 1); // 1-indexed

  // ── Fetchers ───────────────────────────────────────────────────────────────

  async function fetchAccounts() {
    accounts.value = await accountApi.list();
  }

  async function fetchCategories() {
    categories.value = await financeCategoryApi.list();
  }

  async function fetchMerchants() {
    merchants.value = await merchantApi.list();
  }

  async function fetchSummary() {
    loading.value = true;
    error.value = null;
    try {
      summary.value = await financeSummaryApi.get(currentYear.value, currentMonth.value);
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : "Failed to load summary";
    } finally {
      loading.value = false;
    }
  }

  async function fetchAll() {
    loading.value = true;
    error.value = null;
    try {
      await Promise.all([fetchAccounts(), fetchCategories(), fetchMerchants()]);
      await fetchSummary();
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : "Failed to load finance data";
    } finally {
      loading.value = false;
    }
  }

  // ── Month navigation ───────────────────────────────────────────────────────

  async function prevMonth() {
    if (currentMonth.value === 1) {
      currentMonth.value = 12;
      currentYear.value -= 1;
    } else {
      currentMonth.value -= 1;
    }
    await fetchSummary();
  }

  async function nextMonth() {
    if (currentMonth.value === 12) {
      currentMonth.value = 1;
      currentYear.value += 1;
    } else {
      currentMonth.value += 1;
    }
    await fetchSummary();
  }

  async function goToMonth(year: number, month: number) {
    currentYear.value = year;
    currentMonth.value = month;
    await fetchSummary();
  }

  // ── Account actions ────────────────────────────────────────────────────────

  async function createAccount(data: Omit<FinanceAccount, "id" | "created_at">) {
    await accountApi.create(data);
    await Promise.all([fetchAccounts(), fetchSummary()]);
  }

  async function updateAccount(id: number, data: Partial<Omit<FinanceAccount, "id" | "created_at">>) {
    await accountApi.update(id, data);
    await Promise.all([fetchAccounts(), fetchSummary()]);
  }

  async function deleteAccount(id: number) {
    await accountApi.delete(id);
    await Promise.all([fetchAccounts(), fetchSummary()]);
  }

  async function upsertAccountValue(accountId: number, amount: string) {
    await accountValueApi.upsert(accountId, currentYear.value, currentMonth.value, amount);
    await fetchSummary();
  }

  // ── Category actions ───────────────────────────────────────────────────────

  async function createCategory(data: Pick<FinanceCategory, "name" | "type">) {
    await financeCategoryApi.create(data);
    await Promise.all([fetchCategories(), fetchSummary()]);
  }

  async function updateCategory(id: number, data: Partial<Pick<FinanceCategory, "name" | "type">>) {
    await financeCategoryApi.update(id, data);
    await Promise.all([fetchCategories(), fetchSummary()]);
  }

  async function deleteCategory(id: number) {
    await financeCategoryApi.delete(id);
    await Promise.all([fetchCategories(), fetchSummary()]);
  }

  // ── Merchant actions ───────────────────────────────────────────────────────

  async function createMerchant(name: string) {
    const merchant = await merchantApi.create(name);
    merchants.value = [...merchants.value, merchant].sort((a, b) => a.name.localeCompare(b.name));
    return merchant;
  }

  async function updateMerchant(id: number, data: Partial<Pick<Merchant, "name" | "archived">>) {
    await merchantApi.update(id, data);
    await fetchMerchants();
  }

  async function deleteMerchant(id: number) {
    await merchantApi.delete(id);
    await fetchMerchants();
  }

  // ── Transaction actions ────────────────────────────────────────────────────

  async function createTransaction(data: TransactionCreate) {
    await transactionApi.create(data);
    await fetchSummary();
  }

  async function updateTransaction(id: number, data: TransactionUpdate) {
    await transactionApi.update(id, data);
    await fetchSummary();
  }

  async function deleteTransaction(id: number) {
    await transactionApi.delete(id);
    await fetchSummary();
  }

  return {
    accounts,
    categories,
    merchants,
    summary,
    loading,
    error,
    currentYear,
    currentMonth,
    fetchAll,
    fetchSummary,
    prevMonth,
    nextMonth,
    goToMonth,
    createAccount,
    updateAccount,
    deleteAccount,
    upsertAccountValue,
    createCategory,
    updateCategory,
    deleteCategory,
    createMerchant,
    updateMerchant,
    deleteMerchant,
    createTransaction,
    updateTransaction,
    deleteTransaction,
  };
});

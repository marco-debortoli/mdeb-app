import type {
  AccountValue,
  FinanceAccount,
  FinanceCategory,
  Merchant,
  MonthlySummary,
  Transaction,
  TransactionCreate,
  TransactionUpdate,
} from "@/modules/finance/types";

const BASE = "/api/finance";

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// ── Accounts ──────────────────────────────────────────────────────────────────

export const accountApi = {
  list: () => request<FinanceAccount[]>(`${BASE}/accounts`),

  create: (data: Omit<FinanceAccount, "id" | "created_at">) =>
    request<FinanceAccount>(`${BASE}/accounts`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  update: (id: number, data: Partial<Omit<FinanceAccount, "id" | "created_at">>) =>
    request<FinanceAccount>(`${BASE}/accounts/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  delete: (id: number) => request<void>(`${BASE}/accounts/${id}`, { method: "DELETE" }),
};

// ── Account Values ─────────────────────────────────────────────────────────────

export const accountValueApi = {
  upsert: (accountId: number, year: number, month: number, amount: string) =>
    request<AccountValue>(`${BASE}/accounts/${accountId}/values/${year}/${month}`, {
      method: "PUT",
      body: JSON.stringify({ amount }),
    }),

  delete: (accountId: number, year: number, month: number) =>
    request<void>(`${BASE}/accounts/${accountId}/values/${year}/${month}`, { method: "DELETE" }),
};

// ── Categories ────────────────────────────────────────────────────────────────

export const financeCategoryApi = {
  list: () => request<FinanceCategory[]>(`${BASE}/categories`),

  create: (data: Pick<FinanceCategory, "name" | "type">) =>
    request<FinanceCategory>(`${BASE}/categories`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  update: (id: number, data: Partial<Pick<FinanceCategory, "name" | "type">>) =>
    request<FinanceCategory>(`${BASE}/categories/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  delete: (id: number) => request<void>(`${BASE}/categories/${id}`, { method: "DELETE" }),
};

// ── Merchants ─────────────────────────────────────────────────────────────────

export const merchantApi = {
  list: () => request<Merchant[]>(`${BASE}/merchants`),

  create: (name: string) =>
    request<Merchant>(`${BASE}/merchants`, {
      method: "POST",
      body: JSON.stringify({ name }),
    }),

  update: (id: number, data: Partial<Pick<Merchant, "name" | "archived">>) =>
    request<Merchant>(`${BASE}/merchants/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  delete: (id: number) => request<void>(`${BASE}/merchants/${id}`, { method: "DELETE" }),
};

// ── Transactions ──────────────────────────────────────────────────────────────

export const transactionApi = {
  list: (year?: number, month?: number) => {
    const params = new URLSearchParams();
    if (year != null) params.set("year", String(year));
    if (month != null) params.set("month", String(month));
    const qs = params.toString();
    return request<Transaction[]>(`${BASE}/transactions${qs ? `?${qs}` : ""}`);
  },

  create: (data: TransactionCreate) =>
    request<Transaction>(`${BASE}/transactions`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  update: (id: number, data: TransactionUpdate) =>
    request<Transaction>(`${BASE}/transactions/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  delete: (id: number) => request<void>(`${BASE}/transactions/${id}`, { method: "DELETE" }),
};

// ── Summary ───────────────────────────────────────────────────────────────────

export const financeSummaryApi = {
  get: (year: number, month: number) => request<MonthlySummary>(`${BASE}/summary?year=${year}&month=${month}`),
};

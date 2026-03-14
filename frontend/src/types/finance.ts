export type AccountType = "debit" | "credit" | "investment" | "other";
export type FinanceCategoryType = "credit" | "debit" | "transfer";

export interface FinanceAccount {
  id: number;
  name: string;
  type: AccountType;
  start_date: string;
  end_date: string | null;
  archived: boolean;
  profit_eligible: boolean;
  created_at: string;
}

export interface AccountValue {
  id: number;
  account_id: number;
  year: number;
  month: number;
  amount: string;
}

export interface FinanceCategory {
  id: number;
  name: string;
  type: FinanceCategoryType;
  created_at: string;
}

export interface Merchant {
  id: number;
  name: string;
  archived: boolean;
  created_at: string;
}

export interface Transaction {
  id: number;
  date: string;
  amount: string;
  account_id: number;
  category_id: number;
  merchant_id: number | null;
  to_account_id: number | null;
  account: FinanceAccount;
  category: FinanceCategory;
  merchant: Merchant | null;
  to_account: FinanceAccount | null;
  created_at: string;
  updated_at: string;
}

export interface TransactionCreate {
  date: string;
  amount: string;
  account_id: number;
  category_id: number;
  merchant_id?: number | null;
  to_account_id?: number | null;
}

export interface TransactionUpdate {
  date?: string;
  amount?: string;
  account_id?: number;
  category_id?: number;
  merchant_id?: number;
  to_account_id?: number | null;
}

export interface AccountMonthlySummary {
  account: FinanceAccount;
  value: AccountValue | null;
  delta: string;
  reconciled: boolean;
}

export interface CategoryMonthlySummary {
  category: FinanceCategory;
  total: string;
}

export interface CategoriesByType {
  credit: CategoryMonthlySummary[];
  debit: CategoryMonthlySummary[];
  transfer: CategoryMonthlySummary[];
}

export interface MonthlySummary {
  year: number;
  month: number;
  transactions: Transaction[];
  accounts: AccountMonthlySummary[];
  categories: CategoriesByType;
  monthly_profit: string;
}

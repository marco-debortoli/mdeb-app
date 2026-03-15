from datetime import date as Date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.finance import AccountType, FinanceCategoryType


# ── Account ───────────────────────────────────────────────────────────────────

class AccountCreate(BaseModel):
    name: str = Field(..., max_length=200)
    type: AccountType
    start_date: Date
    end_date: Date | None = None
    archived: bool = False
    profit_eligible: bool = True


class AccountUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    type: AccountType | None = None
    start_date: Date | None = None
    end_date: Date | None = None
    archived: bool | None = None
    profit_eligible: bool | None = None


class AccountRead(BaseModel):
    id: int
    name: str
    type: AccountType
    start_date: Date
    end_date: Date | None
    archived: bool
    profit_eligible: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── AccountValue ──────────────────────────────────────────────────────────────

class AccountValueUpsert(BaseModel):
    amount: Decimal = Field(..., decimal_places=2)


class AccountValueRead(BaseModel):
    id: int
    account_id: int
    year: int
    month: int
    amount: Decimal

    model_config = {"from_attributes": True}


# ── FinanceCategory ───────────────────────────────────────────────────────────

class FinanceCategoryCreate(BaseModel):
    name: str = Field(..., max_length=100)
    type: FinanceCategoryType


class FinanceCategoryUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    type: FinanceCategoryType | None = None


class FinanceCategoryRead(BaseModel):
    id: int
    name: str
    type: FinanceCategoryType
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Merchant ──────────────────────────────────────────────────────────────────

class MerchantCreate(BaseModel):
    name: str = Field(..., max_length=200)
    archived: bool = False


class MerchantUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    archived: bool | None = None


class MerchantRead(BaseModel):
    id: int
    name: str
    archived: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Transaction ───────────────────────────────────────────────────────────────

class TransactionCreate(BaseModel):
    date: Date
    amount: Decimal = Field(..., decimal_places=2)
    account_id: int | None = None
    category_id: int
    merchant_id: int | None = None
    to_account_id: int | None = None


class TransactionUpdate(BaseModel):
    date: Date | None = None
    amount: Decimal | None = Field(None, decimal_places=2)
    account_id: int | None = None
    category_id: int | None = None
    merchant_id: int | None = None
    to_account_id: int | None = None


class TransactionRead(BaseModel):
    id: int
    date: Date
    amount: Decimal
    description: str | None
    account_id: int | None
    category_id: int
    merchant_id: int | None
    to_account_id: int | None
    account: AccountRead | None
    category: FinanceCategoryRead
    merchant: MerchantRead | None
    to_account: AccountRead | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Monthly Summary ───────────────────────────────────────────────────────────

class AccountMonthlySummary(BaseModel):
    account: AccountRead
    value: AccountValueRead | None
    delta: Decimal
    reconciled: bool

    model_config = {"from_attributes": True}


class CategoryMonthlySummary(BaseModel):
    category: FinanceCategoryRead
    total: Decimal

    model_config = {"from_attributes": True}


class CategoriesByType(BaseModel):
    credit: list[CategoryMonthlySummary]
    debit: list[CategoryMonthlySummary]
    transfer: list[CategoryMonthlySummary]


class MonthlySummary(BaseModel):
    year: int
    month: int
    transactions: list[TransactionRead]
    accounts: list[AccountMonthlySummary]
    categories: CategoriesByType
    monthly_profit: Decimal

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.finance.models import (
    AccountValue, FinanceAccount, FinanceCategory, FinanceCategoryType, Merchant, Transaction,
)
from app.finance.schemas import (
    AccountCreate, AccountMonthlySummary, AccountRead, AccountUpdate, AccountValueRead,
    AccountValueUpsert, CategoriesByType, CategoryMonthlySummary, FinanceCategoryCreate,
    FinanceCategoryRead, FinanceCategoryUpdate, MerchantCreate, MerchantRead, MerchantUpdate,
    MonthlySummary, TransactionCreate, TransactionRead, TransactionUpdate,
)

router = APIRouter()


def _load_transaction_relations():
    return (
        selectinload(Transaction.account),
        selectinload(Transaction.category),
        selectinload(Transaction.merchant),
        selectinload(Transaction.to_account),
    )


# ── Accounts ──────────────────────────────────────────────────────────────────

@router.get("/accounts", response_model=list[AccountRead])
async def list_accounts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FinanceAccount).order_by(FinanceAccount.name))
    return result.scalars().all()


@router.post("/accounts", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
async def create_account(body: AccountCreate, db: AsyncSession = Depends(get_db)):
    account = FinanceAccount(**body.model_dump())
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


@router.get("/accounts/{account_id}", response_model=AccountRead)
async def get_account(account_id: int, db: AsyncSession = Depends(get_db)):
    account = await db.get(FinanceAccount, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.put("/accounts/{account_id}", response_model=AccountRead)
async def update_account(account_id: int, body: AccountUpdate, db: AsyncSession = Depends(get_db)):
    account = await db.get(FinanceAccount, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(account, field, value)
    await db.commit()
    await db.refresh(account)
    return account


@router.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(account_id: int, db: AsyncSession = Depends(get_db)):
    account = await db.get(FinanceAccount, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    await db.delete(account)
    await db.commit()


# ── Account Values ────────────────────────────────────────────────────────────

@router.get("/account-values", response_model=list[AccountValueRead])
async def list_account_values(
    account_id: int | None = Query(None),
    year: int | None = Query(None),
    month: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    q = select(AccountValue)
    if account_id is not None:
        q = q.where(AccountValue.account_id == account_id)
    if year is not None:
        q = q.where(AccountValue.year == year)
    if month is not None:
        q = q.where(AccountValue.month == month)
    result = await db.execute(q)
    return result.scalars().all()


@router.put("/accounts/{account_id}/values/{year}/{month}", response_model=AccountValueRead)
async def upsert_account_value(
    account_id: int,
    year: int,
    month: int,
    body: AccountValueUpsert,
    db: AsyncSession = Depends(get_db),
):
    account = await db.get(FinanceAccount, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    result = await db.execute(
        select(AccountValue).where(
            AccountValue.account_id == account_id,
            AccountValue.year == year,
            AccountValue.month == month,
        )
    )
    av = result.scalar_one_or_none()
    if av:
        av.amount = body.amount
    else:
        av = AccountValue(account_id=account_id, year=year, month=month, amount=body.amount)
        db.add(av)
    await db.commit()
    await db.refresh(av)
    return av


@router.delete("/accounts/{account_id}/values/{year}/{month}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account_value(
    account_id: int, year: int, month: int, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(AccountValue).where(
            AccountValue.account_id == account_id,
            AccountValue.year == year,
            AccountValue.month == month,
        )
    )
    av = result.scalar_one_or_none()
    if not av:
        raise HTTPException(status_code=404, detail="Account value not found")
    await db.delete(av)
    await db.commit()


# ── Categories ────────────────────────────────────────────────────────────────

@router.get("/categories", response_model=list[FinanceCategoryRead])
async def list_finance_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FinanceCategory).order_by(FinanceCategory.name))
    return result.scalars().all()


@router.post("/categories", response_model=FinanceCategoryRead, status_code=status.HTTP_201_CREATED)
async def create_finance_category(body: FinanceCategoryCreate, db: AsyncSession = Depends(get_db)):
    cat = FinanceCategory(**body.model_dump())
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return cat


@router.put("/categories/{category_id}", response_model=FinanceCategoryRead)
async def update_finance_category(
    category_id: int, body: FinanceCategoryUpdate, db: AsyncSession = Depends(get_db)
):
    cat = await db.get(FinanceCategory, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(cat, field, value)
    await db.commit()
    await db.refresh(cat)
    return cat


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_finance_category(category_id: int, db: AsyncSession = Depends(get_db)):
    cat = await db.get(FinanceCategory, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    await db.delete(cat)
    await db.commit()


# ── Merchants ─────────────────────────────────────────────────────────────────

@router.get("/merchants", response_model=list[MerchantRead])
async def list_merchants(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Merchant).order_by(Merchant.name))
    return result.scalars().all()


@router.post("/merchants", response_model=MerchantRead, status_code=status.HTTP_201_CREATED)
async def create_merchant(body: MerchantCreate, db: AsyncSession = Depends(get_db)):
    merchant = Merchant(**body.model_dump())
    db.add(merchant)
    await db.commit()
    await db.refresh(merchant)
    return merchant


@router.put("/merchants/{merchant_id}", response_model=MerchantRead)
async def update_merchant(
    merchant_id: int, body: MerchantUpdate, db: AsyncSession = Depends(get_db)
):
    merchant = await db.get(Merchant, merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(merchant, field, value)
    await db.commit()
    await db.refresh(merchant)
    return merchant


@router.delete("/merchants/{merchant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_merchant(merchant_id: int, db: AsyncSession = Depends(get_db)):
    merchant = await db.get(Merchant, merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    await db.delete(merchant)
    await db.commit()


# ── Transactions ──────────────────────────────────────────────────────────────

@router.get("/transactions", response_model=list[TransactionRead])
async def list_transactions(
    year: int | None = Query(None),
    month: int | None = Query(None),
    account_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    q = select(Transaction).options(*_load_transaction_relations())
    if year is not None and month is not None:
        from sqlalchemy import extract
        q = q.where(
            extract("year", Transaction.date) == year,
            extract("month", Transaction.date) == month,
        )
    if account_id is not None:
        q = q.where(Transaction.account_id == account_id)
    q = q.order_by(Transaction.date.desc(), Transaction.created_at.desc())
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/transactions", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
async def create_transaction(body: TransactionCreate, db: AsyncSession = Depends(get_db)):
    txn = Transaction(**body.model_dump())
    db.add(txn)
    await db.commit()
    await db.refresh(txn)
    result = await db.execute(
        select(Transaction).where(Transaction.id == txn.id).options(*_load_transaction_relations())
    )
    return result.scalar_one()


@router.get("/transactions/{transaction_id}", response_model=TransactionRead)
async def get_transaction(transaction_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Transaction)
        .where(Transaction.id == transaction_id)
        .options(*_load_transaction_relations())
    )
    txn = result.scalar_one_or_none()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return txn


@router.put("/transactions/{transaction_id}", response_model=TransactionRead)
async def update_transaction(
    transaction_id: int, body: TransactionUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Transaction)
        .where(Transaction.id == transaction_id)
        .options(*_load_transaction_relations())
    )
    txn = result.scalar_one_or_none()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(txn, field, value)
    await db.commit()
    result = await db.execute(
        select(Transaction)
        .where(Transaction.id == transaction_id)
        .options(*_load_transaction_relations())
    )
    return result.scalar_one()


@router.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(transaction_id: int, db: AsyncSession = Depends(get_db)):
    txn = await db.get(Transaction, transaction_id)
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    await db.delete(txn)
    await db.commit()


# ── Monthly Summary ───────────────────────────────────────────────────────────

@router.get("/summary", response_model=MonthlySummary)
async def monthly_summary(
    year: int = Query(...),
    month: int = Query(...),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import extract

    # All transactions for the month
    txn_result = await db.execute(
        select(Transaction)
        .options(*_load_transaction_relations())
        .where(
            extract("year", Transaction.date) == year,
            extract("month", Transaction.date) == month,
        )
        .order_by(Transaction.date.desc(), Transaction.created_at.desc())
    )
    transactions = txn_result.scalars().all()

    # Compute per-account transaction deltas.
    # Debit category = money in (+), credit category = money out (-).
    # For transfers: source account loses money (-), destination account gains money (+).
    account_deltas: dict[int, Decimal] = {}
    for txn in transactions:
        if txn.account_id is not None:
            account_deltas.setdefault(txn.account_id, Decimal("0"))
            if txn.category.type == FinanceCategoryType.DEBIT:
                account_deltas[txn.account_id] += txn.amount
            elif txn.category.type == FinanceCategoryType.CREDIT:
                account_deltas[txn.account_id] -= txn.amount
            else:  # TRANSFER
                account_deltas[txn.account_id] -= txn.amount
        if txn.category.type == FinanceCategoryType.TRANSFER and txn.to_account_id is not None:
            account_deltas.setdefault(txn.to_account_id, Decimal("0"))
            account_deltas[txn.to_account_id] += txn.amount

    # Fetch all account values for this month
    av_result = await db.execute(
        select(AccountValue).where(AccountValue.year == year, AccountValue.month == month)
    )
    account_values: dict[int, AccountValue] = {av.account_id: av for av in av_result.scalars().all()}

    # Fetch previous month's account values for reconciliation baseline
    prev_year, prev_month = (year - 1, 12) if month == 1 else (year, month - 1)
    prev_av_result = await db.execute(
        select(AccountValue).where(AccountValue.year == prev_year, AccountValue.month == prev_month)
    )
    prev_account_values: dict[int, AccountValue] = {av.account_id: av for av in prev_av_result.scalars().all()}

    # Determine which accounts to show: active during this month.
    # Condition: start_date < first day of month AND (end_date is None OR end_date >= first day of month)
    from datetime import date as date_type
    month_start = date_type(year, month, 1)

    acc_result = await db.execute(select(FinanceAccount).order_by(FinanceAccount.name))
    all_accounts = acc_result.scalars().all()

    account_summaries: list[AccountMonthlySummary] = []
    for acc in all_accounts:
        if acc.start_date > month_start:
            continue
        if acc.end_date is not None and acc.end_date < month_start:
            continue
        delta = account_deltas.get(acc.id, Decimal("0"))
        av = account_values.get(acc.id)
        prev_av = prev_account_values.get(acc.id)
        prev_amount = prev_av.amount if prev_av is not None else Decimal("0")
        reconciled = av is not None and av.amount == prev_amount + delta
        account_summaries.append(
            AccountMonthlySummary(
                account=acc,
                value=av,
                delta=delta,
                reconciled=reconciled,
            )
        )

    # Per-category totals
    category_totals: dict[int, Decimal] = {}
    category_map: dict[int, FinanceCategory] = {}
    for txn in transactions:
        category_totals.setdefault(txn.category_id, Decimal("0"))
        category_totals[txn.category_id] += txn.amount
        category_map[txn.category_id] = txn.category

    categories_by_type: dict[str, list[CategoryMonthlySummary]] = {
        "credit": [], "debit": [], "transfer": []
    }
    for cat_id, total in category_totals.items():
        cat = category_map[cat_id]
        entry = CategoryMonthlySummary(category=cat, total=total)
        categories_by_type[cat.type.value].append(entry)

    # Monthly profit = sum(debit) - sum(credit), profit_eligible accounts only.
    # External transfers (account=None, to_account set) count as income to to_account if profit_eligible.
    monthly_profit = Decimal("0")
    for txn in transactions:
        if txn.category.type == FinanceCategoryType.TRANSFER:
            # External transfer in: account is None, money arrives at to_account
            if txn.account is None and txn.to_account is not None and txn.to_account.profit_eligible:
                monthly_profit += txn.amount
            continue
        if txn.account is None or not txn.account.profit_eligible:
            continue
        if txn.category.type == FinanceCategoryType.DEBIT:
            monthly_profit += txn.amount
        elif txn.category.type == FinanceCategoryType.CREDIT:
            monthly_profit -= txn.amount

    return MonthlySummary(
        year=year,
        month=month,
        transactions=transactions,
        accounts=account_summaries,
        categories=CategoriesByType(**categories_by_type),
        monthly_profit=monthly_profit,
    )

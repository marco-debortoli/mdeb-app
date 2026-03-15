"""
Finance data import script.

Run from inside the backend Docker container:
    docker compose cp import/ backend:/app/import/
    docker compose exec backend python import_finance.py
"""
import asyncio
import csv
import os
from datetime import date
from decimal import Decimal

from app.database import AsyncSessionLocal
from app.models.finance import (
    AccountType,
    AccountValue,
    FinanceAccount,
    FinanceCategory,
    FinanceCategoryType,
    Merchant,
    Transaction,
)

CSV_DIR = os.path.join(os.path.dirname(__file__), "import")


def parse_null(val: str) -> str | None:
    return None if val == "NULL" else val


def parse_bool(val: str) -> bool:
    return val.strip() == "True"


def parse_date(val: str) -> date | None:
    if not val or val == "NULL" or val == "None":
        return None
    return date.fromisoformat(val)


def read_csv(filename: str) -> list[dict]:
    path = os.path.join(CSV_DIR, filename)
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


async def main() -> None:
    async with AsyncSessionLocal() as session:

        # ── 1. FinanceCategory ────────────────────────────────────────────────
        print("Importing categories...")
        cat_map: dict[str, int] = {}  # uuid -> db id
        for row in read_csv("categories.csv"):
            obj = FinanceCategory(
                name=row["name"],
                type=FinanceCategoryType(row["category_type"]),
            )
            session.add(obj)
            await session.flush()
            cat_map[row["uuid"]] = obj.id
        print(f"  {len(cat_map)} categories inserted.")

        # ── 2. Merchant ───────────────────────────────────────────────────────
        print("Importing merchants...")
        merchant_map: dict[str, int] = {}  # uuid -> db id
        for row in read_csv("merchants.csv"):
            obj = Merchant(name=row["name"], archived=False)
            session.add(obj)
            await session.flush()
            merchant_map[row["uuid"]] = obj.id
        print(f"  {len(merchant_map)} merchants inserted.")

        # ── 3. FinanceAccount ─────────────────────────────────────────────────
        print("Importing accounts...")
        account_map: dict[str, int] = {}  # uuid -> db id
        for row in read_csv("accounts.csv"):
            end_date = parse_date(row["end_date"])
            obj = FinanceAccount(
                name=row["name"],
                type=AccountType(row["account_type"]),
                start_date=parse_date(row["start_date"]),
                end_date=end_date,
                archived=end_date is not None,
                profit_eligible=parse_bool(row["include_monthly_profit"]),
            )
            session.add(obj)
            await session.flush()
            account_map[row["uuid"]] = obj.id
        print(f"  {len(account_map)} accounts inserted.")

        # ── 4. AccountValue ───────────────────────────────────────────────────
        print("Importing account values...")
        av_count = 0
        for row in read_csv("account_values.csv"):
            d = date.fromisoformat(row["date"])
            obj = AccountValue(
                account_id=account_map[row["account"]],
                year=d.year,
                month=d.month,
                amount=Decimal(row["value"]),
            )
            session.add(obj)
            av_count += 1
        await session.flush()
        print(f"  {av_count} account values inserted.")

        # ── 5. Transaction ────────────────────────────────────────────────────
        print("Importing transactions...")
        tx_count = 0
        skipped = 0
        for row in read_csv("transactions.csv"):
            account_uuid = parse_null(row["account"])
            to_account_uuid = parse_null(row["to_account"])
            merchant_uuid = parse_null(row["merchant"])
            description = parse_null(row["name"])

            # Validate FK references exist
            if account_uuid and account_uuid not in account_map:
                print(f"  SKIP tx {row['uuid']}: unknown account {account_uuid}")
                skipped += 1
                continue
            if to_account_uuid and to_account_uuid not in account_map:
                print(f"  SKIP tx {row['uuid']}: unknown to_account {to_account_uuid}")
                skipped += 1
                continue
            if row["category"] not in cat_map:
                print(f"  SKIP tx {row['uuid']}: unknown category {row['category']}")
                skipped += 1
                continue
            if merchant_uuid and merchant_uuid not in merchant_map:
                print(f"  SKIP tx {row['uuid']}: unknown merchant {merchant_uuid}")
                skipped += 1
                continue

            obj = Transaction(
                date=date.fromisoformat(row["date"]),
                amount=Decimal(row["amount"]),
                description=description,
                account_id=account_map[account_uuid] if account_uuid else None,
                to_account_id=account_map[to_account_uuid] if to_account_uuid else None,
                category_id=cat_map[row["category"]],
                merchant_id=merchant_map[merchant_uuid] if merchant_uuid else None,
            )
            session.add(obj)
            tx_count += 1

        await session.flush()
        print(f"  {tx_count} transactions inserted, {skipped} skipped.")

        # ── Commit ────────────────────────────────────────────────────────────
        await session.commit()
        print("Done. All records committed.")


if __name__ == "__main__":
    asyncio.run(main())

import calendar
from datetime import date as date_type, timedelta

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import Date, and_, cast, extract, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.finance import Transaction
from app.models.health import HealthLog
from app.models.journal import DayRating, JournalEntry
from app.models.task import Task, TaskStatus
from app.models.time_tracking import TimeCategory, TimeEntry
from app.schemas.finance import TransactionRead
from app.schemas.health import HealthLogRead
from app.schemas.journal import DayRatingRead, JournalEntryRead
from app.schemas.task import TaskSummary
from app.schemas.time_tracking import TimeEntryRead

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────

class DaySignals(BaseModel):
    has_journal: bool = False
    has_transactions: bool = False
    has_completed_tasks: bool = False
    has_time_entries: bool = False
    has_health_log: bool = False


class MonthOverviewResponse(BaseModel):
    year: int
    month: int
    days: dict[str, DaySignals]


class DayProfileResponse(BaseModel):
    date: date_type
    journal: JournalEntryRead | None
    rating: DayRatingRead | None
    transactions: list[TransactionRead]
    completed_tasks: list[TaskSummary]
    time_entries: list[TimeEntryRead]
    health_log: HealthLogRead | None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/month-overview", response_model=MonthOverviewResponse)
async def get_month_overview(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    db: AsyncSession = Depends(get_db),
):
    """Return per-day presence signals for a given month."""
    _, num_days = calendar.monthrange(year, month)
    signals: dict[str, DaySignals] = {
        str(date_type(year, month, d)): DaySignals()
        for d in range(1, num_days + 1)
    }

    def in_month(col):
        return and_(extract("year", col) == year, extract("month", col) == month)

    # Journal entries
    result = await db.execute(select(JournalEntry.date).where(in_month(JournalEntry.date)))
    for d in result.scalars():
        k = str(d)
        if k in signals:
            signals[k].has_journal = True

    # Financial transactions
    result = await db.execute(select(Transaction.date).where(in_month(Transaction.date)))
    for d in result.scalars():
        k = str(d)
        if k in signals:
            signals[k].has_transactions = True

    # Completed tasks
    result = await db.execute(
        select(Task.completed_date).where(
            and_(
                Task.status == TaskStatus.COMPLETE,
                Task.completed_date.isnot(None),
                in_month(Task.completed_date),
            )
        )
    )
    for d in result.scalars():
        if d is not None:
            k = str(d)
            if k in signals:
                signals[k].has_completed_tasks = True

    # Time entries
    result = await db.execute(select(TimeEntry.date).where(in_month(TimeEntry.date)))
    for d in result.scalars():
        k = str(d)
        if k in signals:
            signals[k].has_time_entries = True

    # Health logs
    result = await db.execute(select(HealthLog.date).where(in_month(HealthLog.date)))
    for d in result.scalars():
        k = str(d)
        if k in signals:
            signals[k].has_health_log = True

    return MonthOverviewResponse(year=year, month=month, days=signals)


@router.get("/day/{entry_date}", response_model=DayProfileResponse)
async def get_day_profile(entry_date: date_type, db: AsyncSession = Depends(get_db)):
    """Return the full day profile for a given date."""
    # Journal entry
    result = await db.execute(select(JournalEntry).where(JournalEntry.date == entry_date))
    journal = result.scalar_one_or_none()

    # Day rating
    result = await db.execute(select(DayRating).where(DayRating.date == entry_date))
    rating = result.scalar_one_or_none()

    # Financial transactions
    result = await db.execute(
        select(Transaction)
        .options(
            selectinload(Transaction.account),
            selectinload(Transaction.category),
            selectinload(Transaction.merchant),
            selectinload(Transaction.to_account),
        )
        .where(Transaction.date == entry_date)
        .order_by(Transaction.created_at)
    )
    transactions = list(result.scalars().all())

    # Completed tasks
    result = await db.execute(
        select(Task)
        .options(
            selectinload(Task.category),
            selectinload(Task.project),
        )
        .where(Task.status == TaskStatus.COMPLETE, Task.completed_date == entry_date)
        .order_by(Task.updated_at)
    )
    completed_tasks = list(result.scalars().all())

    # Time entries — includes overnight entries from the previous day that end on entry_date
    prev_date = entry_date - timedelta(days=1)
    result = await db.execute(
        select(TimeEntry)
        .options(
            selectinload(TimeEntry.category).selectinload(TimeCategory.subcategories),
            selectinload(TimeEntry.subcategory),
        )
        .where(
            or_(
                TimeEntry.date == entry_date,
                and_(
                    TimeEntry.date == prev_date,
                    cast(TimeEntry.end_time, Date) == entry_date,
                ),
            )
        )
        .order_by(TimeEntry.start_time)
    )
    time_entries = [TimeEntryRead.from_orm_with_duration(e) for e in result.scalars().all()]

    # Health log
    result = await db.execute(select(HealthLog).where(HealthLog.date == entry_date))
    health_log = result.scalar_one_or_none()

    return DayProfileResponse(
        date=entry_date,
        journal=journal,
        rating=rating,
        transactions=transactions,
        completed_tasks=completed_tasks,
        time_entries=time_entries,
        health_log=health_log,
    )

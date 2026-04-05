from datetime import date as date_type

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import extract, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.journal.models import DayRating, JournalEntry
from app.journal.schemas import DayRatingRead, DayRatingUpsert, JournalEntryRead, JournalEntryUpsert

journal_router = APIRouter()
day_ratings_router = APIRouter()


# ── Journal Entries ───────────────────────────────────────────────────────────

@journal_router.get("/dates", response_model=list[str])
async def list_entry_dates(db: AsyncSession = Depends(get_db)):
    """Return ISO date strings for all days that have a journal entry."""
    result = await db.execute(select(JournalEntry.date).order_by(JournalEntry.date))
    return [str(d) for d in result.scalars().all()]


@journal_router.get("/on-this-day", response_model=list[JournalEntryRead])
async def on_this_day(
    month: int = Query(..., ge=1, le=12),
    day: int = Query(..., ge=1, le=31),
    exclude_year: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Return all journal entries from previous years on the same month/day."""
    q = select(JournalEntry).where(
        extract("month", JournalEntry.date) == month,
        extract("day", JournalEntry.date) == day,
    )
    if exclude_year is not None:
        q = q.where(extract("year", JournalEntry.date) != exclude_year)
    q = q.order_by(JournalEntry.date.desc())
    result = await db.execute(q)
    return result.scalars().all()


@journal_router.get("/{entry_date}", response_model=JournalEntryRead)
async def get_entry(entry_date: date_type, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(JournalEntry).where(JournalEntry.date == entry_date)
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="No journal entry for this date")
    return entry


@journal_router.put("/{entry_date}", response_model=JournalEntryRead)
async def upsert_entry(
    entry_date: date_type, body: JournalEntryUpsert, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(JournalEntry).where(JournalEntry.date == entry_date)
    )
    entry = result.scalar_one_or_none()
    if entry is None:
        entry = JournalEntry(date=entry_date, content=body.content)
        db.add(entry)
    else:
        entry.content = body.content
    await db.commit()
    await db.refresh(entry)
    return entry


# ── Day Ratings ───────────────────────────────────────────────────────────────

@day_ratings_router.get("/{rating_date}", response_model=DayRatingRead)
async def get_rating(rating_date: date_type, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(DayRating).where(DayRating.date == rating_date)
    )
    rating = result.scalar_one_or_none()
    if not rating:
        raise HTTPException(status_code=404, detail="No rating for this date")
    return rating


@day_ratings_router.put("/{rating_date}", response_model=DayRatingRead)
async def upsert_rating(
    rating_date: date_type, body: DayRatingUpsert, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(DayRating).where(DayRating.date == rating_date)
    )
    rating = result.scalar_one_or_none()
    if rating is None:
        rating = DayRating(date=rating_date, rating=body.rating)
        db.add(rating)
    else:
        rating.rating = body.rating
    await db.commit()
    await db.refresh(rating)
    return rating

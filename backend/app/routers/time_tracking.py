import calendar
from datetime import date as PyDate

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.time_tracking import TimeCategory, TimeEntry, TimeSubcategory
from app.schemas.time_tracking import (
    CategorySummary,
    DayEntries,
    MonthEntriesResponse,
    MonthSummaryResponse,
    TimeCategoryCreate,
    TimeCategoryRead,
    TimeCategoryUpdate,
    TimeEntryCreate,
    TimeEntryRead,
    TimeEntryResponse,
    TimeEntryUpdate,
    TimeSubcategoryCreate,
    TimeSubcategoryRead,
    TimeSubcategoryUpdate,
)

router = APIRouter()


# ── Helpers ────────────────────────────────────────────────────────────────────

def _load_entry_relations():
    return (
        selectinload(TimeEntry.category).selectinload(TimeCategory.subcategories),
        selectinload(TimeEntry.subcategory),
    )


def _parse_month(month: str) -> tuple[int, int]:
    """Parse 'YYYY-MM' into (year, month) integers."""
    try:
        year, mon = month.split("-")
        return int(year), int(mon)
    except Exception:
        raise HTTPException(status_code=400, detail="month must be in YYYY-MM format")


def _detect_overlaps(
    entries: list[TimeEntry], exclude_id: int | None = None
) -> dict[int, list[int]]:
    """
    For each entry, find which other entries on the same date overlap.
    Returns {entry_id: [conflicting_entry_id, ...]}
    """
    # Group by date
    by_date: dict[PyDate, list[TimeEntry]] = {}
    for e in entries:
        if exclude_id is not None and e.id == exclude_id:
            continue
        by_date.setdefault(e.date, []).append(e)

    result: dict[int, list[int]] = {}
    for day_entries in by_date.values():
        for i, a in enumerate(day_entries):
            for b in day_entries[i + 1:]:
                if a.start_time < b.end_time and b.start_time < a.end_time:
                    result.setdefault(a.id, []).append(b.id)
                    result.setdefault(b.id, []).append(a.id)
    return result


def _entry_to_response(entry: TimeEntry, overlap_map: dict[int, list[int]]) -> TimeEntryResponse:
    conflicts = overlap_map.get(entry.id, [])
    read = TimeEntryRead.from_orm_with_duration(entry)
    return TimeEntryResponse(
        **read.model_dump(),
        has_overlap=len(conflicts) > 0,
        conflicting_entry_ids=conflicts,
    )


# ── Categories ─────────────────────────────────────────────────────────────────

@router.get("/categories", response_model=list[TimeCategoryRead])
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TimeCategory)
        .options(selectinload(TimeCategory.subcategories))
        .order_by(TimeCategory.name)
    )
    return result.scalars().all()


@router.post("/categories", response_model=TimeCategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(body: TimeCategoryCreate, db: AsyncSession = Depends(get_db)):
    cat = TimeCategory(**body.model_dump())
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    result = await db.execute(
        select(TimeCategory)
        .where(TimeCategory.id == cat.id)
        .options(selectinload(TimeCategory.subcategories))
    )
    return result.scalar_one()


@router.put("/categories/{category_id}", response_model=TimeCategoryRead)
async def update_category(
    category_id: int, body: TimeCategoryUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(TimeCategory)
        .where(TimeCategory.id == category_id)
        .options(selectinload(TimeCategory.subcategories))
    )
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(cat, field, value)
    await db.commit()
    result = await db.execute(
        select(TimeCategory)
        .where(TimeCategory.id == category_id)
        .options(selectinload(TimeCategory.subcategories))
    )
    return result.scalar_one()


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    cat = await db.get(TimeCategory, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    cat.is_active = False
    await db.commit()


# ── Subcategories ──────────────────────────────────────────────────────────────

@router.post(
    "/subcategories", response_model=TimeSubcategoryRead, status_code=status.HTTP_201_CREATED
)
async def create_subcategory(body: TimeSubcategoryCreate, db: AsyncSession = Depends(get_db)):
    cat = await db.get(TimeCategory, body.time_category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    sub = TimeSubcategory(**body.model_dump())
    db.add(sub)
    await db.commit()
    await db.refresh(sub)
    return sub


@router.put("/subcategories/{subcategory_id}", response_model=TimeSubcategoryRead)
async def update_subcategory(
    subcategory_id: int, body: TimeSubcategoryUpdate, db: AsyncSession = Depends(get_db)
):
    sub = await db.get(TimeSubcategory, subcategory_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(sub, field, value)
    await db.commit()
    await db.refresh(sub)
    return sub


@router.delete("/subcategories/{subcategory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subcategory(subcategory_id: int, db: AsyncSession = Depends(get_db)):
    sub = await db.get(TimeSubcategory, subcategory_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    sub.is_active = False
    await db.commit()


# ── Entries ────────────────────────────────────────────────────────────────────

@router.get("/entries", response_model=MonthEntriesResponse)
async def list_entries(
    month: str = Query(..., description="YYYY-MM"),
    db: AsyncSession = Depends(get_db),
):
    year, mon = _parse_month(month)

    # Fetch all entries for the month
    start_date = PyDate(year, mon, 1)
    end_date = PyDate(year, mon, calendar.monthrange(year, mon)[1])

    result = await db.execute(
        select(TimeEntry)
        .options(*_load_entry_relations())
        .where(TimeEntry.date >= start_date, TimeEntry.date <= end_date)
        .order_by(TimeEntry.date, TimeEntry.start_time)
    )
    entries = list(result.scalars().all())

    # Detect overlaps across all fetched entries
    overlap_map = _detect_overlaps(entries)

    # Group by date
    by_date: dict[PyDate, list[TimeEntry]] = {}
    for e in entries:
        by_date.setdefault(e.date, []).append(e)

    # Build day blocks for every day in the month
    days: list[DayEntries] = []
    for day_num in range(1, end_date.day + 1):
        d = PyDate(year, mon, day_num)
        day_entries = by_date.get(d, [])
        entry_reads = [TimeEntryRead.from_orm_with_duration(e) for e in day_entries]
        total_minutes = sum(e.duration_minutes for e in entry_reads)
        has_overlap = any(entry.id in overlap_map for entry in day_entries)
        days.append(DayEntries(
            date=d,
            entries=entry_reads,
            total_minutes=total_minutes,
            has_overlap=has_overlap,
        ))

    return MonthEntriesResponse(days=days)


@router.post("/entries", response_model=TimeEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_entry(body: TimeEntryCreate, db: AsyncSession = Depends(get_db)):
    entry = TimeEntry(**body.model_dump())
    db.add(entry)
    await db.commit()
    await db.refresh(entry)

    # Reload with relations
    result = await db.execute(
        select(TimeEntry)
        .where(TimeEntry.id == entry.id)
        .options(*_load_entry_relations())
    )
    entry = result.scalar_one()

    # Check overlaps for this date
    date_result = await db.execute(
        select(TimeEntry)
        .where(TimeEntry.date == entry.date)
        .options(*_load_entry_relations())
    )
    day_entries = list(date_result.scalars().all())
    overlap_map = _detect_overlaps(day_entries)

    return _entry_to_response(entry, overlap_map)


@router.put("/entries/{entry_id}", response_model=TimeEntryResponse)
async def update_entry(
    entry_id: int, body: TimeEntryUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(TimeEntry)
        .where(TimeEntry.id == entry_id)
        .options(*_load_entry_relations())
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    updates = body.model_dump(exclude_unset=True)

    # If start/end times are being updated, validate end > start after merging
    new_start = updates.get("start_time", entry.start_time)
    new_end = updates.get("end_time", entry.end_time)
    if new_end <= new_start:
        raise HTTPException(status_code=422, detail="end_time must be after start_time")
    if (new_end - new_start).total_seconds() > 86400:
        raise HTTPException(status_code=422, detail="Entry duration cannot exceed 24 hours")

    for field, value in updates.items():
        setattr(entry, field, value)
    await db.commit()

    # Reload
    result = await db.execute(
        select(TimeEntry)
        .where(TimeEntry.id == entry_id)
        .options(*_load_entry_relations())
    )
    entry = result.scalar_one()

    # Check overlaps
    date_result = await db.execute(
        select(TimeEntry)
        .where(TimeEntry.date == entry.date)
        .options(*_load_entry_relations())
    )
    day_entries = list(date_result.scalars().all())
    overlap_map = _detect_overlaps(day_entries)

    return _entry_to_response(entry, overlap_map)


@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entry(entry_id: int, db: AsyncSession = Depends(get_db)):
    entry = await db.get(TimeEntry, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    await db.delete(entry)
    await db.commit()


# ── Summary ────────────────────────────────────────────────────────────────────

@router.get("/summary", response_model=MonthSummaryResponse)
async def monthly_summary(
    month: str = Query(..., description="YYYY-MM"),
    db: AsyncSession = Depends(get_db),
):
    year, mon = _parse_month(month)
    start_date = PyDate(year, mon, 1)
    end_date = PyDate(year, mon, calendar.monthrange(year, mon)[1])

    result = await db.execute(
        select(TimeEntry)
        .options(selectinload(TimeEntry.category))
        .where(TimeEntry.date >= start_date, TimeEntry.date <= end_date)
    )
    entries = result.scalars().all()

    # Aggregate by category
    category_minutes: dict[int, int] = {}
    category_map: dict[int, TimeCategory] = {}
    for e in entries:
        minutes = int((e.end_time - e.start_time).total_seconds() / 60)
        category_minutes[e.time_category_id] = category_minutes.get(e.time_category_id, 0) + minutes
        category_map[e.time_category_id] = e.category

    categories = [
        CategorySummary(
            category_id=cat_id,
            category_name=category_map[cat_id].name,
            color=category_map[cat_id].color,
            total_minutes=mins,
        )
        for cat_id, mins in sorted(category_minutes.items(), key=lambda x: -x[1])
    ]

    return MonthSummaryResponse(
        categories=categories,
        grand_total_minutes=sum(c.total_minutes for c in categories),
    )

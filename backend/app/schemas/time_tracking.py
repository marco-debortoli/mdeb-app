from datetime import date as PyDate, datetime

from pydantic import BaseModel, Field, ValidationInfo, field_validator


# ── TimeSubcategory ────────────────────────────────────────────────────────────

class TimeSubcategoryCreate(BaseModel):
    time_category_id: int
    name: str = Field(..., max_length=100)


class TimeSubcategoryUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    is_active: bool | None = None


class TimeSubcategoryRead(BaseModel):
    id: int
    time_category_id: int
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── TimeCategory ───────────────────────────────────────────────────────────────

class TimeCategoryCreate(BaseModel):
    name: str = Field(..., max_length=100)
    color: str = Field(..., max_length=20)
    icon: str | None = Field(None, max_length=50)


class TimeCategoryUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    color: str | None = Field(None, max_length=20)
    icon: str | None = Field(None, max_length=50)
    is_active: bool | None = None


class TimeCategoryRead(BaseModel):
    id: int
    name: str
    color: str
    icon: str | None
    is_active: bool
    subcategories: list[TimeSubcategoryRead]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── TimeEntry ──────────────────────────────────────────────────────────────────

def _validate_15min(dt: datetime, field_name: str) -> datetime:
    if dt.minute not in (0, 15, 30, 45) or dt.second != 0:
        raise ValueError(f"{field_name} must be on a 15-minute boundary (minutes: 00, 15, 30, or 45)")
    return dt


class TimeEntryCreate(BaseModel):
    date: PyDate
    start_time: datetime
    end_time: datetime
    time_category_id: int
    time_subcategory_id: int | None = None
    notes: str | None = Field(None, max_length=500)

    @field_validator("start_time")
    @classmethod
    def validate_start(cls, v: datetime) -> datetime:
        return _validate_15min(v, "start_time")

    @field_validator("end_time")
    @classmethod
    def validate_end(cls, v: datetime) -> datetime:
        return _validate_15min(v, "end_time")

    @field_validator("end_time")
    @classmethod
    def validate_end_after_start(cls, v: datetime, info: ValidationInfo) -> datetime:
        start = info.data.get("start_time")
        if start is not None and v <= start:
            raise ValueError("end_time must be after start_time")
        duration = (v - start).total_seconds() / 3600 if start else 0
        if start is not None and duration > 24:
            raise ValueError("Entry duration cannot exceed 24 hours")
        return v


class TimeEntryUpdate(BaseModel):
    date: PyDate | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    time_category_id: int | None = None
    time_subcategory_id: int | None = None
    notes: str | None = Field(None, max_length=500)

    @field_validator("start_time")
    @classmethod
    def validate_start(cls, v: datetime | None) -> datetime | None:
        if v is not None:
            return _validate_15min(v, "start_time")
        return v

    @field_validator("end_time")
    @classmethod
    def validate_end(cls, v: datetime | None) -> datetime | None:
        if v is not None:
            return _validate_15min(v, "end_time")
        return v


class TimeEntryRead(BaseModel):
    id: int
    date: PyDate
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    time_category_id: int
    time_subcategory_id: int | None
    notes: str | None
    category: TimeCategoryRead
    subcategory: TimeSubcategoryRead | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_with_duration(cls, entry: object) -> "TimeEntryRead":
        e = entry  # type: ignore
        minutes = int((e.end_time - e.start_time).total_seconds() / 60)
        data = {
            "id": e.id,
            "date": e.date,
            "start_time": e.start_time,
            "end_time": e.end_time,
            "duration_minutes": minutes,
            "time_category_id": e.time_category_id,
            "time_subcategory_id": e.time_subcategory_id,
            "notes": e.notes,
            "category": e.category,
            "subcategory": e.subcategory,
            "created_at": e.created_at,
            "updated_at": e.updated_at,
        }
        return cls.model_validate(data)


class TimeEntryResponse(TimeEntryRead):
    has_overlap: bool
    conflicting_entry_ids: list[int]


# ── Monthly responses ──────────────────────────────────────────────────────────

class DayEntries(BaseModel):
    date: PyDate
    entries: list[TimeEntryRead]
    total_minutes: int
    has_overlap: bool


class MonthEntriesResponse(BaseModel):
    days: list[DayEntries]


class CategorySummary(BaseModel):
    category_id: int
    category_name: str
    color: str
    total_minutes: int


class MonthSummaryResponse(BaseModel):
    categories: list[CategorySummary]
    grand_total_minutes: int

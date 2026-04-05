from datetime import date, datetime

from pydantic import BaseModel, Field


# ── Journal Entry ─────────────────────────────────────────────────────────────

class JournalEntryUpsert(BaseModel):
    content: str = Field(default="")


class JournalEntryRead(BaseModel):
    id: int
    date: date
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Day Rating ────────────────────────────────────────────────────────────────

class DayRatingUpsert(BaseModel):
    rating: int = Field(..., ge=1, le=5)


class DayRatingRead(BaseModel):
    id: int
    date: date
    rating: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

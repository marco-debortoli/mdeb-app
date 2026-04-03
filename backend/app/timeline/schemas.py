from datetime import date as date_type

from pydantic import BaseModel

from app.finance.schemas import TransactionRead
from app.health.schemas import HealthLogRead
from app.journal.schemas import DayRatingRead, JournalEntryRead
from app.tasks.schemas import TaskSummary
from app.time_tracking.schemas import TimeEntryRead


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

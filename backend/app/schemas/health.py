from datetime import date, datetime

from pydantic import BaseModel, computed_field


def sleep_score_to_rating(score: int | None) -> int | None:
    """Convert a Garmin sleep score (0–100) to a 1–5 rating."""
    if score is None:
        return None
    if score <= 39:
        return 1
    if score <= 59:
        return 2
    if score <= 74:
        return 3
    if score <= 84:
        return 4
    return 5


class HealthLogRead(BaseModel):
    date: date
    steps: int | None
    sleep_score: int | None
    energy_rating: int | None
    weight_kg: float | None
    garmin_body_battery_low: int | None
    garmin_body_battery_high: int | None
    resting_hr: int | None
    synced_at: datetime | None
    intensity_minutes_moderate: int | None
    intensity_minutes_vigorous: int | None
    stress_score: int | None

    @computed_field  # type: ignore[misc]
    @property
    def sleep_rating(self) -> int | None:
        return sleep_score_to_rating(self.sleep_score)

    model_config = {"from_attributes": True}


class HealthLogUpsert(BaseModel):
    energy_rating: int | None = None
    weight_kg: float | None = None


class SyncRequest(BaseModel):
    start_date: date | None = None
    end_date: date | None = None


class SyncResponse(BaseModel):
    upserted: int
    dates: list[str]

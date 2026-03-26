from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class HealthLog(Base):
    __tablename__ = "health_logs"

    date: Mapped[date] = mapped_column(Date, primary_key=True)
    steps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sleep_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    energy_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    garmin_body_battery_low: Mapped[int | None] = mapped_column(Integer, nullable=True)
    garmin_body_battery_high: Mapped[int | None] = mapped_column(Integer, nullable=True)
    resting_hr: Mapped[int | None] = mapped_column(Integer, nullable=True)
    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    intensity_minutes_moderate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    intensity_minutes_vigorous: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stress_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

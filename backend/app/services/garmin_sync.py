from dataclasses import dataclass, field
from datetime import date, timedelta

from garminconnect import Garmin
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# Garmin fields managed by sync (never overwrites energy_rating / weight_kg)
_GARMIN_FIELDS = [
    "steps",
    "sleep_score",
    "garmin_body_battery_low",
    "garmin_body_battery_high",
    "resting_hr",
    "intensity_minutes_moderate",
    "intensity_minutes_vigorous",
    "stress_score",
]


@dataclass
class SyncResult:
    upserted: int = 0
    dates: list[str] = field(default_factory=list)


class GarminSyncService:
    def __init__(self, email: str, password: str) -> None:
        self._email = email
        self._password = password

    def _get_client(self) -> Garmin:
        client = Garmin(self._email, self._password)
        client.login()
        return client

    async def sync(
        self, db: AsyncSession, start_date: date, end_date: date
    ) -> SyncResult:
        client = self._get_client()
        result = SyncResult()

        current = start_date
        while current <= end_date:
            date_str = current.isoformat()
            garmin_data = self._fetch_day(client, date_str)

            if garmin_data is not None:
                await self._upsert(db, current, garmin_data)
                result.upserted += 1
                result.dates.append(date_str)

            current += timedelta(days=1)

        await db.commit()
        return result

    def _fetch_day(self, client: Garmin, date_str: str) -> dict | None:
        data: dict = {}

        # Daily stats: steps, intensity minutes, stress
        try:
            stats = client.get_stats(date_str)
            if stats:
                data["steps"] = stats.get("totalSteps")
                data["intensity_minutes_moderate"] = stats.get("moderateIntensityMinutes")
                data["intensity_minutes_vigorous"] = stats.get("vigorousIntensityMinutes")
                stress = stats.get("averageStressLevel")
                # Garmin returns -1 when stress data is unavailable
                data["stress_score"] = stress if isinstance(stress, int) and stress >= 0 else None
        except Exception:
            pass

        # Sleep score
        try:
            sleep = client.get_sleep_data(date_str)
            if sleep:
                daily_sleep = sleep.get("dailySleepDTO") or {}
                scores = daily_sleep.get("sleepScores") or {}
                overall = scores.get("overall") or {}
                data["sleep_score"] = overall.get("value")
        except Exception:
            pass

        # Body battery low/high — bodyBatteryValuesArray entries are [timestamp, value, ...]
        try:
            battery = client.get_body_battery(date_str, date_str)
            if battery:
                values: list[int] = []
                for day in battery:
                    for entry in day.get("bodyBatteryValuesArray") or []:
                        if isinstance(entry, (list, tuple)) and len(entry) > 1:
                            v = entry[1]
                        elif isinstance(entry, dict):
                            v = entry.get("value")
                        else:
                            continue
                        if isinstance(v, (int, float)):
                            values.append(int(v))
                if values:
                    data["garmin_body_battery_low"] = min(values)
                    data["garmin_body_battery_high"] = max(values)
        except Exception:
            pass

        # Resting heart rate
        try:
            rhr = client.get_rhr_day(date_str)
            if rhr:
                metrics_map = (rhr.get("allMetrics") or {}).get("metricsMap") or {}
                rhr_list = metrics_map.get("WELLNESS_RESTING_HEART_RATE") or []
                if rhr_list:
                    data["resting_hr"] = rhr_list[0].get("value")
        except Exception:
            pass

        return data if data else None

    async def _upsert(self, db: AsyncSession, log_date: date, data: dict) -> None:
        present = {
            col: data[col]
            for col in _GARMIN_FIELDS
            if col in data and data[col] is not None
        }

        insert_cols = ["date"] + list(present.keys()) + ["synced_at"]
        insert_vals = [":log_date"] + [f":{k}" for k in present.keys()] + ["NOW()"]
        set_parts = [f"{k} = :{k}" for k in present.keys()] + ["synced_at = NOW()"]

        params: dict = {"log_date": log_date, **present}

        sql = text(
            f"INSERT INTO health_logs ({', '.join(insert_cols)}) "
            f"VALUES ({', '.join(insert_vals)}) "
            f"ON CONFLICT (date) DO UPDATE SET {', '.join(set_parts)}"
        )
        await db.execute(sql, params)

import io
import zipfile
from dataclasses import dataclass, field
from datetime import date, timedelta

import fitparse
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


# ── Garmin Sync ───────────────────────────────────────────────────────────────

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


# ── FIT Import ────────────────────────────────────────────────────────────────

class FitImportService:
    def parse_zip(self, zip_bytes: bytes) -> dict:
        result: dict = {}
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            for name in zf.namelist():
                upper = name.upper()
                fit_bytes = zf.read(name)
                try:
                    if "SLEEP_DATA" in upper:
                        self._parse_sleep(fit_bytes, result)
                    elif "WELLNESS" in upper:
                        self._parse_wellness(fit_bytes, result)
                    elif "METRICS" in upper:
                        self._parse_metrics(fit_bytes, result)
                except Exception:
                    pass  # skip unparseable files
        return self._finalize(result)

    def _parse_sleep(self, fit_bytes: bytes, result: dict) -> None:
        fit = fitparse.FitFile(io.BytesIO(fit_bytes))
        for msg in fit.get_messages("sleep_assessment"):
            val = msg.get_value("overall_sleep_score")
            if isinstance(val, int) and val >= 0:
                result["sleep_score"] = val
                break

    def _parse_wellness(self, fit_bytes: bytes, result: dict) -> None:
        fit = fitparse.FitFile(io.BytesIO(fit_bytes))
        for msg in fit.get_messages():
            name = msg.name
            if name == "monitoring":
                s = msg.get_value("steps")
                if isinstance(s, int) and s > 0:
                    result.setdefault("_step_values", []).append(s)
                mod = msg.get_value("moderate_intensity_minutes")
                vig = msg.get_value("vigorous_intensity_minutes")
                if isinstance(mod, int):
                    result.setdefault("_mod_values", []).append(mod)
                if isinstance(vig, int):
                    result.setdefault("_vig_values", []).append(vig)
            elif name == "stress_level":
                v = msg.get_value("stress_level_value")
                if isinstance(v, int) and v >= 0:
                    result.setdefault("_stress_values", []).append(v)
            elif name == "hrv_status_summary":
                rhr = msg.get_value("resting_heart_rate")
                if isinstance(rhr, int) and rhr > 0:
                    result["resting_hr"] = rhr
            elif name == "body_battery_level":
                v = msg.get_value("body_battery_level")
                if isinstance(v, int) and 0 <= v <= 100:
                    result.setdefault("_battery_values", []).append(v)
            # Developer data fallback for body battery
            for field in msg.fields:
                if "body_battery" in (field.name or "").lower():
                    if isinstance(field.value, int) and 0 <= field.value <= 100:
                        result.setdefault("_battery_values", []).append(field.value)

    def _parse_metrics(self, fit_bytes: bytes, result: dict) -> None:
        self._parse_wellness(fit_bytes, result)

    def _finalize(self, result: dict) -> dict:
        if "_step_values" in result:
            result["steps"] = max(result.pop("_step_values"))
        if "_mod_values" in result:
            result["intensity_minutes_moderate"] = max(result.pop("_mod_values"))
        else:
            result.pop("_mod_values", None)
        if "_vig_values" in result:
            result["intensity_minutes_vigorous"] = max(result.pop("_vig_values"))
        else:
            result.pop("_vig_values", None)
        if "_stress_values" in result:
            vals = result.pop("_stress_values")
            result["stress_score"] = round(sum(vals) / len(vals))
        if "_battery_values" in result:
            vals = result.pop("_battery_values")
            result["garmin_body_battery_low"] = min(vals)
            result["garmin_body_battery_high"] = max(vals)
        return {k: v for k, v in result.items() if k in _GARMIN_FIELDS and v is not None}

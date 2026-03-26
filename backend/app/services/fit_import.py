import io
import zipfile

import fitparse

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

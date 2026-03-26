from datetime import date as date_type

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.health import HealthLog
from app.schemas.health import HealthLogRead, HealthLogUpsert, SyncRequest, SyncResponse
from app.services.fit_import import FitImportService
from app.services.garmin_sync import GarminSyncService

router = APIRouter()


@router.get("/logs", response_model=list[HealthLogRead])
async def list_logs(
    start: date_type | None = Query(None),
    end: date_type | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(HealthLog).order_by(HealthLog.date.desc())
    if start:
        stmt = stmt.where(HealthLog.date >= start)
    if end:
        stmt = stmt.where(HealthLog.date <= end)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/logs/{log_date}", response_model=HealthLogRead)
async def get_log(log_date: date_type, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(HealthLog).where(HealthLog.date == log_date))
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="No health log for this date")
    return log


@router.put("/logs/{log_date}", response_model=HealthLogRead)
async def upsert_log(
    log_date: date_type, body: HealthLogUpsert, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(HealthLog).where(HealthLog.date == log_date))
    log = result.scalar_one_or_none()
    if log is None:
        log = HealthLog(date=log_date)
        db.add(log)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(log, field, value)
    await db.commit()
    await db.refresh(log)
    return log


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


@router.post("/upload-fit/{log_date}", response_model=HealthLogRead)
async def upload_fit(
    log_date: date_type,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="File must be a .zip archive")

    zip_bytes = await file.read()
    try:
        data = FitImportService().parse_zip(zip_bytes)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Failed to parse ZIP: {exc}")

    if not data:
        raise HTTPException(status_code=422, detail="No recognisable health data found in ZIP")

    present = {col: data[col] for col in _GARMIN_FIELDS if col in data}
    insert_cols = ["date"] + list(present.keys()) + ["synced_at"]
    insert_vals = [":log_date"] + [f":{k}" for k in present.keys()] + ["NOW()"]
    set_parts = [f"{k} = :{k}" for k in present.keys()] + ["synced_at = NOW()"]
    params: dict = {"log_date": log_date, **present}

    await db.execute(
        text(
            f"INSERT INTO health_logs ({', '.join(insert_cols)}) "
            f"VALUES ({', '.join(insert_vals)}) "
            f"ON CONFLICT (date) DO UPDATE SET {', '.join(set_parts)}"
        ),
        params,
    )
    await db.commit()

    result = await db.execute(select(HealthLog).where(HealthLog.date == log_date))
    return result.scalar_one()


@router.post("/sync", response_model=SyncResponse)
async def sync_garmin(body: SyncRequest, db: AsyncSession = Depends(get_db)):
    from datetime import date as today_type
    today = today_type.today()
    start = body.start_date or today
    end = body.end_date or today

    service = GarminSyncService(settings.garmin_email, settings.garmin_password)
    sync_result = await service.sync(db, start, end)
    return SyncResponse(upserted=sync_result.upserted, dates=sync_result.dates)

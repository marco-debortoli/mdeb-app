from datetime import date as date_type

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.journal import DayRating
from app.schemas.journal import DayRatingRead, DayRatingUpsert

router = APIRouter()


@router.get("/{rating_date}", response_model=DayRatingRead)
async def get_rating(rating_date: date_type, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(DayRating).where(DayRating.date == rating_date)
    )
    rating = result.scalar_one_or_none()
    if not rating:
        raise HTTPException(status_code=404, detail="No rating for this date")
    return rating


@router.put("/{rating_date}", response_model=DayRatingRead)
async def upsert_rating(
    rating_date: date_type, body: DayRatingUpsert, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(DayRating).where(DayRating.date == rating_date)
    )
    rating = result.scalar_one_or_none()
    if rating is None:
        rating = DayRating(date=rating_date, rating=body.rating)
        db.add(rating)
    else:
        rating.rating = body.rating
    await db.commit()
    await db.refresh(rating)
    return rating

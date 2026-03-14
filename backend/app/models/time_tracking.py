from datetime import datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TimeCategory(Base):
    __tablename__ = "time_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str] = mapped_column(String(20), nullable=False)
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    subcategories: Mapped[list["TimeSubcategory"]] = relationship(
        "TimeSubcategory", back_populates="category", cascade="all, delete-orphan",
        order_by="TimeSubcategory.name",
    )
    entries: Mapped[list["TimeEntry"]] = relationship("TimeEntry", back_populates="category")


class TimeSubcategory(Base):
    __tablename__ = "time_subcategories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    time_category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("time_categories.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    category: Mapped[TimeCategory] = relationship("TimeCategory", back_populates="subcategories")
    entries: Mapped[list["TimeEntry"]] = relationship("TimeEntry", back_populates="subcategory")


class TimeEntry(Base):
    __tablename__ = "time_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Reporting/grouping date — user-assigned, typically the start date
    date: Mapped[Date] = mapped_column(Date, nullable=False, index=True)
    # Full datetimes — end_time may be on the next calendar day (for overnight entries)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    time_category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("time_categories.id", ondelete="RESTRICT"), nullable=False
    )
    time_subcategory_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("time_subcategories.id", ondelete="SET NULL"), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    category: Mapped[TimeCategory] = relationship("TimeCategory", back_populates="entries")
    subcategory: Mapped[TimeSubcategory | None] = relationship(
        "TimeSubcategory", back_populates="entries"
    )

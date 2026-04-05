import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean, Date, DateTime, Enum, ForeignKey, Integer, Numeric, String,
    UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AccountType(str, enum.Enum):
    DEBIT = "debit"
    CREDIT = "credit"
    INVESTMENT = "investment"
    OTHER = "other"


class FinanceCategoryType(str, enum.Enum):
    CREDIT = "credit"
    DEBIT = "debit"
    TRANSFER = "transfer"


class FinanceAccount(Base):
    __tablename__ = "finance_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[AccountType] = mapped_column(
        Enum(AccountType, name="accounttype", values_callable=lambda e: [m.value for m in e]), nullable=False
    )
    start_date: Mapped[Date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    profit_eligible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    values: Mapped[list["AccountValue"]] = relationship(
        "AccountValue", back_populates="account", cascade="all, delete-orphan"
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", foreign_keys="Transaction.account_id", back_populates="account"
    )
    transfer_in: Mapped[list["Transaction"]] = relationship(
        "Transaction", foreign_keys="Transaction.to_account_id", back_populates="to_account"
    )


class AccountValue(Base):
    __tablename__ = "account_values"
    __table_args__ = (UniqueConstraint("account_id", "year", "month"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("finance_accounts.id", ondelete="CASCADE"), nullable=False
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    account: Mapped[FinanceAccount] = relationship("FinanceAccount", back_populates="values")


class FinanceCategory(Base):
    __tablename__ = "finance_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[FinanceCategoryType] = mapped_column(
        Enum(FinanceCategoryType, name="financecategorytype", values_callable=lambda e: [m.value for m in e]),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", back_populates="category"
    )


class Merchant(Base):
    __tablename__ = "merchants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", back_populates="merchant"
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[Date] = mapped_column(Date, nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    account_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("finance_accounts.id", ondelete="RESTRICT"), nullable=True
    )
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("finance_categories.id", ondelete="RESTRICT"), nullable=False
    )
    merchant_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("merchants.id", ondelete="RESTRICT"), nullable=True
    )
    to_account_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("finance_accounts.id", ondelete="RESTRICT"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    account: Mapped[FinanceAccount] = relationship(
        "FinanceAccount", foreign_keys=[account_id], back_populates="transactions"
    )
    category: Mapped[FinanceCategory] = relationship("FinanceCategory", back_populates="transactions")
    merchant: Mapped[Merchant | None] = relationship("Merchant", back_populates="transactions")
    to_account: Mapped[FinanceAccount | None] = relationship(
        "FinanceAccount", foreign_keys=[to_account_id], back_populates="transfer_in"
    )

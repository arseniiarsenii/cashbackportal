import enum
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base
from .utils import utc_now


@enum.unique
class UserStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"


class ChangeTrackingBase(Base):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=utc_now, nullable=True, index=True
    )


class User(ChangeTrackingBase):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, nullable=False, index=True, unique=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus), nullable=False, index=True, default=UserStatus.active)

    purchases: Mapped[list["UserPurchase"]] = relationship(
        "UserPurchase",
        foreign_keys="[UserPurchase.user_id]",
        order_by="UserPurchase.executed_at",
        lazy="selectin",
    )


@enum.unique
class CashBackLevelEnum(str, enum.Enum):
    basic = "basic"
    silver = "silver"
    gold = "gold"
    platinum = "platinum"


class CashBackLevel(ChangeTrackingBase):
    __tablename__ = "cashback_levels"

    id: Mapped[CashBackLevelEnum] = mapped_column(SAEnum(CashBackLevelEnum), primary_key=True, index=True)
    display_name: Mapped[str] = mapped_column(String, nullable=False, index=True, unique=True)
    cashback_percent: Mapped[Decimal] = mapped_column(Numeric, nullable=False, index=True)
    min_purchases_amount_rub: Mapped[Optional[Decimal]] = mapped_column(Numeric, nullable=True, index=True)
    max_purchases_amount_rub: Mapped[Optional[Decimal]] = mapped_column(Numeric, nullable=True, index=True)


class UserPurchase(ChangeTrackingBase):
    __tablename__ = "user_purchases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), nullable=False, index=True)
    amount_equiv_rub: Mapped[Decimal] = mapped_column(Numeric, nullable=False, index=True)
    merchant_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    user: Mapped[User] = relationship(User, back_populates="purchases", lazy="joined")

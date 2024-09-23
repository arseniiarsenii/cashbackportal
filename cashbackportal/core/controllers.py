from decimal import Decimal

from sqlalchemy import and_, asc, func, nulls_first, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from . import models
from .utils import start_of_month


async def create_user(db_session: AsyncSession, email: str, password: str, name: str) -> models.User:
    from .auth import hash_password

    user = models.User(
        email=email,
        hashed_password=hash_password(password),
        name=name,
    )
    db_session.add(user)
    return user


async def get_user_by_email(db_session: AsyncSession, email: str) -> models.User | None:
    return (await db_session.execute(select(models.User).where(models.User.email == email))).scalar_one_or_none()


async def get_all_cashback_levels(db_session: AsyncSession) -> list[models.CashBackLevel]:
    return list(
        (
            await db_session.execute(
                select(models.CashBackLevel).order_by(nulls_first(asc(models.CashBackLevel.min_purchases_amount_rub)))
            )
        )
        .scalars()
        .all()
    )


async def get_current_user_cashback_level(
    db_session: AsyncSession, user: models.User
) -> tuple[models.CashBackLevel, Decimal]:
    purchase_amt_sq = (
        select(func.coalesce(func.sum(models.UserPurchase.amount_equiv_rub), Decimal(0))).where(
            and_(
                models.UserPurchase.user_id == user.id,
                models.UserPurchase.executed_at >= start_of_month(),
            )
        )
    ).scalar_subquery()
    stmt = select(models.CashBackLevel, purchase_amt_sq).where(
        and_(
            or_(
                models.CashBackLevel.min_purchases_amount_rub <= purchase_amt_sq,
                models.CashBackLevel.min_purchases_amount_rub.is_(None),
            ),
            or_(
                models.CashBackLevel.max_purchases_amount_rub > purchase_amt_sq,
                models.CashBackLevel.max_purchases_amount_rub.is_(None),
            ),
        )
    )
    level, purchases_amount_rub = (await db_session.execute(stmt)).one()
    return level, purchases_amount_rub

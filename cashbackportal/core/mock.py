import random
from datetime import timezone
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from .auth import hash_password
from .db import async_session
from .models import CashBackLevel, CashBackLevelEnum, User, UserPurchase
from .utils import random_dt, start_of_month, utc_now


async def _create_cashback_levels(session: AsyncSession) -> None:
    cashback_levels = (
        CashBackLevel(
            id=CashBackLevelEnum.basic,
            display_name="Basic",
            cashback_percent=Decimal(1),
            min_purchases_amount_rub=None,
            max_purchases_amount_rub=Decimal(50_000),
        ),
        CashBackLevel(
            id=CashBackLevelEnum.silver,
            display_name="Silver",
            cashback_percent=Decimal(2),
            min_purchases_amount_rub=Decimal(50_000),
            max_purchases_amount_rub=Decimal(200_000),
        ),
        CashBackLevel(
            id=CashBackLevelEnum.gold,
            display_name="Gold",
            cashback_percent=Decimal(3),
            min_purchases_amount_rub=Decimal(200_000),
            max_purchases_amount_rub=Decimal(500_000),
        ),
        CashBackLevel(
            id=CashBackLevelEnum.platinum,
            display_name="Platinum",
            cashback_percent=Decimal(5),
            min_purchases_amount_rub=Decimal(500_000),
            max_purchases_amount_rub=None,
        ),
    )
    session.add_all(cashback_levels)


async def _create_mock_user(session: AsyncSession, no: int) -> User:
    first_names = ["Alice", "Bob", "Charlie", "David", "Eve"]
    last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown"]
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    user = User(
        email=f"test{no}@example.com",
        hashed_password=hash_password("foobar42"),
        name=f"{first_name} {last_name}",
    )
    session.add(user)
    return user


async def _create_mock_purchase(session: AsyncSession, user: User) -> UserPurchase:
    merchant_names = ["Amazon", "eBay", "AliExpress", "Ozon", "Wildberries"]
    user_purchase = UserPurchase(
        user_id=user.id,
        amount_equiv_rub=Decimal(random.randrange(100, 50_000, step=100)),
        merchant_name=random.choice(merchant_names),
        executed_at=random_dt(start_of_month(), utc_now()).astimezone(tz=timezone.utc),
    )
    session.add(user_purchase)
    return user_purchase


async def populate_tables() -> None:
    async with async_session() as session:
        async with session.begin():
            await _create_cashback_levels(session)
            for i in range(5):
                user = await _create_mock_user(session, i)
                await session.flush()
                for _ in range(random.randint(1, 21)):
                    await _create_mock_purchase(session, user)

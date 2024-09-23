from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from cashbackportal.core import models


class CashBackLevel(BaseModel):
    id: models.CashBackLevelEnum
    display_name: str
    cashback_percent: Decimal
    min_purchases_amount_rub: Decimal | None
    max_purchases_amount_rub: Decimal | None


class UserCashbackLevel(BaseModel):
    level_id: models.CashBackLevelEnum
    purchases_amount_rub: Decimal


class Purchase(BaseModel):
    amount_equiv_rub: Decimal
    merchant_name: str
    executed_at: datetime

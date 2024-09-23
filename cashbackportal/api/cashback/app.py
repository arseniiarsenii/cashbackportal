from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from cashbackportal.core import controllers, models, utils

from .. import templates
from ..dependencies import get_db_session, get_user
from . import schemas

router = APIRouter(tags=["Cashback"])


@router.get("/all-levels", dependencies=(Depends(get_user),))
async def get_all_cashback_levels(db_session: AsyncSession = Depends(get_db_session)) -> list[schemas.CashBackLevel]:
    all_levels = await controllers.get_all_cashback_levels(db_session)
    return [schemas.CashBackLevel.model_validate(level, from_attributes=True) for level in all_levels]


@router.get("/my-level")
async def get_cashback_level_by_user(
    db_session: AsyncSession = Depends(get_db_session),
    user: models.User = Depends(get_user),
) -> schemas.UserCashbackLevel:
    level, purchases_amount_rub = await controllers.get_current_user_cashback_level(db_session, user)
    return schemas.UserCashbackLevel(
        level_id=level.id,
        purchases_amount_rub=purchases_amount_rub,
    )


@router.get("/my-purchases")
async def get_purchases_this_month(user: models.User = Depends(get_user)) -> list[schemas.Purchase]:
    start_of_month = utils.start_of_month().replace(tzinfo=None)
    return [
        schemas.Purchase.model_validate(purchase, from_attributes=True)
        for purchase in user.purchases
        if purchase.executed_at >= start_of_month
    ]


@router.get("/", include_in_schema=False)
async def get_my_cashback_page(
    request: Request,
    db_session: AsyncSession = Depends(get_db_session),
    user: models.User = Depends(get_user),
) -> HTMLResponse:
    cashback_levels = await controllers.get_all_cashback_levels(db_session)
    current_level, total_purchase_amount = await controllers.get_current_user_cashback_level(db_session, user)
    start_of_month = utils.start_of_month().replace(tzinfo=None)
    user_purchases = [purchase for purchase in user.purchases if purchase.executed_at >= start_of_month]
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "cashback_levels": cashback_levels,
            "current_level": current_level,
            "user_purchases": user_purchases,
            "total_purchase_amount": total_purchase_amount,
            "current_user": user,
        },
    )

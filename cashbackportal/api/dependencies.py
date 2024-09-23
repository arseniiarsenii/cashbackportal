from typing import AsyncIterator, Optional

from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse

from cashbackportal.core import models
from cashbackportal.core.auth import get_current_user
from cashbackportal.core.db import async_session

auth_scheme = HTTPBearer()


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with async_session.begin() as session:
        yield session


async def get_user(
    access_token: Optional[str] = Cookie(None),
    db_session: AsyncSession = Depends(get_db_session),
) -> models.User | RedirectResponse:
    if access_token is None:
        raise HTTPException(status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": "/users/sign-in"},)
    return await get_current_user(db_session, access_token)

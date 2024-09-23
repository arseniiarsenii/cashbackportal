from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from ..core.db import create_all
from ..core.mock import populate_tables
from .cashback.app import router as cashback_router
from .users.app import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await create_all()
    await populate_tables()
    yield


app = FastAPI(title="Cashback Portal API", version="0.1.0", lifespan=lifespan)
app.include_router(users_router, prefix="/users")
app.include_router(cashback_router)

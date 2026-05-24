from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
import asyncio
import logging

from fastapi import FastAPI, Request
from prisma import Prisma

from app.ml_service import ml_runtime

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    prisma = Prisma()
    await prisma.connect()
    app.state.prisma = prisma

    async def load_models_background() -> None:
        try:
            await asyncio.to_thread(ml_runtime.load_models_sync)
        except Exception as exc:
            logger.warning("Background ML model load failed: %s", exc)

    ml_task = asyncio.create_task(load_models_background())
    try:
        yield
    finally:
        ml_task.cancel()
        with suppress(asyncio.CancelledError):
            await ml_task
        await prisma.disconnect()


async def get_prisma(request: Request) -> AsyncIterator[Prisma]:
    yield request.app.state.prisma

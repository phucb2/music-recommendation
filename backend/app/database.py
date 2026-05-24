from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from prisma import Prisma


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    prisma = Prisma()
    await prisma.connect()
    app.state.prisma = prisma
    try:
        yield
    finally:
        await prisma.disconnect()


async def get_prisma(request: Request) -> AsyncIterator[Prisma]:
    yield request.app.state.prisma

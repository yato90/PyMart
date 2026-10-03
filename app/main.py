from fastapi import FastAPI, Depends

from contextlib import asynccontextmanager

from app.kafka.producer import start_producer, stop_producer
from app.api.routers.categories import router as categories_router
from app.api.routers.products import router as products_router
from app.api.routers.auth import router as auth_router
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    await start_producer()

    yield

    await stop_producer()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(categories_router)

@app.get("/health")
async def health_check():
    return {"status":"ok"}


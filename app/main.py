from fastapi import FastAPI, Depends, Request
import time

from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from contextlib import asynccontextmanager

from app.api.routers.categories import router as categories_router
from app.api.routers.products import router as products_router
from app.api.routers.auth import router as auth_router
from app.core.config import settings

from app.core.metrics import (
    HTTP_REQUESTS_TOTAL,
    HTTP_REQUEST_DURATION_SECONDS,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(categories_router)

@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start = time.perf_counter()

    response = await call_next(request)

    duration = time.perf_counter() - start

    route = request.scope.get("route")

    if route is not None:
        path = route.path
    else:
        path = request.url.path

    HTTP_REQUESTS_TOTAL.labels(
        method=request.method,
        path=path,
        status=response.status_code,
    ).inc()

    HTTP_REQUEST_DURATION_SECONDS.labels(
        method=request.method,
        path=path,
    ).observe(duration)

    return response

@app.get("/health")
async def health_check():
    return {"status":"ok"}

@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )

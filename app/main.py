from fastapi import FastAPI, Depends

from app.api.routers.products import router as products_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.include_router(products_router)

@app.get("/health")
async def health_check():
    return {"status":"ok"}


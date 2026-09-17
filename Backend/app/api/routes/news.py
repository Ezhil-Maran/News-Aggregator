from fastapi import APIRouter

from app.services.pipeline import run_pipeline

router = APIRouter(
    prefix="/api",
    tags=["News"]
)


@router.get("/news")
async def get_news():
    return await run_pipeline()
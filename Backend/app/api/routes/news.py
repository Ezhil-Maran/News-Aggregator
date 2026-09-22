from fastapi import APIRouter
import asyncio
from app.services.pipeline import run_pipeline
from app.services.news_retrieval import get_latest_news
from fastapi.responses import JSONResponse

from app.api.models.news_schema import (
    NewsSuccessResponse,
    NewsErrorResponse,
)

router = APIRouter(
    prefix="/api",
    tags=["News"]
)

refresh_lock = asyncio.Lock()

@router.get(
    "/news",
    response_model=NewsSuccessResponse | NewsErrorResponse
)
async def get_news():
    return get_latest_news()


@router.post(
    "/news/refresh",
    response_model=NewsSuccessResponse | NewsErrorResponse,
    responses={
        409: {
            "description": "A news refresh is already running",
        },
        500: {
            "model": NewsErrorResponse,
            "description": "News refresh failed",
        },
    },
)
async def refresh_news():

    if refresh_lock.locked():
        return JSONResponse(
            status_code=409,
            content={
                "success": False,
                "error": "A news refresh is already in progress.",
            },
        )

    async with refresh_lock:

        result = await run_pipeline()

        if not result.get("success", False):
            return JSONResponse(
                status_code=500,
                content=result,
            )

        return result
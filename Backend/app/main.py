from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.config.logging_config import logger
from app.api.database.database import init_db

from app.services.pipeline import run_pipeline
from app.api.models.qwen_loader import load_model

# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="Unified News Backend - Stable Research Version"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
async def startup():

    init_db()

    logger.info("Loading Qwen model...")

    load_model()

    logger.info("Backend initialized.")


# ============================================================
# ROUTES
# ============================================================

@app.get("/news")
async def get_news():

    return await run_pipeline()
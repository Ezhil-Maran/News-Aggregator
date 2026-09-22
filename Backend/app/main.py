from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.config.logging_config import logger
from app.api.database.database import init_db
from app.api.models.qwen_loader import load_model
from app.api.routes.news import router as news_router
from app.api.routes.health import router as health_router   

# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="Unified News Backend - Stable Research Version"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(news_router)
app.include_router(health_router)

# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
async def startup():

    init_db()

    logger.info("Loading Qwen model...")

    load_model()

    logger.info("Backend initialized.")
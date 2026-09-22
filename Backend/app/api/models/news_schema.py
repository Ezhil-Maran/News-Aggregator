from pydantic import BaseModel
from typing import List, Optional


# ============================================================
# SINGLE SOURCE ARTICLE
# ============================================================

class SingleSourceArticle(BaseModel):
    title: str
    link: str
    domain: str
    published: str
    content: str


# ============================================================
# GENERATED AI ARTICLE
# ============================================================

class GeneratedArticle(BaseModel):
    headline: str
    content: str
    sources: List[str]
    article_count: int


# ============================================================
# PIPELINE STATISTICS
# ============================================================

class NewsStatistics(BaseModel):
    total_articles: int
    clusters: int
    generated_articles: int
    single_source_articles: int


# ============================================================
# SUCCESS RESPONSE
# ============================================================

class NewsSuccessResponse(BaseModel):
    success: bool
    generated_at: str
    processing_time_seconds: float
    statistics: NewsStatistics
    generated_articles: List[GeneratedArticle]
    single_source_articles: List[SingleSourceArticle]


# ============================================================
# ERROR RESPONSE
# ============================================================

class NewsErrorResponse(BaseModel):
    success: bool
    generated_at: Optional[str] = None
    processing_time_seconds: float
    error: str
    statistics: dict
    generated_articles: List[GeneratedArticle]
    single_source_articles: List[SingleSourceArticle]
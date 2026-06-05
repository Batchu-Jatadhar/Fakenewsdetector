from pydantic import BaseModel
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime


class AnalysisRequest(BaseModel):
    input_type: str  # 'text' or 'url'
    content: str


class SuspiciousPhrase(BaseModel):
    text: str
    start: int
    end: int
    reason: str


class ExplanationData(BaseModel):
    reasoning: str
    suspicious_phrases: List[SuspiciousPhrase]


class FactCheckResponse(BaseModel):
    id: UUID
    source: str
    claim_text: Optional[str] = None
    verdict: Optional[str] = None
    publisher: Optional[str] = None
    url: Optional[str] = None

    class Config:
        from_attributes = True


class AnalysisResponse(BaseModel):
    id: UUID
    user_id: UUID
    input_type: str
    source_url: Optional[str] = None
    content_text: str
    fake_probability: Optional[float] = None
    trust_score: Optional[float] = None
    roberta_score: Optional[float] = None
    sbert_score: Optional[float] = None
    confidence: Optional[float] = None
    source_credibility: Optional[Any] = None
    explanation: Optional[Any] = None
    status: str
    created_at: datetime
    fact_checks: List[FactCheckResponse] = []

    class Config:
        from_attributes = True


class AnalysisListItem(BaseModel):
    id: UUID
    input_type: str
    source_url: Optional[str] = None
    content_text: str
    fake_probability: Optional[float] = None
    trust_score: Optional[float] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedAnalyses(BaseModel):
    items: List[AnalysisListItem]
    total: int
    page: int
    limit: int
    pages: int

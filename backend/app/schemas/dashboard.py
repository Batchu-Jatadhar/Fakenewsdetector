from pydantic import BaseModel
from typing import List, Optional


class DashboardStats(BaseModel):
    total_analyses: int
    total_fake: int
    total_real: int
    total_uncertain: int
    misinformation_rate: float
    avg_confidence: float


class ModelMetrics(BaseModel):
    accuracy: Optional[float] = None
    f1_score: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    total_evaluated: int = 0


class FeedbackRequest(BaseModel):
    analysis_id: str
    label: str  # 'real' or 'fake'
    notes: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: str
    analysis_id: str
    user_id: str
    label: str
    notes: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class DomainStats(BaseModel):
    domain: str
    total_analyses: int
    total_fake: int
    total_real: int
    total_uncertain: int
    misinformation_rate: float
    avg_confidence: Optional[float] = None


class TopDomain(BaseModel):
    domain: str
    total_analyses: int
    misinformation_rate: float

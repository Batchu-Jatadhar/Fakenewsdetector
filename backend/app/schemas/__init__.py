from app.schemas.auth import UserRegister, UserLogin, UserResponse, TokenResponse
from app.schemas.analysis import (
    AnalysisRequest, AnalysisResponse, AnalysisListItem,
    PaginatedAnalyses, FactCheckResponse, ExplanationData, SuspiciousPhrase
)
from app.schemas.dashboard import DashboardStats, ModelMetrics, FeedbackRequest, FeedbackResponse

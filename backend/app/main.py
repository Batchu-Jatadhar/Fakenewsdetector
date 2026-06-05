from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import create_tables
from app.routers import auth, analysis, history, dashboard, admin, feedback


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and load ML models
    await create_tables()
    # ML models are loaded lazily on first request
    yield
    # Shutdown


app = FastAPI(
    title="Fake News Detection & Verification Platform",
    description="AI-powered semantic misinformation detection using RoBERTa and Sentence-BERT",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(analysis.router, prefix="/api", tags=["Analysis"])
app.include_router(history.router, prefix="/api", tags=["History"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(feedback.router, prefix="/api", tags=["Feedback"])


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "fake-news-detector"}

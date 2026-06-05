import math
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.analysis import Analysis
from app.models.feedback import Feedback
from app.schemas.analysis import AnalysisResponse, PaginatedAnalyses, AnalysisListItem
from app.schemas.auth import UserResponse
from app.schemas.dashboard import FeedbackRequest, FeedbackResponse
from app.middleware.auth import require_role

router = APIRouter()


@router.get("/analyses", response_model=PaginatedAnalyses)
async def get_all_analyses(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("analyst", "admin")),
):
    offset = (page - 1) * limit

    count_result = await db.execute(select(func.count(Analysis.id)))
    total = count_result.scalar() or 0

    query = (
        select(Analysis)
        .order_by(Analysis.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(query)
    analyses = result.scalars().all()

    return PaginatedAnalyses(
        items=[AnalysisListItem.model_validate(a) for a in analyses],
        total=total,
        page=page,
        limit=limit,
        pages=math.ceil(total / limit) if total > 0 else 0,
    )


@router.post("/feedback", status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    data: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("analyst", "admin")),
):
    # Verify analysis exists
    result = await db.execute(select(Analysis).where(Analysis.id == data.analysis_id))
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")

    if data.label not in ("real", "fake"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Label must be 'real' or 'fake'")

    feedback = Feedback(
        analysis_id=UUID(data.analysis_id),
        user_id=current_user.id,
        label=data.label,
        notes=data.notes,
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)
    return {"id": str(feedback.id), "message": "Feedback submitted successfully"}


@router.get("/users")
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    return [UserResponse.model_validate(u) for u in users]

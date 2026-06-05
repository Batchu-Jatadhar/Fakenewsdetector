import math
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.analysis import Analysis
from app.schemas.analysis import AnalysisListItem, PaginatedAnalyses
from app.middleware.auth import get_current_user

router = APIRouter()


@router.get("/history", response_model=PaginatedAnalyses)
async def get_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    offset = (page - 1) * limit

    # Count total
    count_query = select(func.count(Analysis.id)).where(Analysis.user_id == current_user.id)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Fetch page
    query = (
        select(Analysis)
        .where(Analysis.user_id == current_user.id)
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

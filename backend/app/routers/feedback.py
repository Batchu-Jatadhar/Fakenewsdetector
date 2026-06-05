from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.analysis import Analysis
from app.models.feedback import Feedback
from app.schemas.dashboard import FeedbackRequest, FeedbackResponse
from app.middleware.auth import get_current_user


router = APIRouter()


@router.post("/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_user_feedback(
    data: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify that the analysis exists
    result = await db.execute(select(Analysis).where(Analysis.id == data.analysis_id))
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found",
        )

    # Regular users can only give feedback on their own analyses
    if current_user.role == "user" and analysis.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only submit feedback on your own analyses",
        )

    if data.label not in ("real", "fake"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Label must be 'real' or 'fake'",
        )

    # Prevent duplicate feedback from the same user on the same analysis
    existing_result = await db.execute(
        select(Feedback).where(
            Feedback.analysis_id == str(analysis.id),
            Feedback.user_id == current_user.id,
        )
    )
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already submitted feedback for this analysis",
        )

    feedback = Feedback(
        analysis_id=str(analysis.id),
        user_id=current_user.id,
        label=data.label,
        notes=data.notes,
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)

    return FeedbackResponse.model_validate(feedback)


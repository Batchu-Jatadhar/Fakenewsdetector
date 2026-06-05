from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.models.analysis import Analysis, FactCheck
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.middleware.auth import get_current_user
from app.services.ml_service import run_analysis_pipeline
from app.services.scraper import extract_article_text

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_content(
    data: AnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Extract text from URL if needed
    content_text = data.content
    source_url = None

    if data.input_type == "url":
        source_url = data.content
        try:
            content_text = await extract_article_text(data.content)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to extract article text: {str(e)}",
            )

    if not content_text or len(content_text.strip()) < 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content text is too short for analysis (minimum 20 characters)",
        )

    # Create analysis record
    analysis = Analysis(
        user_id=current_user.id,
        input_type=data.input_type,
        source_url=source_url,
        content_text=content_text[:10000],  # Limit stored text
        status="pending",
    )
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)

    # Run ML pipeline
    try:
        result = await run_analysis_pipeline(
            content_text,
            str(analysis.id),
            db,
            source_url=source_url,
        )

        analysis.fake_probability = result["fake_probability"]
        analysis.trust_score = result["trust_score"]
        analysis.roberta_score = result["roberta_score"]
        analysis.sbert_score = result["sbert_score"]
        analysis.confidence = result["confidence"]
        analysis.explanation = result["explanation"]
        analysis.status = "completed"

        # Store fact checks
        for fc in result.get("fact_checks", []):
            fact_check = FactCheck(
                analysis_id=analysis.id,
                source=fc["source"],
                claim_text=fc.get("claim_text"),
                verdict=fc.get("verdict"),
                publisher=fc.get("publisher"),
                url=fc.get("url"),
            )
            db.add(fact_check)

        await db.commit()
        await db.refresh(analysis)
    except Exception as e:
        analysis.status = "error"
        analysis.explanation = {"reasoning": f"Analysis failed: {str(e)}", "suspicious_phrases": []}
        await db.commit()
        await db.refresh(analysis)

    # Reload with relationships
    result = await db.execute(
        select(Analysis)
        .options(selectinload(Analysis.fact_checks))
        .where(Analysis.id == analysis.id)
    )
    analysis = result.scalar_one()
    return AnalysisResponse.model_validate(analysis)


@router.get("/analysis/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Analysis)
        .options(selectinload(Analysis.fact_checks))
        .where(Analysis.id == analysis_id)
    )
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")

    # Users can only see their own analyses unless admin/analyst
    if current_user.role == "user" and analysis.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return AnalysisResponse.model_validate(analysis)

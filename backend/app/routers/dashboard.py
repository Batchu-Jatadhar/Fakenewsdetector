from urllib.parse import urlparse

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.analysis import Analysis
from app.models.feedback import Feedback
from app.schemas.dashboard import DashboardStats, ModelMetrics, DomainStats, TopDomain
from app.middleware.auth import get_current_user

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Total analyses
    total_result = await db.execute(select(func.count(Analysis.id)).where(Analysis.status == "completed"))
    total_analyses = total_result.scalar() or 0

    # Fake count (fake_probability > 0.6)
    fake_result = await db.execute(
        select(func.count(Analysis.id)).where(
            Analysis.status == "completed",
            Analysis.fake_probability > 0.6,
        )
    )
    total_fake = fake_result.scalar() or 0

    # Real count (fake_probability < 0.3)
    real_result = await db.execute(
        select(func.count(Analysis.id)).where(
            Analysis.status == "completed",
            Analysis.fake_probability < 0.3,
        )
    )
    total_real = real_result.scalar() or 0

    total_uncertain = total_analyses - total_fake - total_real

    # Avg confidence
    avg_result = await db.execute(
        select(func.avg(Analysis.confidence)).where(Analysis.status == "completed")
    )
    avg_confidence = avg_result.scalar() or 0.0

    misinformation_rate = (total_fake / total_analyses * 100) if total_analyses > 0 else 0.0

    return DashboardStats(
        total_analyses=total_analyses,
        total_fake=total_fake,
        total_real=total_real,
        total_uncertain=total_uncertain,
        misinformation_rate=round(misinformation_rate, 2),
        avg_confidence=round(float(avg_confidence), 4),
    )


@router.get("/metrics", response_model=ModelMetrics)
async def get_model_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Compute metrics from feedback-labeled analyses
    result = await db.execute(
        select(Analysis.fake_probability, Feedback.label)
        .join(Feedback, Feedback.analysis_id == Analysis.id)
        .where(Analysis.status == "completed")
    )
    rows = result.all()

    if not rows:
        return ModelMetrics(total_evaluated=0)

    tp = fp = tn = fn = 0
    for fake_prob, label in rows:
        predicted_fake = (fake_prob or 0) > 0.5
        actual_fake = label == "fake"
        if predicted_fake and actual_fake:
            tp += 1
        elif predicted_fake and not actual_fake:
            fp += 1
        elif not predicted_fake and not actual_fake:
            tn += 1
        else:
            fn += 1

    total = tp + fp + tn + fn
    accuracy = (tp + tn) / total if total > 0 else None
    precision = tp / (tp + fp) if (tp + fp) > 0 else None
    recall = tp / (tp + fn) if (tp + fn) > 0 else None
    f1 = (2 * precision * recall / (precision + recall)) if precision and recall else None

    return ModelMetrics(
        accuracy=round(accuracy, 4) if accuracy else None,
        f1_score=round(f1, 4) if f1 else None,
        precision=round(precision, 4) if precision else None,
        recall=round(recall, 4) if recall else None,
        total_evaluated=total,
    )


def _extract_domain(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return host


@router.get("/domain/{domain}", response_model=DomainStats)
async def get_domain_stats(
    domain: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Load analyses for this domain (best-effort string filtering)
    result = await db.execute(
        select(
            Analysis.source_url,
            Analysis.fake_probability,
            Analysis.confidence,
        ).where(
            Analysis.status == "completed",
            Analysis.source_url.isnot(None),
        )
    )
    rows = result.all()

    total = fake_count = real_count = 0
    confidences: list[float] = []

    target = domain.lower()
    if target.startswith("www."):
        target = target[4:]

    for source_url, fake_prob, confidence in rows:
        if not source_url:
            continue
        if _extract_domain(source_url) != target:
            continue

        total += 1
        if fake_prob is not None:
            if fake_prob > 0.6:
                fake_count += 1
            elif fake_prob < 0.3:
                real_count += 1
        if confidence is not None:
            confidences.append(confidence)

    uncertain = total - fake_count - real_count
    misinformation_rate = (fake_count / total * 100) if total > 0 else 0.0
    avg_conf = sum(confidences) / len(confidences) if confidences else None

    return DomainStats(
        domain=target,
        total_analyses=total,
        total_fake=fake_count,
        total_real=real_count,
        total_uncertain=uncertain,
        misinformation_rate=round(misinformation_rate, 2),
        avg_confidence=round(float(avg_conf), 4) if avg_conf is not None else None,
    )


@router.get("/domains/top", response_model=list[TopDomain])
async def get_top_domains(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Aggregate per-domain stats in Python for now
    result = await db.execute(
        select(
            Analysis.source_url,
            Analysis.fake_probability,
        ).where(
            Analysis.status == "completed",
            Analysis.source_url.isnot(None),
        )
    )
    rows = result.all()

    stats: dict[str, dict[str, float]] = {}

    for source_url, fake_prob in rows:
        if not source_url:
            continue
        domain = _extract_domain(source_url)
        if not domain:
            continue

        d = stats.setdefault(domain, {"total": 0, "fake": 0})
        d["total"] += 1
        if fake_prob is not None and fake_prob > 0.6:
            d["fake"] += 1

    domains: list[TopDomain] = []
    for domain, values in stats.items():
        total = int(values["total"])
        if total == 0:
            continue
        misinformation_rate = values["fake"] / total * 100
        domains.append(
            TopDomain(
                domain=domain,
                total_analyses=total,
                misinformation_rate=round(misinformation_rate, 2),
            )
        )

    # Sort by misinformation rate (desc), then by total analyses (desc)
    domains.sort(key=lambda d: (d.misinformation_rate, d.total_analyses), reverse=True)
    return domains[:limit]


import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    input_type = Column(String(10), nullable=False)  # 'text' or 'url'
    source_url = Column(Text, nullable=True)
    content_text = Column(Text, nullable=False)
    fake_probability = Column(Float, nullable=True)
    trust_score = Column(Float, nullable=True)
    roberta_score = Column(Float, nullable=True)
    sbert_score = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    explanation = Column(JSON, nullable=True)
    status = Column(String(20), nullable=False, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="analyses")
    fact_checks = relationship("FactCheck", back_populates="analysis", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="analysis", cascade="all, delete-orphan")


class FactCheck(Base):
    __tablename__ = "fact_checks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String(36), ForeignKey("analyses.id"), nullable=False)
    source = Column(String(100), nullable=False)
    claim_text = Column(Text, nullable=True)
    verdict = Column(String(100), nullable=True)
    publisher = Column(String(255), nullable=True)
    url = Column(Text, nullable=True)

    analysis = relationship("Analysis", back_populates="fact_checks")

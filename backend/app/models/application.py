from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    resume_snapshot_json = Column(Text, nullable=False)
    status = Column(String(50), default="SUBMITTED", nullable=False)
    # Status machine:
    # SUBMITTED -> VIEWED -> AI_SCREENING -> AI_INTERVIEW_PENDING -> AI_INTERVIEW_DONE -> ENTERPRISE_INTERVIEW -> OFFER -> HIRED
    # or REJECTED / WITHDRAWN
    current_stage_id = Column(Integer, nullable=True)
    withdraw_reason = Column(String(255), nullable=True)
    reject_reason = Column(String(255), nullable=True)
    match_score = Column(Integer, default=85, nullable=False)
    assigned_recruiter_id = Column(Integer, nullable=True)
    is_in_talent_pool = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    status_history = relationship("ApplicationStatusHistory", back_populates="application", cascade="all, delete-orphan")
    pipeline_records = relationship("CandidatePipelineRecord", back_populates="application", cascade="all, delete-orphan")
    tags = relationship("CandidateTag", back_populates="application", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="application")

class ApplicationStatusHistory(Base):
    __tablename__ = "application_status_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    from_status = Column(String(50), nullable=True)
    to_status = Column(String(50), nullable=False)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    note = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    application = relationship("Application", back_populates="status_history")

class CandidatePipelineRecord(Base):
    __tablename__ = "candidate_pipeline_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    stage_name = Column(String(50), nullable=False)
    entered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    left_at = Column(DateTime, nullable=True)
    actor_id = Column(Integer, nullable=True)
    note = Column(String(255), nullable=True)

    application = relationship("Application", back_populates="pipeline_records")

class CandidateTag(Base):
    __tablename__ = "candidate_tags"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    tag = Column(String(50), nullable=False)

    application = relationship("Application", back_populates="tags")

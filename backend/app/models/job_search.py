"""用户私有的求职计划；与企业候选人及官网访问记录独立。"""
from datetime import datetime
from sqlalchemy import Column, Date, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from app.core.database import Base


class JobSearchOpportunity(Base):
    __tablename__ = "job_search_opportunities"
    __table_args__ = (UniqueConstraint("user_id", "dedup_key", name="uq_job_search_user_key"),
                      Index("uq_job_search_user_source_job", "user_id", "source_job_id", unique=True))

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    dedup_key = Column(String(64), nullable=False)
    source_job_id = Column(Integer, ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(150), nullable=False)
    company_name = Column(String(150), nullable=False)
    location = Column(String(150), nullable=True)
    salary_note = Column(String(150), nullable=True)
    source_url = Column(String(2048), nullable=True)
    jd_text = Column(Text, nullable=False, default="")
    required_skills_json = Column(Text, nullable=False, default="[]")
    experience_years = Column(Integer, nullable=True)
    deadline = Column(Date, nullable=True)
    status = Column(String(30), nullable=False, default="SAVED")
    note = Column(Text, nullable=False, default="")
    feedback = Column(Text, nullable=False, default="")
    next_follow_up = Column(Date, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    last_contact_at = Column(DateTime, nullable=True)
    follow_up_count = Column(Integer, nullable=False, default=0)
    version = Column(Integer, nullable=False, default=1)
    history_json = Column(Text, nullable=False, default="[]")
    analysis_json = Column(Text, nullable=True)
    prep_json = Column(Text, nullable=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

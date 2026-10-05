from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, UniqueConstraint
from app.core.database import Base


class ExternalApplication(Base):
    """用户自己的官网投递笔记，不进入企业候选人库，不授予任何简历权限。"""
    __tablename__ = "external_applications"
    __table_args__ = (UniqueConstraint("user_id", "job_id", name="uq_external_user_job"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    job_title = Column(String(150), nullable=False)
    company_name = Column(String(100), nullable=False)
    official_apply_url = Column(String(2048), nullable=False)
    status = Column(String(30), default="LINK_OPENED", nullable=False)
    note = Column(String(1000), nullable=True)
    history_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

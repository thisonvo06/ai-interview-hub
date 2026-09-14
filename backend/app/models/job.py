from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50), nullable=False)  # 后端, 前端, 数据, 算法, 架构, 综合

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    title = Column(String(150), nullable=False)
    category = Column(String(50), default="后端开发", nullable=False)
    city = Column(String(50), nullable=False)
    salary_min = Column(Integer, default=15, nullable=False)  # in k
    salary_max = Column(Integer, default=25, nullable=False)  # in k
    education = Column(String(50), default="本科及以上", nullable=False)
    experience = Column(String(50), default="1-3年", nullable=False)
    type = Column(String(50), default="全职", nullable=False)  # 全职, 实习, 兼职
    headcount = Column(Integer, default=1, nullable=False)
    description = Column(Text, nullable=False)
    duties = Column(Text, nullable=False)
    requirements = Column(Text, nullable=False)
    bonus = Column(Text, nullable=True)
    skills_required = Column(String(255), default="Java,Spring Boot,MySQL,Redis", nullable=False)
    status = Column(String(50), default="DRAFT", nullable=False)  # DRAFT, PENDING_REVIEW, PUBLISHED, PAUSED, CLOSED, REJECTED
    reject_reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    company = relationship("Company", back_populates="jobs")
    department = relationship("Department", back_populates="jobs")
    skills = relationship("JobSkill", back_populates="job", cascade="all, delete-orphan")
    competencies = relationship("JobCompetency", back_populates="job", cascade="all, delete-orphan")
    favorites = relationship("JobFavorite", back_populates="job", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="job")

class JobSkill(Base):
    __tablename__ = "job_skills"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    skill_name = Column(String(100), nullable=False)
    level = Column(String(50), default="熟练", nullable=False)  # 了解, 熟悉, 熟练, 精通
    required = Column(Boolean, default=True, nullable=False)

    job = relationship("Job", back_populates="skills")

class JobCompetency(Base):
    __tablename__ = "job_competencies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    competency_name = Column(String(100), nullable=False)
    weight = Column(Float, default=20.0, nullable=False)       # Sum of weights should be 100%
    required_score = Column(Float, default=75.0, nullable=False)

    job = relationship("Job", back_populates="competencies")

class JobFavorite(Base):
    __tablename__ = "job_favorites"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    job = relationship("Job", back_populates="favorites")

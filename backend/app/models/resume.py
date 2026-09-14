from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), default="我的个人简历", nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    file_url = Column(String(255), nullable=True)
    file_name = Column(String(255), nullable=True)
    status = Column(String(50), default="ACTIVE", nullable=False)
    target_job_id = Column(Integer, nullable=True)
    target_job_title = Column(String(100), default="Java开发工程师", nullable=False)
    completeness = Column(Integer, default=70, nullable=False)  # 0-100%
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="resumes")
    educations = relationship("ResumeEducation", back_populates="resume", cascade="all, delete-orphan")
    projects = relationship("ResumeProject", back_populates="resume", cascade="all, delete-orphan")
    work_experiences = relationship("ResumeWorkExperience", back_populates="resume", cascade="all, delete-orphan")
    skills = relationship("ResumeSkill", back_populates="resume", cascade="all, delete-orphan")
    ai_analyses = relationship("ResumeAIAnalysis", back_populates="resume", cascade="all, delete-orphan")

class ResumeEducation(Base):
    __tablename__ = "resume_educations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    school = Column(String(100), nullable=False)
    major = Column(String(100), nullable=False)
    degree = Column(String(50), default="本科", nullable=False)
    start_date = Column(String(50), nullable=False)
    end_date = Column(String(50), nullable=False)

    resume = relationship("Resume", back_populates="educations")

class ResumeProject(Base):
    __tablename__ = "resume_projects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    name = Column(String(150), nullable=False)
    role = Column(String(100), default="核心开发", nullable=False)
    description = Column(Text, nullable=False)
    technologies = Column(String(255), default="Spring Boot,MySQL,Redis", nullable=False)
    start_date = Column(String(50), nullable=False)
    end_date = Column(String(50), nullable=False)

    resume = relationship("Resume", back_populates="projects")

class ResumeWorkExperience(Base):
    __tablename__ = "resume_work_experiences"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    company = Column(String(150), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    start_date = Column(String(50), nullable=False)
    end_date = Column(String(50), nullable=False)

    resume = relationship("Resume", back_populates="work_experiences")

class ResumeSkill(Base):
    __tablename__ = "resume_skills"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    skill_name = Column(String(100), nullable=False)
    level = Column(String(50), default="熟练", nullable=False)
    evidence = Column(String(255), nullable=True)

    resume = relationship("Resume", back_populates="skills")

class ResumeAIAnalysis(Base):
    __tablename__ = "resume_ai_analyses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    analysis_type = Column(String(50), default="COMPREHENSIVE", nullable=False)
    result_json = Column(Text, nullable=False)  # Parsed JSON result
    prompt_version = Column(String(50), default="v1.0", nullable=False)
    model = Column(String(50), default="mock-ai", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    resume = relationship("Resume", back_populates="ai_analyses")

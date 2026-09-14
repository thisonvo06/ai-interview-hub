from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class PersonalProfile(Base):
    __tablename__ = "personal_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    profile_type = Column(String(50), default="STUDENT", nullable=False)  # STUDENT, GRADUATE, EXPERIENCED
    name = Column(String(100), nullable=False)
    avatar_url = Column(String(255), nullable=True)
    gender = Column(String(20), nullable=True)
    education = Column(String(50), nullable=True)      # 本科, 硕士, 博士, 大专
    school = Column(String(100), nullable=True)
    major = Column(String(100), nullable=True)
    graduation_year = Column(Integer, nullable=True)
    work_years = Column(Integer, default=0, nullable=False)
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="profile")

class CareerPreference(Base):
    __tablename__ = "career_preferences"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    target_job_id = Column(Integer, nullable=True)
    target_job_title = Column(String(100), default="Java后端开发工程师", nullable=False)
    target_cities = Column(String(255), default="北京,上海,深圳", nullable=False)
    salary_min = Column(Integer, default=15, nullable=False)  # in k (15k)
    salary_max = Column(Integer, default=25, nullable=False)  # in k (25k)
    job_status = Column(String(50), default="LOOKING", nullable=False) # LOOKING, OPEN_TO_OFFERS, NOT_LOOKING
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="career_preference")

class Competency(Base):
    __tablename__ = "competencies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # 技术能力, 项目经验, 系统设计, 沟通表达, 综合素质

class UserCompetency(Base):
    __tablename__ = "user_competencies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    competency_id = Column(Integer, nullable=True)
    competency_name = Column(String(100), nullable=False)
    score = Column(Float, default=60.0, nullable=False)
    confidence = Column(Float, default=0.8, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class CompetencyHistory(Base):
    __tablename__ = "competency_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    competency_id = Column(Integer, nullable=True)
    competency_name = Column(String(100), nullable=False)
    score = Column(Float, nullable=False)
    source_type = Column(String(50), nullable=False)  # INTERVIEW, ASSESSMENT, RESUME, PRACTICE
    source_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

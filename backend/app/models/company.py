from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(150), unique=True, index=True, nullable=False)
    logo_url = Column(String(255), nullable=True)
    industry = Column(String(100), nullable=False)
    size = Column(String(50), nullable=False)  # 0-50人, 50-150人, 150-500人, 500-2000人, 2000人以上
    address = Column(String(255), nullable=True)
    city = Column(String(50), nullable=False)
    intro = Column(Text, nullable=True)
    status = Column(String(50), default="UNVERIFIED", nullable=False)  # UNVERIFIED, REVIEWING, VERIFIED, REJECTED, SUSPENDED
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    members = relationship("CompanyMember", back_populates="company", cascade="all, delete-orphan")
    departments = relationship("Department", back_populates="company", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="company", cascade="all, delete-orphan")
    verifications = relationship("CompanyVerification", back_populates="company", cascade="all, delete-orphan")

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey("departments.id"), nullable=True)

    company = relationship("Company", back_populates="departments")
    members = relationship("CompanyMember", back_populates="department")
    jobs = relationship("Job", back_populates="department")

class CompanyMember(Base):
    __tablename__ = "company_members"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    role_code = Column(String(50), default="RECRUITER", nullable=False)  # OWNER, ADMIN, RECRUITER, INTERVIEWER, HIRING_MANAGER
    status = Column(String(50), default="ACTIVE", nullable=False)        # ACTIVE, DISABLED
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    company = relationship("Company", back_populates="members")
    user = relationship("User", back_populates="company_memberships")
    department = relationship("Department", back_populates="members")

class CompanyVerification(Base):
    __tablename__ = "company_verifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    status = Column(String(50), default="PENDING", nullable=False)  # PENDING, APPROVED, REJECTED
    submitted_data_json = Column(Text, nullable=False)              # Business license, contact person, credentials JSON
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    opinion = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    company = relationship("Company", back_populates="verifications")

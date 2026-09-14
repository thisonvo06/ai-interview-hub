from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(30), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    account_type = Column(String(20), default="PERSONAL", nullable=False)  # PERSONAL, ENTERPRISE, ADMIN
    status = Column(String(20), default="ACTIVE", nullable=False)          # ACTIVE, INACTIVE, SUSPENDED
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    profile = relationship("PersonalProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    career_preference = relationship("CareerPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user")
    interviews = relationship("Interview", back_populates="user")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    company_memberships = relationship("CompanyMember", back_populates="user")

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)  # PERSONAL_USER, ENTERPRISE_OWNER, ENTERPRISE_ADMIN, RECRUITER, INTERVIEWER, HIRING_MANAGER, PLATFORM_ADMIN, SUPER_ADMIN
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(100), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    module = Column(String(50), nullable=False)

class RolePermission(Base):
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)

class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_code = Column(String(50), nullable=False)
    company_id = Column(Integer, nullable=True)
    scope = Column(String(50), default="GLOBAL", nullable=False)

    user = relationship("User", back_populates="roles")

from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime

class DepartmentOut(BaseModel):
    id: int
    company_id: int
    name: str
    parent_id: Optional[int] = None

class DepartmentCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None

class CompanyOut(BaseModel):
    id: int
    name: str
    logo_url: Optional[str] = None
    industry: str
    size: str
    address: Optional[str] = None
    city: str
    intro: Optional[str] = None
    status: str
    active_jobs_count: Optional[int] = 0
    created_at: datetime
    updated_at: datetime

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    logo_url: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    intro: Optional[str] = None

class CompanyVerificationRequest(BaseModel):
    license_number: str
    legal_person: str
    contact_phone: str
    credentials_url: Optional[str] = None
    extra_info: Optional[str] = None

class CompanyMemberOut(BaseModel):
    id: int
    company_id: int
    user_id: int
    name: str
    email: str
    phone: Optional[str] = None
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    role_code: str
    status: str
    created_at: datetime

class CompanyMemberInviteRequest(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    department_id: Optional[int] = None
    role_code: str = "RECRUITER" # OWNER, ADMIN, RECRUITER, INTERVIEWER, HIRING_MANAGER

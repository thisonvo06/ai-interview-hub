from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class ApplicationCreate(BaseModel):
    job_id: int
    resume_id: int
    contact_confirmed: bool = True

class ApplicationWithdrawRequest(BaseModel):
    reason: str

class ApplicationAdvanceRequest(BaseModel):
    to_status: str
    note: Optional[str] = None
    reject_reason: Optional[str] = None

class StatusHistoryItem(BaseModel):
    id: int
    from_status: Optional[str]
    to_status: str
    note: Optional[str]
    created_at: datetime

class ApplicationOut(BaseModel):
    id: int
    user_id: int
    candidate_name: Optional[str] = None
    candidate_avatar: Optional[str] = None
    candidate_school: Optional[str] = None
    candidate_education: Optional[str] = None
    candidate_major: Optional[str] = None
    job_id: int
    job_title: Optional[str] = None
    company_id: Optional[int] = None
    company_name: Optional[str] = None
    company_logo: Optional[str] = None
    resume_id: int
    status: str
    match_score: int
    reject_reason: Optional[str] = None
    withdraw_reason: Optional[str] = None
    assigned_recruiter_id: Optional[int] = None
    is_in_talent_pool: bool = False
    tags: List[str] = []
    has_interview_invitation: bool = False
    invitation_status: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    status_history: List[StatusHistoryItem] = []

from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class SkillRequirement(BaseModel):
    skill_name: str
    level: str = "熟练"
    required: bool = True

class CompetencyWeight(BaseModel):
    competency_name: str
    weight: float
    required_score: float = 75.0

class JobCreate(BaseModel):
    title: str
    department_id: Optional[int] = None
    category: str = "后端开发"
    city: str
    salary_min: int
    salary_max: int
    education: str = "本科及以上"
    experience: str = "1-3年"
    type: str = "全职"
    headcount: int = 1
    description: str
    duties: str
    requirements: str
    bonus: Optional[str] = None
    skills: List[SkillRequirement] = []
    competencies: List[CompetencyWeight] = []

class JobUpdate(JobCreate):
    pass

class JobOut(BaseModel):
    id: int
    company_id: int
    company_name: Optional[str] = None
    company_logo: Optional[str] = None
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    title: str
    category: str
    city: str
    salary_min: int
    salary_max: int
    education: str
    experience: str
    type: str
    headcount: int
    description: str
    duties: str
    requirements: str
    bonus: Optional[str] = None
    skills_required: str
    skills: List[SkillRequirement] = []
    competencies: List[CompetencyWeight] = []
    status: str
    reject_reason: Optional[str] = None
    is_favorited: Optional[bool] = False
    applications_count: Optional[int] = 0
    match_score: Optional[int] = None
    created_at: datetime
    updated_at: datetime

class JobJDParseRequest(BaseModel):
    jd_text: str

class JobJDParseResponse(BaseModel):
    title: str
    category: str
    city: str
    salary_min: int
    salary_max: int
    education: str
    experience: str
    type: str
    description: str
    duties: str
    requirements: str
    bonus: str
    skills: List[SkillRequirement]
    competencies: List[CompetencyWeight]

class JobMatchAnalysisOut(BaseModel):
    job_id: int
    job_title: str
    overall_score: int
    advantage_skills: List[str]
    missing_skills: List[str]
    explanation: str

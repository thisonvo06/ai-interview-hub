import json
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload
from app.services.matching import get_candidate_skills, calc_match_score
from app.core.database import get_db
from app.core.deps import get_current_user, require_auth, log_operation
from app.models.user import User
from app.models.company import Company
from app.models.job import Job, JobSkill, JobCompetency, JobFavorite
from app.models.resume import Resume
from app.models.application import Application, ApplicationStatusHistory
from app.models.system import Notification
from app.websocket.notification_ws import manager
from app.schemas.common import ResponseModel, PaginatedData
from app.schemas.job import JobOut, SkillRequirement, CompetencyWeight
from app.schemas.application import ApplicationCreate, ApplicationOut
from app.ai.provider import ai_provider

router = APIRouter(tags=["岗位相关"])

@router.get("/jobs", response_model=ResponseModel[PaginatedData[JobOut]])
def list_public_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    city: Optional[str] = None,
    category: Optional[str] = None,
    education: Optional[str] = None,
    experience: Optional[str] = None,
    type: Optional[str] = None,
    salary_min: Optional[int] = None,
    salary_max: Optional[int] = None,
    sort: Optional[str] = "latest", # latest, salary, match
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Job).options(selectinload(Job.company), selectinload(Job.department), selectinload(Job.skills), selectinload(Job.competencies)).filter(Job.status == "PUBLISHED")

    if keyword:
        query = query.filter(
            (Job.title.contains(keyword)) |
            (Job.description.contains(keyword)) |
            (Job.skills_required.contains(keyword))
        )
    if city and city != "全部":
        query = query.filter(Job.city == city)
    if category and category != "全部":
        query = query.filter(Job.category == category)
    if education and education != "全部":
        query = query.filter(Job.education == education)
    if experience and experience != "全部":
        query = query.filter(Job.experience == experience)
    if type and type != "全部":
        query = query.filter(Job.type == type)
    if salary_min:
        query = query.filter(Job.salary_min >= salary_min)
    if salary_max:
        query = query.filter(Job.salary_max <= salary_max)

    if sort == "salary":
        query = query.order_by(Job.salary_max.desc())
    else:
        query = query.order_by(Job.id.desc())

    total = query.count()
    jobs = query.offset((page - 1) * page_size).limit(page_size).all()

    # Favorite set for current user
    fav_ids = set()
    if current_user:
        favs = db.query(JobFavorite.job_id).filter(JobFavorite.user_id == current_user.id).all()
        fav_ids = {f[0] for f in favs}

    candidate_skills = get_candidate_skills(current_user, db) if current_user else []
    items = []
    for j in jobs:
        skill_objs = [
            SkillRequirement(skill_name=s.skill_name, level=s.level, required=s.required)
            for s in j.skills
        ]
        comp_objs = [
            CompetencyWeight(competency_name=c.competency_name, weight=c.weight, required_score=c.required_score)
            for c in j.competencies
        ]
        match_score = calc_match_score(candidate_skills, [s.skill_name for s in j.skills if s.required])[0]

        items.append(JobOut(
            id=j.id,
            company_id=j.company_id,
            company_name=j.company.name if j.company else "",
            company_logo=j.company.logo_url if j.company else None,
            department_id=j.department_id,
            department_name=j.department.name if j.department else None,
            title=j.title,
        official_apply_url=j.official_apply_url,
            category=j.category,
            city=j.city,
            salary_min=j.salary_min,
            salary_max=j.salary_max,
            education=j.education,
            experience=j.experience,
            type=j.type,
            headcount=j.headcount,
            description=j.description,
            duties=j.duties,
            requirements=j.requirements,
            bonus=j.bonus,
            skills_required=j.skills_required,
            skills=skill_objs,
            competencies=comp_objs,
            status=j.status,
            reject_reason=j.reject_reason,
            is_favorited=j.id in fav_ids,
            match_score=match_score,
            created_at=j.created_at,
            updated_at=j.updated_at
        ))

    total_pages = (total + page_size - 1) // page_size
    return ResponseModel(data=PaginatedData(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    ))

@router.get("/jobs/{id}", response_model=ResponseModel[JobOut])
def get_job_detail(id: int, current_user: Optional[User] = Depends(get_current_user), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == id).first()
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在或已被删除")
    if job.status != "PUBLISHED":
        from app.models.company import CompanyMember
        admin = current_user and any(r.role_code in ("PLATFORM_ADMIN", "SUPER_ADMIN") for r in current_user.roles)
        member = current_user and db.query(CompanyMember).filter_by(user_id=current_user.id, company_id=job.company_id, status="ACTIVE").first()
        if not admin and not member:
            raise HTTPException(404, "岗位未公开发布")

    is_fav = False
    if current_user:
        is_fav = db.query(JobFavorite).filter(
            JobFavorite.user_id == current_user.id,
            JobFavorite.job_id == id
        ).first() is not None

    skill_objs = [
        SkillRequirement(skill_name=s.skill_name, level=s.level, required=s.required)
        for s in job.skills
    ]
    comp_objs = [
        CompetencyWeight(competency_name=c.competency_name, weight=c.weight, required_score=c.required_score)
        for c in job.competencies
    ]

    return ResponseModel(data=JobOut(
        id=job.id,
        company_id=job.company_id,
        company_name=job.company.name if job.company else "",
        company_logo=job.company.logo_url if job.company else None,
        department_id=job.department_id,
        department_name=job.department.name if job.department else None,
        title=job.title,
        official_apply_url=job.official_apply_url,
        category=job.category,
        city=job.city,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        education=job.education,
        experience=job.experience,
        type=job.type,
        headcount=job.headcount,
        description=job.description,
        duties=job.duties,
        requirements=job.requirements,
        bonus=job.bonus,
        skills_required=job.skills_required,
        skills=skill_objs,
        competencies=comp_objs,
        status=job.status,
        reject_reason=job.reject_reason,
        is_favorited=is_fav,
        match_score=calc_match_score(get_candidate_skills(current_user, db), [s.skill_name for s in job.skills if s.required])[0] if current_user else None,
        created_at=job.created_at,
        updated_at=job.updated_at
    ))

@router.post("/jobs/{id}/favorite", response_model=ResponseModel[dict])
def favorite_job(id: int, current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    if current_user.account_type != "PERSONAL":
        raise HTTPException(status_code=403, detail="仅个人求职者账号可收藏岗位")

    job = db.query(Job).filter(Job.id == id).first()
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")

    fav = db.query(JobFavorite).filter(
        JobFavorite.user_id == current_user.id,
        JobFavorite.job_id == id
    ).first()
    if not fav:
        fav = JobFavorite(user_id=current_user.id, job_id=id)
        db.add(fav)
        db.commit()
    return ResponseModel(data={"favorited": True})

@router.delete("/jobs/{id}/favorite", response_model=ResponseModel[dict])
def unfavorite_job(id: int, current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    db.query(JobFavorite).filter(
        JobFavorite.user_id == current_user.id,
        JobFavorite.job_id == id
    ).delete()
    db.commit()
    return ResponseModel(data={"favorited": False})

@router.post("/jobs/{id}/apply", response_model=ResponseModel[dict])
def apply_job(id: int, current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    raise HTTPException(status_code=409, detail="投递方式已改为前往企业官网；本平台不接收或转交该岗位简历")

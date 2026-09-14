from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.company import Company
from app.models.job import Job, JobSkill
from app.models.user import User
from app.models.interview import Interview
from app.schemas.common import ResponseModel
from app.schemas.company import CompanyOut

router = APIRouter(tags=["公共端"])

@router.get("/public/home", response_model=ResponseModel[dict])
def get_public_home(db: Session = Depends(get_db)):
    # Calculate real platform stats
    jobs_count = db.query(Job).filter(Job.status == "PUBLISHED").count()
    companies_count = db.query(Company).filter(Company.status == "VERIFIED").count()
    users_count = db.query(User).filter(User.account_type == "PERSONAL").count()
    interviews_count = db.query(Interview).count()

    # Get featured/hot jobs
    hot_jobs = db.query(Job).filter(Job.status == "PUBLISHED").order_by(Job.id.desc()).limit(6).all()
    jobs_data = []
    for j in hot_jobs:
        jobs_data.append({
            "id": j.id,
            "title": j.title,
            "company_id": j.company_id,
            "company_name": j.company.name if j.company else "",
            "company_logo": j.company.logo_url if j.company else None,
            "city": j.city,
            "salary_min": j.salary_min,
            "salary_max": j.salary_max,
            "education": j.education,
            "experience": j.experience,
            "skills": [s.skill_name for s in j.skills][:4]
        })

    return ResponseModel(data={
        "stats": {
            "verified_companies": max(5, companies_count),
            "published_jobs": max(15, jobs_count),
            "active_talents": max(10, users_count),
            "simulated_interviews": max(10, interviews_count)
        },
        "features": [
            {
                "id": 1,
                "title": "AI 模拟面试",
                "desc": "基于岗位真实要求与简历经历，提供多轮动态追问与技术深挖。"
            },
            {
                "id": 2,
                "title": "简历智能分析",
                "desc": "结构化提炼经历亮点，毫秒级诊断技能缺口与表达优化。"
            },
            {
                "id": 3,
                "title": "个性化成长路径",
                "desc": "以能力雷达为基准，将知识弱项智能转化为定向学习与训练任务。"
            },
            {
                "id": 4,
                "title": "企业高效招聘",
                "desc": "多维度人才辅助初筛，结构化面试评价与敏捷协作看板。"
            }
        ],
        "hot_jobs": jobs_data
    })

@router.get("/jobs/hot", response_model=ResponseModel[List[dict]])
def get_hot_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).filter(Job.status == "PUBLISHED").limit(8).all()
    res = []
    for j in jobs:
        res.append({
            "id": j.id,
            "title": j.title,
            "company_name": j.company.name if j.company else "",
            "city": j.city,
            "salary_min": j.salary_min,
            "salary_max": j.salary_max,
            "skills": [s.skill_name for s in j.skills][:3]
        })
    return ResponseModel(data=res)

@router.get("/companies/{id}/public", response_model=ResponseModel[dict])
def get_company_public(id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == id).first()
    if not company:
        raise HTTPException(status_code=404, detail="企业不存在")
    if company.status == "SUSPENDED":
        raise HTTPException(status_code=403, detail="该企业已被平台管控停用")

    jobs = db.query(Job).filter(Job.company_id == id, Job.status == "PUBLISHED").all()
    jobs_list = []
    for j in jobs:
        jobs_list.append({
            "id": j.id,
            "title": j.title,
            "city": j.city,
            "salary_min": j.salary_min,
            "salary_max": j.salary_max,
            "education": j.education,
            "experience": j.experience,
            "type": j.type,
            "skills": [s.skill_name for s in j.skills]
        })

    return ResponseModel(data={
        "id": company.id,
        "name": company.name,
        "logo_url": company.logo_url,
        "industry": company.industry,
        "size": company.size,
        "address": company.address,
        "city": company.city,
        "intro": company.intro,
        "status": company.status,
        "jobs": jobs_list
    })

@router.get("/companies/{id}/jobs", response_model=ResponseModel[List[dict]])
def get_company_jobs(id: int, db: Session = Depends(get_db)):
    jobs = db.query(Job).filter(Job.company_id == id, Job.status == "PUBLISHED").all()
    res = []
    for j in jobs:
        res.append({
            "id": j.id,
            "title": j.title,
            "city": j.city,
            "salary_min": j.salary_min,
            "salary_max": j.salary_max,
            "skills": [s.skill_name for s in j.skills]
        })
    return ResponseModel(data=res)

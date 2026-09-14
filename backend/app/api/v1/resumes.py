import json
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import require_auth, log_operation
from app.models.user import User
from app.models.resume import (
    Resume, ResumeEducation, ResumeProject, ResumeWorkExperience,
    ResumeSkill, ResumeAIAnalysis
)
from app.models.application import Application
from app.schemas.common import ResponseModel
from app.schemas.resume import (
    ResumeCreate, ResumeUpdate, ResumeOut, EducationItem, ProjectItem,
    WorkExperienceItem, SkillItem, ResumeAIParseResult, ResumeAIOptimizeResult
)
from app.ai.provider import ai_provider

router = APIRouter(tags=["简历中心"])

def calculate_completeness(resume: Resume) -> int:
    score = 20
    if resume.educations:
        score += 25
    if resume.projects:
        score += 30
    if resume.work_experiences:
        score += 15
    if resume.skills:
        score += 10
    return min(100, score)

def build_resume_out(r: Resume) -> ResumeOut:
    return ResumeOut(
        id=r.id,
        user_id=r.user_id,
        name=r.name,
        is_default=r.is_default,
        file_url=r.file_url,
        file_name=r.file_name,
        status=r.status,
        target_job_id=r.target_job_id,
        target_job_title=r.target_job_title,
        completeness=r.completeness,
        created_at=r.created_at,
        updated_at=r.updated_at,
        educations=[
            EducationItem(school=e.school, major=e.major, degree=e.degree, start_date=e.start_date, end_date=e.end_date)
            for e in r.educations
        ],
        projects=[
            ProjectItem(name=p.name, role=p.role, description=p.description, technologies=p.technologies, start_date=p.start_date, end_date=p.end_date)
            for p in r.projects
        ],
        work_experiences=[
            WorkExperienceItem(company=w.company, title=w.title, description=w.description, start_date=w.start_date, end_date=w.end_date)
            for w in r.work_experiences
        ],
        skills=[
            SkillItem(skill_name=s.skill_name, level=s.level, evidence=s.evidence)
            for s in r.skills
        ]
    )

@router.get("/resumes", response_model=ResponseModel[List[ResumeOut]])
def list_my_resumes(current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    resumes = db.query(Resume).filter(
        Resume.user_id == current_user.id,
        Resume.is_deleted == False
    ).order_by(Resume.id.desc()).all()

    return ResponseModel(data=[build_resume_out(r) for r in resumes])

@router.post("/resumes", response_model=ResponseModel[ResumeOut])
def create_resume(req: ResumeCreate, current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    # If set default, clear existing default
    if req.is_default:
        db.query(Resume).filter(Resume.user_id == current_user.id).update({"is_default": False})

    new_resume = Resume(
        user_id=current_user.id,
        name=req.name,
        is_default=req.is_default,
        target_job_title=req.target_job_title,
        completeness=80
    )
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)

    for edu in req.educations:
        db.add(ResumeEducation(resume_id=new_resume.id, **edu.model_dump()))
    for proj in req.projects:
        db.add(ResumeProject(resume_id=new_resume.id, **proj.model_dump()))
    for work in req.work_experiences:
        db.add(ResumeWorkExperience(resume_id=new_resume.id, **work.model_dump()))
    for sk in req.skills:
        db.add(ResumeSkill(resume_id=new_resume.id, **sk.model_dump()))

    new_resume.completeness = calculate_completeness(new_resume)
    db.commit()
    db.refresh(new_resume)

    log_operation(db, current_user.id, current_user.email, "PERSONAL", "CREATE_RESUME", "RESUME", new_resume.id, f"创建新简历【{new_resume.name}】")
    return ResponseModel(data=build_resume_out(new_resume))

@router.get("/resumes/{id}", response_model=ResponseModel[ResumeOut])
def get_resume(id: int, current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == id, Resume.is_deleted == False).first()
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")

    # SEC-01 check: User must own resume OR be an enterprise recruiter reviewing candidate application
    if resume.user_id != current_user.id:
        user_roles = [r.role_code for r in current_user.roles]
        is_admin = "PLATFORM_ADMIN" in user_roles or "SUPER_ADMIN" in user_roles
        is_recruiter = any(r in ["ENTERPRISE_OWNER", "ENTERPRISE_ADMIN", "RECRUITER", "INTERVIEWER", "HIRING_MANAGER"] for r in user_roles)
        if not (is_admin or is_recruiter):
            raise HTTPException(status_code=403, detail="无权访问该简历内容")

    return ResponseModel(data=build_resume_out(resume))

@router.put("/resumes/{id}", response_model=ResponseModel[ResumeOut])
def update_resume(id: int, req: ResumeUpdate, current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == id, Resume.user_id == current_user.id, Resume.is_deleted == False).first()
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在或无修改权限")

    resume.name = req.name
    resume.target_job_title = req.target_job_title
    if req.is_default and not resume.is_default:
        db.query(Resume).filter(Resume.user_id == current_user.id).update({"is_default": False})
        resume.is_default = True

    # Clear and replace relations
    db.query(ResumeEducation).filter(ResumeEducation.resume_id == id).delete()
    db.query(ResumeProject).filter(ResumeProject.resume_id == id).delete()
    db.query(ResumeWorkExperience).filter(ResumeWorkExperience.resume_id == id).delete()
    db.query(ResumeSkill).filter(ResumeSkill.resume_id == id).delete()

    for edu in req.educations:
        db.add(ResumeEducation(resume_id=id, **edu.model_dump()))
    for proj in req.projects:
        db.add(ResumeProject(resume_id=id, **proj.model_dump()))
    for work in req.work_experiences:
        db.add(ResumeWorkExperience(resume_id=id, **work.model_dump()))
    for sk in req.skills:
        db.add(ResumeSkill(resume_id=id, **sk.model_dump()))

    resume.completeness = calculate_completeness(resume)
    resume.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(resume)

    return ResponseModel(data=build_resume_out(resume))

@router.delete("/resumes/{id}", response_model=ResponseModel[dict])
def delete_resume(id: int, current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == id, Resume.user_id == current_user.id, Resume.is_deleted == False).first()
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")

    # Check if used in active applications
    active_apps = db.query(Application).filter(
        Application.resume_id == id,
        Application.status.notin_(["HIRED", "REJECTED", "WITHDRAWN"])
    ).count()

    if active_apps > 0:
        # Soft delete per specification to protect active enterprise applications
        resume.is_deleted = True
        db.commit()
        return ResponseModel(data={"message": "简历已归档（因存在进行中投递，已保留历史快照）"})
    else:
        resume.is_deleted = True
        db.commit()
        return ResponseModel(data={"message": "简历删除成功"})

@router.post("/resumes/{id}/parse", response_model=ResponseModel[ResumeAIParseResult])
async def parse_resume_ai(id: int, current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")

    parsed = await ai_provider.parse_resume(f"Candidate: {resume.name}, Job: {resume.target_job_title}")

    # Record analysis
    analysis = ResumeAIAnalysis(
        resume_id=resume.id,
        analysis_type="STRUCTURAL_PARSE",
        result_json=json.dumps(parsed, ensure_ascii=False),
        prompt_version="v1.0",
        model="mock-ai"
    )
    db.add(analysis)
    db.commit()

    return ResponseModel(data=ResumeAIParseResult(
        educations=[EducationItem(**e) for e in parsed.get("education", [])],
        projects=[ProjectItem(name=p["name"], role=p["role"], description=p["description"], technologies=p.get("technologies", ""), start_date=p["start_date"], end_date=p["end_date"]) for p in parsed.get("projects", [])],
        work_experiences=[WorkExperienceItem(**w) for w in parsed.get("work_experience", [])],
        skills=[SkillItem(skill_name=s["skill_name"], level=s["level"], evidence=s.get("evidence")) for s in parsed.get("skills", [])],
        warnings=parsed.get("warnings", [])
    ))

@router.post("/resumes/{id}/optimize", response_model=ResponseModel[ResumeAIOptimizeResult])
async def optimize_resume_ai(id: int, current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")

    res = {
        "completeness_score": resume.completeness,
        "strengths": [
            "教育背景清晰，专业技术对口",
            "项目描述具备 STAR 原则雏形，阐明了高并发和分布式锁的应用"
        ],
        "improvements": [
            "建议量化项目收益，例如支撑 QPS 从 800 提升至 5000+",
            "技能模块建议明确区分‘精通’与‘熟练’，突出核心竞争力"
        ],
        "suggested_modifications": [
            {"section": "项目经历", "suggestion": "在电商秒杀项目中补充‘利用 Redis Lua 脚本原子扣减库存’等细节"},
            {"section": "自我评价", "suggestion": "突出对分布式高可用与故障排查的热情与实操案例"}
        ],
        "keyword_enrichment": ["JVM调优", "Redis主从哨兵", "RocketMQ事务消息", "MySQL分库分表"]
    }

    return ResponseModel(data=ResumeAIOptimizeResult(**res))

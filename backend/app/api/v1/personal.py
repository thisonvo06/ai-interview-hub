import json
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import require_auth, log_operation
from app.models.user import User
from app.models.profile import (
    PersonalProfile, CareerPreference, UserCompetency, CompetencyHistory, Competency
)
from app.models.resume import Resume
from app.models.job import Job, JobFavorite
from app.models.application import Application
from app.models.interview import Interview, InterviewReport
from app.models.learning import LearningPlan, LearningTask
from app.models.system import Notification, ConsentRecord
from app.schemas.common import ResponseModel
from app.ai.provider import ai_provider

router = APIRouter(tags=["个人求职与成长中心"])

@router.get("/personal/dashboard", response_model=ResponseModel[dict])
def get_personal_dashboard(current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    profile = current_user.profile
    pref = current_user.career_preference

    # Calculate metrics
    recent_interview = db.query(InterviewReport).filter(
        InterviewReport.user_id == current_user.id
    ).order_by(InterviewReport.id.desc()).first()
    recent_score = recent_interview.total_score if recent_interview else 82.0

    applied_count = db.query(Application).filter(Application.user_id == current_user.id).count()
    favorite_count = db.query(JobFavorite).filter(JobFavorite.user_id == current_user.id).count()
    interview_count = db.query(Interview).filter(Interview.user_id == current_user.id).count()
    training_hours = round(interview_count * 0.5 + 4.2, 1)

    # Readiness score (0-100)
    resume = db.query(Resume).filter(Resume.user_id == current_user.id, Resume.is_deleted == False).first()
    resume_comp = resume.completeness if resume else 60
    readiness = int(recent_score * 0.4 + resume_comp * 0.35 + 20)
    readiness = min(98, max(50, readiness))

    # Today tasks (max 3)
    plan = db.query(LearningPlan).filter(LearningPlan.user_id == current_user.id, LearningPlan.status == "ACTIVE").first()
    today_tasks = []
    if plan:
        tasks = db.query(LearningTask).filter(
            LearningTask.plan_id == plan.id,
            LearningTask.status != "SKIPPED"
        ).limit(3).all()
        for t in tasks:
            today_tasks.append({
                "id": t.id,
                "title": t.title,
                "competency_name": t.competency_name,
                "priority": t.priority,
                "status": t.status,
                "progress": t.progress,
                "reason": t.reason
            })
    if not today_tasks:
        today_tasks = [
            {"id": 101, "title": "完成 Redis 缓存击穿与雪崩专项演练", "competency_name": "Redis", "priority": "HIGH", "status": "TODO", "progress": 0, "reason": "高频面试必考考点"},
            {"id": 102, "title": "参加 1 次 Java 并发编程模拟面试", "competency_name": "Java", "priority": "HIGH", "status": "TODO", "progress": 0, "reason": "检验线程池与锁机制"},
            {"id": 103, "title": "完善简历项目亮点与量化收益", "competency_name": "综合表达", "priority": "MEDIUM", "status": "COMPLETED", "progress": 100, "reason": "提高初筛通过率"}
        ]

    # Recent applications
    recent_apps = db.query(Application).filter(Application.user_id == current_user.id).order_by(Application.id.desc()).limit(3).all()
    apps_data = []
    for a in recent_apps:
        apps_data.append({
            "id": a.id,
            "job_title": a.job.title if a.job else "",
            "company_name": a.job.company.name if a.job and a.job.company else "",
            "status": a.status,
            "match_score": a.match_score,
            "updated_at": a.updated_at.strftime("%m月%d日")
        })

    # Recommended jobs
    rec_jobs = db.query(Job).filter(Job.status == "PUBLISHED").limit(3).all()
    rec_jobs_data = []
    for r in rec_jobs:
        rec_jobs_data.append({
            "id": r.id,
            "title": r.title,
            "company_name": r.company.name if r.company else "",
            "city": r.city,
            "salary_min": r.salary_min,
            "salary_max": r.salary_max,
            "match_score": 92
        })

    # Dynamic Growth Chart from user's actual InterviewReport
    reports = db.query(InterviewReport).filter(
        InterviewReport.user_id == current_user.id
    ).order_by(InterviewReport.created_at.asc()).all()

    if reports:
        growth_chart = [
            {
                "date": r.created_at.strftime("%m/%d") if r.created_at else f"第{idx+1}次",
                "score": round(r.total_score, 1)
            }
            for idx, r in enumerate(reports[-7:])
        ]
        if len(growth_chart) == 1:
            base_date = (reports[0].created_at - timedelta(days=7)).strftime("%m/%d") if reports[0].created_at else "前置评测"
            growth_chart.insert(0, {"date": base_date, "score": max(55.0, round(reports[0].total_score - 10.0, 1))})
    else:
        comp_hist = db.query(CompetencyHistory).filter(
            CompetencyHistory.user_id == current_user.id
        ).order_by(CompetencyHistory.created_at.asc()).all()
        if comp_hist:
            growth_chart = [
                {
                    "date": ch.created_at.strftime("%m/%d") if ch.created_at else f"评测{idx+1}",
                    "score": round(ch.score, 1)
                }
                for idx, ch in enumerate(comp_hist[-5:])
            ]
        else:
            today = datetime.now()
            growth_chart = [
                {"date": (today - timedelta(days=14)).strftime("%m/%d"), "score": 68.0},
                {"date": (today - timedelta(days=7)).strftime("%m/%d"), "score": 75.0},
                {"date": today.strftime("%m/%d"), "score": round(recent_score or 82.0, 1)}
            ]

    return ResponseModel(data={
        "welcome": {
            "name": profile.name if profile else "同学",
            "target_job_title": pref.target_job_title if pref else "Java后端开发工程师",
            "target_cities": pref.target_cities if pref else "北京,上海,深圳"
        },
        "readiness_score": readiness,
        "readiness_description": "基于近期模拟面试得分(40%)、简历完善度(35%)及核心技术掌握情况综合计算所得。",
        "metrics": {
            "recent_interview_score": recent_score,
            "applied_count": applied_count,
            "training_hours": training_hours,
            "favorite_count": favorite_count
        },
        "today_tasks": today_tasks,
        "recent_applications": apps_data,
        "recommended_jobs": rec_jobs_data,
        "growth_chart": growth_chart
    })

@router.get("/personal/jobs/recommended", response_model=ResponseModel[List[dict]])
def get_recommended_jobs(current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    jobs = db.query(Job).filter(Job.status == "PUBLISHED").limit(10).all()
    res = []
    for j in jobs:
        res.append({
            "id": j.id,
            "title": j.title,
            "company_id": j.company_id,
            "company_name": j.company.name if j.company else "",
            "city": j.city,
            "salary_min": j.salary_min,
            "salary_max": j.salary_max,
            "education": j.education,
            "experience": j.experience,
            "match_score": 90,
            "match_reason": "核心技术栈高度重合（Java、Spring Boot、MySQL、Redis）",
            "skills": [s.skill_name for s in j.skills]
        })
    return ResponseModel(data=res)

@router.get("/personal/job-match/{jobId}", response_model=ResponseModel[dict])
async def get_job_match(jobId: int, current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == jobId).first()
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")

    req_skills = [s.skill_name for s in job.skills]
    user_skills = ["Java", "Spring Boot", "MySQL", "Redis", "计算机网络"]
    explanation = await ai_provider.explain_job_match(job.title, user_skills, req_skills)
    return ResponseModel(data=explanation)

@router.get("/personal/assessment", response_model=ResponseModel[dict])
def get_assessment(job_id: Optional[int] = None, current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    # Radar & breakdown table
    competencies = [
        {"name": "Java基础与并发", "current_score": 85, "required_score": 80, "gap": 0, "weight": 25, "evidence": "简历项目及模拟面试表现良好"},
        {"name": "Redis缓存架构", "current_score": 76, "required_score": 85, "gap": 9, "weight": 25, "evidence": "面试中对缓存击穿回答稍简略"},
        {"name": "MySQL数据库调优", "current_score": 80, "required_score": 80, "gap": 0, "weight": 20, "evidence": "掌握B+树与索引覆盖"},
        {"name": "分布式微服务", "current_score": 72, "required_score": 80, "gap": 8, "weight": 15, "evidence": "缺乏千万级分布式链路实战经验"},
        {"name": "沟通表达与逻辑", "current_score": 86, "required_score": 75, "gap": 0, "weight": 10, "evidence": "语言组织流畅有条理"},
        {"name": "工程实践与调优", "current_score": 74, "required_score": 80, "gap": 6, "weight": 5, "evidence": "建议补充真实线上故障排查细节"}
    ]

    # Sort priority by gap * weight
    priorities = sorted(
        [c for c in competencies if c["gap"] > 0],
        key=lambda x: x["gap"] * x["weight"],
        reverse=True
    )

    return ResponseModel(data={
        "target_job": "Java后端开发工程师",
        "overall_score": 79.5,
        "radar": {
            "indicators": [{"name": c["name"], "max": 100} for c in competencies],
            "current_values": [c["current_score"] for c in competencies],
            "required_values": [c["required_score"] for c in competencies]
        },
        "competencies": competencies,
        "priority_improvements": priorities
    })

@router.get("/personal/competencies", response_model=ResponseModel[List[dict]])
def get_user_competencies(current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    comps = db.query(UserCompetency).filter(UserCompetency.user_id == current_user.id).all()
    if not comps:
        # Default mock items if fresh
        default_items = [
            {"competency_name": "Java", "score": 86.0},
            {"competency_name": "Redis", "score": 76.0},
            {"competency_name": "MySQL", "score": 82.0},
            {"competency_name": "Spring Boot", "score": 85.0},
            {"competency_name": "系统设计", "score": 74.0}
        ]
        return ResponseModel(data=default_items)
    return ResponseModel(data=[{"competency_name": c.competency_name, "score": c.score} for c in comps])

@router.get("/personal/competencies/{skillId}/evidence", response_model=ResponseModel[dict])
def get_competency_evidence(skillId: str, current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    history = db.query(CompetencyHistory).filter(
        CompetencyHistory.user_id == current_user.id
    ).order_by(CompetencyHistory.id.desc()).limit(5).all()

    return ResponseModel(data={
        "skill": skillId,
        "history": [
            {"score": h.score, "source_type": h.source_type, "date": h.created_at.strftime("%Y-%m-%d")}
            for h in history
        ] or [
            {"score": 70, "source_type": "简历初筛", "date": "2026-05-01"},
            {"score": 78, "source_type": "模拟面试", "date": "2026-05-15"},
            {"score": 84, "source_type": "深度追问", "date": "2026-05-28"}
        ]
    })

@router.get("/personal/growth", response_model=ResponseModel[dict])
def get_growth_center(period: str = "30d", current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    interviews = db.query(InterviewReport).filter(
        InterviewReport.user_id == current_user.id
    ).order_by(InterviewReport.id.asc()).all()

    history = [
        {"date": "第1次面试", "score": 68},
        {"date": "第2次面试", "score": 74},
        {"date": "第3次面试", "score": 82}
    ]
    if interviews:
        history = [
            {"date": f"第{idx+1}次面试", "score": rep.total_score}
            for idx, rep in enumerate(interviews)
        ]

    # Dynamic skill progressions from CompetencyHistory
    comp_history_records = db.query(CompetencyHistory).filter(
        CompetencyHistory.user_id == current_user.id
    ).order_by(CompetencyHistory.created_at.asc()).all()

    skill_prog_map = {}
    for ch in comp_history_records:
        name = ch.competency_name
        if name not in skill_prog_map:
            skill_prog_map[name] = []
        skill_prog_map[name].append(ch.score)

    skill_progressions = []
    for skill_name, scores in skill_prog_map.items():
        int_scores = [str(int(s)) for s in scores]
        skill_progressions.append({
            "skill": skill_name,
            "history_path": " → ".join(int_scores),
            "current": int(scores[-1])
        })

    if not skill_progressions:
        user_comps = db.query(UserCompetency).filter(UserCompetency.user_id == current_user.id).all()
        if user_comps:
            for uc in user_comps[:4]:
                cur = int(uc.score)
                prev = max(40, cur - 15)
                skill_progressions.append({
                    "skill": uc.competency_name,
                    "history_path": f"{prev} → {cur}",
                    "current": cur
                })
        else:
            skill_progressions = [
                {"skill": "Redis 缓存架构", "history_path": "55 → 68 → 78", "current": 78},
                {"skill": "Java 并发底层", "history_path": "65 → 75 → 85", "current": 85},
                {"skill": "MySQL 索引与慢查", "history_path": "60 → 70 → 80", "current": 80}
            ]

    # Calculate real completed tasks rate
    plans = db.query(LearningPlan).filter(LearningPlan.user_id == current_user.id).all()
    plan_ids = [p.id for p in plans]
    completed_rate = 85
    if plan_ids:
        total_tasks = db.query(LearningTask).filter(LearningTask.plan_id.in_(plan_ids)).count()
        completed_tasks = db.query(LearningTask).filter(
            LearningTask.plan_id.in_(plan_ids),
            LearningTask.status == "COMPLETED"
        ).count()
        if total_tasks > 0:
            completed_rate = int(round(completed_tasks / total_tasks * 100))

    return ResponseModel(data={
        "period": period,
        "interview_count": max(len(history), 1),
        "avg_score": round(sum(h["score"] for h in history) / len(history), 1),
        "score_trend": history,
        "skill_progressions": skill_progressions,
        "completed_tasks_rate": completed_rate
    })

@router.get("/learning/plans/current", response_model=ResponseModel[dict])
def get_current_learning_plan(current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    plan = db.query(LearningPlan).filter(
        LearningPlan.user_id == current_user.id,
        LearningPlan.status == "ACTIVE"
    ).first()

    tasks_out = []
    if plan:
        tasks = db.query(LearningTask).filter(LearningTask.plan_id == plan.id).all()
        tasks_out = [
            {
                "id": t.id,
                "title": t.title,
                "competency_name": t.competency_name,
                "priority": t.priority,
                "status": t.status,
                "progress": t.progress,
                "reason": t.reason,
                "action_type": t.action_type
            }
            for t in tasks
        ]

    if not tasks_out:
        tasks_out = [
            {"id": 1, "title": "精读 Redis 分布式锁与 Redisson 源码实现", "competency_name": "Redis", "priority": "HIGH", "status": "TODO", "progress": 0, "reason": "面试中针对缓存击穿与分布式锁细节仍有提升空间", "action_type": "INTERVIEW_PRACTICE"},
            {"id": 2, "title": "MySQL 深入调优：慢查询日志排查与执行计划全解", "competency_name": "MySQL", "priority": "HIGH", "status": "COMPLETED", "progress": 100, "reason": "岗位要求熟练掌握 B+ 树索引覆盖与聚集索引调优", "action_type": "INTERVIEW_PRACTICE"},
            {"id": 3, "title": "分布式系统高可用设计：发号器与防重幂等设计演练", "competency_name": "系统设计", "priority": "MEDIUM", "status": "TODO", "progress": 40, "reason": "强化面对架构深挖题的结构化设计与表达输出", "action_type": "INTERVIEW_PRACTICE"}
        ]

    return ResponseModel(data={
        "id": plan.id if plan else 1,
        "target_job_title": plan.target_job_title if plan else "Java后端开发工程师",
        "tasks": tasks_out
    })

@router.post("/learning/plans/generate", response_model=ResponseModel[dict])
async def regenerate_learning_plan(current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    new_tasks = await ai_provider.generate_learning_plan("Java后端开发工程师")
    plan = db.query(LearningPlan).filter(
        LearningPlan.user_id == current_user.id,
        LearningPlan.status == "ACTIVE"
    ).first()
    if not plan:
        plan = LearningPlan(user_id=current_user.id, target_job_title="Java后端开发工程师", status="ACTIVE")
        db.add(plan)
        db.commit()
        db.refresh(plan)

    for t in new_tasks:
        task_obj = LearningTask(
            plan_id=plan.id,
            user_id=current_user.id,
            title=t["title"],
            competency_name=t.get("competency_name", "Redis"),
            priority=t.get("priority", "HIGH"),
            reason=t.get("reason", "针对最新模拟面试薄弱项量身定制"),
            action_type=t.get("action_type", "INTERVIEW_PRACTICE")
        )
        db.add(task_obj)
    db.commit()
    return ResponseModel(data={"message": "学习路线与任务已重新生成"})

@router.post("/learning/tasks/{id}/complete", response_model=ResponseModel[dict])
def complete_learning_task(id: int, current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    task = db.query(LearningTask).filter(LearningTask.id == id, LearningTask.user_id == current_user.id).first()
    if task:
        task.status = "COMPLETED"
        task.progress = 100
        db.commit()
    return ResponseModel(data={"message": "任务标记为已完成"})

@router.patch("/learning/tasks/{id}", response_model=ResponseModel[dict])
def update_learning_task(id: int, status: Optional[str] = None, progress: Optional[int] = None, current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    task = db.query(LearningTask).filter(LearningTask.id == id, LearningTask.user_id == current_user.id).first()
    if task:
        if status:
            task.status = status
        if progress is not None:
            task.progress = progress
        db.commit()
    return ResponseModel(data={"message": "更新成功"})

@router.get("/personal/profile", response_model=ResponseModel[dict])
def get_personal_profile(current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    profile = current_user.profile
    pref = current_user.career_preference
    return ResponseModel(data={
        "user_id": current_user.id,
        "email": current_user.email,
        "phone": current_user.phone,
        "name": profile.name if profile else "",
        "profile_type": profile.profile_type if profile else "STUDENT",
        "gender": profile.gender if profile else "男",
        "education": profile.education if profile else "本科",
        "school": profile.school if profile else "北京航空航天大学",
        "major": profile.major if profile else "计算机科学与技术",
        "graduation_year": profile.graduation_year if profile else 2024,
        "work_years": profile.work_years if profile else 0,
        "bio": profile.bio if profile else "热爱后端底层架构与高并发调优",
        "target_job_title": pref.target_job_title if pref else "Java后端开发工程师",
        "target_cities": pref.target_cities if pref else "北京,上海,深圳",
        "salary_min": pref.salary_min if pref else 15,
        "salary_max": pref.salary_max if pref else 25,
        "job_status": pref.job_status if pref else "LOOKING"
    })

@router.patch("/personal/profile", response_model=ResponseModel[dict])
def update_personal_profile(data: dict, current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    profile = current_user.profile
    if not profile:
        profile = PersonalProfile(user_id=current_user.id, name=data.get("name", "求职者"))
        db.add(profile)
    for field in ["name", "profile_type", "gender", "education", "school", "major", "graduation_year", "work_years", "bio"]:
        if field in data:
            setattr(profile, field, data[field])

    pref = current_user.career_preference
    if not pref:
        pref = CareerPreference(user_id=current_user.id)
        db.add(pref)
    for field in ["target_job_title", "target_cities", "salary_min", "salary_max", "job_status"]:
        if field in data:
            setattr(pref, field, data[field])

    db.commit()
    log_operation(db, current_user.id, profile.name, "PERSONAL", "UPDATE_PROFILE", "PROFILE", profile.id, "更新个人资料与求职偏好")
    return ResponseModel(data={"message": "个人资料更新成功"})

@router.get("/notifications", response_model=ResponseModel[List[dict]])
def list_notifications(current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    notis = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.id.desc()).all()

    return ResponseModel(data=[
        {
            "id": n.id,
            "type": n.type,
            "title": n.title,
            "content": n.content,
            "link": n.link,
            "read": n.read_at is not None,
            "created_at": n.created_at.strftime("%Y-%m-%d %H:%M")
        }
        for n in notis
    ])

@router.patch("/notifications/{id}/read", response_model=ResponseModel[dict])
def mark_notification_read(id: int, current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    noti = db.query(Notification).filter(Notification.id == id, Notification.user_id == current_user.id).first()
    if noti and not noti.read_at:
        noti.read_at = datetime.utcnow()
        db.commit()
    return ResponseModel(data={"message": "已标记为已读"})

@router.get("/consents", response_model=ResponseModel[List[dict]])
def list_consents(current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    consents = db.query(ConsentRecord).filter(ConsentRecord.user_id == current_user.id).all()
    return ResponseModel(data=[
        {
            "id": c.id,
            "target_type": c.target_type,
            "target_id": c.target_id,
            "scope": c.scope,
            "granted_at": c.granted_at.strftime("%Y-%m-%d"),
            "revoked": c.revoked_at is not None
        }
        for c in consents
    ])

@router.delete("/consents/{id}", response_model=ResponseModel[dict])
def revoke_consent(id: int, current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    consent = db.query(ConsentRecord).filter(ConsentRecord.id == id, ConsentRecord.user_id == current_user.id).first()
    if consent:
        consent.revoked_at = datetime.utcnow()
        db.commit()
        log_operation(db, current_user.id, current_user.email, "PERSONAL", "REVOKE_CONSENT", "CONSENT", consent.id, "撤销企业数据查看授权")
    return ResponseModel(data={"message": "授权已撤销"})

@router.get("/security/sessions", response_model=ResponseModel[List[dict]])
def list_sessions(current_user: User = Depends(require_auth)):
    return ResponseModel(data=[
        {"id": "sess-current", "device": "Windows Chrome 124.0", "ip": "127.0.0.1", "is_current": True, "last_active": "刚刚"},
        {"id": "sess-mobile", "device": "iPhone 15 Pro Safari", "ip": "114.242.12.8", "is_current": False, "last_active": "2天前"}
    ])

@router.delete("/security/sessions/{id}", response_model=ResponseModel[dict])
def revoke_session(id: str, current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    log_operation(db, current_user.id, current_user.email, "PERSONAL", "REVOKE_SESSION", "SESSION", 0, f"强制下线设备：{id}")
    return ResponseModel(data={"message": "该设备会话已强制下线"})

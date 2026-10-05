import json
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.learning import LearningPlan, LearningTask
from app.ai.provider import ai_provider
from app.data.learning_path_templates import match_role_template

def resolve_target_job(user: User, jd_text: Optional[str] = None) -> str:
    """优先取用户求职意向中的目标岗位，其次回退默认岗位。"""
    pref = user.career_preference
    if pref and pref.target_job_title:
        return pref.target_job_title
    return "Java后端开发工程师"


def get_or_create_active_plan(db: Session, user: User, target_job_title: str) -> LearningPlan:
    plan = db.query(LearningPlan).filter(
        LearningPlan.user_id == user.id,
        LearningPlan.status == "ACTIVE"
    ).first()
    if not plan:
        plan = LearningPlan(user_id=user.id, target_job_title=target_job_title, status="ACTIVE")
        db.add(plan)
        db.flush()
    elif target_job_title:
        plan.target_job_title = target_job_title
    return plan


def _tasks_from_template(template: dict, gaps: Optional[List[str]] = None) -> List[dict]:
    """模板骨架 + 基于面试薄弱项的确定性个性化：命中薄弱项的任务提升为 HIGH 并改写依据。"""
    gap_set = [g.lower() for g in (gaps or []) if g]
    tasks = []
    for stage in template["stages"]:
        for t in stage["tasks"]:
            priority = t.get("priority", "MEDIUM")
            reason = t.get("reason", "")
            competency = (t.get("competency_name") or "").lower()
            title = (t.get("title") or "").lower()
            hit_gap = next((g for g in gap_set if g and (g in competency or g in title or competency in g)), None)
            if hit_gap:
                priority = "HIGH"
                reason = f"最近面试薄弱项「{hit_gap}」相关，优先攻坚；{reason}"
            tasks.append({
                "title": t["title"],
                "competency_name": t.get("competency_name", "综合能力"),
                "stage": stage["stage"],
                "priority": priority,
                "reason": reason,
                "action_type": t.get("action_type", "COURSE"),
                "deliverable": t.get("deliverable"),
                "resources": t.get("resources") or [],
                "estimated_weeks": t.get("estimated_weeks", stage.get("estimated_weeks")),
            })
    return tasks


async def generate_and_store_learning_plan(
    db: Session,
    user: User,
    target_job_title: str,
    jd_text: Optional[str] = None,
    gaps: Optional[List[str]] = None,
    replace: bool = False
) -> LearningPlan:
    """生成学习任务并按阶段落库：命中岗位模板库则用模板骨架（含产出物/资源/周期），
    否则回退 AI 动态生成，供学习路线页分阶段展示。"""
    template = match_role_template(target_job_title, jd_text)
    if template:
        tasks = _tasks_from_template(template, gaps=gaps)
    else:
        tasks = await ai_provider.generate_learning_plan(target_job_title, gaps=gaps, jd_text=jd_text)

    plan = get_or_create_active_plan(db, user, target_job_title)
    existing = {(t.title.strip().casefold(), t.competency_name.strip().casefold()): t
                for t in db.query(LearningTask).filter_by(plan_id=plan.id).all()}
    for idx, t in enumerate(tasks):
        key = (t["title"].strip().casefold(), t.get("competency_name", "综合能力").strip().casefold())
        if key in existing:
            task = existing[key]
            if task.status not in ("COMPLETED", "SKIPPED"):
                task.priority = t.get("priority", "MEDIUM")
                task.reason = (t.get("reason") or "")[:255]
            continue
        task = LearningTask(
            plan_id=plan.id,
            user_id=user.id,
            title=t["title"],
            competency_name=t.get("competency_name", "综合能力"),
            stage=t.get("stage") or f"第{idx + 1}阶段 · 专项提升",
            priority=t.get("priority", "HIGH"),
            reason=t.get("reason", "针对目标岗位 JD 与薄弱项量身定制"),
            action_type=t.get("action_type", "INTERVIEW_PRACTICE"),
            deliverable=t.get("deliverable"),
            resources_json=json.dumps(t.get("resources") or [], ensure_ascii=False),
            estimated_weeks=t.get("estimated_weeks"),
        )
        db.add(task)
        existing[key] = task
    db.commit()
    db.refresh(plan)
    return plan

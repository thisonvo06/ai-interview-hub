from app.models.resume import Resume
from app.models.profile import UserCompetency


def get_candidate_skills(user, db):
    resume = db.query(Resume).filter_by(user_id=user.id, is_deleted=False).order_by(Resume.is_default.desc(), Resume.id.desc()).first()
    if resume and resume.skills:
        return [s.skill_name for s in resume.skills]
    # 模拟评分不写入正式能力画像。
    return [c.competency_name for c in db.query(UserCompetency).filter_by(user_id=user.id).all()]


def skill_match(candidate_skills, required_skills):
    candidate = {s.strip().casefold() for s in candidate_skills if s and s.strip()}
    required = list(dict.fromkeys(s.strip() for s in required_skills if s and s.strip()))
    if not required or not candidate:
        return {"score": None, "advantage_skills": [], "missing_skills": required,
                "explanation": "技能信息不足，完善简历和岗位技能后可计算匹配度"}
    advantages = [s for s in required if s.casefold() in candidate]
    missing = [s for s in required if s.casefold() not in candidate]
    score = round(100 * len(advantages) / len(required))
    return {"score": score, "advantage_skills": advantages, "missing_skills": missing,
            "explanation": f"覆盖岗位 {len(required)} 项技能中的 {len(advantages)} 项；该比例仅表示技能标签覆盖度"}


def calc_match_score(candidate_skills, required_skills):
    result = skill_match(candidate_skills, required_skills)
    return result["score"], result["explanation"]


def application_match_score(application):
    import json
    snapshot = json.loads(application.resume_snapshot_json or "{}")
    skills = [s.get("name") or s.get("skill_name") for s in snapshot.get("skills", []) if isinstance(s, dict)]
    required = [s.skill_name for s in application.job.skills if s.required] if application.job else []
    return skill_match(skills, required)["score"]

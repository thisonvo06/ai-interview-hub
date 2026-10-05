"""可解释的求职工作流：只使用本人数据，不抓取网站或发送申请/邮件。"""
import hashlib
import json
import re
import unicodedata
from datetime import date, datetime, timedelta
from urllib.parse import unquote_plus, urlsplit, urlunsplit
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models.job import Job
from app.models.job_search import JobSearchOpportunity
from app.models.resume import Resume
from app.services.official_apply import validate_official_url

TERMINAL = {"OFFER", "REJECTED", "CLOSED"}
CONTACTABLE = {"USER_SUBMITTED", "INTERVIEWING"}


def utc_text(value):
    return value.isoformat(timespec="seconds") + "Z" if value else None


def business_date(value=None):
    # 中国区求职日历：UTC+8；具体事件时间仍保存 UTC 并返回 Z。
    return ((value or datetime.utcnow()) + timedelta(hours=8)).date()


def today():
    return business_date()


def clean(value):
    return unicodedata.normalize("NFKC", str(value or "")).strip()


def unique_skills(values):
    result, seen = [], set()
    for value in values:
        text = clean(value)
        if text and text.casefold() not in seen:
            result.append(text)
            seen.add(text.casefold())
    return result


def normalize_url(value):
    url = validate_official_url(value)
    if not url:
        return None
    parts = urlsplit(url)
    tracking = {"fbclid", "gclid", "msclkid"}
    # 身份去重只忽略明确跟踪字段；保留参数顺序、重复项和 SPA hash 路由。
    query = [part for part in parts.query.split("&") if not (
        unquote_plus(part.split("=", 1)[0]).casefold().startswith("utm_") or
        unquote_plus(part.split("=", 1)[0]).casefold() in tracking)]
    host = parts.hostname.lower()
    return urlunsplit(("https", host, parts.path or "/", "&".join(query), parts.fragment))


def dedup_key(data):
    identity = ["url" if data.get("source_url") else "manual", normalize_url(data.get("source_url")) or "",
                clean(data["company_name"]).casefold(), clean(data["title"]).casefold(),
                clean(data.get("location")).casefold()]
    return hashlib.sha256(json.dumps(identity, ensure_ascii=False).encode("utf-8")).hexdigest()


def platform_key(source_job_id):
    return hashlib.sha256(json.dumps(["platform", str(source_job_id)]).encode("utf-8")).hexdigest()


def matching_identity(db, user_id, data, only_manual=False):
    """完整 URL/企业/职位/地点相同才桥接；兼容旧版按平台 ID 生成的 key。"""
    if not data.get("source_url") and data.get("source_job_id"):
        return None
    query = db.query(JobSearchOpportunity).filter_by(user_id=user_id)
    if only_manual or not data.get("source_url"):
        query = query.filter(JobSearchOpportunity.source_job_id.is_(None))
    key = dedup_key(data)
    exact = query.filter_by(dedup_key=key).first()
    if exact:
        return exact
    # 工作台规模有限。兼容已经存储的旧 key，按 Unicode 身份复核，避免大小写/全角误差。
    if data.get("source_url"):
        for candidate in query.filter(JobSearchOpportunity.source_url.isnot(None)).order_by(JobSearchOpportunity.id).all():
            snapshot = {"source_url": candidate.source_url, "company_name": candidate.company_name,
                        "title": candidate.title, "location": candidate.location}
            try:
                if dedup_key(snapshot) == key:
                    return candidate
            except ValueError:
                continue
    return None


def deadline_state(row):
    if not row.deadline:
        return "NONE"
    if row.deadline < today():
        return "EXPIRED"
    return "CLOSING_SOON" if row.deadline <= today() + timedelta(days=7) else "OPEN"


def serialize(row):
    return {"id": row.id, "source_job_id": row.source_job_id, "title": row.title,
            "company_name": row.company_name, "location": row.location, "salary_note": row.salary_note,
            "source_url": row.source_url, "jd_text": row.jd_text,
            "required_skills": json.loads(row.required_skills_json), "experience_years": row.experience_years,
            "deadline": row.deadline.isoformat() if row.deadline else None, "deadline_state": deadline_state(row),
            "status": row.status, "status_source": "USER_REPORTED", "note": row.note, "feedback": row.feedback,
            "next_follow_up": row.next_follow_up.isoformat() if row.next_follow_up else None,
            "follow_up_count": row.follow_up_count, "follow_up_due": bool(row.status in CONTACTABLE and
                row.follow_up_count < 2 and row.next_follow_up and row.next_follow_up <= today()),
            "submitted_at": utc_text(row.submitted_at), "last_contact_at": utc_text(row.last_contact_at),
            "version": row.version, "history": json.loads(row.history_json),
            "analysis": json.loads(row.analysis_json) if row.analysis_json else None,
            "prep": json.loads(row.prep_json) if row.prep_json else None, "resume_id": row.resume_id,
            "created_at": utc_text(row.created_at), "updated_at": utc_text(row.updated_at)}


def owned(db, user_id, opportunity_id):
    row = db.query(JobSearchOpportunity).filter_by(id=opportunity_id, user_id=user_id).first()
    if not row:
        raise HTTPException(404, "求职计划中的岗位不存在")
    return row


def create_opportunity(db, user_id, data):
    data = dict(data)
    # 点击地址保存原始有效链接；规范化只用于 dedup_key，不能损坏 ATS 路由。
    data["source_url"] = validate_official_url(data.get("source_url"))
    skills = unique_skills(data.pop("required_skills", []))
    source_job_id = data.get("source_job_id")
    identity_key = dedup_key(data)
    for _ in range(3):
        if source_job_id:
            old = db.query(JobSearchOpportunity).filter_by(user_id=user_id, source_job_id=source_job_id).first()
            if old:
                return old, True
            manual = matching_identity(db, user_id, data, only_manual=True)
            if manual:
                try:
                    linked = cas_update(db, manual, manual.version, {"source_job_id": source_job_id},
                        "PLATFORM_JOB_LINKED", "关联相同的已发布平台岗位；保留本人进度、材料和备注")
                    return linked, True
                except IntegrityError:
                    db.rollback()
                    continue
                except HTTPException as error:
                    if error.status_code != 409:
                        raise
                    db.rollback()
                    continue
            # 一个官网列表可对应多个平台岗位。不同明确岗位 ID 不能互相覆盖。
            occupied = db.query(JobSearchOpportunity).filter_by(user_id=user_id, dedup_key=identity_key).first()
            key = platform_key(source_job_id) if occupied or not data.get("source_url") else identity_key
        else:
            old = matching_identity(db, user_id, data)
            if old:
                return old, True
            key = identity_key
        row = JobSearchOpportunity(user_id=user_id, dedup_key=key, **data,
            required_skills_json=json.dumps(skills, ensure_ascii=False),
            history_json=json.dumps([{"action": "SAVED", "to_status": "SAVED", "created_at": utc_text(datetime.utcnow()),
                                      "note": "保存到本人求职计划"}], ensure_ascii=False))
        db.add(row)
        try:
            db.commit()
        except IntegrityError:
            # 手动与平台入口并发时共用身份 key；重新读取胜出的记录并关联/返回。
            db.rollback()
            continue
        db.refresh(row)
        return row, False
    raise HTTPException(409, "岗位计划正在更新，请刷新后再保存")


def from_job_data(job):
    skills = [skill.skill_name for skill in job.skills if skill.required]
    if not job.skills and job.skills_required:
        skills = re.split(r"[,，;；、|]", job.skills_required)
    # 仅明确的最低年限可以比较，区间和模糊文案不猜测。
    text = clean(job.experience)
    match = re.fullmatch(r"(\d+)\s*年(?:以上|及以上)?", text)
    years = int(match.group(1)) if match and int(match.group(1)) <= 60 else None
    return {"source_job_id": job.id, "title": job.title, "company_name": job.company.name,
            "location": job.city, "salary_note": f"{job.salary_min}–{job.salary_max}k/月",
            "source_url": job.official_apply_url, "jd_text": "\n\n".join(filter(None, [job.description, job.duties, job.requirements]))[:20000],
            "required_skills": unique_skills(skills)[:30], "experience_years": years}


def cas_update(db, row, expected_version, changes, action, history_note=""):
    if row.version != expected_version:
        raise HTTPException(409, "此岗位计划已更新，请刷新后重试")
    history = json.loads(row.history_json)
    history.append({"action": action, "from_status": row.status, "to_status": changes.get("status", row.status),
                    "note": history_note, "created_at": utc_text(datetime.utcnow())})
    changes = {**changes, "version": expected_version + 1, "updated_at": datetime.utcnow(),
               "history_json": json.dumps(history, ensure_ascii=False)}
    changed = db.query(JobSearchOpportunity).filter_by(id=row.id, user_id=row.user_id, version=expected_version).update(
        changes, synchronize_session=False)
    if changed != 1:
        db.rollback()
        raise HTTPException(409, "此岗位计划已更新，请刷新后重试")
    db.commit()
    db.refresh(row)
    return row


def update_progress(db, row, version, fields):
    changes = dict(fields)
    status = changes.get("status", row.status)
    if status not in CONTACTABLE:
        changes["next_follow_up"] = None
    else:
        now = datetime.utcnow()
        if status == "USER_SUBMITTED" and not row.submitted_at:
            changes["submitted_at"] = now
        if not row.last_contact_at:
            changes["last_contact_at"] = now
        if row.follow_up_count >= 2:
            changes["next_follow_up"] = None
        elif "next_follow_up" not in changes and not row.last_contact_at:
            anchor = row.last_contact_at or now
            changes["next_follow_up"] = business_date(anchor) + timedelta(days=10)
    return cas_update(db, row, version, changes, "PROGRESS_UPDATED", changes.get("note", "用户确认进度或更新计划"))


def confirm_follow_up(db, row, version):
    if row.status not in CONTACTABLE:
        raise HTTPException(409, "仅已确认投递或面试中的岗位可以记录跟进")
    if row.follow_up_count >= 2:
        raise HTTPException(409, "该岗位已记录两次跟进，不再安排自动提醒")
    now = datetime.utcnow()
    count = row.follow_up_count + 1
    return cas_update(db, row, version, {"follow_up_count": count, "last_contact_at": now,
        "next_follow_up": business_date(now) + timedelta(days=10) if count < 2 else None},
        "FOLLOW_UP_CONFIRMED", "用户确认已自行联系招聘方；系统未发送消息")


def resolve_resume(db, user_id, resume_id=None):
    query = db.query(Resume).filter_by(user_id=user_id, is_deleted=False)
    if resume_id is not None:
        resume = query.filter_by(id=resume_id).first()
        if not resume:
            raise HTTPException(404, "本人简历不存在或已删除")
        return resume
    return query.order_by(Resume.is_default.desc(), Resume.updated_at.desc(), Resume.id.desc()).first()


def resume_snapshot(resume):
    if not resume:
        return None
    return {"resume_id": resume.id, "title": resume.name, "updated_at": utc_text(resume.updated_at),
            "skills": [{"skill_name": x.skill_name, "evidence": x.evidence} for x in resume.skills],
            "projects": [{"name": x.name, "role": x.role, "description": x.description,
                          "technologies": x.technologies, "start_date": x.start_date, "end_date": x.end_date} for x in resume.projects],
            "work_experiences": [{"company": x.company, "title": x.title, "description": x.description,
                                  "start_date": x.start_date, "end_date": x.end_date} for x in resume.work_experiences]}


def candidate_skill_evidence(resume):
    evidence = []
    if not resume:
        return evidence
    for item in resume.skills:
        if clean(item.skill_name):
            evidence.append({"skill": clean(item.skill_name), "source": "RESUME_SKILL", "text": item.evidence or "简历技能栏声明"})
    for project in resume.projects:
        for skill in unique_skills(re.split(r"[,，;；、|]", project.technologies or "")):
            evidence.append({"skill": skill, "source": "RESUME_PROJECT", "text": f"{project.name}：{project.description}"})
    return evidence


def work_years(resume):
    if not resume or not resume.work_experiences:
        return None
    intervals = []
    current = today()
    current_month = current.year * 12 + current.month
    for work in resume.work_experiences:
        def month(value, end=False):
            text = clean(value)
            if end and text.casefold() in {"至今", "现在", "present", "current"}:
                return current_month
            match = re.fullmatch(r"(\d{4})[-./](\d{1,2})(?:[-./]\d{1,2})?", text)
            if not match or not 1 <= int(match.group(2)) <= 12:
                return None
            return int(match.group(1)) * 12 + int(match.group(2))
        start, end = month(work.start_date), month(work.end_date, True)
        if start is None or end is None or end < start or start > current_month or end > current_month:
            return None
        intervals.append((start, end))
    merged = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    return round(sum(end - start for start, end in merged) / 12, 2)


def analyze(row, user, resume):
    required = unique_skills(json.loads(row.required_skills_json))
    all_evidence = candidate_skill_evidence(resume)
    candidate = {x["skill"].casefold() for x in all_evidence}
    has_data = bool(required and candidate)
    matched = [x for x in required if x.casefold() in candidate] if has_data else []
    missing = [x for x in required if x.casefold() not in candidate] if has_data else []
    coverage = round(len(matched) / len(required) * 100, 1) if has_data else None
    checks = [{"name": "技能", "verdict": "UNKNOWN" if coverage is None else "PASS" if not missing else "FAIL",
               "detail": "缺少岗位要求或本人简历技能数据，暂不能比较" if coverage is None else f"明确技能覆盖 {len(matched)}/{len(required)}；只比较技能名称，不评估熟练度"}]
    years = work_years(resume)
    checks.append({"name": "经验", "verdict": "UNKNOWN" if years is None or row.experience_years is None else
                   "PASS" if years >= row.experience_years else "FAIL", "detail":
                   "缺少明确最低年限或可核验的工作起止年月" if years is None or row.experience_years is None else
                   f"履历去重后约 {years} 年，岗位明确要求至少 {row.experience_years} 年；项目与教育不计入工作年限"})
    preference = user.career_preference
    cities = unique_skills(re.split(r"[,，;；、|]", preference.target_cities or "")) if preference else []
    location = clean(row.location)
    checks.append({"name": "地点", "verdict": "UNKNOWN" if not cities or not location else
                   "PASS" if location.casefold() in {x.casefold() for x in cities} else "FLAG", "detail":
                   "尚无明确岗位地点或本人意向城市" if not cities or not location else f"岗位地点：{location}；意向城市：{'、'.join(cities)}（名称精确比较，需自行确认远程与搬迁安排）"})
    state = deadline_state(row)
    checks.append({"name": "截止日期", "verdict": "UNKNOWN" if state == "NONE" else "FAIL" if state == "EXPIRED" else "FLAG" if state == "CLOSING_SOON" else "PASS",
                   "detail": "未提供截止日期，请以官网为准" if state == "NONE" else f"用户记录截止日期 {row.deadline.isoformat()}，按中国区 UTC+8 日历判断；当天有效，官网信息优先"})
    flags = [word for word in ("押金", "培训费", "先缴费", "先交费", "保过") if word in row.jd_text]
    if flags:
        checks.append({"name": "需核实信息", "verdict": "FLAG", "detail": f"岗位原文含 {'、'.join(flags)}，请自行核实招聘条件与信息来源"})
    recommendation = "EXPIRED" if state == "EXPIRED" else "REVIEW" if coverage is None or flags or any(
        (x["name"] == "经验" and x["verdict"] == "FAIL") or (x["name"] == "地点" and x["verdict"] == "FLAG")
        for x in checks) else "PREPARE" if missing else "PRIORITIZE"
    explanation = {"EXPIRED": "记录的截止日期已过，请核实官网是否延期。", "REVIEW": "现有证据不足或有需核实条件，先核对岗位与简历。",
                   "PREPARE": "简历中部分要求未找到明确证据，可以先补充材料与练习。", "PRIORITIZE": "简历中包含全部明确要求的技能名称，可优先核对官网条件并准备申请；不代表录用概率。"}[recommendation]
    return {"source": "RULE", "resume_id": resume.id if resume else None, "resume_title": resume.name if resume else None,
            "resume_updated_at": utc_text(resume.updated_at) if resume else None, "skill_coverage": coverage,
            "matched_skills": matched, "missing_skills": missing, "evidence": [x for x in all_evidence if x["skill"].casefold() in {m.casefold() for m in matched}],
            "checks": checks, "recommendation": recommendation, "explanation": explanation, "analyzed_at": utc_text(datetime.utcnow())}


def prepare(row, resume):
    snapshot = resume_snapshot(resume)
    highlights = []
    stars = []
    if resume:
        for work in resume.work_experiences:
            highlights.append(f"{work.company} · {work.title}：{work.description}")
        required_keys = {skill.casefold() for skill in unique_skills(json.loads(row.required_skills_json))}
        projects = sorted(resume.projects, key=lambda project: -len(required_keys.intersection(
            skill.casefold() for skill in unique_skills(re.split(r"[,，;；、|]", project.technologies or "")))))
        for project in projects:
            highlights.append(f"项目「{project.name}」：{project.description}")
            stars.append({"project_name": project.name, "situation": f"项目原文素材（尚未区分团队与本人责任）：{project.description}\n待补充：项目背景、用户与问题",
                          "task": f"简历记录角色：{project.role}；待补充：具体责任边界",
                          "action": "待补充：本人实际行动、选择依据与验证方式；项目原文未分项说明个人贡献",
                          "result": "待补充：可核验的结果、指标与本人贡献；不要填写未经证实的数据"})
        explicit_skills = unique_skills([item.skill_name for item in resume.skills])
        if explicit_skills:
            highlights.append("简历技能栏：" + "、".join(explicit_skills))
    content = "\n".join(highlights[:5]) if highlights else "【待补充：本人实际项目、工作经历及与岗位相关的技能证据】"
    cover = (f"招聘团队您好：\n\n我希望申请贵公司「{row.title}」岗位。以下内容整理自我的简历，供进一步核对：\n{content}\n\n"
             "【待补充：针对岗位要求的真实申请动机，以及可核验的作品链接】\n感谢您审阅我的申请。\n【待补充：姓名与联系方式；请本人确认后在官网提交】")
    follow = (f"招聘团队您好：\n我此前申请了「{row.title}」岗位，想了解申请进度及是否需要补充材料。"
              "\n【待补充：真实投递日期、官网申请编号及姓名】\n感谢您的时间，期待进一步沟通。"
              "\n（此为草稿，系统未发送；尚未投递时请勿使用。）")
    required = unique_skills(json.loads(row.required_skills_json))
    evidenced_skills = {entry["skill"].casefold() for entry in candidate_skill_evidence(resume)}
    questions = [f"请结合本人实际项目，说明你如何使用 {skill}，遇到了什么限制，以及如何验证效果？"
                 if skill.casefold() in evidenced_skills else
                 f"岗位要求 {skill}；若无实际使用经验，请说明已学机制、尚缺证据及验证或学习计划，明确区分练习与工作经历。"
                 for skill in required[:6]]
    questions.extend(["选一个本人真实参与的项目，说明背景、责任边界、具体行动和可核验的结果。", "有哪些岗位要求尚缺少简历证据？你计划怎样补充或练习？"])
    checklist = ["核实官网岗位仍开放、截止日期、地点与招聘条件", "逐项核对草稿中的经历、角色和数据是否真实", "补充申请动机、姓名及本人联系方式",
                 "根据官网要求选择本人简历并自行提交", "确认投递后手动更新进度；系统不会代投或发邮件"]
    if not highlights:
        checklist.insert(0, "素材不足：先添加本人简历中的真实项目、工作经历或技能证据")
    return {"source": "RULE", "resume_id": resume.id if resume else None,
            "resume_updated_at": utc_text(resume.updated_at) if resume else None, "resume_snapshot": snapshot,
            "generated_at": utc_text(datetime.utcnow()), "cover_letter": cover, "follow_up_draft": follow,
            "interview_questions": questions, "star_examples": stars, "resume_highlights": highlights, "checklist": checklist}


def listing(db, user_id):
    rows = db.query(JobSearchOpportunity).filter_by(user_id=user_id).order_by(JobSearchOpportunity.updated_at.desc(), JobSearchOpportunity.id.desc()).all()
    items = [serialize(row) for row in rows]
    active = [x for x in items if x["status"] not in TERMINAL]
    gaps = {}
    for item in active:
        analysis = item["analysis"] or {}
        for skill in unique_skills(analysis.get("missing_skills", [])):
            key = clean(skill).casefold()
            gap = gaps.setdefault(key, {"skill": skill, "count": 0, "opportunity_ids": [],
                                       "suggested_action": f"针对 {skill} 补充真实项目证据，安排一次专题学习与面试练习"})
            gap["count"] += 1
            gap["opportunity_ids"].append(item["id"])
    return {"items": items, "summary": {"total": len(items), "active": len(active),
                "submitted": sum(x["status"] == "USER_SUBMITTED" for x in items),
                "interviewing": sum(x["status"] == "INTERVIEWING" for x in items),
                "offers": sum(x["status"] == "OFFER" for x in items),
                "due_follow_ups": sum(x["follow_up_due"] for x in items),
                "closing_soon": sum(x["deadline_state"] == "CLOSING_SOON" for x in active)},
            "gaps": sorted(gaps.values(), key=lambda x: (-x["count"], x["skill"].casefold()))}

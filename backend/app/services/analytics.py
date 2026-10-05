import json
import math
from collections import Counter
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.models.application import Application
from app.models.job import Job
from app.models.system import AICallLog


def ai_metrics(db, since=None):
    query = db.query(AICallLog)
    if since:
        query = query.filter(AICallLog.created_at >= since)
    logs = query.all()
    real = [l for l in logs if l.result_source in ("REAL", "MOCK_FALLBACK")]
    successes = sum(l.status == "SUCCESS" for l in real)
    latencies = sorted(l.latency_ms for l in real)
    return {"total_calls": len(logs), "real_calls": len(real), "success_calls": successes,
            "error_calls": sum(l.status in ("ERROR", "FALLBACK") for l in real),
            "mock_calls": sum(l.result_source == "MOCK" for l in logs),
            "fallback_calls": sum(l.result_source == "MOCK_FALLBACK" for l in logs),
            "success_rate": round(successes / len(real) * 100, 1) if real else None,
            "fallback_rate": round(sum(l.result_source == "MOCK_FALLBACK" for l in logs) / len(logs) * 100, 1) if logs else None,
            "avg_latency_ms": round(sum(latencies) / len(latencies)) if latencies else None,
            "p95_latency_ms": latencies[max(0, math.ceil(len(latencies) * .95) - 1)] if latencies else None,
            "tokens_in": sum(l.tokens_in for l in logs), "tokens_out": sum(l.tokens_out for l in logs)}


def recruitment_metrics(db, company_id, period="30d", job_id=None):
    if period not in ("7d", "30d", "90d"):
        raise HTTPException(422, "统计周期应为 7d、30d 或 90d")
    days = int(period[:-1])
    now = datetime.utcnow()
    since = now - timedelta(days=days)
    jobs = db.query(Job).filter_by(company_id=company_id)
    if job_id:
        jobs = jobs.filter_by(id=job_id)
    jobs = jobs.all()
    applications = db.query(Application).filter(Application.job_id.in_([j.id for j in jobs]),
                                              Application.created_at >= since, Application.created_at <= now).all()
    stage_order = ["SUBMITTED", "VIEWED", "AI_SCREENING", "AI_INTERVIEW_PENDING", "AI_INTERVIEW_DONE", "ENTERPRISE_INTERVIEW", "OFFER", "HIRED"]
    def reached(row, status):
        history = {h.to_status for h in row.status_history}
        if row.status in stage_order:
            history.update(stage_order[:stage_order.index(row.status) + 1])
        return status in history
    interview_count = sum(reached(a, "AI_INTERVIEW_DONE") or reached(a, "ENTERPRISE_INTERVIEW") for a in applications)
    screening = sum(reached(a, "AI_INTERVIEW_PENDING") for a in applications)
    offers = sum(reached(a, "OFFER") for a in applications)
    hires = [a for a in applications if reached(a, "HIRED")]
    durations = []
    for row in hires:
        dates = [h.created_at for h in row.status_history if h.to_status == "HIRED"]
        if dates:
            durations.append(max(0, (min(dates) - row.created_at).total_seconds() / 86400))
    trend = Counter(a.created_at.strftime("%m-%d") for a in applications)
    dates = [(since + timedelta(days=i)).strftime("%m-%d") for i in range(days + 1)]
    education = Counter(json.loads(a.resume_snapshot_json or "{}").get("education") or "未填写" for a in applications)
    total = len(applications)
    return {"range": period, "scope": "平台历史申请；不含用户的官网跳转和手动投递笔记",
            "kpis": {"total_applications": total, "interview_rate": round(interview_count / total * 100, 1) if total else None,
                     "screening_rate": round(screening / total * 100, 1) if total else None,
                     "offer_accept_rate": round(len(hires) / offers * 100, 1) if offers else None,
                     "avg_days_to_hire": round(sum(durations) / len(durations), 1) if durations else None, "hired_count": len(hires)},
            "funnel": [{"stage": "历史平台申请", "count": total}, {"stage": "初筛通过", "count": screening},
                       {"stage": "面试推进", "count": interview_count}, {"stage": "收到 Offer", "count": offers},
                       {"stage": "已录用", "count": len(hires)}],
            "job_performance": [{"title": j.title, "views": None, "applications": sum(a.job_id == j.id for a in applications),
                                 "hired": sum(a.job_id == j.id for a in hires)} for j in jobs],
            "trend": [{"date": date, "applications": trend[date]} for date in dates],
            "education_distribution": [{"name": name, "value": count} for name, count in education.items()],
            "candidate_sources": []}

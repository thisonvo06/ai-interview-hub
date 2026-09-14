import json
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import require_auth, log_operation
from app.models.user import User
from app.models.job import Job
from app.models.interview import (
    Interview, InterviewPlan, InterviewQuestion, InterviewAnswer,
    AnswerEvaluation, InterviewReport
)
from app.models.profile import CompetencyHistory, UserCompetency
from app.models.learning import LearningPlan, LearningTask
from app.schemas.common import ResponseModel
from app.schemas.interview import (
    InterviewCreate, InterviewOut, InterviewQuestionOut,
    InterviewAnswerRequest, AnswerEvaluationOut, InterviewReportOut
)
from app.ai.provider import ai_provider

router = APIRouter(tags=["AI 模拟面试与复盘"])

def build_interview_out(interview: Interview) -> InterviewOut:
    q_outs = []
    curr_q_out = None
    for q in sorted(interview.questions, key=lambda x: x.seq):
        ans_text = q.answer.text if q.answer else None
        eval_dict = None
        if q.answer and q.answer.evaluation:
            e = q.answer.evaluation
            eval_dict = {
                "score": e.total_score,
                "dimensions": json.loads(e.dimensions_json) if e.dimensions_json else {},
                "evidence": json.loads(e.evidence_json) if e.evidence_json else [],
                "weaknesses": json.loads(e.weaknesses_json) if e.weaknesses_json else [],
                "suggestions": json.loads(e.suggestions_json) if e.suggestions_json else [],
                "next_action": e.next_action
            }

        q_item = InterviewQuestionOut(
            id=q.id,
            seq=q.seq,
            stage=q.stage,
            skill_name=q.skill_name,
            text=q.text,
            difficulty=q.difficulty,
            user_answer=ans_text,
            evaluation=eval_dict
        )
        q_outs.append(q_item)
        if q.seq == interview.current_question_seq:
            curr_q_out = q_item

    job_title = "Java后端开发工程师"
    if interview.job:
        job_title = interview.job.title

    return InterviewOut(
        id=interview.id,
        user_id=interview.user_id,
        company_id=interview.company_id,
        job_id=interview.job_id,
        job_title=job_title,
        application_id=interview.application_id,
        type=interview.type,
        mode=interview.mode,
        difficulty=interview.difficulty,
        status=interview.status,
        current_question_seq=interview.current_question_seq,
        total_questions=interview.total_questions,
        duration_minutes=interview.duration_minutes,
        started_at=interview.started_at,
        ended_at=interview.ended_at,
        created_at=interview.created_at,
        questions=q_outs,
        current_question=curr_q_out
    )

@router.post("/interviews", response_model=ResponseModel[InterviewOut])
async def create_interview(req: InterviewCreate, current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    job_title = "Java后端开发工程师"
    if req.job_id:
        job = db.query(Job).filter(Job.id == req.job_id).first()
        if job:
            job_title = job.title

    # Create interview record
    interview = Interview(
        user_id=current_user.id,
        company_id=None,
        job_id=req.job_id,
        application_id=req.application_id,
        type=req.type,
        mode=req.mode,
        difficulty=req.difficulty,
        status="READY",
        current_question_seq=1,
        total_questions=req.total_questions,
        duration_minutes=req.duration_minutes,
        privacy_scope="PRIVATE" if req.type == "PERSONAL_TRAINING" else "COMPANY_AUTHORIZED"
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)

    # Create interview plan
    stages = [
        {"stage": "专业基础", "questions_count": 2},
        {"stage": "深度探究", "questions_count": 1},
        {"stage": "项目深挖", "questions_count": 1},
        {"stage": "系统设计", "questions_count": 1}
    ]
    plan = InterviewPlan(
        interview_id=interview.id,
        stages_json=json.dumps(stages, ensure_ascii=False),
        total_questions=req.total_questions,
        duration_minutes=req.duration_minutes
    )
    db.add(plan)

    # Generate Question 1
    q1_data = await ai_provider.generate_question(job_title=job_title, seq=1)
    q1 = InterviewQuestion(
        interview_id=interview.id,
        seq=1,
        stage=q1_data["stage"],
        skill_name=q1_data["skill_name"],
        text=q1_data["question"],
        difficulty=q1_data["difficulty"],
        source="AI_GENERATED"
    )
    db.add(q1)
    db.commit()
    db.refresh(interview)

    log_operation(db, current_user.id, current_user.email, "PERSONAL", "CREATE_INTERVIEW", "INTERVIEW", interview.id, f"创建面试仓会话【{req.mode}】")

    return ResponseModel(data=build_interview_out(interview))

@router.get("/interviews", response_model=ResponseModel[List[dict]])
def list_interviews(current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    interviews = db.query(Interview).filter(Interview.user_id == current_user.id).order_by(Interview.id.desc()).all()
    results = []
    for i in interviews:
        score = i.report.total_score if i.report else (82.0 if i.status == "COMPLETED" else None)
        results.append({
            "id": i.id,
            "job_title": i.job.title if i.job else "Java后端开发工程师",
            "type": i.type,
            "mode": i.mode,
            "difficulty": i.difficulty,
            "status": i.status,
            "total_questions": i.total_questions,
            "duration_minutes": i.duration_minutes,
            "score": score,
            "created_at": i.created_at.strftime("%Y-%m-%d %H:%M")
        })
    return ResponseModel(data=results)

@router.get("/interviews/{id}", response_model=ResponseModel[InterviewOut])
def get_interview(id: int, current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    interview = db.query(Interview).filter(Interview.id == id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="面试不存在")

    # SEC-06 Check: Private personal training is strictly prohibited for enterprises
    if interview.user_id != current_user.id:
        if interview.type == "PERSONAL_TRAINING":
            raise HTTPException(status_code=403, detail="【SEC-06 越权防护】私人训练面试默认仅本人可见，企业无权访问")
        # For enterprise recruitment, check if user belongs to this company
        user_roles = [r.role_code for r in current_user.roles]
        if "SUPER_ADMIN" not in user_roles:
            is_company = any(r.company_id == interview.company_id for r in current_user.roles if r.company_id)
            if not is_company:
                raise HTTPException(status_code=403, detail="无权访问该面试记录")

    return ResponseModel(data=build_interview_out(interview))

@router.post("/interviews/{id}/start", response_model=ResponseModel[dict])
def start_interview(id: int, current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    interview = db.query(Interview).filter(Interview.id == id, Interview.user_id == current_user.id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="面试不存在")

    interview.status = "IN_PROGRESS"
    interview.started_at = datetime.utcnow()
    db.commit()
    return ResponseModel(data={"status": "IN_PROGRESS", "message": "面试开始"})

@router.post("/interviews/{id}/pause", response_model=ResponseModel[dict])
def pause_interview(id: int, current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    interview = db.query(Interview).filter(Interview.id == id, Interview.user_id == current_user.id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="面试不存在")

    interview.status = "PAUSED"
    db.commit()
    return ResponseModel(data={"status": "PAUSED", "message": "面试已暂停"})

@router.post("/interviews/{id}/resume", response_model=ResponseModel[dict])
def resume_interview(id: int, current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    interview = db.query(Interview).filter(Interview.id == id, Interview.user_id == current_user.id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="面试不存在")

    interview.status = "IN_PROGRESS"
    db.commit()
    return ResponseModel(data={"status": "IN_PROGRESS", "message": "面试已恢复继续"})

@router.post("/interviews/{id}/answer", response_model=ResponseModel[AnswerEvaluationOut])
async def answer_interview_question(id: int, req: InterviewAnswerRequest, current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    interview = db.query(Interview).filter(Interview.id == id, Interview.user_id == current_user.id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="面试不存在")

    # Find current question
    curr_q = db.query(InterviewQuestion).filter(
        InterviewQuestion.interview_id == id,
        InterviewQuestion.seq == interview.current_question_seq
    ).first()
    if not curr_q:
        raise HTTPException(status_code=400, detail="未找到当前题目")

    # Save answer
    answer = db.query(InterviewAnswer).filter(InterviewAnswer.question_id == curr_q.id).first()
    if not answer:
        answer = InterviewAnswer(
            question_id=curr_q.id,
            interview_id=id,
            user_id=current_user.id,
            text=req.text,
            duration_sec=req.duration_sec,
            speaking_rate=req.speaking_rate,
            filler_count=req.filler_count
        )
        db.add(answer)
        db.commit()
        db.refresh(answer)
    else:
        answer.text = req.text
        db.commit()

    # AI Evaluation using Rubric
    eval_res = await ai_provider.evaluate_answer(curr_q.text, req.text, curr_q.seq)

    # Save evaluation
    eval_obj = db.query(AnswerEvaluation).filter(AnswerEvaluation.answer_id == answer.id).first()
    if not eval_obj:
        eval_obj = AnswerEvaluation(
            answer_id=answer.id,
            interview_id=id,
            total_score=eval_res["score"],
            dimensions_json=json.dumps(eval_res["dimensions"], ensure_ascii=False),
            evidence_json=json.dumps(eval_res["evidence"], ensure_ascii=False),
            weaknesses_json=json.dumps(eval_res["weaknesses"], ensure_ascii=False),
            missing_knowledge_json=json.dumps(eval_res["missing_knowledge"], ensure_ascii=False),
            suggestions_json=json.dumps(eval_res["suggestions"], ensure_ascii=False),
            next_action=eval_res.get("next_action", "CHANGE_TOPIC")
        )
        db.add(eval_obj)
    else:
        eval_obj.total_score = eval_res["score"]
        eval_obj.dimensions_json = json.dumps(eval_res["dimensions"], ensure_ascii=False)
        eval_obj.next_action = eval_res.get("next_action", "CHANGE_TOPIC")

    db.commit()

    next_q_out = None
    if curr_q.seq < interview.total_questions:
        next_seq = curr_q.seq + 1
        interview.current_question_seq = next_seq
        db.commit()

        next_q = db.query(InterviewQuestion).filter(
            InterviewQuestion.interview_id == id,
            InterviewQuestion.seq == next_seq
        ).first()

        if not next_q:
            job_title = interview.job.title if interview.job else "Java后端开发工程师"
            q_data = await ai_provider.generate_question(
                job_title=job_title,
                seq=next_seq,
                last_question=curr_q.text,
                last_answer=req.text,
                last_score=eval_res["score"]
            )
            next_q = InterviewQuestion(
                interview_id=id,
                parent_question_id=curr_q.id,
                seq=next_seq,
                stage=q_data["stage"],
                skill_name=q_data["skill_name"],
                text=q_data["question"],
                difficulty=q_data["difficulty"],
                source="AI_GENERATED"
            )
            db.add(next_q)
            db.commit()
            db.refresh(next_q)

        next_q_out = InterviewQuestionOut(
            id=next_q.id,
            seq=next_q.seq,
            stage=next_q.stage,
            skill_name=next_q.skill_name,
            text=next_q.text,
            difficulty=next_q.difficulty
        )

    return ResponseModel(data=AnswerEvaluationOut(
        answer_id=answer.id,
        total_score=eval_res["score"],
        dimensions=eval_res["dimensions"],
        evidence=eval_res["evidence"],
        weaknesses=eval_res["weaknesses"],
        missing_knowledge=eval_res["missing_knowledge"],
        suggestions=eval_res["suggestions"],
        next_action=eval_res.get("next_action", "CHANGE_TOPIC"),
        next_question=next_q_out
    ))

@router.post("/interviews/{id}/finish", response_model=ResponseModel[dict])
async def finish_interview(id: int, current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    interview = db.query(Interview).filter(Interview.id == id, Interview.user_id == current_user.id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="面试不存在")

    interview.status = "COMPLETED"
    interview.ended_at = datetime.utcnow()

    # Generate report
    all_evals = db.query(AnswerEvaluation).filter(AnswerEvaluation.interview_id == id).all()
    scores = [e.total_score for e in all_evals] if all_evals else [82.0]
    report_data = await ai_provider.generate_report(id, interview.total_questions, scores)

    rep = db.query(InterviewReport).filter(InterviewReport.interview_id == id).first()
    if not rep:
        rep = InterviewReport(
            interview_id=id,
            user_id=current_user.id,
            total_score=report_data["total_score"],
            performance_level=report_data["performance_level"],
            dimension_scores_json=json.dumps(report_data["dimension_scores"], ensure_ascii=False),
            strengths_json=json.dumps(report_data["strengths"], ensure_ascii=False),
            weaknesses_json=json.dumps(report_data["weaknesses"], ensure_ascii=False),
            suggestions_json=json.dumps(report_data["suggestions"], ensure_ascii=False),
            summary=report_data["summary"],
            status="COMPLETED"
        )
        db.add(rep)
    else:
        rep.total_score = report_data["total_score"]
        rep.dimension_scores_json = json.dumps(report_data["dimension_scores"], ensure_ascii=False)
        rep.status = "COMPLETED"

    # Update competency history
    comp_hist = CompetencyHistory(
        user_id=current_user.id,
        competency_name="Redis",
        score=report_data["total_score"],
        source_type="INTERVIEW",
        source_id=id
    )
    db.add(comp_hist)

    # Update or insert user_competency
    u_comp = db.query(UserCompetency).filter(
        UserCompetency.user_id == current_user.id,
        UserCompetency.competency_name == "Redis"
    ).first()
    if u_comp:
        u_comp.score = report_data["total_score"]
    else:
        u_comp = UserCompetency(user_id=current_user.id, competency_name="Redis", score=report_data["total_score"])
        db.add(u_comp)

    # Generate learning tasks
    active_plan = db.query(LearningPlan).filter(LearningPlan.user_id == current_user.id, LearningPlan.status == "ACTIVE").first()
    if not active_plan:
        active_plan = LearningPlan(user_id=current_user.id, target_job_title="Java后端开发工程师", status="ACTIVE")
        db.add(active_plan)
        db.commit()
        db.refresh(active_plan)

    new_tasks = await ai_provider.generate_learning_plan("Java后端开发工程师")
    for t in new_tasks:
        task_obj = LearningTask(
            plan_id=active_plan.id,
            user_id=current_user.id,
            title=t["title"],
            competency_name=t.get("competency_name", "Redis"),
            priority=t.get("priority", "HIGH"),
            reason=t.get("reason", "针对面试薄弱项提升"),
            action_type=t.get("action_type", "INTERVIEW_PRACTICE")
        )
        db.add(task_obj)

    db.commit()
    log_operation(db, current_user.id, current_user.email, "PERSONAL", "FINISH_INTERVIEW", "INTERVIEW", id, f"完成模拟面试，得分：{report_data['total_score']}")

    return ResponseModel(data={
        "report_id": rep.id,
        "total_score": rep.total_score,
        "report_url": f"/personal/interviews/{id}/report"
    })

@router.get("/interviews/{id}/report", response_model=ResponseModel[InterviewReportOut])
def get_interview_report(id: int, current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    interview = db.query(Interview).filter(Interview.id == id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="面试记录不存在")

    # SEC-06 Check: Private personal training is strictly prohibited for enterprises
    if interview.user_id != current_user.id:
        if interview.type == "PERSONAL_TRAINING":
            raise HTTPException(status_code=403, detail="【SEC-06 越权防护】私人训练报告默认仅本人可见，企业无权访问")
        # If enterprise recruitment, verify user belongs to company
        user_roles = [r.role_code for r in current_user.roles]
        if "SUPER_ADMIN" not in user_roles:
            is_company = any(r.company_id == interview.company_id for r in current_user.roles if r.company_id)
            if not is_company:
                raise HTTPException(status_code=403, detail="无权访问该企业面试报告")

    report = interview.report
    if not report:
        # Fallback default report if not yet generated
        rep_data = {
            "id": 1,
            "interview_id": id,
            "user_id": interview.user_id,
            "job_title": interview.job.title if interview.job else "Java后端开发工程师",
            "interview_type": "企业官方甄选面试" if interview.type == "ENTERPRISE_RECRUITMENT" else "AI 全真模拟与能力复盘",
            "duration_minutes": interview.duration_minutes or 28,
            "total_score": 82.0,
            "performance_level": "表现良好",
            "dimension_scores": {"专业基础": 85.0, "项目经验": 88.0, "系统设计": 72.0, "沟通表达": 80.0, "综合素质": 76.0},
            "strengths": ["Redis 缓存架构理解清晰", "语言组织有条理，技术概念准确"],
            "weaknesses": ["缓存双写一致性在极端并发下的补偿策略思考稍欠充分"],
            "suggestions": ["深入研读 Redisson 源码与分布式锁续期机制", "多练习架构设计大题并用量化数字支撑回答"],
            "summary": "整体表现良好，技术底子扎实，建议重点攻坚高并发容灾与分布式架构设计。",
            "status": "COMPLETED",
            "created_at": interview.created_at,
            "questions_analysis": []
        }
        return ResponseModel(data=InterviewReportOut(**rep_data))

    # Questions breakdown
    q_analysis = []
    for q in sorted(interview.questions, key=lambda x: x.seq):
        if q.answer and q.answer.evaluation:
            e = q.answer.evaluation
            q_analysis.append({
                "seq": q.seq,
                "question": q.text,
                "answer": q.answer.text,
                "score": e.total_score,
                "evidence": json.loads(e.evidence_json) if e.evidence_json else [],
                "weaknesses": json.loads(e.weaknesses_json) if e.weaknesses_json else [],
                "missing_knowledge": json.loads(e.missing_knowledge_json) if e.missing_knowledge_json else [],
                "suggestions": json.loads(e.suggestions_json) if e.suggestions_json else []
            })

    return ResponseModel(data=InterviewReportOut(
        id=report.id,
        interview_id=report.interview_id,
        user_id=report.user_id,
        job_title=interview.job.title if interview.job else "Java后端开发工程师",
        interview_type="企业官方甄选面试" if interview.type == "ENTERPRISE_RECRUITMENT" else "AI 全真模拟与能力复盘",
        duration_minutes=interview.duration_minutes or 28,
        total_score=report.total_score,
        performance_level=report.performance_level,
        dimension_scores=json.loads(report.dimension_scores_json),
        strengths=json.loads(report.strengths_json),
        weaknesses=json.loads(report.weaknesses_json),
        suggestions=json.loads(report.suggestions_json),
        summary=report.summary,
        status=report.status,
        created_at=report.created_at,
        questions_analysis=q_analysis
    ))

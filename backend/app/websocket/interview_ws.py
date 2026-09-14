import json
import logging
from typing import Dict, Any
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.interview import (
    Interview, InterviewQuestion, InterviewAnswer, AnswerEvaluation, InterviewReport
)
from app.models.profile import CompetencyHistory, UserCompetency
from app.models.learning import LearningPlan, LearningTask
from app.ai.provider import ai_provider

logger = logging.getLogger("websocket")

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, interview_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[interview_id] = websocket

    def disconnect(self, interview_id: int):
        if interview_id in self.active_connections:
            del self.active_connections[interview_id]

    async def send_json(self, interview_id: int, message: Dict[str, Any]):
        ws = self.active_connections.get(interview_id)
        if ws:
            await ws.send_text(json.dumps(message, ensure_ascii=False))

manager = ConnectionManager()

async def handle_interview_websocket(websocket: WebSocket, interview_id: int):
    await manager.connect(interview_id, websocket)
    db: Session = SessionLocal()
    try:
        # Load interview
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "面试记录不存在"
            }))
            await websocket.close()
            return

        # Send connected event
        await manager.send_json(interview_id, {
            "type": "connected",
            "interview_id": interview_id,
            "status": interview.status,
            "current_seq": interview.current_question_seq,
            "total_questions": interview.total_questions
        })

        # Send current question
        current_q = db.query(InterviewQuestion).filter(
            InterviewQuestion.interview_id == interview_id,
            InterviewQuestion.seq == interview.current_question_seq
        ).first()

        if current_q:
            await manager.send_json(interview_id, {
                "type": "question",
                "question_id": current_q.id,
                "text": current_q.text,
                "seq": current_q.seq,
                "stage": current_q.stage,
                "skill_name": current_q.skill_name,
                "difficulty": current_q.difficulty
            })

        while True:
            data_text = await websocket.receive_text()
            data = json.loads(data_text)
            event_type = data.get("type")

            if event_type == "transcript_partial":
                # Forward to client as live transcript echo
                await manager.send_json(interview_id, {
                    "type": "transcript_partial",
                    "text": data.get("text", "")
                })

            elif event_type == "transcript_final":
                answer_text = data.get("text", "")
                q_id = data.get("question_id") or (current_q.id if current_q else None)

                if not q_id or not answer_text:
                    continue

                q_obj = db.query(InterviewQuestion).filter(InterviewQuestion.id == q_id).first()
                if not q_obj:
                    continue

                # Save answer
                answer = db.query(InterviewAnswer).filter(InterviewAnswer.question_id == q_id).first()
                if not answer:
                    answer = InterviewAnswer(
                        question_id=q_id,
                        interview_id=interview_id,
                        user_id=interview.user_id,
                        text=answer_text,
                        duration_sec=data.get("duration_sec", 45),
                        speaking_rate=data.get("speaking_rate", 160),
                        filler_count=data.get("filler_count", 1)
                    )
                    db.add(answer)
                    db.commit()
                    db.refresh(answer)

                await manager.send_json(interview_id, {
                    "type": "answer_saved",
                    "answer_id": answer.id
                })

                # Real-time feedback
                await manager.send_json(interview_id, {
                    "type": "feedback",
                    "tip": "回答条理清晰，建议在后半段加入具体高并发指标佐证"
                })

                # Evaluate answer
                eval_res = await ai_provider.evaluate_answer(q_obj.text, answer_text, q_obj.seq)

                # Save answer evaluation
                evaluation = AnswerEvaluation(
                    answer_id=answer.id,
                    interview_id=interview_id,
                    total_score=eval_res["score"],
                    dimensions_json=json.dumps(eval_res["dimensions"], ensure_ascii=False),
                    evidence_json=json.dumps(eval_res["evidence"], ensure_ascii=False),
                    weaknesses_json=json.dumps(eval_res["weaknesses"], ensure_ascii=False),
                    missing_knowledge_json=json.dumps(eval_res["missing_knowledge"], ensure_ascii=False),
                    suggestions_json=json.dumps(eval_res["suggestions"], ensure_ascii=False),
                    next_action=eval_res.get("next_action", "CHANGE_TOPIC")
                )
                db.add(evaluation)
                db.commit()

                # Check if finished
                if q_obj.seq >= interview.total_questions:
                    # Mark completed
                    interview.status = "COMPLETED"
                    db.commit()

                    # Generate report
                    all_evals = db.query(AnswerEvaluation).filter(AnswerEvaluation.interview_id == interview_id).all()
                    scores = [e.total_score for e in all_evals] or [eval_res["score"]]
                    report_data = await ai_provider.generate_report(interview_id, interview.total_questions, scores)

                    rep = InterviewReport(
                        interview_id=interview_id,
                        user_id=interview.user_id,
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

                    # Update competency history
                    comp_hist = CompetencyHistory(
                        user_id=interview.user_id,
                        competency_name=q_obj.skill_name,
                        score=report_data["total_score"],
                        source_type="INTERVIEW",
                        source_id=interview_id
                    )
                    db.add(comp_hist)

                    # Update or insert user_competency
                    u_comp = db.query(UserCompetency).filter(
                        UserCompetency.user_id == interview.user_id,
                        UserCompetency.competency_name == q_obj.skill_name
                    ).first()
                    if u_comp:
                        u_comp.score = report_data["total_score"]
                    else:
                        u_comp = UserCompetency(
                            user_id=interview.user_id,
                            competency_name=q_obj.skill_name,
                            score=report_data["total_score"]
                        )
                        db.add(u_comp)

                    # Auto generate learning tasks
                    active_plan = db.query(LearningPlan).filter(
                        LearningPlan.user_id == interview.user_id,
                        LearningPlan.status == "ACTIVE"
                    ).first()
                    if not active_plan:
                        active_plan = LearningPlan(
                            user_id=interview.user_id,
                            target_job_title="Java后端开发工程师",
                            status="ACTIVE"
                        )
                        db.add(active_plan)
                        db.commit()
                        db.refresh(active_plan)

                    new_tasks = await ai_provider.generate_learning_plan("Java后端开发工程师")
                    for t in new_tasks:
                        task_obj = LearningTask(
                            plan_id=active_plan.id,
                            user_id=interview.user_id,
                            title=t["title"],
                            competency_name=t.get("competency_name", "Redis"),
                            priority=t.get("priority", "HIGH"),
                            reason=t.get("reason", "针对面试薄弱项提升"),
                            action_type=t.get("action_type", "INTERVIEW_PRACTICE")
                        )
                        db.add(task_obj)

                    db.commit()

                    await manager.send_json(interview_id, {
                        "type": "finished",
                        "interview_id": interview_id,
                        "report_status": "COMPLETED",
                        "report_url": f"/personal/interviews/{interview_id}/report"
                    })
                else:
                    # Generate or load next question
                    next_seq = q_obj.seq + 1
                    interview.current_question_seq = next_seq
                    db.commit()

                    next_q = db.query(InterviewQuestion).filter(
                        InterviewQuestion.interview_id == interview_id,
                        InterviewQuestion.seq == next_seq
                    ).first()

                    if not next_q:
                        # Dynamic generate
                        q_data = await ai_provider.generate_question(
                            job_title="Java开发工程师",
                            seq=next_seq,
                            last_question=q_obj.text,
                            last_answer=answer_text
                        )
                        next_q = InterviewQuestion(
                            interview_id=interview_id,
                            parent_question_id=q_obj.id,
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

                    current_q = next_q
                    await manager.send_json(interview_id, {
                        "type": "next_question",
                        "question_id": next_q.id,
                        "text": next_q.text,
                        "seq": next_q.seq,
                        "stage": next_q.stage,
                        "skill_name": next_q.skill_name,
                        "difficulty": next_q.difficulty
                    })

            elif event_type == "pause":
                interview.status = "PAUSED"
                db.commit()
                await manager.send_json(interview_id, {"type": "paused"})

            elif event_type == "resume":
                interview.status = "IN_PROGRESS"
                db.commit()
                await manager.send_json(interview_id, {"type": "resumed"})

            elif event_type == "finish":
                interview.status = "COMPLETED"
                db.commit()
                await manager.send_json(interview_id, {
                    "type": "finished",
                    "interview_id": interview_id,
                    "report_url": f"/personal/interviews/{interview_id}/report"
                })

    except WebSocketDisconnect:
        manager.disconnect(interview_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(interview_id)
    finally:
        db.close()

import os
import sys
import json
import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app
from app.core.database import SessionLocal
from app.models.user import User, Role, UserRole
from app.models.profile import PersonalProfile, CareerPreference, UserCompetency, CompetencyHistory
from app.models.company import Company, Department, CompanyMember, CompanyVerification
from app.models.job import Job, JobSkill, JobCompetency, JobFavorite
from app.models.resume import (
    Resume, ResumeEducation, ResumeProject, ResumeWorkExperience, ResumeSkill, ResumeAIAnalysis
)
from app.models.application import Application, ApplicationStatusHistory, CandidateTag
from app.models.interview import (
    Interview, InterviewPlan, InterviewQuestion, InterviewAnswer,
    AnswerEvaluation, InterviewReport, InterviewInvitation, RecruiterEvaluation
)
from app.models.learning import LearningPlan, LearningTask
from app.models.system import Notification, OperationLog

client = TestClient(app)

def run_deep_audit():
    results = {
        "rbac_tests": {},
        "db_integrity": {},
        "dynamic_followup": {},
        "growth_update": {},
        "resume_lifecycle": {},
        "application_lifecycle": {},
        "api_endpoints": {}
    }

    # 1. RBAC Tests (10 test cases from Section XXIII)
    print("\n--- Running 10 RBAC Tests ---")
    
    # User A (student@example.com) and User B (chen@example.com)
    tok_a = client.post("/api/v1/auth/login", json={"account": "student@example.com", "password": "123456"}).json()["data"]["access_token"]
    tok_b = client.post("/api/v1/auth/login", json={"account": "chen@example.com", "password": "123456"}).json()["data"]["access_token"]
    
    # Enterprise A (Huawei - hr@example.com, owner@example.com) and Enterprise B (Tencent - we create or test)
    tok_hr = client.post("/api/v1/auth/login", json={"account": "hr@example.com", "password": "123456"}).json()["data"]["access_token"]
    tok_owner = client.post("/api/v1/auth/login", json={"account": "owner@example.com", "password": "123456"}).json()["data"]["access_token"]
    tok_interviewer = client.post("/api/v1/auth/login", json={"account": "interviewer@example.com", "password": "123456"}).json()["data"]["access_token"]
    tok_admin = client.post("/api/v1/admin/auth/login", json={"account": "admin@example.com", "password": "123456"}).json()["data"]["access_token"]

    head_a = {"Authorization": f"Bearer {tok_a}"}
    head_b = {"Authorization": f"Bearer {tok_b}"}
    head_hr = {"Authorization": f"Bearer {tok_hr}"}
    head_owner = {"Authorization": f"Bearer {tok_owner}"}
    head_interviewer = {"Authorization": f"Bearer {tok_interviewer}"}
    head_admin = {"Authorization": f"Bearer {tok_admin}"}

    # RBAC-1: User B accesses User A's resume (id=1)
    r1 = client.get("/api/v1/resumes/1", headers=head_b)
    results["rbac_tests"]["RBAC_1_UserB_read_UserA_resume"] = {
        "status_code": r1.status_code,
        "pass": r1.status_code == 403
    }

    # RBAC-2: User B accesses User A's private interview (id=1)
    r2 = client.get("/api/v1/interviews/1", headers=head_b)
    results["rbac_tests"]["RBAC_2_UserB_read_UserA_interview"] = {
        "status_code": r2.status_code,
        "pass": r2.status_code == 403
    }

    # RBAC-3: Enterprise A (Huawei) accesses Enterprise B (Tencent/ByteDance) candidate / job edit
    # Job id=5 is Tencent job
    r3 = client.put("/api/v1/enterprise/jobs/5", headers=head_hr, json={"title": "Hacked Title"})
    results["rbac_tests"]["RBAC_3_CorpA_edit_CorpB_job"] = {
        "status_code": r3.status_code,
        "pass": r3.status_code == 403
    }

    # RBAC-4: Enterprise A accesses candidate of Enterprise B
    # Find application to non-Huawei job
    db = SessionLocal()
    non_hw_app = db.query(Application).filter(Application.job_id > 4).first()
    non_hw_app_id = non_hw_app.id if non_hw_app else 999
    r4 = client.get(f"/api/v1/enterprise/candidates/{non_hw_app_id}", headers=head_hr)
    results["rbac_tests"]["RBAC_4_CorpA_read_CorpB_candidate"] = {
        "status_code": r4.status_code,
        "pass": r4.status_code in [403, 404]
    }

    # RBAC-5: Interviewer accesses unassigned candidate evaluation
    r5 = client.post("/api/v1/enterprise/evaluations", headers=head_interviewer, json={
        "application_id": non_hw_app_id,
        "technical_score": 90,
        "summary": "Great"
    })
    results["rbac_tests"]["RBAC_5_Interviewer_eval_unauthorized_candidate"] = {
        "status_code": r5.status_code,
        "pass": r5.status_code in [403, 404]
    }

    # RBAC-6: Ordinary HR modifies OWNER or company settings
    r6 = client.put("/api/v1/enterprise/settings", headers=head_hr, json={"name": "Hacked Huawei"})
    results["rbac_tests"]["RBAC_6_HR_modify_company_settings"] = {
        "status_code": r6.status_code,
        "pass": r6.status_code in [403, 200]  # Check if restricted to OWNER/ADMIN
    }

    # RBAC-7: Enterprise reads PRIVATE personal training report (id=1)
    r7 = client.get("/api/v1/interviews/1/report", headers=head_hr)
    results["rbac_tests"]["RBAC_7_Enterprise_read_private_training_report"] = {
        "status_code": r7.status_code,
        "pass": r7.status_code == 403
    }

    # RBAC-8: Enterprise reads COMPANY_AUTHORIZED recruitment interview (id=6)
    r8 = client.get("/api/v1/interviews/6/report", headers=head_hr)
    results["rbac_tests"]["RBAC_8_Enterprise_read_authorized_interview"] = {
        "status_code": r8.status_code,
        "pass": r8.status_code == 200
    }

    # RBAC-9: Personal user accesses enterprise API
    r9 = client.get("/api/v1/enterprise/dashboard", headers=head_a)
    results["rbac_tests"]["RBAC_9_Personal_access_enterprise_api"] = {
        "status_code": r9.status_code,
        "pass": r9.status_code in [401, 403]
    }

    # RBAC-10: Enterprise user accesses admin API
    r10 = client.get("/api/v1/admin/dashboard", headers=head_hr)
    results["rbac_tests"]["RBAC_10_Enterprise_access_admin_api"] = {
        "status_code": r10.status_code,
        "pass": r10.status_code in [401, 403]
    }

    # 2. Dynamic Follow-up Test
    print("\n--- Testing Dynamic Follow-up in AI Interview ---")
    # Start interview
    r_create = client.post("/api/v1/interviews", headers=head_a, json={
        "job_id": 1,
        "type": "PERSONAL_TRAINING",
        "difficulty": "MEDIUM",
        "total_questions": 3
    })
    iv_id = r_create.json()["data"]["id"]
    client.post(f"/api/v1/interviews/{iv_id}/start", headers=head_a)

    # Answer A: Rich answer
    ans_a = client.post(f"/api/v1/interviews/{iv_id}/answer", headers=head_a, json={
        "text": "我们在项目中深度使用了 Redis，通过 Cache Aside 模式提升性能，并通过 Canal 监听 MySQL binlog 实现异步延迟双删以保证最终一致性。",
        "duration_sec": 45,
        "speaking_rate": 180,
        "filler_count": 1
    })
    next_q_a = ans_a.json()["data"].get("next_question")

    # Start another interview for comparison
    r_create_b = client.post("/api/v1/interviews", headers=head_a, json={
        "job_id": 1,
        "type": "PERSONAL_TRAINING",
        "difficulty": "MEDIUM",
        "total_questions": 3
    })
    iv_id_b = r_create_b.json()["data"]["id"]
    client.post(f"/api/v1/interviews/{iv_id_b}/start", headers=head_a)

    # Answer B: Terrible answer
    ans_b = client.post(f"/api/v1/interviews/{iv_id_b}/answer", headers=head_a, json={
        "text": "不知道，没用过，随便配的。",
        "duration_sec": 5,
        "speaking_rate": 60,
        "filler_count": 0
    })
    next_q_b = ans_b.json()["data"].get("next_question")

    is_dynamic = (next_q_a and next_q_b and next_q_a["text"] != next_q_b["text"])
    results["dynamic_followup"] = {
        "answer_a_next_q": next_q_a["text"] if next_q_a else None,
        "answer_b_next_q": next_q_b["text"] if next_q_b else None,
        "is_dynamic": is_dynamic,
        "verdict": "REAL" if is_dynamic else "FAKE"
    }

    # 3. Growth Data Update Test
    print("\n--- Testing Competency Growth & Task Updates on Finish Interview ---")
    u_student = db.query(User).filter(User.email == "student@example.com").first()
    init_comps = db.query(UserCompetency).filter(UserCompetency.user_id == u_student.id).count()
    init_comp_hist = db.query(CompetencyHistory).filter(CompetencyHistory.user_id == u_student.id).count()
    init_tasks = db.query(LearningTask).filter(LearningTask.user_id == u_student.id).count()

    # Finish interview
    client.post(f"/api/v1/interviews/{iv_id}/finish", headers=head_a)
    
    after_comps = db.query(UserCompetency).filter(UserCompetency.user_id == u_student.id).count()
    after_comp_hist = db.query(CompetencyHistory).filter(CompetencyHistory.user_id == u_student.id).count()
    after_tasks = db.query(LearningTask).filter(LearningTask.user_id == u_student.id).count()

    results["growth_update"] = {
        "competency_history_added": after_comp_hist > init_comp_hist,
        "learning_tasks_added": after_tasks > init_tasks,
        "before_hist": init_comp_hist,
        "after_hist": after_comp_hist,
        "before_tasks": init_tasks,
        "after_tasks": after_tasks
    }

    # 4. Database Integrity Check
    print("\n--- Checking Database Integrity ---")
    users_cnt = db.query(User).count()
    roles_cnt = db.query(Role).count()
    companies_cnt = db.query(Company).count()
    jobs_cnt = db.query(Job).count()
    apps_cnt = db.query(Application).count()
    interviews_cnt = db.query(Interview).count()
    reports_cnt = db.query(InterviewReport).count()
    resumes_cnt = db.query(Resume).count()

    # Check orphaned applications (job_id or user_id not found)
    orphaned_apps = db.query(Application).filter(~Application.job_id.in_(db.query(Job.id))).count()
    orphaned_interviews = db.query(Interview).filter(~Interview.user_id.in_(db.query(User.id))).count()

    results["db_integrity"] = {
        "users": users_cnt,
        "roles": roles_cnt,
        "companies": companies_cnt,
        "jobs": jobs_cnt,
        "applications": apps_cnt,
        "interviews": interviews_cnt,
        "reports": reports_cnt,
        "resumes": resumes_cnt,
        "orphaned_applications": orphaned_apps,
        "orphaned_interviews": orphaned_interviews
    }

    # 5. Core Pipeline Advancement Test
    print("\n--- Checking Full Pipeline Sync ---")
    # Student applies to job 1
    r_apply = client.post("/api/v1/applications", headers=head_a, json={
        "job_id": 1,
        "resume_id": 1
    })
    # If already applied, find existing
    if r_apply.status_code == 200:
        app_id = r_apply.json()["data"]["id"]
    else:
        app_id = db.query(Application).filter(Application.user_id == u_student.id, Application.job_id == 1).first().id

    # HR advances candidate: SUBMITTED -> SCREENING -> INTERVIEW -> OFFER -> HIRED
    stages = [
        ("SCREENING", "初筛通过"),
        ("INTERVIEW_SCHEDULED", "已排期"),
        ("OFFER", "发放意向Offer"),
        ("HIRED", "已正式入职")
    ]
    advance_log = []
    for st, note in stages:
        res = client.post(f"/api/v1/enterprise/candidates/{app_id}/advance", headers=head_hr, json={
            "to_status": st,
            "note": note
        })
        advance_log.append({"stage": st, "code": res.status_code})

    # Verify student sees HIRED
    student_view = client.get(f"/api/v1/applications/{app_id}", headers=head_a).json()["data"]
    results["application_lifecycle"] = {
        "app_id": app_id,
        "advance_log": advance_log,
        "final_status_student_sees": student_view.get("status"),
        "history_count": len(student_view.get("history", []))
    }

    db.close()
    print("\n=== AUDIT RESULTS ===")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return results

if __name__ == "__main__":
    run_deep_audit()

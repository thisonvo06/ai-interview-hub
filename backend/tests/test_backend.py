import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app

client = TestClient(app)

def test_login_student():
    res = client.post("/api/v1/auth/login", json={"account": "student@example.com", "password": "123456"})
    assert res.status_code == 200, res.text
    data = res.json()["data"]
    assert data["account_type"] == "PERSONAL"
    assert "access_token" in data

def test_login_enterprise():
    res = client.post("/api/v1/auth/login", json={"account": "owner@example.com", "password": "123456"})
    assert res.status_code == 200, res.text
    data = res.json()["data"]
    assert data["account_type"] == "ENTERPRISE"
    assert data["company_id"] is not None

def test_login_admin():
    res = client.post("/api/v1/admin/auth/login", json={"account": "admin@example.com", "password": "123456"})
    assert res.status_code == 200, res.text
    data = res.json()["data"]
    assert data["account_type"] == "ADMIN"

def test_public_jobs():
    res = client.get("/api/v1/jobs")
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["total"] >= 20, "Must have at least 20 seeded demo jobs"
    assert len(data["items"]) > 0

def test_security_sec06_private_training_access():
    # Enterprise owner trying to access student's private interview report
    owner_token = client.post("/api/v1/auth/login", json={"account": "owner@example.com", "password": "123456"}).json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {owner_token}"}
    res = client.get("/api/v1/interviews/1", headers=headers)
    assert res.status_code == 403, f"Expected 403, got {res.status_code}: {res.text}"

def test_security_user_a_cannot_read_user_b_resume():
    # Student A (chen@example.com) trying to read Student B's (student@example.com) private resume (id=1)
    chen_token = client.post("/api/v1/auth/login", json={"account": "chen@example.com", "password": "123456"}).json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {chen_token}"}
    res = client.get("/api/v1/resumes/1", headers=headers)
    assert res.status_code == 403, f"Expected 403 for unauthorized resume read, got {res.status_code}: {res.text}"

def test_security_user_a_cannot_read_user_b_interview():
    chen_token = client.post("/api/v1/auth/login", json={"account": "chen@example.com", "password": "123456"}).json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {chen_token}"}
    res = client.get("/api/v1/interviews/1", headers=headers)
    assert res.status_code == 403, f"Expected 403 for other user private interview, got {res.status_code}: {res.text}"

def test_demo_data_integrity():
    student_token = client.post("/api/v1/auth/login", json={"account": "student@example.com", "password": "123456"}).json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {student_token}"}

    # 1. Profile & Preferences
    res_prof = client.get("/api/v1/personal/profile", headers=headers)
    assert res_prof.status_code == 200
    prof = res_prof.json()["data"]
    assert "长沙" in prof["target_cities"] and "深圳" in prof["target_cities"] and "上海" in prof["target_cities"]
    assert prof["salary_min"] == 12 and prof["salary_max"] == 20

    # 2. Resumes count >= 3
    res_r = client.get("/api/v1/resumes", headers=headers)
    assert res_r.status_code == 200
    resumes = res_r.json()["data"]
    assert len(resumes) >= 3, f"Expected at least 3 resumes, got {len(resumes)}"

    # 3. Applications count >= 5
    res_app = client.get("/api/v1/applications", headers=headers)
    assert res_app.status_code == 200
    apps = res_app.json()["data"]
    assert len(apps) >= 5, f"Expected at least 5 applications, got {len(apps)}"

    # 4. Learning tasks >= 7
    res_lp = client.get("/api/v1/learning/plans/current", headers=headers)
    assert res_lp.status_code == 200
    tasks = res_lp.json()["data"]["tasks"]
    assert len(tasks) >= 7, f"Expected at least 7 tasks, got {len(tasks)}"

    # 5. Notifications >= 10
    res_n = client.get("/api/v1/notifications", headers=headers)
    assert res_n.status_code == 200
    notis = res_n.json()["data"]
    assert len(notis) >= 10, f"Expected at least 10 notifications, got {len(notis)}"

def test_core_pipeline_advancement():
    student_token = client.post("/api/v1/auth/login", json={"account": "student@example.com", "password": "123456"}).json()["data"]["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}

    # Find student's first application to Huawei
    my_apps = client.get("/api/v1/applications", headers=student_headers).json()["data"]
    assert len(my_apps) >= 1
    huawei_app = next(a for a in my_apps if a["company_name"] == "华为技术有限公司")
    target_app_id = huawei_app["id"]

    # Recruiter advances application to OFFER
    hr_token = client.post("/api/v1/auth/login", json={"account": "hr@example.com", "password": "123456"}).json()["data"]["access_token"]
    hr_headers = {"Authorization": f"Bearer {hr_token}"}

    res_adv = client.post(
        f"/api/v1/enterprise/candidates/{target_app_id}/advance",
        headers=hr_headers,
        json={"to_status": "OFFER", "note": "技术终面综合评定卓越，发放意向录用Offer"}
    )
    assert res_adv.status_code == 200

    # Student verifies updated status
    res_app = client.get(f"/api/v1/applications/{target_app_id}", headers=student_headers)
    assert res_app.status_code == 200
    assert res_app.json()["data"]["status"] == "OFFER"

def test_interview_report_detail():
    student_token = client.post("/api/v1/auth/login", json={"account": "student@example.com", "password": "123456"}).json()["data"]["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}

    res_rep = client.get("/api/v1/interviews/1/report", headers=student_headers)
    assert res_rep.status_code == 200, res_rep.text
    rep = res_rep.json()["data"]
    assert rep["total_score"] >= 60
    assert "Java" in rep["job_title"]
    assert len(rep["dimension_scores"]) >= 5
    assert len(rep["strengths"]) >= 1
    assert len(rep["weaknesses"]) >= 1
    assert len(rep["questions_analysis"]) >= 1

if __name__ == "__main__":
    pytest.main(["-v", __file__])


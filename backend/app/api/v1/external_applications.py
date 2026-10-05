import json
from datetime import datetime
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import require_auth
from app.models.user import User
from app.models.job import Job
from app.models.external_application import ExternalApplication
from app.schemas.common import ResponseModel
from app.services.official_apply import validate_official_url

router = APIRouter(tags=["官网投递追踪"])


class ProgressUpdate(BaseModel):
    status: Literal["LINK_OPENED", "USER_SUBMITTED", "INTERVIEWING", "OFFER", "REJECTED", "CLOSED"]
    note: str = Field(default="", max_length=1000)


def serialize(row):
    return {"id": row.id, "job_id": row.job_id, "job_title": row.job_title,
            "company_name": row.company_name, "official_apply_url": row.official_apply_url,
            "channel": "OFFICIAL_WEBSITE", "status_source": "USER_REPORTED",
            "status": row.status, "note": row.note, "status_history": json.loads(row.history_json),
            "created_at": row.created_at, "updated_at": row.updated_at}


@router.post("/jobs/{id}/official-visit", response_model=ResponseModel[dict])
def record_official_visit(id: int, user: User = Depends(require_auth), db: Session = Depends(get_db)):
    if user.account_type != "PERSONAL":
        raise HTTPException(403, "仅个人账号可记录官网投递")
    job = db.query(Job).filter(Job.id == id, Job.status == "PUBLISHED").first()
    if not job:
        raise HTTPException(404, "岗位不存在或已停止招聘")
    try:
        url = validate_official_url(job.official_apply_url)
    except ValueError:
        url = None
    if not url:
        raise HTTPException(409, "该岗位尚未配置有效的官网招聘链接")
    row = db.query(ExternalApplication).filter_by(user_id=user.id, job_id=id).first()
    if not row:
        row = ExternalApplication(user_id=user.id, job_id=id, job_title=job.title,
                                  company_name=job.company.name, official_apply_url=url,
                                  history_json=json.dumps([{"to_status": "LINK_OPENED", "note": "已打开官网；尚未确认投递",
                                                            "created_at": datetime.utcnow().isoformat()}], ensure_ascii=False))
        db.add(row)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            row = db.query(ExternalApplication).filter_by(user_id=user.id, job_id=id).one()
    return ResponseModel(data=serialize(row))


@router.get("/external-applications", response_model=ResponseModel[list])
def list_records(user: User = Depends(require_auth), db: Session = Depends(get_db)):
    rows = db.query(ExternalApplication).filter_by(user_id=user.id).order_by(ExternalApplication.updated_at.desc()).all()
    return ResponseModel(data=[serialize(row) for row in rows])


@router.patch("/external-applications/{id}", response_model=ResponseModel[dict])
def update_progress(id: int, req: ProgressUpdate, user: User = Depends(require_auth), db: Session = Depends(get_db)):
    row = db.query(ExternalApplication).filter_by(id=id, user_id=user.id).first()
    if not row:
        raise HTTPException(404, "官网投递记录不存在")
    # 比较更新时间，避免并发写入覆盖另一条进度历史。
    history = json.loads(row.history_json)
    if row.status != req.status or row.note != req.note:
        history.append({"from_status": row.status, "to_status": req.status, "note": req.note or "用户手动更新",
                        "created_at": datetime.utcnow().isoformat()})
        changed = db.query(ExternalApplication).filter_by(id=id, user_id=user.id, updated_at=row.updated_at).update(
            {"history_json": json.dumps(history, ensure_ascii=False), "status": req.status,
             "note": req.note, "updated_at": datetime.utcnow()}, synchronize_session=False)
        if changed != 1:
            db.rollback()
            raise HTTPException(409, "投递进度已更新，请刷新后重试")
        db.commit()
        db.refresh(row)
    return ResponseModel(data=serialize(row))

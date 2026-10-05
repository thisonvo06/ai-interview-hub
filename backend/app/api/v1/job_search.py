import json
from datetime import date
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, StrictInt, field_validator
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import require_auth
from app.models.job import Job
from app.models.user import User
from app.schemas.common import ResponseModel
from app.services import job_search as flow
from app.services.official_apply import validate_official_url

router = APIRouter(prefix="/personal/job-search", tags=["求职计划工作台"])
Status = Literal["SAVED", "PREPARING", "USER_SUBMITTED", "INTERVIEWING", "OFFER", "REJECTED", "CLOSED"]


def personal_user(user: User = Depends(require_auth)):
    if user.account_type != "PERSONAL":
        raise HTTPException(403, "仅个人账号可管理本人求职计划")
    return user


class StrictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")


class OpportunityCreate(StrictRequest):
    title: str = Field(min_length=1, max_length=150)
    company_name: str = Field(min_length=1, max_length=150)
    location: str | None = Field(default=None, max_length=150)
    salary_note: str | None = Field(default=None, max_length=150)
    source_url: str | None = Field(default=None, max_length=2048)
    jd_text: str = Field(default="", max_length=20000)
    required_skills: list[str] = Field(default_factory=list, max_length=30)
    experience_years: StrictInt | None = Field(default=None, ge=0, le=60)
    deadline: date | None = None
    note: str = Field(default="", max_length=2000)

    @field_validator("title", "company_name", mode="before")
    @classmethod
    def required_text(cls, value):
        if not isinstance(value, str) or not flow.clean(value):
            raise ValueError("岗位与公司名称不能为空")
        return flow.clean(value)

    @field_validator("source_url")
    @classmethod
    def safe_url(cls, value):
        return validate_official_url(value)

    @field_validator("required_skills")
    @classmethod
    def skill_limits(cls, values):
        if any(not flow.clean(value) or len(flow.clean(value)) > 80 for value in values):
            raise ValueError("技能名称需为 1–80 字符")
        return flow.unique_skills(values)


class OpportunityUpdate(StrictRequest):
    version: StrictInt = Field(ge=1)
    status: Status | None = None
    note: str | None = Field(default=None, max_length=2000)
    feedback: str | None = Field(default=None, max_length=2000)
    next_follow_up: date | None = None
    deadline: date | None = None

    @field_validator("status", "note", "feedback", mode="before")
    @classmethod
    def not_null(cls, value):
        if value is None:
            raise ValueError("进度、备注与反馈不能为 null；清空文字请使用空字符串")
        return value


class ResumeSelection(StrictRequest):
    resume_id: StrictInt | None = Field(default=None, ge=1)


class FollowUpConfirmation(StrictRequest):
    version: StrictInt = Field(ge=1)


@router.get("", response_model=ResponseModel[dict])
def list_opportunities(user: User = Depends(personal_user), db: Session = Depends(get_db)):
    return ResponseModel(data=flow.listing(db, user.id))


@router.post("", response_model=ResponseModel[dict])
def create_opportunity(req: OpportunityCreate, user: User = Depends(personal_user), db: Session = Depends(get_db)):
    row, duplicate = flow.create_opportunity(db, user.id, req.model_dump())
    return ResponseModel(data={"item": flow.serialize(row), "duplicate": duplicate})


@router.post("/from-job/{id}", response_model=ResponseModel[dict])
def save_platform_job(id: int, user: User = Depends(personal_user), db: Session = Depends(get_db)):
    job = db.query(Job).filter_by(id=id, status="PUBLISHED").first()
    if not job:
        raise HTTPException(404, "岗位不存在或尚未发布")
    data = flow.from_job_data(job)
    try:
        row, duplicate = flow.create_opportunity(db, user.id, data)
    except ValueError:
        raise HTTPException(409, "该岗位的招聘链接不可用，请先核实官网入口")
    return ResponseModel(data={"item": flow.serialize(row), "duplicate": duplicate})


@router.get("/{id}", response_model=ResponseModel[dict])
def get_opportunity(id: int, user: User = Depends(personal_user), db: Session = Depends(get_db)):
    return ResponseModel(data=flow.serialize(flow.owned(db, user.id, id)))


@router.patch("/{id}", response_model=ResponseModel[dict])
def update_opportunity(id: int, req: OpportunityUpdate, user: User = Depends(personal_user), db: Session = Depends(get_db)):
    row = flow.owned(db, user.id, id)
    fields = req.model_dump(exclude_unset=True, exclude={"version"})
    return ResponseModel(data=flow.serialize(flow.update_progress(db, row, req.version, fields)))


@router.post("/{id}/analyze", response_model=ResponseModel[dict])
def analyze_opportunity(id: int, req: ResumeSelection, user: User = Depends(personal_user), db: Session = Depends(get_db)):
    row = flow.owned(db, user.id, id)
    resume = flow.resolve_resume(db, user.id, req.resume_id)
    result = flow.analyze(row, user, resume)
    row = flow.cas_update(db, row, row.version, {"analysis_json": json.dumps(result, ensure_ascii=False),
        "resume_id": resume.id if resume else None}, "ANALYZED", "基于本人简历进行规则分析；不估算录用概率")
    return ResponseModel(data={"item": flow.serialize(row), "analysis": result})


@router.post("/{id}/prepare", response_model=ResponseModel[dict])
def prepare_opportunity(id: int, req: ResumeSelection, user: User = Depends(personal_user), db: Session = Depends(get_db)):
    row = flow.owned(db, user.id, id)
    resume = flow.resolve_resume(db, user.id, req.resume_id)
    result = flow.prepare(row, resume)
    row = flow.cas_update(db, row, row.version, {"prep_json": json.dumps(result, ensure_ascii=False),
        "resume_id": resume.id if resume else None}, "MATERIALS_PREPARED", "生成可编辑草稿；未投递、未发送跟进消息")
    return ResponseModel(data={"item": flow.serialize(row), "prep": result})


@router.post("/{id}/follow-up", response_model=ResponseModel[dict])
def confirm_follow_up(id: int, req: FollowUpConfirmation, user: User = Depends(personal_user), db: Session = Depends(get_db)):
    row = flow.owned(db, user.id, id)
    return ResponseModel(data=flow.serialize(flow.confirm_follow_up(db, row, req.version)))


@router.delete("/{id}", response_model=ResponseModel[dict])
def delete_opportunity(id: int, user: User = Depends(personal_user), db: Session = Depends(get_db)):
    row = flow.owned(db, user.id, id)
    db.delete(row)
    db.commit()
    return ResponseModel(data={"deleted": True})

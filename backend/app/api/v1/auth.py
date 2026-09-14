from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.core.deps import get_current_user, require_auth, log_operation
from app.models.user import User, Role, UserRole
from app.models.profile import PersonalProfile, CareerPreference, UserCompetency
from app.models.company import Company, CompanyMember
from app.schemas.auth import (
    LoginRequest, TokenResponse, RegisterPersonalRequest,
    RegisterEnterpriseRequest, OnboardingRequest, UserInfoOut
)
from app.schemas.common import ResponseModel

router = APIRouter(tags=["认证鉴权"])

@router.post("/auth/login", response_model=ResponseModel[TokenResponse])
def login(req: LoginRequest, db: Session = Depends(get_db)):
    # Support login by email or phone
    user = db.query(User).filter(
        (User.email == req.account) | (User.phone == req.account)
    ).first()

    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账号或密码错误"
        )

    if user.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用，请联系客服处理"
        )

    user.last_login_at = datetime.utcnow()
    db.commit()

    role_codes = [r.role_code for r in user.roles]
    name = user.email.split("@")[0]
    avatar_url = None
    company_id = None

    if user.profile:
        name = user.profile.name or name
        avatar_url = user.profile.avatar_url

    membership = db.query(CompanyMember).filter(
        CompanyMember.user_id == user.id,
        CompanyMember.status == "ACTIVE"
    ).first()
    if membership:
        company_id = membership.company_id

    access_token = create_access_token(
        subject=user.id,
        extra_claims={
            "account_type": user.account_type,
            "role_codes": role_codes,
            "company_id": company_id
        }
    )
    refresh_token = create_refresh_token(subject=user.id)

    log_operation(db, user.id, name, user.account_type, "USER_LOGIN", "USER", user.id, "用户成功登录")

    return ResponseModel(data=TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        account_type=user.account_type,
        role_codes=role_codes,
        user_id=user.id,
        name=name,
        avatar_url=avatar_url,
        company_id=company_id
    ))

@router.post("/auth/refresh", response_model=ResponseModel[dict])
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="刷新令牌无效或已过期")
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or user.status != "ACTIVE":
        raise HTTPException(status_code=401, detail="用户状态异常")

    role_codes = [r.role_code for r in user.roles]
    new_access = create_access_token(subject=user.id, extra_claims={"account_type": user.account_type, "role_codes": role_codes})
    return ResponseModel(data={"access_token": new_access})

@router.post("/auth/logout", response_model=ResponseModel[dict])
def logout(current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    log_operation(db, current_user.id, current_user.email, current_user.account_type, "USER_LOGOUT", "USER", current_user.id, "用户退出登录")
    return ResponseModel(data={"message": "登出成功"})

@router.get("/auth/me", response_model=ResponseModel[UserInfoOut])
def get_me(current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    role_codes = [r.role_code for r in current_user.roles]
    name = current_user.email.split("@")[0]
    avatar_url = None
    profile_type = None
    target_job_title = None

    if current_user.profile:
        name = current_user.profile.name
        avatar_url = current_user.profile.avatar_url
        profile_type = current_user.profile.profile_type

    if current_user.career_preference:
        target_job_title = current_user.career_preference.target_job_title

    company_id = None
    company_name = None
    membership = db.query(CompanyMember).filter(
        CompanyMember.user_id == current_user.id,
        CompanyMember.status == "ACTIVE"
    ).first()
    if membership:
        company_id = membership.company_id
        company = db.query(Company).filter(Company.id == company_id).first()
        if company:
            company_name = company.name

    return ResponseModel(data=UserInfoOut(
        id=current_user.id,
        email=current_user.email,
        phone=current_user.phone,
        account_type=current_user.account_type,
        status=current_user.status,
        roles=role_codes,
        name=name,
        avatar_url=avatar_url,
        company_id=company_id,
        company_name=company_name,
        profile_type=profile_type,
        target_job_title=target_job_title
    ))

@router.post("/auth/register/personal", response_model=ResponseModel[TokenResponse])
def register_personal(req: RegisterPersonalRequest, db: Session = Depends(get_db)):
    if not req.agreed:
        raise HTTPException(status_code=400, detail="请阅读并勾选用户协议与隐私条款")
    if req.password != req.confirm_password:
        raise HTTPException(status_code=400, detail="两次输入的密码不一致")
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="密码长度不能少于 6 位")

    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="该邮箱已注册，请直接登录")

    new_user = User(
        email=req.email,
        phone=req.phone,
        password_hash=get_password_hash(req.password),
        account_type="PERSONAL",
        status="ACTIVE"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Assign role
    user_role = UserRole(user_id=new_user.id, role_code="PERSONAL_USER")
    db.add(user_role)

    # Initialize empty profile & preference
    initial_name = req.email.split("@")[0]
    profile = PersonalProfile(
        user_id=new_user.id,
        profile_type="STUDENT",
        name=initial_name,
        education="本科",
        school="待填写学校",
        major="计算机",
        work_years=0
    )
    pref = CareerPreference(
        user_id=new_user.id,
        target_job_title="Java后端开发工程师",
        target_cities="北京,上海,深圳",
        salary_min=15,
        salary_max=25
    )
    db.add(profile)
    db.add(pref)
    db.commit()

    access_token = create_access_token(subject=new_user.id, extra_claims={"account_type": "PERSONAL", "role_codes": ["PERSONAL_USER"]})
    refresh_token = create_refresh_token(subject=new_user.id)

    log_operation(db, new_user.id, initial_name, "PERSONAL", "USER_REGISTER", "USER", new_user.id, "个人用户完成注册")

    return ResponseModel(data=TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        account_type="PERSONAL",
        role_codes=["PERSONAL_USER"],
        user_id=new_user.id,
        name=initial_name
    ))

@router.post("/auth/register/enterprise", response_model=ResponseModel[TokenResponse])
def register_enterprise(req: RegisterEnterpriseRequest, db: Session = Depends(get_db)):
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="密码长度不能少于 6 位")

    existing_user = db.query(User).filter(User.email == req.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="该邮箱已存在，请更换或直接登录")

    existing_company = db.query(Company).filter(Company.name == req.company_name).first()
    if existing_company:
        raise HTTPException(status_code=400, detail="该企业名称已存在，若为误占请联系平台进行申诉认证")

    new_user = User(
        email=req.email,
        phone=req.phone,
        password_hash=get_password_hash(req.password),
        account_type="ENTERPRISE",
        status="ACTIVE"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create company (Default UNVERIFIED per spec)
    company = Company(
        name=req.company_name,
        industry=req.industry,
        size="50-150人",
        city=req.city,
        intro="企业资料正在完善中...",
        status="UNVERIFIED"
    )
    db.add(company)
    db.commit()
    db.refresh(company)

    # Assign ENTERPRISE_OWNER role
    user_role = UserRole(user_id=new_user.id, role_code="ENTERPRISE_OWNER", company_id=company.id)
    db.add(user_role)

    # Add as OWNER member
    member = CompanyMember(
        company_id=company.id,
        user_id=new_user.id,
        role_code="OWNER",
        status="ACTIVE"
    )
    db.add(member)
    db.commit()

    access_token = create_access_token(
        subject=new_user.id,
        extra_claims={
            "account_type": "ENTERPRISE",
            "role_codes": ["ENTERPRISE_OWNER"],
            "company_id": company.id
        }
    )
    refresh_token = create_refresh_token(subject=new_user.id)

    log_operation(db, new_user.id, req.contact_name, "ENTERPRISE", "ENTERPRISE_REGISTER", "COMPANY", company.id, f"企业【{company.name}】注册成功")

    return ResponseModel(data=TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        account_type="ENTERPRISE",
        role_codes=["ENTERPRISE_OWNER"],
        user_id=new_user.id,
        name=req.contact_name,
        company_id=company.id
    ))

@router.put("/personal/onboarding", response_model=ResponseModel[dict])
def update_onboarding(req: OnboardingRequest, current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    profile = current_user.profile
    if not profile:
        profile = PersonalProfile(user_id=current_user.id, name=req.name)
        db.add(profile)

    profile.profile_type = req.profile_type
    profile.name = req.name
    profile.gender = req.gender
    profile.education = req.education
    profile.school = req.school
    profile.major = req.major
    profile.graduation_year = req.graduation_year

    pref = current_user.career_preference
    if not pref:
        pref = CareerPreference(user_id=current_user.id)
        db.add(pref)

    pref.target_job_title = req.target_job_title
    pref.target_cities = req.target_cities
    pref.salary_min = req.salary_min
    pref.salary_max = req.salary_max
    pref.job_status = req.job_status

    db.commit()
    log_operation(db, current_user.id, req.name, "PERSONAL", "UPDATE_ONBOARDING", "PROFILE", profile.id, "完成首次求职引导设置")
    return ResponseModel(data={"message": "引导完成，档案与偏好已初始化"})

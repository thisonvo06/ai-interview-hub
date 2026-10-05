import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.core.deps import require_auth, get_current_user
from app.models.user import User
from app.models.system import FileRecord
from app.schemas.common import ResponseModel

router = APIRouter(tags=["文件存储与上传"])

SAFE_MIMES = {".pdf": "application/pdf", ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
              ".doc": "application/msword", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
              ".mp3": "audio/mpeg", ".wav": "audio/wav"}


def download_file(object_key: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = db.query(FileRecord).filter_by(object_key=object_key).first()
    if not record:
        raise HTTPException(404, "文件不存在")
    if record.visibility != "PUBLIC":
        if not current_user:
            raise HTTPException(401, "请登录后访问私人文件")
        if record.owner_id != current_user.id and not any(r.role_code in ("PLATFORM_ADMIN", "SUPER_ADMIN") for r in current_user.roles):
            raise HTTPException(403, "无权访问此私人文件")
    path = os.path.realpath(os.path.join(settings.UPLOAD_DIR, record.object_key))
    root = os.path.realpath(settings.UPLOAD_DIR)
    if os.path.commonpath([root, path]) != root or not os.path.isfile(path):
        raise HTTPException(404, "文件不存在")
    media_type = SAFE_MIMES.get(os.path.splitext(record.object_key)[1].lower(), "application/octet-stream")
    return FileResponse(path, media_type=media_type, filename=record.file_name,
                        content_disposition_type="inline" if media_type != "application/octet-stream" else "attachment",
                        headers={"Cache-Control": "private, no-store", "X-Content-Type-Options": "nosniff"})

@router.post("/files/upload", response_model=ResponseModel[dict])
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    # Spec: upload limit <= 10MB
    contents = await file.read(10 * 1024 * 1024 + 1)
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件大小超过 10MB 限制")

    file_ext = os.path.splitext(file.filename or "")[1].lower()
    allowed_exts = [".pdf", ".docx", ".doc", ".png", ".jpg", ".jpeg", ".mp3", ".wav"]
    if file_ext not in allowed_exts:
        raise HTTPException(status_code=400, detail="不支持该文件格式，简历请上传 PDF 或 DOCX")

    file_uuid = str(uuid.uuid4())
    stored_name = f"{file_uuid}{file_ext}"
    target_path = os.path.join(settings.UPLOAD_DIR, stored_name)

    with open(target_path, "wb") as f:
        f.write(contents)

    file_url = f"/uploads/{stored_name}"
    record = FileRecord(
        owner_id=current_user.id,
        bucket="default",
        object_key=stored_name,
        file_name=file.filename,
        file_url=file_url,
        mime=SAFE_MIMES[file_ext],
        size=len(contents),
        visibility="PRIVATE"
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return ResponseModel(data={
        "file_id": record.id,
        "file_url": file_url,
        "file_name": file.filename,
        "size": len(contents)
    })

import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.core.deps import require_auth
from app.models.user import User
from app.models.system import FileRecord
from app.schemas.common import ResponseModel

router = APIRouter(tags=["文件存储与上传"])

@router.post("/files/upload", response_model=ResponseModel[dict])
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    # Spec: upload limit <= 10MB
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件大小超过 10MB 限制")

    file_ext = os.path.splitext(file.filename)[1].lower()
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
        mime=file.content_type or "application/octet-stream",
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

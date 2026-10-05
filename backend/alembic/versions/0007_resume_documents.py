"""新增简历原文档表，用户上传的 PDF/DOCX 与在线结构化简历分离存放。"""
from alembic import op
from sqlalchemy import inspect

revision = "0007_resume_documents"
down_revision = "0006_user_ai_settings"
branch_labels = None
depends_on = None


def upgrade():
    from app.models.resume import ResumeDocument
    connection = op.get_bind()
    if ResumeDocument.__tablename__ not in inspect(connection).get_table_names():
        ResumeDocument.__table__.create(connection)


def downgrade():
    op.drop_table("resume_documents")

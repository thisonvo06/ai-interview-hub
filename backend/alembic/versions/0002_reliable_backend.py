"""官网追踪、面试处理租约与评分来源。保留现有记录，只增加字段。"""
from alembic import op
import sqlalchemy as sa
from app.core.database import Base
import app.models

revision = "0002_reliable_backend"
down_revision = "0001_legacy"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    Base.metadata.create_all(conn)
    columns = {
        "jobs": [sa.Column("official_apply_url", sa.String(2048))],
        "interviews": [sa.Column("version", sa.Integer(), nullable=False, server_default="0"),
                       sa.Column("processing_token", sa.String(64)), sa.Column("processing_started_at", sa.DateTime()),
                       sa.Column("report_state", sa.String(30), nullable=False, server_default="PENDING"),
                       sa.Column("learning_state", sa.String(30), nullable=False, server_default="PENDING")],
        "interview_answers": [sa.Column("request_id", sa.String(64)), sa.Column("payload_hash", sa.String(64)),
                              sa.Column("processing_state", sa.String(30), nullable=False, server_default="PENDING"),
                              sa.Column("result_json", sa.Text())],
        "answer_evaluations": [sa.Column("provenance_json", sa.Text())],
        "interview_reports": [sa.Column("provenance_json", sa.Text())],
        "competency_history": [sa.Column("evidence_json", sa.Text())],
        "ai_call_logs": [sa.Column("business_id", sa.Integer()), sa.Column("request_id", sa.String(64)),
                         sa.Column("result_source", sa.String(30), nullable=False, server_default="UNKNOWN")],
    }
    for table, additions in columns.items():
        existing = {c["name"] for c in sa.inspect(conn).get_columns(table)}
        for column in additions:
            if column.name not in existing:
                op.add_column(table, column)
    conn.execute(sa.text("UPDATE interviews SET report_state='COMPLETED', learning_state='UNKNOWN' "
                         "WHERE id IN (SELECT interview_id FROM interview_reports)"))
    conn.execute(sa.text("UPDATE interview_answers SET processing_state='COMPLETED' "
                         "WHERE id IN (SELECT answer_id FROM answer_evaluations)"))


def downgrade():
    raise RuntimeError("此迁移包含用户投递与评分记录，请先备份并采用前向修复，禁止自动丢弃数据")

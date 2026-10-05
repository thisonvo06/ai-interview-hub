"""接管旧版自动补列；历史语音演示数据只清洗一次。"""
from alembic import op
from sqlalchemy import inspect, text
from app.core.database import Base
import app.models

revision = "0001_legacy"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    Base.metadata.create_all(conn)
    required_columns = {
        "interviews": {
            "resume_id": "INTEGER",
            "jd_text": "TEXT",
            "purpose": "VARCHAR(30)",
            "derived_from_id": "INTEGER",
            "current_question_shown_at": "DATETIME",
            "paused_at": "DATETIME",
        },
        "interview_answers": {
            "overtime": "BOOLEAN",
            "overtime_sec": "INTEGER",
        },
        "learning_tasks": {
            "stage": "VARCHAR(100)",
            "deliverable": "VARCHAR(255)",
            "resources_json": "TEXT",
            "estimated_weeks": "INTEGER",
        },
        "interview_plans": {
            "paper_json": "TEXT",
        },
        "interview_questions": {
            "bank_id": "INTEGER",
            "question_type": "VARCHAR(20)",
            "reference_points_json": "TEXT",
            "hints": "VARCHAR(255)",
            "time_limit_sec": "INTEGER",
        },
    }
    inspector = inspect(conn)
    existing_tables = set(inspector.get_table_names())
    for table, columns in required_columns.items():
        if table not in existing_tables:
            continue
        current = {c["name"] for c in inspector.get_columns(table)}
        for col_name, col_type in columns.items():
            if col_name not in current:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}"))
                current.add(col_name)

        # 旧数据补默认值：新增列在 SQLite 中为 NULL，需回填以保持查询语义一致
        defaults = {
            "interview_questions": {
                "question_type": "PROFESSIONAL",
                "time_limit_sec": 180,
            },
            "interviews": {
                "purpose": "NORMAL",
            },
            "interview_answers": {
                "overtime": 0,
                "overtime_sec": 0,
            },
        }.get(table, {})
        for col_name, default_val in defaults.items():
            literal = default_val if isinstance(default_val, int) else f"'{default_val}'"
            conn.execute(text(f"UPDATE {table} SET {col_name} = {literal} WHERE {col_name} IS NULL"))

    # 一次性数据清洗：语音链路从未接入，历史 answers 的 speaking_rate/filler_count
    # 全部来自旧接口/种子的假默认值（160/2），统一归零为"未测量"语义
    if "interview_answers" in existing_tables:
        inspector2 = inspect(conn)
        acols = {c["name"] for c in inspector2.get_columns("interview_answers")}
        if {"speaking_rate", "filler_count"} <= acols:
            conn.execute(text(
                "UPDATE interview_answers SET speaking_rate = 0, filler_count = 0 "
                "WHERE speaking_rate != 0 OR filler_count != 0"
            ))


def downgrade():
    raise RuntimeError("旧数据库基线不可自动删除，请从备份恢复")

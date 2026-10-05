"""新增私有求职计划工作台，不读取或修改既有业务记录。"""
from alembic import op
from sqlalchemy import inspect

revision = "0004_job_search"
down_revision = "0003_official_entries"
branch_labels = None
depends_on = None


def upgrade():
    from app.models.job_search import JobSearchOpportunity
    connection = op.get_bind()
    if JobSearchOpportunity.__tablename__ not in inspect(connection).get_table_names():
        JobSearchOpportunity.__table__.create(connection)


def downgrade():
    # 保留用户自行整理的岗位、材料和反馈，避免降级时丢失私有数据。
    pass

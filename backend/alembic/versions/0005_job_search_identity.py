"""桥接手动导入与平台保存，约束每人同一平台岗位只能关联一次。"""
from alembic import op
from sqlalchemy import inspect

revision = "0005_job_search_identity"
down_revision = "0004_job_search"
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    names = {index["name"] for index in inspect(connection).get_indexes("job_search_opportunities")}
    if "uq_job_search_user_source_job" not in names:
        op.create_index("uq_job_search_user_source_job", "job_search_opportunities", ["user_id", "source_job_id"], unique=True)


def downgrade():
    # 保留已绑定的来源与用户材料；降级无需拆散现有记录。
    pass

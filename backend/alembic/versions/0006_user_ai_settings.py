"""新增用户级 AI 服务配置表，普通用户可绑定自己的 API Key。"""
from alembic import op
from sqlalchemy import inspect

revision = "0006_user_ai_settings"
down_revision = "0005_job_search_identity"
branch_labels = None
depends_on = None


def upgrade():
    from app.models.system import UserAISetting
    connection = op.get_bind()
    if UserAISetting.__tablename__ not in inspect(connection).get_table_names():
        UserAISetting.__table__.create(connection)


def downgrade():
    # 保留用户自行绑定的个人 Key 配置，避免降级时丢失用户凭据。
    pass

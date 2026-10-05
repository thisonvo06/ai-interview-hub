"""为既有演示企业补官网招聘列表入口，不覆盖企业自定义链接。"""
from alembic import op
from sqlalchemy import text

revision = "0003_official_entries"
down_revision = "0002_reliable_backend"
branch_labels = None
depends_on = None


def upgrade():
    from app.data.official_recruitment import OFFICIAL_RECRUITMENT
    conn = op.get_bind()
    for name, url in OFFICIAL_RECRUITMENT.items():
        conn.execute(text("UPDATE jobs SET official_apply_url=:url WHERE official_apply_url IS NULL "
                          "AND company_id IN (SELECT id FROM companies WHERE name=:name)"), {"url": url, "name": name})


def downgrade():
    # 官方链接可能已被用户使用，不删除投递历史或企业配置。
    pass

"""在测试收集（import main）之前切换到临时数据库，保护工作区数据。"""
import atexit
import os
import sys
import tempfile
from pathlib import Path
import pytest

_temp = tempfile.TemporaryDirectory(prefix="interview-tests-")
os.environ["DATABASE_URL"] = "sqlite:///" + (Path(_temp.name) / "test.db").as_posix()
os.environ["UPLOAD_DIR"] = str(Path(_temp.name) / "uploads")
os.environ["AI_MODE"] = "mock"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture(scope="session", autouse=True)
def prepare_isolated_database(request):
    from app.core.database import engine
    # 旧的演示数据测试仍可运行，但只在隔离数据库中准备数据。
    if any(item.module.__name__.endswith("test_backend") for item in request.session.items):
        from scripts.seed_demo import seed
        seed(reset=True)
    yield
    engine.dispose()


def pytest_sessionfinish(session, exitstatus):
    from app.core.database import engine
    engine.dispose()
    _temp.cleanup()

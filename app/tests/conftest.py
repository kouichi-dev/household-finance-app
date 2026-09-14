import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from routers import get_db
import os
from alembic.config import Config
from alembic import command

SQLALCHEMY_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
alembic_cfg = Config("alembic.ini")
alembic_cfg.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)

@pytest.fixture(scope="session", autouse=True)
def migrations():
    command.upgrade(alembic_cfg, "head")
    yield
    command.downgrade(alembic_cfg, "base")

@pytest.fixture
def connection():
    connection = engine.connect()
    transaction = connection.begin()
    yield connection
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(connection):
    def override_get_db():
        db = TestingSessionLocal(bind=connection, join_transaction_mode="create_savepoint")
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

# エンドポイントをテストするために、ログイン情報を返す
@pytest.fixture
def auth(client):
    user = client.post("/users", json={
        "name": "taro",
        "email": "taro@example.com",
        "password": "password123"
    }).json()
    login = client.post("/auth/login", data={
        "username": "taro@example.com",
        "password": "password123"
    }).json()
    return {
        "user_id": user["id"],
        "headers": {"Authorization": f"Bearer {login['access_token']}"},
        "refresh_token": login["refresh_token"]
    }

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from main import app
from routers import get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# テストクライアントを渡す関数
@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

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
        "headers": {"Authorization": f"Bearer {login['access_token']}"}
    }

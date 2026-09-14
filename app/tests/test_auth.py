from sqlalchemy import update
from models import RefreshTokens
from datetime import datetime, timedelta, timezone

def test_リフレッシュトークン取得(client):
    client.post("/users", json={"name": "taro", "email": "taro@example.com", "password": "password123"})
    response = client.post("/auth/login", data={"username": "taro@example.com", "password": "password123"})
    body = response.json()
    assert response.status_code == 200
    assert "refresh_token" in body
    assert body["refresh_token"]

def test_リフレッシュ後のアクセストークンが有効(client,auth):
    response = client.post("/auth/refresh", json={"refresh_token": auth["refresh_token"]})
    body = response.json()
    assert response.status_code == 200
    assert "access_token" in body
    assert body["access_token"]

    new_token = body["access_token"]
    me = client.get("/users/me", headers={"Authorization": f"Bearer {new_token}"})
    assert me.status_code == 200

def test_リフレッシュトークンはログアウト後に401(client, auth):
    logout = client.post("/auth/logout", json={"refresh_token": auth["refresh_token"]})
    assert logout.status_code == 204
    response = client.post("/auth/refresh", json={"refresh_token": auth["refresh_token"]})
    assert response.status_code == 401

def test_不正なリフレッシュトークンは401を返す(client):
    response = client.post("/auth/refresh", json={"refresh_token": "invalid-token"})
    assert response.status_code == 401

def test_期限切れのリフレッシュトークンは401(client, auth, connection):
    connection.execute(
        update(RefreshTokens)
        .where(RefreshTokens.token == auth["refresh_token"])
        .values(expires_at=datetime.now(timezone.utc) - timedelta(days=1))
    )
    response = client.post("/auth/refresh", json={"refresh_token": auth["refresh_token"]})
    assert response.status_code == 401

def test_リフレッシュトークンはパスワード変更後に401(client, auth):
    updated = client.patch(f"/users/{auth['user_id']}", json={"password": "newpass123"}, headers=auth["headers"])
    assert updated.status_code == 200
    response = client.post("/auth/refresh", json={"refresh_token": auth["refresh_token"]})
    assert response.status_code == 401

def test_リフレッシュトークンは名前変更後も有効(client, auth):
    updated = client.patch(f"/users/{auth['user_id']}", json={"name": "jiro"}, headers=auth["headers"])
    assert updated.status_code == 200
    response = client.post("/auth/refresh", json={"refresh_token": auth["refresh_token"]})
    assert response.status_code == 200

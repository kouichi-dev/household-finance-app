import hashlib
from sqlalchemy import update, select
from models import RefreshTokens
from datetime import datetime, timedelta, timezone
from auth import create_access_token

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
        .where(RefreshTokens.token_hash == hashlib.sha256(auth["refresh_token"].encode()).hexdigest())
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

def test_リフレッシュトークンはDBにハッシュで保存される(client, auth, connection):
    saved = connection.execute(select(RefreshTokens.token_hash)).scalar_one()
    assert saved != auth["refresh_token"]
    assert saved == hashlib.sha256(auth["refresh_token"].encode()).hexdigest()

def test_不正なアクセストークンは401でWWW_Authenticateを返す(client):
    response = client.get("/users/me", headers={"Authorization": "Bearer invalid"})
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"

def test_subのないアクセストークンは401でWWW_Authenticateを返す(client):
    token = create_access_token({})
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"

def test_削除済みユーザーのアクセストークンは401でWWW_Authenticateを返す(client, auth):
    deleted = client.delete(f"/users/{auth['user_id']}", headers=auth["headers"])
    assert deleted.status_code == 204
    response = client.get("/users/me", headers=auth["headers"])
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"

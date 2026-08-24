def test_リフレッシュトークン取得(client):
    client.post("/users", json={"name": "taro", "email": "taro@example.com", "password": "password123"})
    response = client.post("/auth/login", data={"username": "taro@example.com", "password": "password123"})
    body = response.json()
    assert response.status_code == 200
    assert "refresh_token" in body  # エンドポイントの"refresh_token"をタイポしていた場合、サーバーは正常に動くがトークンが機能しないため
    assert body["refresh_token"]    # refresh_tokenの存在確認

def test_リフレッシュ後のアクセストークンが有効(client,auth):
    response = client.post("/auth/refresh", json={"refresh_token": auth["refresh_token"]})
    body = response.json()
    assert response.status_code == 200
    assert "access_token" in body
    assert body["access_token"]

    new_token = body["access_token"]
    me = client.get("/users/me", headers={"Authorization": f"Bearer {new_token}"})
    assert me.status_code == 200

    


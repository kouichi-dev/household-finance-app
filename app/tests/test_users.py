def test_ユーザー登録(client):
    response = client.post("/users", json={
        "name": "taro",
        "email": "taro@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "taro@example.com"

def test_ログイン(client):
    client.post("/users", json={"name": "taro", "email": "taro@example.com", "password": "password123"})
    response = client.post("/auth/login", data={"username": "taro@example.com", "password": "password123"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_ユーザー取得(client, auth):
    response = client.get(f"/users/{auth['user_id']}", headers=auth["headers"])
    assert response.status_code == 200

def test_ユーザー更新(client, auth):
    response = client.patch(f"/users/{auth['user_id']}", json={"name": "jiro", "email": "jiro@example.com", "password": "newpass"}, headers=auth["headers"])
    assert response.status_code == 200
    assert response.json()["name"] == "jiro"

def test_ユーザー削除(client, auth):
    response = client.delete(f"/users/{auth['user_id']}", headers=auth["headers"])
    assert response.status_code == 200

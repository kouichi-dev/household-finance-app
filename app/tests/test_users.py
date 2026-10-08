def test_ユーザー登録(client):
    response = client.post("/users", json={
        "name": "taro",
        "email": "taro@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "taro@example.com"

def test_ユーザー登録_emailの形式が不正は422(client):
    response = client.post("/users", json={"name": "taro", "email": "abc", "password": "password123"})
    assert response.status_code == 422

def test_ユーザー登録_nameが21文字は422(client):
    response = client.post("/users", json={"name": "a" * 21, "email": "taro@example.com", "password": "password123"})
    assert response.status_code == 422

def test_ユーザー登録_emailが31文字は422(client):
    response = client.post("/users", json={"name": "taro", "email": "a" * 19 + "@example.com", "password": "password123"})
    assert response.status_code == 422

def test_重複メールは登録できない(client):
    client.post("/users", json={
        "name": "taro", "email": "taro@example.com", "password": "password123"
    })
    response = client.post("/users", json={
        "name": "jiro", "email": "taro@example.com", "password": "password456"
    })
    assert response.status_code == 409

def test_ユーザー取得(client, auth):
    response = client.get(f"/users/{auth['user_id']}", headers=auth["headers"])
    assert response.status_code == 200

def test_他人のデータへのアクセスは403(client, auth):
    user_b = client.post("/users", json={
        "name": "jiro",
        "email": "jiro@example.com",
        "password": "password123"
    }).json()
    response = client.get(f"/users/{user_b['id']}", headers=auth["headers"])    
    assert response.status_code == 403

def test_ユーザー更新(client, auth):
    response = client.patch(f"/users/{auth['user_id']}", json={"name": "jiro", "email": "jiro@example.com", "password": "newpass"}, headers=auth["headers"])
    assert response.status_code == 200
    assert response.json()["name"] == "jiro"

def test_ユーザー部分更新_nameだけ(client, auth):
    r = client.patch(f"/users/{auth['user_id']}", json={"name": "newname"}, headers=auth["headers"])
    assert r.status_code == 200
    assert r.json()["name"] == "newname"
    assert r.json()["email"] == "taro@example.com"

def test_ユーザー更新_nameにnullは422(client, auth):
    response = client.patch(f"/users/{auth['user_id']}", json={"name": None, "email": "jiro@example.com", "password": "newpass"}, headers=auth["headers"])
    assert response.status_code == 422

def test_ユーザー更新_passwordにnullは422(client, auth):
    response = client.patch(f"/users/{auth['user_id']}", json={"name": "jiro", "email": "jiro@example.com", "password": None}, headers=auth["headers"])
    assert response.status_code == 422

def test_ユーザー更新_nameが21文字は422(client, auth):
    response = client.patch(f"/users/{auth['user_id']}", json={"name": "a" * 21}, headers=auth["headers"])
    assert response.status_code == 422

def test_他人のIDでは更新できない(client, auth):
    response = client.patch("/users/9999", json={"name": "x", "email": "x@x.com", "password": "x"}, headers=auth["headers"])
    assert response.status_code == 403

def test_メール変更後もトークンが有効(client, auth):
    client.patch(f"/users/{auth['user_id']}", json={"email": "changed@example.com"}, headers=auth["headers"])
    # 変更前に取ったトークンで /users/me → まだ使える（id基盤なので）
    r = client.get("/users/me", headers=auth["headers"])
    assert r.status_code == 200

def test_ユーザー削除(client, auth):
    response = client.delete(f"/users/{auth['user_id']}", headers=auth["headers"])
    assert response.status_code == 204

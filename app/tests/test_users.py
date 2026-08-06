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

def test_存在しないユーザーログイン(client):
    response = client.post("/auth/login", data={"username": "nobody@example.com", "password": "x"})
    assert response.status_code == 401

def test_他人のデータへのアクセス(client, auth):
    user_b = client.post("/users", json={
        "name": "jiro",
        "email": "jiro@example.com",
        "password": "password123"
    }).json()
    response = client.get(f"/users/{user_b['id']}", headers=auth["headers"])    
    assert response.status_code == 403

def test_ユーザー取得(client, auth):
    response = client.get(f"/users/{auth['user_id']}", headers=auth["headers"])
    assert response.status_code == 200



def test_ユーザー更新(client, auth):
    response = client.patch(f"/users/{auth['user_id']}", json={"name": "jiro", "email": "jiro@example.com", "password": "newpass"}, headers=auth["headers"])
    assert response.status_code == 200
    assert response.json()["name"] == "jiro"

def test_存在しないユーザー更新(client, auth):
    response = client.patch("/users/9999", json={"name": "x", "email": "x@x.com", "password": "x"}, headers=auth["headers"])
    assert response.status_code == 403

def test_ユーザー削除(client, auth):
    response = client.delete(f"/users/{auth['user_id']}", headers=auth["headers"])
    assert response.status_code == 204

def test_重複メールは登録できない(client):
    client.post("/users", json={
        "name": "taro", "email": "taro@example.com", "password": "password123"
    })
    # 同じemailでもう一度登録
    response = client.post("/users", json={
        "name": "jiro", "email": "taro@example.com", "password": "password456"
    })
    assert response.status_code == 409

    
def test_ログイン失敗_存在有無でメッセージが変わらない(client):
    # 存在有無でメッセージを変えると列挙攻撃を許すため、同一であることを保証する
    client.post("/users", json={"name": "taro", "email": "taro@example.com", "password": "password123"})
    # ① 存在しないメール
    r1 = client.post("/auth/login", data={"username": "nobody@example.com", "password": "x"})
    # ② 存在するがパスワード違い
    r2 = client.post("/auth/login", data={"username": "taro@example.com", "password": "wrong"})
    assert r1.status_code == r2.status_code == 401
    assert r1.json()["detail"] == r2.json()["detail"]

def test_ユーザー部分更新_nameだけ(client, auth):
    # name だけ送る → email は元のまま
    r = client.patch(f"/users/{auth['user_id']}", json={"name": "newname"}, headers=auth["headers"])
    assert r.status_code == 200
    assert r.json()["name"] == "newname"
    assert r.json()["email"] == "taro@example.com"   # 送ってないので不変

def test_メール変更後もトークンが有効(client, auth):
    # email を変更
    client.patch(f"/users/{auth['user_id']}", json={"email": "changed@example.com"}, headers=auth["headers"])
    # 変更前に取ったトークンで /users/me → まだ使える（id基盤なので）
    r = client.get("/users/me", headers=auth["headers"])
    assert r.status_code == 200

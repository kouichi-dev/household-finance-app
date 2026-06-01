def test_カテゴリ登録(client, auth):
    response = client.post("/categories", json={"name": "食費"}, headers=auth["headers"])
    assert response.status_code == 200
    assert response.json()["name"] == "食費"

def test_カテゴリ一覧取得(client, auth):
    client.post("/categories", json={"name": "食費"}, headers=auth["headers"])
    response = client.get("/categories", headers=auth["headers"])
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_カテゴリ更新(client, auth):
    created = client.post("/categories", json={"name": "食費"}, headers=auth["headers"]).json()
    response = client.patch(f"/categories/{created['id']}", json={"name": "交通費"}, headers=auth["headers"])
    assert response.status_code == 200
    assert response.json()["name"] == "交通費"

def test_カテゴリ削除(client, auth):
    created = client.post("/categories", json={"name": "食費"}, headers=auth["headers"]).json()
    response = client.delete(f"/categories/{created['id']}", headers=auth["headers"])
    assert response.status_code == 200

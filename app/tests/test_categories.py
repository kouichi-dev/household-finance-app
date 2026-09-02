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
    assert response.status_code == 204


def test_同名カテゴリは409(client, auth):
    client.post("/categories", json={"name": "食費"}, headers=auth["headers"])
    r = client.post("/categories", json={"name": "食費"}, headers=auth["headers"])
    assert r.status_code == 409

def test_カテゴリ一覧_name順で返る(client, auth):
    client.post("/categories", json={"name": "わ"}, headers=auth["headers"])
    client.post("/categories", json={"name": "あ"}, headers=auth["headers"])
    response = client.get("/categories", headers=auth["headers"])
    assert response.status_code == 200
    assert [category["name"] for category in response.json()] == ["あ","わ"]

def test_カテゴリ削除で取引が未分類(client, auth):
    category = client.post("/categories", json={"name": "食費"}, headers=auth["headers"]).json()
    client.post("/transactions", json={
        "amount": 1000,
        "kind": "expense",
        "description": "ランチ",
        "transaction_date": "2026-06-15",
        "category_id": category["id"]
    }, headers=auth["headers"])
    client.delete(f"/categories/{category["id"]}", headers=auth["headers"])
    response = client.get("/transactions", headers=auth["headers"])
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1
    assert response.json()["items"][0]["category_id"] is None
    


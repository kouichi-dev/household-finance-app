def test_収支登録(client, auth):
    response = client.post("/transactions", json={
        "amount": 1000,
        "type": "expense",
        "description": "ランチ",
        "transaction_date": "2026-06-15"
    }, headers=auth["headers"])
    assert response.status_code == 200
    assert response.json()["amount"] == 1000

def test_収支一覧取得(client, auth):
    client.post("/transactions", json={"amount": 1000, "type": "expense","transaction_date": "2026-06-15"}, headers=auth["headers"])
    response = client.get("/transactions?page=1&limit=20", headers=auth["headers"])
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_認証なしアクセス(client):
    response = client.get("/transactions")
    assert response.status_code == 401

def test_収支更新(client, auth):
    created = client.post("/transactions", json={"amount": 1000, "type": "expense","transaction_date": "2026-06-15"}, headers=auth["headers"]).json()
    response = client.patch(f"/transactions/{created['id']}", json={"amount": 2000, "type": "expense","transaction_date": "2026-06-15"}, headers=auth["headers"])
    assert response.status_code == 200
    assert response.json()["amount"] == 2000

def test_収支削除(client, auth):
    created = client.post("/transactions", json={"amount": 1000, "type": "expense","transaction_date": "2026-06-15"}, headers=auth["headers"]).json()
    response = client.delete(f"/transactions/{created['id']}", headers=auth["headers"])
    assert response.status_code == 200

def test_収支集計(client, auth):
    client.post("/transactions", json={"amount": 1000, "type": "expense","transaction_date": "2026-06-15"}, headers=auth["headers"])
    response = client.get("/transactions/summary?type=monthly&year=2026&month=6", headers=auth["headers"])
    assert response.status_code == 200

# 週次で収支の合計が取得できることを確認するテスト
def test_週次集計(client, auth):
    client.post("/transactions", json={"amount": 1000, "type": "expense","transaction_date": "2026-06-15"}, headers=auth["headers"])
    response = client.get("/transactions/summary?type=weekly&year=2026&week=1", headers=auth["headers"])
    assert response.status_code == 200

def test_不正なpageは422になる(client, auth):
    response = client.get("/transactions?page=0", headers=auth["headers"])
    assert response.status_code == 422

def test_limit上限超過は422になる(client, auth):
    response = client.get("/transactions?limit=101", headers=auth["headers"])
    assert response.status_code == 422

def test_limit下限未満は422になる(client, auth):
    response = client.get("/transactions?limit=0", headers=auth["headers"])
    assert response.status_code == 422    
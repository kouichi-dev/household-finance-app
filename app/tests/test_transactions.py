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

def test_他人のカテゴリは紐づけできない(client, auth):
    # 別ユーザーB を作ってカテゴリを持たせる
    client.post("/users", json={"name": "jiro", "email": "jiro@example.com", "password": "password123"})
    login_b = client.post("/auth/login", data={"username": "jiro@example.com", "password": "password123"}).json()
    headers_b = {"Authorization": f"Bearer {login_b['access_token']}"}
    category_b = client.post("/categories", json={"name": "娯楽"}, headers=headers_b).json()

    # A（auth）が B のカテゴリidで収支作成 → 404
    response = client.post("/transactions", json={
        "amount": 1000, "type": "expense", "transaction_date": "2026-06-15",
        "category_id": category_b["id"]
    }, headers=auth["headers"])
    assert response.status_code == 404

# 存在しないカテゴリidは弾く（FK違反500を防ぐ）
def test_存在しないカテゴリは紐づけできない(client, auth):
    response = client.post("/transactions", json={
        "amount": 1000, "type": "expense", "transaction_date": "2026-06-15",
        "category_id": 9999
    }, headers=auth["headers"])
    assert response.status_code == 404

# 自分のカテゴリなら正常に紐づく（正規フローが壊れてない確認）
def test_自分のカテゴリは紐づけできる(client, auth):
    category = client.post("/categories", json={"name": "食費"}, headers=auth["headers"]).json()
    response = client.post("/transactions", json={
        "amount": 1000, "type": "expense", "transaction_date": "2026-06-15",
        "category_id": category["id"]
    }, headers=auth["headers"])
    assert response.status_code == 200
    assert response.json()["category_id"] == category["id"]

    # monthly なのに month 未指定 → 422（条件付き必須・service側）
def test_summary_monthlyでmonth無しは422(client, auth):
    response = client.get("/transactions/summary?type=monthly&year=2026", headers=auth["headers"])
    assert response.status_code == 422

# weekly なのに week 未指定 → 422（条件付き必須・service側）
def test_summary_weeklyでweek無しは422(client, auth):
    response = client.get("/transactions/summary?type=weekly&year=2026", headers=auth["headers"])
    assert response.status_code == 422

# month 範囲外 → 422（範囲・router側 Query）
def test_summary_month範囲外は422(client, auth):
    response = client.get("/transactions/summary?type=monthly&year=2026&month=13", headers=auth["headers"])
    assert response.status_code == 422

# week 範囲外 → 422（範囲・router側 Query）
def test_summary_week範囲外は422(client, auth):
    response = client.get("/transactions/summary?type=weekly&year=2026&week=60", headers=auth["headers"])
    assert response.status_code == 422

def test_summary_週次_ISO年境界(client, auth):
# 2023-01-01 は ISO 2022年 第52週
    client.post("/transactions", json={"amount": 1000, "type": "income",
        "transaction_date": "2023-01-01"}, headers=auth["headers"])

    # ISO的に正しい year=2022, week=52 → 拾える
    r1 = client.get("/transactions/summary?type=weekly&year=2022&week=52", headers=auth["headers"])
    assert r1.json()["income"] == 1000

    # 暦年に釣られた year=2023, week=52 → 拾わない
    r2 = client.get("/transactions/summary?type=weekly&year=2023&week=52", headers=auth["headers"])
    assert r2.json()["income"] == 0

# サイレントバグの回帰テスト：transaction_date が実際に更新される
def test_収支更新_日付が反映される(client, auth):
    created = client.post("/transactions", json={"amount": 1000, "type": "expense",
        "transaction_date": "2026-06-15"}, headers=auth["headers"]).json()
    r = client.patch(f"/transactions/{created['id']}",
        json={"transaction_date": "2026-07-20"}, headers=auth["headers"])
    assert r.status_code == 200
    assert r.json()["transaction_date"] == "2026-07-20"

# 部分更新：amount だけ送る → description は不変
def test_収支部分更新_amountだけ(client, auth):
    created = client.post("/transactions", json={"amount": 1000, "type": "expense",
        "transaction_date": "2026-06-15", "description": "ランチ"}, headers=auth["headers"]).json()
    r = client.patch(f"/transactions/{created['id']}", json={"amount": 2000}, headers=auth["headers"])
    assert r.status_code == 200
    assert r.json()["amount"] == 2000
    assert r.json()["description"] == "ランチ"   # 送ってないので不変

# 家計簿アプリ

収支とカテゴリを管理する REST API です。
「雑に使えて、シンプルであること」を設計の軸に、入力は最小の手数、見返しは月・年の2画面で完結する家計簿を想定しています。

## 主な機能

- ユーザー登録・ログイン（JWT。アクセストークン + リフレッシュトークン）
- 収支の登録・一覧・更新・削除（ページネーション、期間・カテゴリ・収支種別で絞り込み）
- カテゴリの登録・一覧・更新・削除（登録時に初期カテゴリ6件を自動作成）
- 月次・年次の集計（合計 + カテゴリ別内訳 + 日付別内訳）

## 技術スタック

| 技術 | 用途 |
|------|------|
| FastAPI | Webフレームワーク |
| PostgreSQL | データベース |
| SQLAlchemy | ORMによるDB操作 |
| Alembic | マイグレーション管理 |
| JWT | ステートレス認証 |
| Docker | 環境構築・再現性の担保 |
| pytest | テスト |

## 起動方法

### 前提条件
- Docker / Docker Compose がインストールされていること

### 手順

```bash
git clone https://github.com/kouitchi-dev/household-finance-app.git
cd household-finance-app
cp .env.example .env
# .env を開き、CHANGE_ME の3箇所を実際の値に置き換える
docker compose up --build
```

`db` → `migrate`（`alembic upgrade head`）→ `app` の順に起動します。
起動後、http://localhost:8000/docs で Swagger UI が開きます。

`db/init.sql` はテスト用DB（`household_test`）を作成しますが、
これはDBのデータボリュームが空のときにのみ実行されます。
一度でも起動したことがある場合は、ボリューム（＝DBのデータ）ごと削除してから起動してください。

```bash
docker compose down -v
docker compose up --build
```

### Swagger UI での試し方

1. `POST /users` でユーザーを登録する
2. 右上の **Authorize** を押し、`username` にメールアドレス、`password` にパスワードを入れる
3. 以降、認証が必要なエンドポイントをそのまま呼べる

## エンドポイント一覧

認証欄の「必要」は `Authorization: Bearer <access_token>` ヘッダーが必要です。

### ユーザー・認証
| メソッド | パス | 説明 | 認証 |
|--------|------|------|------|
| POST | /users | ユーザー登録（初期カテゴリ6件も作成） | 不要 |
| GET | /users/me | ログイン中のユーザー取得 | 必要 |
| GET | /users/{id} | ユーザー取得（本人のみ） | 必要 |
| PATCH | /users/{id} | ユーザー更新（本人のみ） | 必要 |
| DELETE | /users/{id} | ユーザー削除（本人のみ） | 必要 |
| POST | /auth/login | ログイン（アクセストークン + リフレッシュトークン発行） | 不要 |
| POST | /auth/refresh | アクセストークン再発行 | 不要（リフレッシュトークンを body で送る） |
| POST | /auth/logout | リフレッシュトークン失効 | 不要（同上） |

### 収支
| メソッド | パス | 説明 | 認証 |
|--------|------|------|------|
| POST | /transactions | 収支登録（取引日を省略すると JST の今日） | 必要 |
| GET | /transactions | 収支一覧（ページネーション・絞り込み） | 必要 |
| GET | /transactions/summary | 収支集計 | 必要 |
| PATCH | /transactions/{id} | 収支更新 | 必要 |
| DELETE | /transactions/{id} | 収支削除 | 必要 |

一覧と集計は同じクエリパラメータで期間・絞り込みを受けます。

| パラメータ | 値 | 説明 |
|---|---|---|
| unit | `monthly` / `yearly` | 期間の単位（省略時 `monthly`） |
| on | 日付（例: `2026-08-15`） | その日を含む期間を対象にする。一覧では省略すると全期間 |
| category_id | カテゴリID / `none` | `none` は未分類のみ。省略時は絞らない |
| kind | `income` / `expense` | 省略時は絞らない |

一覧はこれに加えて `page`（省略時 1）と `limit`（省略時 20、最大 100）を受けます。

集計のレスポンス例（`unit=monthly&on=2026-08-15`）:

```json
{
  "income": 250000,
  "expense": 8500,
  "balance": 241500,
  "by_category": [
    { "category_id": 6, "category_name": "給与", "income": 250000, "expense": 0 },
    { "category_id": 1, "category_name": "食費", "income": 0, "expense": 8000 },
    { "category_id": null, "category_name": null, "income": 0, "expense": 500 }
  ],
  "by_date": [
    { "date": "2026-08-10", "income": 0, "expense": 8000 },
    { "date": "2026-08-12", "income": 0, "expense": 500 },
    { "date": "2026-08-25", "income": 250000, "expense": 0 }
  ]
}
```

- `by_category` は金額の大きい順。未分類は `category_id` / `category_name` が `null`
- `by_date` は日付順で、取引のあった日だけ返す。`unit=yearly` では月ごと（`date` はその月の1日）

### カテゴリ
| メソッド | パス | 説明 | 認証 |
|--------|------|------|------|
| POST | /categories | カテゴリ登録 | 必要 |
| GET | /categories | カテゴリ一覧（名前順） | 必要 |
| PATCH | /categories/{id} | カテゴリ更新 | 必要 |
| DELETE | /categories/{id} | カテゴリ削除（紐づく収支は未分類になる） | 必要 |

詳しい仕様は [DESIGN.md](DESIGN.md) を参照してください。

## 設計のポイント

### 認証はハイブリッド方式
- **アクセストークン**（30分）: JWT の署名だけで検証し、DB を見ない（ステートレス）
- **リフレッシュトークン**（30日）: DB に保存し、ログアウト時に失効できる

一般ユーザー向けのアプリなので、ログアウトやトークン盗難のときに無効化できる必要があります。
毎回のリクエストはステートレスのまま、失効の仕組みだけを DB に持たせました。

### 条件は1箇所、使う場所は2つ
期間と絞り込みの条件を組み立てる処理を1箇所にまとめ、一覧のクエリと集計のクエリの両方がそれを使います。
別々に書くと、明細を足した数字と合計が食い違うバグが起きうるためです。

### 集計は SQL の中で行う
全件を取り出してから Python で足すのではなく、`GROUP BY` と `SUM` で DB 側で集計します。

### クライアントに日付計算をさせない
一覧のレスポンスは「前の期間」「次の期間」の日付（`prev_on` / `next_on`）を含みます。
クライアントはそれを次のリクエストにそのまま入れるだけで、月送りができます。

### 1リクエスト = 1トランザクション
commit はリクエストの最後に1回だけ行います。
ユーザー登録と初期カテゴリ作成のように複数の書き込みがあっても、途中で失敗すれば全部取り消されます。

### インデックス
全クエリが「自分の・期間内の」取引を探すため、`transactions` に `(user_id, transaction_date)` の複合インデックスを張っています。

## アーキテクチャ

router / service / repository の3層構造です。

| 層 | ファイル | 役割 |
|---|---|---|
| router | `routers.py` | リクエスト・レスポンスの処理 |
| service | `services.py` | ビジネスロジック |
| repository | `crud.py` | DB操作 |

### ER図
![ER図](docs/er-diagram.png)

## テスト

```bash
docker compose run --rm app pytest tests/
```

テストDBは本番と同じ PostgreSQL（`household_test`）を使います。
SQLite ではタイムゾーンや外部キー制約の挙動が PostgreSQL と異なるため、本番と揃えています。


# 要件定義

## 機能要件

### 認証
- ユーザー登録・ログインができる
- JWTトークンで認証する
- 自分のデータのみ操作できる
- アクセストークン（短命）とリフレッシュトークン（長命）の2種類を発行する
- アクセストークンが失効したら、リフレッシュトークンで再発行できる
- ログアウト時にリフレッシュトークンを失効できる（無効化する）

### 収支管理
- 収支を登録・取得・更新・削除できる
- 収支にカテゴリを紐づけられる
- 一覧はページネーションで取得できる

### カテゴリ管理
- カテゴリを登録・取得・更新・削除できる
- ユーザー登録時に、初期カテゴリ6件（食費 / 日用品 / 交通費 / 住居 / 娯楽 / 給与）が自動で作られる
  （最初の記録の前にカテゴリ作成を強いないため。不要なものは削除できる）

### 集計
- 月次・年次で収支の合計を取得できる

## 非機能要件
- パスワードはハッシュ化して保存する
- 認証にJWTを使用し、通常のAPIリクエストはステートレスに検証する
  - アクセストークン: JWTの署名で検証し、サーバーにセッションを持たない（ステートレス）。削除済みユーザーを弾くため、ユーザーの取得でDBを参照する
  - リフレッシュトークン: SHA-256 ハッシュでDBに保存し、失効可能にする（再発行・ログアウト時のみDB参照）
- Dockerで環境を再現できる
- Alembicでスキーマ変更を管理する
- pytestでテストを書く
- 日本国内のユーザーを想定する。日付は JST（Asia/Tokyo）基準で判定する
    - サーバー/コンテナのタイムゾーンは UTC のため、「今日」を求めるときは明示的に JST に変換する

## エンドポイント一覧
- POST    /users　　   ユーザー登録
    - 登録と同時に初期カテゴリ6件を作成する（同一トランザクション）
- GET     /users/{id}　ユーザー取得
- PATCH   /users/{id}　ユーザー更新
- DELETE  /users/{id}  ユーザー削除
- POST    /auth/login    ログイン（アクセストークン + リフレッシュトークンを発行）
- POST    /auth/refresh  リフレッシュトークンでアクセストークンを再発行
- POST    /auth/logout   リフレッシュトークンを失効（ログアウト）
- GET     /users/me      ログイン中のユーザー取得

- POST    /transactions          収支登録
    - transaction_date は省略可能。省略時は JST の今日を入れる
- GET /transactions/summary  収支集計取得
    - クエリパラメータ:
      - unit: monthly | yearly（省略時 monthly）
      - on: 日付（例: 2026-08-15）。その日を含む期間を集計する。省略時は JST の今日
      - category_id: カテゴリID | none（未分類のみ）。省略時は絞らない
      - kind: income | expense。省略時は絞らない
    - 未分類は文字列 `none` を送る。`null` や空文字、0 ではない
    - 集計の基準: transaction_date（取引日）が期間に含まれるもの
    - レスポンス:
      - {
          "period": { "unit": monthly | yearly, "start": 期間の初日, "end": 期間の末日 },
          "prev_on": 前の期間の初日,
          "next_on": 次の期間の初日,
          "income": 収入合計,
          "expense": 支出合計,
          "balance": 収支差額(income - expense),
          "by_category": [ { "category_id": ID | null, "category_name": 名前 | null, "income": 収入, "expense": 支出 } ],
          "by_date":     [ { "date": 日付, "income": 収入, "expense": 支出 } ]
        }
    - 前後の期間へ移るときは、prev_on / next_on をそのまま on に入れて送る。クライアントは日付を計算しない
    - income / expense は符号なしの正の値。差額は balance を使い、クライアント側で再計算しない
    - by_category: 取引のあったカテゴリのみ返す。並び順は (income + expense) 降順
      - 未分類は category_id / category_name が null
    - by_date: 取引のあった日付のみ返す。取引ゼロの日は含めない。並び順は date 昇順
      - unit=monthly は1日ごと、unit=yearly は月ごと（date はその月の1日）
      - 収入と支出を分けて返す。給料日など同じ日に両方あるケースを差額1つでは表現できないため

- GET     /transactions?page=1&limit=20   収支一覧取得
    - クエリパラメータ:
      - unit: monthly | yearly（省略時 monthly）
      - on: 日付。その日を含む期間の明細を返す。省略時は JST の今日
      - category_id: カテゴリID | none（未分類のみ）。省略時は絞らない
      - kind: income | expense。省略時は絞らない
    - 並び順: transaction_date 降順、同日は id 降順（新しい順）
    - レスポンス:
      - {
          "period": { "unit": monthly | yearly, "start": 期間の初日, "end": 期間の末日 },
          "prev_on": 前の期間の初日,
          "next_on": 次の期間の初日,
          "items": [ { "id", "amount", "kind", "description", "category_id", "category_name", "created_at", "transaction_date" } ],
          "total_count": 絞り込み後の総件数（ページ分けする前）,
          "page": ページ番号,
          "limit": 1ページの件数
        }
    - 前後の期間へ移るときは、prev_on / next_on をそのまま on に入れて送る。クライアントは日付を計算しない
    - items[].category_name はサーバーが categories を LEFT JOIN して返す。未分類は category_id / category_name が null
- PATCH　 /transactions/{id}     収支更新
- DELETE  /transactions/{id}     収支削除


- POST    /categories       カテゴリ登録
- GET     /categories       カテゴリ一覧取得
    - 並び順: name 昇順
    - 用途: 収支の登録・更新でカテゴリを選ぶための一覧（将来のカテゴリ管理画面でも使う）
    - 期間や絞り込み（unit / on / category_id / kind）には連動しない。取引が0件のカテゴリも含めて全部返す
- PATCH   /categories/{id}  カテゴリ更新
- DELETE  /categories/{id}   カテゴリ削除





## DB設計

### usersテーブル
- id INTEGER PRIMARY KEY
- name VARCHAR(20) NOT NULL
- email VARCHAR(30) NOT NULL UNIQUE
- password VARCHAR(100) NOT NULL
- created_at TIMESTAMP NOT NULL

### transactionsテーブル
- id INTEGER PRIMARY KEY
- user_id INTEGER FOREIGN KEY('users.id') NOT NULL
- category_id INTEGER FOREIGN KEY('categories.id')
- amount INTEGER NOT NULL
- description VARCHAR(50) NULLABLE
- kind VARCHAR(10) NOT NULL CHECK(kind IN ('income', 'expense'))
- transaction_date DATE NOT NULL
- created_at TIMESTAMP NOT NULL

### categoriesテーブル
- id INTEGER PRIMARY KEY
- user_id INTEGER FOREIGN KEY('users.id') NOT NULL
- name VARCHAR(50) NOT NULL

### refresh_tokensテーブル
- id INTEGER PRIMARY KEY
- user_id INTEGER FOREIGN KEY('users.id') NOT NULL
- token_hash VARCHAR(255) NOT NULL UNIQUE
- expires_at TIMESTAMP NOT NULL
- revoked BOOLEAN NOT NULL DEFAULT false
- created_at TIMESTAMP NOT NULL


## アーキテクチャ

### 3層構造
- router   : リクエスト・レスポンスの処理
- service  : ビジネスロジック
- repository: DB操作

### ER図
![ER図](docs/er-diagram.png)

### 技術選定理由
- **FastAPI** : 型安全・自動ドキュメント生成・高速。FastAPIは学習済みであること、軽量で速く、このアプリの規模だと適していることから。
- PostgreSQL : リレーション管理に適したRDB。PostgreSQLを使うのは実務で最も使われているRDBのため。
- JWT : ステートレス認証。JWTを採用するのはステートレスでサーバーがセッションを持たず拡張しやすい(サーバーがログイン情報を持たないためサーバーを増やしやすい)。また、実務で広く使われているため。　　　　　　
- Docker : 環境の再現性を担保できるため


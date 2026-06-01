# 家計簿アプリ

収支・カテゴリを管理するREST APIです。

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
docker-compose up --build
```

## エンドポイント一覧


### 認証
| メソッド | パス | 説明 |
|--------|------|------|
| POST | /users | ユーザー登録 |
| GET | /users/{id} | ユーザー取得 |
| PATCH | /users/{id} | ユーザー更新 |
| DELETE | /users/{id} | ユーザー削除 |
| POST | /auth/login | ログイン（JWTトークン発行） |

### 収支
| メソッド | パス | 説明 |
|--------|------|------|
| POST | /transactions | 収支登録 |
| GET | /transactions?page=1&limit=20 | 収支一覧取得 |
| PATCH | /transactions/{id} | 収支更新 |
| DELETE | /transactions/{id} | 収支削除 |
| GET | /transactions/summary?type=monthly&year=2025&month=1 | 月次・週次集計 |

### カテゴリ
| メソッド | パス | 説明 |
|--------|------|------|
| POST | /categories | カテゴリ登録 |
| GET | /categories | カテゴリ一覧取得 |
| PATCH | /categories/{id} | カテゴリ更新 |
| DELETE | /categories/{id} | カテゴリ削除 |

## テスト

```bash
docker-compose exec app pytest tests/
```


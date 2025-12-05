# Project Structure

```
bedrock-kb-mcp-server/
├── src/                    # メインソースコード
│   ├── __init__.py
│   ├── server.py           # FastMCP サーバー・kb_answer ツール定義
│   ├── bedrock_client.py   # Bedrock API クライアント（RetrieveAndGenerate）
│   ├── config.py           # 環境変数からの設定読み込み
│   ├── models.py           # データクラス（KBResponse, Citation）
│   ├── parser.py           # API レスポンスパーサー
│   └── validation.py       # 入力バリデーション
├── tests/                  # テストコード
│   ├── __init__.py
│   ├── test_server.py          # サーバー統合テスト
│   ├── test_bedrock_client.py  # リクエスト構築テスト
│   ├── test_config.py          # 設定読み込みテスト
│   ├── test_parser.py          # パーサーテスト
│   └── test_validation.py      # バリデーションテスト
├── samlpe/                 # サンプルドキュメント
├── kb_mcp_server.py        # エントリーポイント（開発用）
├── pyproject.toml          # プロジェクト設定・依存関係
└── README.md
```

## モジュール責務

| モジュール | 責務 |
|-----------|------|
| `server.py` | FastMCP サーバー初期化・`kb_answer` ツール定義 |
| `config.py` | 環境変数から `KBConfig` を生成 |
| `models.py` | `KBResponse`, `Citation` データクラス定義 |
| `bedrock_client.py` | API リクエスト構築・実行 |
| `parser.py` | API レスポンスを `KBResponse` に変換 |
| `validation.py` | クエリ文字列のバリデーション |

## テスト方針

- Hypothesis によるプロパティベーステスト
- 各テストは最低 100 例を実行（`max_examples=100`）
- テストクラス名は `TestProperty{N}` 形式で要件との対応を明示

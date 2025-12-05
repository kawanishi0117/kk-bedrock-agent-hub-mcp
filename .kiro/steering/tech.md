# Tech Stack

## 言語・ランタイム

- Python 3.10+
- 型ヒント使用（`dict[str, Any]`, `list[Citation]`, `float | None` など）

## ビルドシステム

- Hatchling（`pyproject.toml` ベース）

## 主要ライブラリ

| ライブラリ | 用途 |
|-----------|------|
| `mcp[server]` | MCP サーバー実装 |
| `fastmcp` | MCP サーバーフレームワーク |
| `boto3` | AWS SDK（Bedrock Agent Runtime） |

## 開発・テスト依存

| ライブラリ | 用途 |
|-----------|------|
| `pytest` | テストフレームワーク |
| `hypothesis` | プロパティベーステスト |
| `pytest-mock` | モック |

## コマンド

```bash
# インストール（開発モード）
pip install -e ".[dev]"

# テスト実行
pytest

# サーバー起動
python kb_mcp_server.py
# または
bedrock-kb-mcp
```

## 環境変数

| 変数名 | 必須 | デフォルト | 説明 |
|--------|------|------------|------|
| `AWS_REGION` | No | `ap-northeast-1` | AWS リージョン |
| `BEDROCK_KB_ID` | Yes | - | Knowledge Base ID |
| `BEDROCK_MODEL_ARN` | Yes | - | 基盤モデルの ARN |
| `AWS_PROFILE` | No | - | AWS 認証プロファイル |

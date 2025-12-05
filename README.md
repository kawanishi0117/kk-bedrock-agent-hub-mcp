# Bedrock Knowledge Base MCP Server

Amazon Bedrock Knowledge Base にクエリを送信する MCP (Model Context Protocol) サーバーです。

## 概要

このサーバーは、AI アシスタント（Claude Desktop、Cursor、Kiro）が Amazon Bedrock Knowledge Base から情報を取得できるようにする `kb_answer` ツールを提供します。

## 機能

- Bedrock RetrieveAndGenerate API を使用した Knowledge Base クエリ
- 環境変数ベースの設定管理
- 引用情報（ソース、スコア）の抽出と返却
- 入力バリデーション

## 環境変数

| 変数名 | 必須 | デフォルト | 説明 |
|--------|------|------------|------|
| `AWS_REGION` | いいえ | `ap-northeast-1` | AWS リージョン |
| `BEDROCK_KB_ID` | はい | - | Knowledge Base ID |
| `BEDROCK_MODEL_ARN` | はい | - | 基盤モデルの ARN |
| `AWS_PROFILE` | いいえ | - | AWS 認証プロファイル |

### 環境変数の設定例

```bash
# Linux/macOS
export AWS_REGION="ap-northeast-1"
export BEDROCK_KB_ID="your-knowledge-base-id"
export BEDROCK_MODEL_ARN="arn:aws:bedrock:ap-northeast-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"

# Windows (PowerShell)
$env:AWS_REGION = "ap-northeast-1"
$env:BEDROCK_KB_ID = "your-knowledge-base-id"
$env:BEDROCK_MODEL_ARN = "arn:aws:bedrock:ap-northeast-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
```

## インストール

```bash
# 開発モードでインストール
pip install -e ".[dev]"
```

## 使用方法

### 直接実行

```bash
python kb_mcp_server.py
```

### コマンドラインから実行

```bash
bedrock-kb-mcp
```

## MCP クライアント設定

### Claude Desktop

`claude_desktop_config.json` に以下を追加:

```json
{
  "mcpServers": {
    "bedrock-kb": {
      "command": "python",
      "args": ["path/to/kb_mcp_server.py"],
      "env": {
        "AWS_REGION": "ap-northeast-1",
        "BEDROCK_KB_ID": "your-kb-id",
        "BEDROCK_MODEL_ARN": "arn:aws:bedrock:ap-northeast-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
      }
    }
  }
}
```

### Cursor

`.cursor/mcp.json` に以下を追加:

```json
{
  "mcpServers": {
    "bedrock-kb": {
      "command": "python",
      "args": ["path/to/kb_mcp_server.py"],
      "env": {
        "AWS_REGION": "ap-northeast-1",
        "BEDROCK_KB_ID": "your-kb-id",
        "BEDROCK_MODEL_ARN": "arn:aws:bedrock:ap-northeast-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
      }
    }
  }
}
```

### Kiro

`.kiro/settings/mcp.json` に以下を追加:

```json
{
  "mcpServers": {
    "bedrock-kb": {
      "command": "python",
      "args": ["path/to/kb_mcp_server.py"],
      "env": {
        "AWS_REGION": "ap-northeast-1",
        "BEDROCK_KB_ID": "your-kb-id",
        "BEDROCK_MODEL_ARN": "arn:aws:bedrock:ap-northeast-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
      }
    }
  }
}
```

## kb_answer ツール

### パラメータ

| パラメータ | 型 | 必須 | デフォルト | 説明 |
|-----------|-----|------|------------|------|
| `query` | string | はい | - | Knowledge Base に送信するクエリ文字列 |
| `max_results` | integer | いいえ | 4 | 取得するソースチャンクの最大数（1-10） |

### 使用例

```
kb_answer("製品の返品ポリシーについて教えてください")
kb_answer("技術仕様を詳しく説明してください", max_results=8)
```

## 開発

### テスト実行

```bash
pytest
```

### プロジェクト構造

```
bedrock-kb-mcp-server/
├── src/                    # メインソースコード
│   ├── __init__.py
│   ├── bedrock_client.py   # Bedrock API クライアント
│   ├── config.py           # 環境変数からの設定読み込み
│   ├── models.py           # データクラス
│   ├── parser.py           # API レスポンスパーサー
│   ├── server.py           # MCP サーバー実装
│   └── validation.py       # 入力バリデーション
├── tests/                  # テストコード
├── kb_mcp_server.py        # メインエントリーポイント
├── pyproject.toml          # プロジェクト設定
└── README.md
```

## ライセンス

MIT

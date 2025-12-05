# kk-bedrock-agent-hub-mcp

Amazon Bedrock Knowledge Base にクエリを送信する MCP (Model Context Protocol) サーバーです。

## 概要

**kk-bedrock-agent-hub-mcp** は、AI アシスタント（Claude Desktop、Cursor、Kiro）が Amazon Bedrock Knowledge Base から情報を取得できるようにする `kb_answer` ツールを提供します。

**注意:** このサーバーは `Retrieve` API を使用し、純粋な検索機能のみを提供します。回答生成（RetrieveAndGenerate）は行わず、基盤モデル ARN は不要です。

## 機能

- Bedrock Retrieve API を使用した Knowledge Base 検索
- 環境変数ベースの設定管理
- 検索結果（コンテンツ、ロケーション、スコア）の抽出と返却
- 入力バリデーション

## 環境変数

| 変数名 | 必須 | デフォルト | 説明 |
|--------|------|------------|------|
| `AWS_REGION` | いいえ | `ap-northeast-1` | AWS リージョン |
| `BEDROCK_KB_ID` | はい | - | Knowledge Base ID |
| `AWS_PROFILE` | いいえ | - | AWS 認証プロファイル |

### 環境変数の設定例

```bash
# Linux/macOS
export AWS_REGION="ap-northeast-1"
export BEDROCK_KB_ID="your-knowledge-base-id"

# Windows (PowerShell)
$env:AWS_REGION = "ap-northeast-1"
$env:BEDROCK_KB_ID = "your-knowledge-base-id"
```

## インストール

### 方法1: Git Clone（推奨）

```bash
# リポジトリをクローン
git clone https://github.com/kawanishi0117/mcp-bedrock-kb.git
cd mcp-bedrock-kb

# 依存関係をインストール
pip install -e .
```

### 方法2: pip で直接インストール

```bash
pip install git+https://github.com/kawanishi0117/mcp-bedrock-kb.git
```

## 使用方法

### 直接実行

```bash
python kb_mcp_server.py
```

### コマンドラインから実行（pip インストール後）

```bash
bedrock-kb-mcp
```


## MCP クライアント設定

クローンしたディレクトリの絶対パスを指定してください。

### Claude Desktop

`claude_desktop_config.json` に以下を追加:

```json
{
  "mcpServers": {
    "kk-bedrock-agent-hub-mcp": {
      "command": "python",
      "args": ["/path/to/mcp-bedrock-kb/kb_mcp_server.py"],
      "env": {
        "BEDROCK_KB_ID": "your-kb-id"
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
    "kk-bedrock-agent-hub-mcp": {
      "command": "python",
      "args": ["/path/to/mcp-bedrock-kb/kb_mcp_server.py"],
      "env": {
        "BEDROCK_KB_ID": "your-kb-id"
      }
    }
  }
}
```

### Kiro

`~/.kiro/settings/mcp.json`（グローバル）または `.kiro/settings/mcp.json`（ワークスペース）に以下を追加:

```json
{
  "mcpServers": {
    "kk-bedrock-agent-hub-mcp": {
      "command": "python",
      "args": ["/path/to/mcp-bedrock-kb/kb_mcp_server.py"],
      "env": {
        "BEDROCK_KB_ID": "your-kb-id"
      }
    }
  }
}
```

### Windows の場合

パスはスラッシュ `/` またはダブルバックスラッシュ `\\` を使用:

```json
{
  "mcpServers": {
    "kk-bedrock-agent-hub-mcp": {
      "command": "python",
      "args": ["C:/Users/username/mcp-bedrock-kb/kb_mcp_server.py"],
      "env": {
        "BEDROCK_KB_ID": "your-kb-id"
      }
    }
  }
}
```

### AWS_PROFILE を使用する場合

AWS 認証プロファイルを指定する場合は `AWS_PROFILE` 環境変数を追加:

```json
{
  "mcpServers": {
    "kk-bedrock-agent-hub-mcp": {
      "command": "python",
      "args": ["/path/to/mcp-bedrock-kb/kb_mcp_server.py"],
      "env": {
        "BEDROCK_KB_ID": "your-kb-id",
        "AWS_PROFILE": "your-profile-name"
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

### レスポンス形式

検索結果は以下の形式で返されます:

```json
{
  "content": "ドキュメントチャンクのテキスト内容",
  "location": {"s3Location": {...}, "type": "S3"},
  "score": 0.85
}
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

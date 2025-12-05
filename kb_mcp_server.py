#!/usr/bin/env python3
"""
Bedrock Knowledge Base MCP Server エントリーポイント

このスクリプトは MCP サーバーを起動するためのメインエントリーポイントです。
stdio モードで実行され、MCP クライアント（Claude Desktop、Cursor、Kiro など）
から呼び出されます。

使用方法:
    python kb_mcp_server.py

環境変数:
    AWS_REGION: AWS リージョン（デフォルト: ap-northeast-1）
    BEDROCK_KB_ID: Knowledge Base ID（必須）
    BEDROCK_MODEL_ARN: 基盤モデルの ARN（必須）
    AWS_PROFILE: AWS 認証プロファイル（オプション）
"""

from src.server import main


if __name__ == "__main__":
    main()

"""
MCP サーバーモジュール

FastMCP を使用して Bedrock Knowledge Base 検索ツールを提供する。
Retrieve API を使用し、純粋な検索機能のみを提供（回答生成なし）。
"""

import json
import boto3
from fastmcp import FastMCP

from src.config import load_config
from src.validation import validate_query, ValidationError
from src.bedrock_client import (
    query_knowledge_base,
    BedrockAuthenticationError,
    BedrockKBNotFoundError,
    BedrockServiceError,
)


# FastMCP サーバーを初期化（要件 4.1: stdio トランスポートモード）
mcp = FastMCP("kk-bedrock-agent-hub-mcp")


@mcp.tool()
def kb_answer(query: str, max_results: int = 4) -> str:
    """
    Amazon Bedrock Knowledge Base を検索し、関連するドキュメントチャンクを返す。
    
    Retrieve API を使用して Knowledge Base から関連ドキュメントを検索する。
    回答生成は行わず、検索結果のみを返す。
    
    Args:
        query: Knowledge Base に送信する検索クエリ文字列
        max_results: 取得するソースチャンクの最大数（デフォルト: 4、範囲: 1-10）
    
    Returns:
        str: 検索結果を含む JSON 形式の文字列。各結果には content, location, score を含む。
    """
    # 入力バリデーション（要件 3.4）
    try:
        validated_query = validate_query(query)
    except ValidationError as e:
        return json.dumps({
            "error": True,
            "error_type": "ValidationError",
            "message": str(e)
        }, ensure_ascii=False)
    
    # max_results の範囲チェック（要件 2.4）
    if max_results < 1:
        max_results = 1
    elif max_results > 10:
        max_results = 10
    
    # 設定を読み込み（要件 1.1, 1.2, 1.3）
    try:
        config = load_config()
    except ValueError as e:
        return json.dumps({
            "error": True,
            "error_type": "ConfigurationError",
            "message": str(e)
        }, ensure_ascii=False)
    
    # Bedrock クライアントを作成
    client = boto3.client(
        "bedrock-agent-runtime",
        region_name=config.aws_region
    )
    
    # Knowledge Base に Retrieve API でクエリを実行（要件 2.1）
    try:
        response = query_knowledge_base(
            client=client,
            config=config,
            query=validated_query,
            max_results=max_results
        )
    except BedrockAuthenticationError as e:
        return json.dumps({
            "error": True,
            "error_type": "AuthenticationError",
            "message": str(e)
        }, ensure_ascii=False)
    except BedrockKBNotFoundError as e:
        return json.dumps({
            "error": True,
            "error_type": "NotFoundError",
            "message": str(e)
        }, ensure_ascii=False)
    except BedrockServiceError as e:
        return json.dumps({
            "error": True,
            "error_type": "ServiceError",
            "message": str(e)
        }, ensure_ascii=False)
    
    # 検索結果をフォーマット（要件 2.2, 2.3, 2.5）
    results_output = []
    for result in response.results:
        result_dict = {
            "content": result.content,
            "location": result.location,
            "score": result.score
        }
        results_output.append(result_dict)
    
    return json.dumps(results_output, ensure_ascii=False, indent=2)


def main() -> None:
    """
    MCP サーバーのエントリーポイント。
    
    stdio モードでサーバーを起動する（要件 4.1）。
    """
    mcp.run()


# エントリーポイント（stdio モード）
if __name__ == "__main__":
    main()

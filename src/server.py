"""
MCP サーバーモジュール

FastMCP を使用して Bedrock Knowledge Base クエリツールを提供する。
"""

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


# FastMCP サーバーを初期化
mcp = FastMCP("bedrock-kb-mcp")


@mcp.tool()
def kb_answer(query: str, max_results: int = 4) -> str:
    """
    Amazon Bedrock Knowledge Base に対してクエリを実行し、回答を取得する。
    
    Args:
        query: Knowledge Base に送信するクエリ文字列
        max_results: 取得するソースチャンクの最大数（デフォルト: 4、範囲: 1-10）
    
    Returns:
        str: Knowledge Base からの回答と引用情報を含む文字列
    """
    # 入力バリデーション
    try:
        validated_query = validate_query(query)
    except ValidationError as e:
        return f"エラー: {str(e)}"
    
    # max_results の範囲チェック
    if max_results < 1:
        max_results = 1
    elif max_results > 10:
        max_results = 10
    
    # 設定を読み込み
    try:
        config = load_config()
    except ValueError as e:
        return f"設定エラー: {str(e)}"
    
    # Bedrock クライアントを作成
    client = boto3.client(
        "bedrock-agent-runtime",
        region_name=config.aws_region
    )
    
    # Knowledge Base にクエリを実行
    try:
        response = query_knowledge_base(
            client=client,
            config=config,
            query=validated_query,
            max_results=max_results
        )
    except BedrockAuthenticationError as e:
        return f"認証エラー: {str(e)}"
    except BedrockKBNotFoundError as e:
        return f"KB未検出エラー: {str(e)}"
    except BedrockServiceError as e:
        return f"サービスエラー: {str(e)}"
    
    # レスポンスをフォーマット
    result_parts = [response.answer]
    
    # 引用情報を追加
    if response.citations:
        result_parts.append("\n\n--- 引用情報 ---")
        for i, citation in enumerate(response.citations, 1):
            result_parts.append(f"\n[{i}] {citation.content[:200]}...")
            if citation.location:
                # S3 ロケーションを表示
                s3_loc = citation.location.get("s3Location", {})
                if s3_loc:
                    uri = s3_loc.get("uri", "不明")
                    result_parts.append(f"    ソース: {uri}")
            if citation.score is not None:
                result_parts.append(f"    スコア: {citation.score:.4f}")
    
    return "".join(result_parts)


def main() -> None:
    """
    MCP サーバーのエントリーポイント。
    
    stdio モードでサーバーを起動する。
    """
    mcp.run()


# エントリーポイント（stdio モード）
if __name__ == "__main__":
    main()

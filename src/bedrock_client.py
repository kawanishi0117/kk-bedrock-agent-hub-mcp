"""
Bedrock クライアントモジュール

Amazon Bedrock Agent Runtime の RetrieveAndGenerate API を呼び出す。
"""

from typing import Any

from botocore.exceptions import ClientError, BotoCoreError

from src.config import KBConfig
from src.models import KBResponse
from src.parser import parse_response


# カスタム例外クラス
class BedrockAuthenticationError(Exception):
    """認証エラーを示す例外"""


class BedrockKBNotFoundError(Exception):
    """Knowledge Base が見つからないエラーを示す例外"""


class BedrockServiceError(Exception):
    """Bedrock サービスの汎用エラーを示す例外"""


def build_retrieve_and_generate_request(
    config: KBConfig,
    query: str,
    max_results: int = 4
) -> dict[str, Any]:
    """
    RetrieveAndGenerate API 用のリクエストボディを構築する。
    
    Args:
        config: Knowledge Base の設定
        query: ユーザーからのクエリ文字列
        max_results: 取得するソースチャンクの最大数（デフォルト: 4）
    
    Returns:
        dict: API リクエスト用のパラメータ辞書
    """
    return {
        "input": {
            "text": query
        },
        "retrieveAndGenerateConfiguration": {
            "type": "KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": config.kb_id,
                "modelArn": config.model_arn,
                "retrievalConfiguration": {
                    "vectorSearchConfiguration": {
                        "numberOfResults": max_results
                    }
                }
            }
        }
    }


def query_knowledge_base(
    client: Any,
    config: KBConfig,
    query: str,
    max_results: int = 4
) -> KBResponse:
    """
    Bedrock Knowledge Base に対して RetrieveAndGenerate API を呼び出す。
    
    Args:
        client: boto3 の bedrock-agent-runtime クライアント
        config: Knowledge Base の設定
        query: ユーザーからのクエリ文字列
        max_results: 取得するソースチャンクの最大数（デフォルト: 4）
    
    Returns:
        KBResponse: パース済みの回答と引用を含むレスポンス
    
    Raises:
        BedrockAuthenticationError: 認証エラーが発生した場合
        BedrockKBNotFoundError: Knowledge Base が見つからない場合
        BedrockServiceError: その他の Bedrock サービスエラーが発生した場合
    """
    # リクエストボディを構築
    request_params = build_retrieve_and_generate_request(config, query, max_results)
    
    try:
        # Bedrock Agent Runtime API を呼び出し
        response = client.retrieve_and_generate(**request_params)
        
        # レスポンスをパースして返す
        return parse_response(response)
    
    except ClientError as e:
        # エラーコードを取得
        error_code = e.response.get("Error", {}).get("Code", "")
        error_message = e.response.get("Error", {}).get("Message", str(e))
        
        # 認証エラーの判定
        # AccessDeniedException, UnauthorizedAccessException, 
        # ExpiredTokenException, InvalidIdentityToken などをキャッチ
        auth_error_codes = [
            "AccessDeniedException",
            "UnauthorizedAccessException",
            "ExpiredTokenException",
            "InvalidIdentityToken",
            "UnrecognizedClientException",
        ]
        if error_code in auth_error_codes:
            raise BedrockAuthenticationError(
                f"認証エラー: AWS 認証情報を確認してください。詳細: {error_message}"
            ) from e
        
        # ResourceNotFound エラーの判定
        if error_code == "ResourceNotFoundException":
            raise BedrockKBNotFoundError(
                f"Knowledge Base が見つかりません: KB ID '{config.kb_id}' を確認してください。"
                f"詳細: {error_message}"
            ) from e
        
        # その他の ClientError は汎用エラーとして処理
        raise BedrockServiceError(
            f"Bedrock API エラー ({error_code}): {error_message}"
        ) from e
    
    except BotoCoreError as e:
        # ネットワークエラーなど boto3 の低レベルエラー
        raise BedrockServiceError(
            f"AWS サービス接続エラー: {str(e)}"
        ) from e
    
    except Exception as e:
        # 予期しないエラーも詳細を保持して再送出
        raise BedrockServiceError(
            f"予期しないエラー ({type(e).__name__}): {str(e)}"
        ) from e

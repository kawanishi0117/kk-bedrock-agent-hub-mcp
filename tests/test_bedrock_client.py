"""
Bedrock クライアントのプロパティテスト

**Feature: bedrock-kb-mcp-server, Property 4: リクエスト構築で全パラメータを含む**
**検証対象: 要件 2.1, 2.4**

**Feature: bedrock-kb-mcp-server, Property 6: APIエラーで例外詳細を保持**
**検証対象: 要件 3.3**
"""

from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError, BotoCoreError
from hypothesis import given, strategies as st, settings

from src.config import KBConfig
from src.bedrock_client import (
    build_retrieve_and_generate_request,
    query_knowledge_base,
    BedrockAuthenticationError,
    BedrockKBNotFoundError,
    BedrockServiceError,
)


# 有効な設定値を生成するストラテジー
# 空文字列や空白のみは除外
valid_string = st.text(
    alphabet=st.characters(
        whitelist_categories=("L", "N"),
        whitelist_characters="-_:/"
    ),
    min_size=1,
    max_size=100
).filter(lambda s: s.strip() != "")

# AWS リージョン形式の文字列
aws_region_strategy = st.sampled_from([
    "ap-northeast-1",
    "us-east-1",
    "us-west-2",
    "eu-west-1",
    "ap-southeast-1",
])

# max_results の有効な範囲（1-10 の整数）
max_results_strategy = st.integers(min_value=1, max_value=10)

# クエリ文字列（空でない文字列）
query_strategy = st.text(min_size=1, max_size=500).filter(lambda s: s.strip() != "")


class TestProperty4RequestBuilding:
    """
    **Feature: bedrock-kb-mcp-server, Property 4: リクエスト構築で全パラメータを含む**
    **検証対象: 要件 2.1, 2.4**

    任意のクエリ文字列と max_results 値に対して、構築された API リクエストは以下を含む：
    - 設定された knowledgeBaseId
    - 設定された modelArn
    - 提供された max_results 値に設定された numberOfResults
    """

    @given(
        kb_id=valid_string,
        model_arn=valid_string,
        aws_region=aws_region_strategy,
        query=query_strategy,
        max_results=max_results_strategy,
    )
    @settings(max_examples=100)
    def test_request_contains_knowledge_base_id(
        self,
        kb_id: str,
        model_arn: str,
        aws_region: str,
        query: str,
        max_results: int,
    ):
        """
        任意の設定値に対して、構築されたリクエストには
        設定された knowledgeBaseId が含まれる。
        """
        config = KBConfig(
            aws_region=aws_region,
            kb_id=kb_id,
            model_arn=model_arn,
        )

        request = build_retrieve_and_generate_request(config, query, max_results)

        # knowledgeBaseId が正しく設定されていることを検証
        kb_config = request["retrieveAndGenerateConfiguration"]["knowledgeBaseConfiguration"]
        assert kb_config["knowledgeBaseId"] == kb_id

    @given(
        kb_id=valid_string,
        model_arn=valid_string,
        aws_region=aws_region_strategy,
        query=query_strategy,
        max_results=max_results_strategy,
    )
    @settings(max_examples=100)
    def test_request_contains_model_arn(
        self,
        kb_id: str,
        model_arn: str,
        aws_region: str,
        query: str,
        max_results: int,
    ):
        """
        任意の設定値に対して、構築されたリクエストには
        設定された modelArn が含まれる。
        """
        config = KBConfig(
            aws_region=aws_region,
            kb_id=kb_id,
            model_arn=model_arn,
        )

        request = build_retrieve_and_generate_request(config, query, max_results)

        # modelArn が正しく設定されていることを検証
        kb_config = request["retrieveAndGenerateConfiguration"]["knowledgeBaseConfiguration"]
        assert kb_config["modelArn"] == model_arn

    @given(
        kb_id=valid_string,
        model_arn=valid_string,
        aws_region=aws_region_strategy,
        query=query_strategy,
        max_results=max_results_strategy,
    )
    @settings(max_examples=100)
    def test_request_contains_number_of_results(
        self,
        kb_id: str,
        model_arn: str,
        aws_region: str,
        query: str,
        max_results: int,
    ):
        """
        任意の max_results 値に対して、構築されたリクエストには
        numberOfResults が正しく設定される。
        """
        config = KBConfig(
            aws_region=aws_region,
            kb_id=kb_id,
            model_arn=model_arn,
        )

        request = build_retrieve_and_generate_request(config, query, max_results)

        # numberOfResults が正しく設定されていることを検証
        kb_config = request["retrieveAndGenerateConfiguration"]["knowledgeBaseConfiguration"]
        retrieval_config = kb_config["retrievalConfiguration"]["vectorSearchConfiguration"]
        assert retrieval_config["numberOfResults"] == max_results

    @given(
        kb_id=valid_string,
        model_arn=valid_string,
        aws_region=aws_region_strategy,
        query=query_strategy,
        max_results=max_results_strategy,
    )
    @settings(max_examples=100)
    def test_request_contains_query_text(
        self,
        kb_id: str,
        model_arn: str,
        aws_region: str,
        query: str,
        max_results: int,
    ):
        """
        任意のクエリ文字列に対して、構築されたリクエストには
        input.text にクエリが含まれる。
        """
        config = KBConfig(
            aws_region=aws_region,
            kb_id=kb_id,
            model_arn=model_arn,
        )

        request = build_retrieve_and_generate_request(config, query, max_results)

        # クエリテキストが正しく設定されていることを検証
        assert request["input"]["text"] == query

    @given(
        kb_id=valid_string,
        model_arn=valid_string,
        aws_region=aws_region_strategy,
        query=query_strategy,
    )
    @settings(max_examples=100)
    def test_default_max_results_is_four(
        self,
        kb_id: str,
        model_arn: str,
        aws_region: str,
        query: str,
    ):
        """
        max_results を指定しない場合、デフォルト値 4 が使用される。
        """
        config = KBConfig(
            aws_region=aws_region,
            kb_id=kb_id,
            model_arn=model_arn,
        )

        # max_results を指定せずに呼び出し
        request = build_retrieve_and_generate_request(config, query)

        # デフォルト値 4 が設定されていることを検証
        kb_config = request["retrieveAndGenerateConfiguration"]["knowledgeBaseConfiguration"]
        retrieval_config = kb_config["retrievalConfiguration"]["vectorSearchConfiguration"]
        assert retrieval_config["numberOfResults"] == 4

    @given(
        kb_id=valid_string,
        model_arn=valid_string,
        aws_region=aws_region_strategy,
        query=query_strategy,
        max_results=max_results_strategy,
    )
    @settings(max_examples=100)
    def test_request_structure_is_valid(
        self,
        kb_id: str,
        model_arn: str,
        aws_region: str,
        query: str,
        max_results: int,
    ):
        """
        任意の入力に対して、構築されたリクエストは
        RetrieveAndGenerate API の期待する構造を持つ。
        """
        config = KBConfig(
            aws_region=aws_region,
            kb_id=kb_id,
            model_arn=model_arn,
        )

        request = build_retrieve_and_generate_request(config, query, max_results)

        # 必須のトップレベルキーが存在することを検証
        assert "input" in request
        assert "retrieveAndGenerateConfiguration" in request

        # input 構造の検証
        assert "text" in request["input"]

        # retrieveAndGenerateConfiguration 構造の検証
        rag_config = request["retrieveAndGenerateConfiguration"]
        assert rag_config["type"] == "KNOWLEDGE_BASE"
        assert "knowledgeBaseConfiguration" in rag_config

        # knowledgeBaseConfiguration 構造の検証
        kb_config = rag_config["knowledgeBaseConfiguration"]
        assert "knowledgeBaseId" in kb_config
        assert "modelArn" in kb_config
        assert "retrievalConfiguration" in kb_config

        # retrievalConfiguration 構造の検証
        retrieval_config = kb_config["retrievalConfiguration"]
        assert "vectorSearchConfiguration" in retrieval_config
        assert "numberOfResults" in retrieval_config["vectorSearchConfiguration"]


# エラーメッセージ生成用のストラテジー
error_message_strategy = st.text(min_size=1, max_size=200).filter(lambda s: s.strip() != "")

# エラーコード生成用のストラテジー（認証エラー以外）
non_auth_error_codes = st.sampled_from([
    "ThrottlingException",
    "ServiceUnavailableException",
    "InternalServerException",
    "ValidationException",
    "ConflictException",
])


class TestProperty6ErrorDetailsPreservation:
    """
    **Feature: bedrock-kb-mcp-server, Property 6: APIエラーで例外詳細を保持**
    **検証対象: 要件 3.3**

    任意の Bedrock API 呼び出しで発生した例外に対して、
    エラーレスポンスは元の例外メッセージまたは型情報を含む。
    """

    @given(
        kb_id=valid_string,
        model_arn=valid_string,
        aws_region=aws_region_strategy,
        query=query_strategy,
        error_message=error_message_strategy,
        error_code=non_auth_error_codes,
    )
    @settings(max_examples=100)
    def test_client_error_preserves_error_message(
        self,
        kb_id: str,
        model_arn: str,
        aws_region: str,
        query: str,
        error_message: str,
        error_code: str,
    ):
        """
        任意の ClientError に対して、発生する例外は
        元のエラーメッセージを含む。
        """
        config = KBConfig(
            aws_region=aws_region,
            kb_id=kb_id,
            model_arn=model_arn,
        )

        # ClientError をシミュレートするモッククライアント
        mock_client = MagicMock()
        mock_client.retrieve_and_generate.side_effect = ClientError(
            error_response={
                "Error": {
                    "Code": error_code,
                    "Message": error_message,
                }
            },
            operation_name="RetrieveAndGenerate",
        )

        # エラーが発生し、元のメッセージが保持されることを検証
        with pytest.raises(BedrockServiceError) as exc_info:
            query_knowledge_base(mock_client, config, query)

        # 元のエラーメッセージが例外に含まれていることを確認
        assert error_message in str(exc_info.value)
        # エラーコードも含まれていることを確認
        assert error_code in str(exc_info.value)

    @given(
        kb_id=valid_string,
        model_arn=valid_string,
        aws_region=aws_region_strategy,
        query=query_strategy,
        error_message=error_message_strategy,
    )
    @settings(max_examples=100)
    def test_botocore_error_preserves_details(
        self,
        kb_id: str,
        model_arn: str,
        aws_region: str,
        query: str,
        error_message: str,
    ):
        """
        任意の BotoCoreError に対して、発生する例外は
        元のエラー詳細を含む。
        """
        config = KBConfig(
            aws_region=aws_region,
            kb_id=kb_id,
            model_arn=model_arn,
        )

        # BotoCoreError をシミュレートするモッククライアント
        mock_client = MagicMock()
        # BotoCoreError は直接インスタンス化できないため、サブクラスを使用
        mock_client.retrieve_and_generate.side_effect = BotoCoreError()

        # エラーが発生することを検証
        with pytest.raises(BedrockServiceError) as exc_info:
            query_knowledge_base(mock_client, config, query)

        # AWS サービス接続エラーであることを確認
        assert "AWS サービス接続エラー" in str(exc_info.value)

    @given(
        kb_id=valid_string,
        model_arn=valid_string,
        aws_region=aws_region_strategy,
        query=query_strategy,
        error_message=error_message_strategy,
    )
    @settings(max_examples=100)
    def test_generic_exception_preserves_type_and_message(
        self,
        kb_id: str,
        model_arn: str,
        aws_region: str,
        query: str,
        error_message: str,
    ):
        """
        任意の予期しない例外に対して、発生する例外は
        元の例外の型名とメッセージを含む。
        """
        config = KBConfig(
            aws_region=aws_region,
            kb_id=kb_id,
            model_arn=model_arn,
        )

        # 予期しない例外をシミュレートするモッククライアント
        mock_client = MagicMock()
        mock_client.retrieve_and_generate.side_effect = RuntimeError(error_message)

        # エラーが発生し、型名とメッセージが保持されることを検証
        with pytest.raises(BedrockServiceError) as exc_info:
            query_knowledge_base(mock_client, config, query)

        # 元の例外の型名が含まれていることを確認
        assert "RuntimeError" in str(exc_info.value)
        # 元のエラーメッセージが含まれていることを確認
        assert error_message in str(exc_info.value)

    @given(
        kb_id=valid_string,
        model_arn=valid_string,
        aws_region=aws_region_strategy,
        query=query_strategy,
        error_message=error_message_strategy,
        error_code=non_auth_error_codes,
    )
    @settings(max_examples=100)
    def test_exception_chain_is_preserved(
        self,
        kb_id: str,
        model_arn: str,
        aws_region: str,
        query: str,
        error_message: str,
        error_code: str,
    ):
        """
        任意の例外に対して、例外チェーン（__cause__）が保持される。
        """
        config = KBConfig(
            aws_region=aws_region,
            kb_id=kb_id,
            model_arn=model_arn,
        )

        # ClientError をシミュレートするモッククライアント
        original_error = ClientError(
            error_response={
                "Error": {
                    "Code": error_code,
                    "Message": error_message,
                }
            },
            operation_name="RetrieveAndGenerate",
        )
        mock_client = MagicMock()
        mock_client.retrieve_and_generate.side_effect = original_error

        # エラーが発生し、例外チェーンが保持されることを検証
        with pytest.raises(BedrockServiceError) as exc_info:
            query_knowledge_base(mock_client, config, query)

        # 元の例外が __cause__ として保持されていることを確認
        assert exc_info.value.__cause__ is original_error



class TestAuthenticationErrorHandling:
    """
    認証エラーハンドリングのユニットテスト
    **検証対象: 要件 3.1**
    """

    def _create_config(self) -> KBConfig:
        """テスト用の設定を作成"""
        return KBConfig(
            aws_region="ap-northeast-1",
            kb_id="test-kb-id",
            model_arn="arn:aws:bedrock:ap-northeast-1::foundation-model/test",
        )

    def test_access_denied_raises_authentication_error(self):
        """AccessDeniedException は BedrockAuthenticationError を発生させる"""
        config = self._create_config()
        mock_client = MagicMock()
        mock_client.retrieve_and_generate.side_effect = ClientError(
            error_response={
                "Error": {
                    "Code": "AccessDeniedException",
                    "Message": "User is not authorized to perform this action",
                }
            },
            operation_name="RetrieveAndGenerate",
        )

        with pytest.raises(BedrockAuthenticationError) as exc_info:
            query_knowledge_base(mock_client, config, "test query")

        assert "認証エラー" in str(exc_info.value)
        assert "AWS 認証情報を確認" in str(exc_info.value)

    def test_unauthorized_access_raises_authentication_error(self):
        """UnauthorizedAccessException は BedrockAuthenticationError を発生させる"""
        config = self._create_config()
        mock_client = MagicMock()
        mock_client.retrieve_and_generate.side_effect = ClientError(
            error_response={
                "Error": {
                    "Code": "UnauthorizedAccessException",
                    "Message": "Unauthorized access",
                }
            },
            operation_name="RetrieveAndGenerate",
        )

        with pytest.raises(BedrockAuthenticationError) as exc_info:
            query_knowledge_base(mock_client, config, "test query")

        assert "認証エラー" in str(exc_info.value)

    def test_expired_token_raises_authentication_error(self):
        """ExpiredTokenException は BedrockAuthenticationError を発生させる"""
        config = self._create_config()
        mock_client = MagicMock()
        mock_client.retrieve_and_generate.side_effect = ClientError(
            error_response={
                "Error": {
                    "Code": "ExpiredTokenException",
                    "Message": "The security token included in the request is expired",
                }
            },
            operation_name="RetrieveAndGenerate",
        )

        with pytest.raises(BedrockAuthenticationError) as exc_info:
            query_knowledge_base(mock_client, config, "test query")

        assert "認証エラー" in str(exc_info.value)

    def test_invalid_identity_token_raises_authentication_error(self):
        """InvalidIdentityToken は BedrockAuthenticationError を発生させる"""
        config = self._create_config()
        mock_client = MagicMock()
        mock_client.retrieve_and_generate.side_effect = ClientError(
            error_response={
                "Error": {
                    "Code": "InvalidIdentityToken",
                    "Message": "Token is invalid",
                }
            },
            operation_name="RetrieveAndGenerate",
        )

        with pytest.raises(BedrockAuthenticationError) as exc_info:
            query_knowledge_base(mock_client, config, "test query")

        assert "認証エラー" in str(exc_info.value)

    def test_unrecognized_client_raises_authentication_error(self):
        """UnrecognizedClientException は BedrockAuthenticationError を発生させる"""
        config = self._create_config()
        mock_client = MagicMock()
        mock_client.retrieve_and_generate.side_effect = ClientError(
            error_response={
                "Error": {
                    "Code": "UnrecognizedClientException",
                    "Message": "The security token is invalid",
                }
            },
            operation_name="RetrieveAndGenerate",
        )

        with pytest.raises(BedrockAuthenticationError) as exc_info:
            query_knowledge_base(mock_client, config, "test query")

        assert "認証エラー" in str(exc_info.value)


class TestKBNotFoundErrorHandling:
    """
    Knowledge Base 未検出エラーハンドリングのユニットテスト
    **検証対象: 要件 3.2**
    """

    def _create_config(self, kb_id: str = "invalid-kb-id") -> KBConfig:
        """テスト用の設定を作成"""
        return KBConfig(
            aws_region="ap-northeast-1",
            kb_id=kb_id,
            model_arn="arn:aws:bedrock:ap-northeast-1::foundation-model/test",
        )

    def test_resource_not_found_raises_kb_not_found_error(self):
        """ResourceNotFoundException は BedrockKBNotFoundError を発生させる"""
        kb_id = "non-existent-kb-id"
        config = self._create_config(kb_id)
        mock_client = MagicMock()
        mock_client.retrieve_and_generate.side_effect = ClientError(
            error_response={
                "Error": {
                    "Code": "ResourceNotFoundException",
                    "Message": f"Knowledge base {kb_id} not found",
                }
            },
            operation_name="RetrieveAndGenerate",
        )

        with pytest.raises(BedrockKBNotFoundError) as exc_info:
            query_knowledge_base(mock_client, config, "test query")

        # エラーメッセージに KB ID が含まれていることを確認
        assert kb_id in str(exc_info.value)
        assert "Knowledge Base が見つかりません" in str(exc_info.value)

    def test_kb_not_found_error_includes_guidance(self):
        """KB 未検出エラーには KB ID 確認のガイダンスが含まれる"""
        kb_id = "test-kb-123"
        config = self._create_config(kb_id)
        mock_client = MagicMock()
        mock_client.retrieve_and_generate.side_effect = ClientError(
            error_response={
                "Error": {
                    "Code": "ResourceNotFoundException",
                    "Message": "Resource not found",
                }
            },
            operation_name="RetrieveAndGenerate",
        )

        with pytest.raises(BedrockKBNotFoundError) as exc_info:
            query_knowledge_base(mock_client, config, "test query")

        # KB ID 確認のガイダンスが含まれていることを確認
        assert "確認してください" in str(exc_info.value)

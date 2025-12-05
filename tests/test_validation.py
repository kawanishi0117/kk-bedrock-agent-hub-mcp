"""
入力バリデーションモジュールのプロパティテスト

**Feature: bedrock-kb-mcp-server, Property 5: 空白のみのクエリを拒否**
**検証対象: 要件 3.4**
"""

import pytest
from hypothesis import given, strategies as st, settings

from src.validation import validate_query, ValidationError


# 空白文字のみで構成される文字列を生成するストラテジー
# スペース、タブ、改行、キャリッジリターン、フォームフィードなど
whitespace_only_strategy = st.text(
    alphabet=st.sampled_from([" ", "\t", "\n", "\r", "\f", "\v"]),
    min_size=0,
    max_size=100
)

# 有効なクエリ文字列を生成するストラテジー
# 少なくとも1つの非空白文字を含む
valid_query_strategy = st.text(
    min_size=1,
    max_size=500
).filter(lambda s: s.strip() != "")


class TestProperty5WhitespaceValidation:
    """
    **Feature: bedrock-kb-mcp-server, Property 5: 空白のみのクエリを拒否**
    **検証対象: 要件 3.4**

    任意の空白文字（スペース、タブ、改行）のみで構成される文字列に対して、
    validate_query() を呼び出すと ValidationError が発生する。
    """

    @given(whitespace_query=whitespace_only_strategy)
    @settings(max_examples=100)
    def test_whitespace_only_queries_are_rejected(self, whitespace_query: str):
        """
        任意の空白のみの文字列に対して、validate_query() は
        ValidationError を発生させる。
        """
        with pytest.raises(ValidationError):
            validate_query(whitespace_query)

    @given(valid_query=valid_query_strategy)
    @settings(max_examples=100)
    def test_valid_queries_return_trimmed_string(self, valid_query: str):
        """
        任意の有効なクエリ（少なくとも1つの非空白文字を含む）に対して、
        validate_query() はトリム済みの文字列を返す。
        """
        result = validate_query(valid_query)

        # 結果はトリム済みであること
        assert result == valid_query.strip()
        # 結果は空でないこと
        assert len(result) > 0

    @given(
        prefix=st.text(alphabet=" \t\n\r", min_size=0, max_size=20),
        content=valid_query_strategy,
        suffix=st.text(alphabet=" \t\n\r", min_size=0, max_size=20),
    )
    @settings(max_examples=100)
    def test_queries_with_surrounding_whitespace_are_trimmed(
        self, prefix: str, content: str, suffix: str
    ):
        """
        任意の有効なコンテンツを持つクエリに対して、前後の空白が
        トリムされた結果が返される。
        """
        query = prefix + content + suffix
        result = validate_query(query)

        # 結果は元のコンテンツのトリム済み版と等しい
        assert result == content.strip()

    def test_empty_string_is_rejected(self):
        """
        空文字列は ValidationError を発生させる。
        """
        with pytest.raises(ValidationError):
            validate_query("")

    def test_none_is_rejected(self):
        """
        None は ValidationError を発生させる。
        """
        with pytest.raises(ValidationError):
            validate_query(None)

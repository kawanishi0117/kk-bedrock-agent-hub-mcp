"""
レスポンスパーサーのプロパティテスト

**Feature: bedrock-kb-mcp-server, Property 3: レスポンスパースで全フィールドを抽出**
**検証対象: 要件 2.2, 2.3, 2.5**
"""

from hypothesis import given, strategies as st, settings

from src.parser import parse_retrieve_response
from src.models import RetrievalResult, KBResponse


# ロケーション情報を生成するストラテジー
location_strategy = st.fixed_dictionaries({
    "type": st.sampled_from(["S3", "WEB", "CONFLUENCE"]),
    "s3Location": st.fixed_dictionaries({
        "uri": st.text(min_size=1, max_size=100).filter(lambda s: s.strip() != ""),
    }),
})

# スコアを生成するストラテジー（None または 0.0-1.0 の float）
score_strategy = st.one_of(
    st.none(),
    st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
)

# 単一の検索結果を生成するストラテジー
retrieval_result_strategy = st.fixed_dictionaries({
    "content": st.fixed_dictionaries({
        "text": st.text(min_size=0, max_size=500),
    }),
    "location": location_strategy,
    "score": score_strategy,
})

# 有効な Bedrock Retrieve API レスポンスを生成するストラテジー
valid_retrieve_response_strategy = st.fixed_dictionaries({
    "retrievalResults": st.lists(retrieval_result_strategy, min_size=0, max_size=10),
})


class TestProperty3ResponseParsing:
    """
    **Feature: bedrock-kb-mcp-server, Property 3: レスポンスパースで全フィールドを抽出**
    **検証対象: 要件 2.2, 2.3, 2.5**

    任意の有効な Bedrock Retrieve API レスポンスに対して、
    パース結果は以下を満たす：
    - results の数は retrievalResults の数と等しい
    - 各結果は retrievalResults から抽出された content, location, score を含む
    """

    @given(response=valid_retrieve_response_strategy)
    @settings(max_examples=100)
    def test_results_count_matches_retrieval_results(self, response: dict):
        """
        任意の有効なレスポンスに対して、パース結果の results 数は
        元のレスポンスの retrievalResults 数と等しい。
        """
        result = parse_retrieve_response(response)

        expected_count = len(response.get("retrievalResults", []))
        assert len(result.results) == expected_count

    @given(response=valid_retrieve_response_strategy)
    @settings(max_examples=100)
    def test_result_fields_match_source(self, response: dict):
        """
        任意の有効なレスポンスに対して、各結果の content, location, score は
        元の retrievalResults の値と一致する。
        """
        result = parse_retrieve_response(response)

        expected_items = response.get("retrievalResults", [])

        # 各結果が正しくパースされていることを検証
        assert len(result.results) == len(expected_items)

        for parsed_result, item in zip(result.results, expected_items):
            # content の検証
            expected_content = item.get("content", {}).get("text", "")
            assert parsed_result.content == expected_content

            # location の検証
            expected_location = item.get("location", {})
            assert parsed_result.location == expected_location

            # score の検証
            expected_score = item.get("score")
            if expected_score is not None:
                assert parsed_result.score == float(expected_score)
            else:
                assert parsed_result.score is None

    @given(response=valid_retrieve_response_strategy)
    @settings(max_examples=100)
    def test_all_results_are_retrieval_result_type(self, response: dict):
        """
        任意の有効なレスポンスに対して、全ての結果は RetrievalResult 型である。
        """
        result = parse_retrieve_response(response)

        for item in result.results:
            assert isinstance(item, RetrievalResult)

    def test_empty_retrieval_results_returns_empty_list(self):
        """
        retrievalResults が空または存在しない場合、空のリストが返される。
        """
        # retrievalResults が空のレスポンス
        response_empty = {"retrievalResults": []}
        result_empty = parse_retrieve_response(response_empty)
        assert result_empty.results == []

        # retrievalResults が存在しないレスポンス
        response_missing = {}
        result_missing = parse_retrieve_response(response_missing)
        assert result_missing.results == []

    @given(response=valid_retrieve_response_strategy)
    @settings(max_examples=100)
    def test_returns_kb_response_type(self, response: dict):
        """
        任意の有効なレスポンスに対して、戻り値は KBResponse 型である。
        """
        result = parse_retrieve_response(response)
        assert isinstance(result, KBResponse)
